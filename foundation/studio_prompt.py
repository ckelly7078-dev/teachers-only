"""Bounded AI authoring: the model designs parameters, Python authors and validates every question."""
import json
import os
import re
from . import studio, studio_ai

PARAMETERS = {
    'percent':'a determines percentage (5a), b amount (20b)',
    'fraction':'a numerator, a+c denominator, b multiplier',
    'equation':'a coefficient, b solution, c constant',
    'rounding':'a,b form integer, c parity chooses nearest 10 or 100',
    'area':'a,b side lengths',
    'hcf':'a*c and b*c', 'lcm':'a*c and b*c', 'midpoint':'a,b midpoint, c offset',
    'ratio':'a:b parts, c amount per part', 'sequence':'a first term, b difference',
    'binary':'a*b+c converted from binary', 'nth-term':'a first term, b difference',
    'indices':'a,b exponents',
    'discount-budget':'a,b kit price, c discount percentage multiplier; delivery and balance',
    'shopping-discount':'bicycle price £20*a, discount 5*b percent, c pounds left after purchase; three parts reduction, sale price, balance',
    'l-shape':'outer width a+b, height b+c, removed b by c corner',
    'trapezium':'parallel sides 2*a and 2*(a+b), height c',
    'pythagoras':'3a,4a rectangle, diagonal 5a; rate b+c',
    'map-scale':'legs a,b cm, c km per cm',
    'expected-frequency':'a,b,c counter counts; draws with replacement',
    'gradient':'rise a, run b, intercept c',
}
DOMAINS={'easy':(2,6),'standard':(4,12),'challenge':(8,18)}
SHOPPING_EXAMPLE = ('Create three 4-mark shopping discount questions about the reduction, sale price and money left in a budget. '
                    'Include worked solutions and mark schemes.')


class InvalidPlan(studio_ai.StudioAIUnavailable):
    """A rejected response, distinct from an unavailable API or unsupported request."""


def require(condition, message):
    if not condition:
        raise InvalidPlan('AI plan rejected: '+message+' No AI drafts saved.')



def author(path,unit,prompt):
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=500:
        raise ValueError('Describe your questions in 1–500 characters.')
    if not studio_ai.available(): raise studio_ai.StudioAIUnavailable('AI Studio is not configured')
    entries=studio.catalog(path,unit)
    if not entries: raise ValueError('No supported question families for this unit')
    families={e['family']:e for e in entries}
    example=prompt.strip().casefold()==SHOPPING_EXAMPLE.casefold()
    if example:
        if 'shopping-discount' not in families: raise ValueError('Shopping questions are unavailable in this unit.')
        families={'shopping-discount':families['shopping-discount']}
        entries=list(families.values())
    options=[]
    for e in entries:
        f=e['family']; q,ans,steps,rubric=studio.build(f,4,4,4)
        options.append(dict(family=f,label=e['label'],skill=e['skill_label'],marks=len(rubric),
            diagram=f in ('l-shape','trapezium','pythagoras'),example=q,parameters=PARAMETERS[f]))
    # Strict enums are supported by structured output. Use a separate nested
    # schema per difficulty so no plan can mix a standard label with easy values.
    def variant(d, bounds):
        lo,hi=bounds
        return {'type':'object','additionalProperties':False,'required':['family','difficulty','a','b','c'],
                'properties':{'family':{'type':'string','enum':list(families)},
                              'difficulty':{'type':'string','enum':[d]},
                              **{k:{'type':'integer','enum':list(range(lo,hi+1))} for k in 'abc'}}}
    item=variant('standard',DOMAINS['standard']) if example else {'anyOf':[variant(d,v) for d,v in DOMAINS.items()]}
    schema={'type':'object','additionalProperties':False,'required':['supported','reason','count','requested_marks','questions'],
            'properties':{'supported':{'type':'boolean'},'reason':{'type':'string'},
                          'count':{'type':'integer','enum':[3] if example else list(range(11))},
                          'requested_marks':{'type':'integer','enum':[4] if example else list(range(5))},
                          'questions':{'type':'array','items':item}}}
    payload=dict(model=os.environ['KB_STUDIO_MODEL'],store=False,max_output_tokens=1800,
                 instructions=('Interpret the teacher request as a bounded original maths design. Use only supplied families, '
                  'respect the selected unit and any explicit count, topic, difficulty, marks, diagram or context constraints. '
                  'If a requested feature cannot be met exactly by these families, set supported=false with a short reason and no questions. '
                  'If supported, choose distinct parameter tuples for 1–10 questions; default count 5, standard difficulty. '
                  'Domains: easy 2–6, standard 4–12, challenge 8–18 inclusive for a,b,c. Distinct questions must differ in used mathematical values, not just an unused parameter. '
                  'requested_marks is explicit marks per question, or 0 if unspecified. Do not claim official CCEA approval. '
                  'Do not invent new wording, code or mathematical operations. Return the structured plan only.') + (
                  ' This is the built-in shopping example; it is supported. Return exactly three distinct standard shopping-discount designs, each with four marks.' if example else ''),
                 input=json.dumps(dict(unit=unit,request=prompt.strip(),families=options),ensure_ascii=True),
                 text={'format':{'type':'json_schema','name':'question_plan','strict':True,'schema':schema}})
    response=studio_ai.send(payload)
    try:
        rows=accept(response,unit,families,known_example=example)
        if example:
            require(len(rows)==3 and all(r['family']=='shopping-discount' and r['marks']==4 for r in rows),
                    'the built-in example requires three four-mark shopping questions.')
        return rows
    except InvalidPlan as exc:
        if not example: raise
        # Only the exact built-in example has an unambiguous local equivalent.
        # No retry or extra API charge. Never persist any invalid AI plan.
        rows=studio.generate(path,unit,'shopping-discount','standard',3)
        return [dict(r,model_role='Local fallback: the AI plan was rejected; no additional API call.',
                     generation_notice=str(exc)+' Generated the built-in example locally instead.') for r in rows]



