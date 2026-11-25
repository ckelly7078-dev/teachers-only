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


def author(path,unit,prompt):
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=500:
        raise ValueError('Describe your questions in 1–500 characters.')
    if not studio_ai.available(): raise studio_ai.StudioAIUnavailable('AI Studio is not configured')
    entries=studio.catalog(path,unit)
    if not entries: raise ValueError('No supported question families for this unit')
    families={e['family']:e for e in entries}
    options=[]
    for e in entries:
        f=e['family']; q,ans,steps,rubric=studio.build(f,4,4,4)
        options.append(dict(family=f,label=e['label'],skill=e['skill_label'],marks=len(rubric),
            diagram=f in ('l-shape','trapezium','pythagoras'),example=q,parameters=PARAMETERS[f]))
    item={'type':'object','additionalProperties':False,'required':['family','difficulty','a','b','c'],
          'properties':{'family':{'type':'string','enum':list(families)},'difficulty':{'type':'string','enum':list(DOMAINS)},
                        **{k:{'type':'integer'} for k in 'abc'}}}
    schema={'type':'object','additionalProperties':False,'required':['supported','reason','count','requested_marks','questions'],
            'properties':{'supported':{'type':'boolean'},'reason':{'type':'string'},'count':{'type':'integer'},
                          'requested_marks':{'type':'integer'},'questions':{'type':'array','items':item}}}
    payload=dict(model=os.environ['KB_STUDIO_MODEL'],store=False,max_output_tokens=1800,
                 instructions=('Interpret the teacher request as a bounded original maths design. Use only supplied families, '
                  'respect the selected unit and any explicit count, topic, difficulty, marks, diagram or context constraints. '
                  'If a requested feature cannot be met exactly by these families, set supported=false with a short reason and no questions. '
                  'If supported, choose distinct parameter tuples for 1–10 questions; default count 5, standard difficulty. '
                  'Domains: easy 2–6, standard 4–12, challenge 8–18 inclusive for a,b,c. '
                  'requested_marks is explicit marks per question, or 0 if unspecified. Do not claim official CCEA approval. '
                  'Do not invent new wording, code or mathematical operations. Return the structured plan only.'),
                 input=json.dumps(dict(unit=unit,request=prompt.strip(),families=options),ensure_ascii=True),
                 text={'format':{'type':'json_schema','name':'question_plan','strict':True,'schema':schema}})
    return accept(studio_ai.send(payload),unit,families)


def accept(response,unit,families):
    try:
        if response['status']!='completed': raise ValueError()
        parts=[p for x in response['output'] if x['type']=='message' for p in x['content']]
        if len(parts)!=1 or parts[0]['type']!='output_text': raise ValueError()
        plan=json.loads(parts[0]['text'],object_pairs_hook=studio_ai.unique_keys)
        if type(plan) is not dict or set(plan)!={'supported','reason','count','requested_marks','questions'}: raise ValueError()
        if type(plan['supported']) is not bool or type(plan['reason']) is not str or len(plan['reason'])>240: raise ValueError()
        if not plan['supported']:
            if plan['questions']!=[]: raise ValueError()
            raise studio_ai.StudioAIUnavailable('Request is outside supported question designs. '+plan['reason'])
        count,marks,items=plan['count'],plan['requested_marks'],plan['questions']
        if type(count) is not int or not 1<=count<=10 or type(marks) is not int or not 0<=marks<=4 or type(items) is not list or len(items)!=count: raise ValueError()
        rows=[]; seen=set()
        for item in items:
            if type(item) is not dict or set(item)!={'family','difficulty','a','b','c'}: raise ValueError()
            f,d=item['family'],item['difficulty']; a,b,c=(item[k] for k in 'abc')
            if f not in families or d not in DOMAINS: raise ValueError()
            lo,hi=DOMAINS[d]
            if any(type(x) is not int or not lo<=x<=hi for x in (a,b,c)): raise ValueError()
            meta={k:v for k,v in families[f].items() if k not in ('family','label')}
            row=studio.make_row(unit,f,d,a,b,c,meta)
            if row['question'] in seen or (marks and row['marks']!=marks): raise ValueError()
            seen.add(row['question'])
            rows.append(dict(row,mode='model',model_role='AI-designed bounded mathematical parameters; locally constructed question',
                             validation='Independent numeric check passed after AI parameter design; proposed rubric requires teacher review'))
        return rows
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise studio_ai.StudioAIUnavailable('AI returned an invalid question plan; no drafts saved. Try a more specific supported request.') from exc