def accept(response,unit,families,known_example=False):
    try:
        require(isinstance(response,dict) and response.get('status')=='completed','the model response did not complete.')
        parts=[p for x in response['output'] if x['type']=='message' for p in x['content']]
        require(len(parts)==1 and parts[0].get('type')=='output_text','the model did not return a single structured text plan.')
        plan=json.loads(parts[0]['text'],object_pairs_hook=studio_ai.unique_keys)
        require(type(plan) is dict and set(plan)=={'supported','reason','count','requested_marks','questions'},'unexpected plan fields.')
        require(type(plan['supported']) is bool and type(plan['reason']) is str and len(plan['reason'])<=240,'invalid support flag or reason.')
        if not plan['supported']:
            require(not known_example,'the model declined the built-in supported example.')
            require(plan['questions']==[],'unsupported response included question designs.')
            raise studio_ai.StudioAIUnavailable('Request is outside supported question designs. '+plan['reason'])
        count,marks,items=plan['count'],plan['requested_marks'],plan['questions']
        require(type(count) is int and 1<=count<=10 and type(items) is list and len(items)==count,'question count does not match the plan.')
        require(type(marks) is int and 0<=marks<=4,'unsupported requested mark total.')
        rows=[]; seen=set()
        for item in items:
            require(type(item) is dict and set(item)=={'family','difficulty','a','b','c'},'unexpected question fields.')
            f,d=item['family'],item['difficulty']; a,b,c=(item[k] for k in 'abc')
            require(type(f) is str and f in families and type(d) is str and d in DOMAINS,'family or difficulty is not supported.')
            lo,hi=DOMAINS[d]
            require(all(type(x) is int and lo<=x<=hi for x in (a,b,c)),'parameters are outside the selected difficulty range.')
            meta={k:v for k,v in families[f].items() if k not in ('family','label')}
            row=studio.make_row(unit,f,d,a,b,c,meta)
            require(row['question'] not in seen,'duplicate questions.')
            require(not marks or row['marks']==marks,'question marks do not match the plan.')
            seen.add(row['question'])
            rows.append(dict(row,mode='model',model_role='AI-designed bounded mathematical parameters; locally constructed question',
                             validation='Independent numeric check passed after AI parameter design; proposed rubric requires teacher review'))
        return rows
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise InvalidPlan('AI plan rejected: malformed or mathematically invalid plan. No AI drafts saved.') from exc
