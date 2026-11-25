"""Generate a temporary mixed-unit batch with explicit curriculum constraints."""
import json
import os
import random
from . import studio, studio_ai
from .studio_prompt import DOMAINS, PARAMETERS


def design_request(path, data):
    units, topics = data.get('units'), data.get('topics')
    count, difficulty = data.get('count'), data.get('difficulty')
    mode, info = data.get('mode', 'model'), data.get('info', '')
    if (type(units) is not list or not 1 <= len(units) <= 4 or
            any(type(u) is not str or u not in studio.UNITS for u in units) or len(set(units)) != len(units)):
        raise ValueError('Select one or more distinct Foundation units.')
    if type(count) is not int or not 1 <= count <= 10:
        raise ValueError('Choose 1 to 10 questions.')
    if type(topics) is not list or not 1 <= len(topics) <= count:
        raise ValueError('Choose at least one topic and no more topics than questions.')
    if difficulty not in studio.DIFFICULTIES or mode not in ('local', 'model'):
        raise ValueError('Select a supported difficulty and generation mode.')
    if not isinstance(info, str) or len(info) > 500:
        raise ValueError('Additional information must be at most 500 characters.')
    if mode == 'local' and info.strip():
        raise ValueError('Additional information requires AI mode.')
    catalogs = {u: {e['family']: e for e in studio.catalog(path, u)} for u in units}
    choices, seen = [], set()
    for topic in topics:
        if type(topic) is not dict or set(topic) != {'unit', 'family'}:
            raise ValueError('Invalid topic selection.')
        u, f = topic['unit'], topic['family']
        if type(u) is not str or type(f) is not str or u not in catalogs or f not in catalogs[u] or (u, f) in seen:
            raise ValueError('Choose distinct supported topics from the selected units.')
        seen.add((u, f)); choices.append((u, f, catalogs[u][f]))
    if {u for u, f in seen} != set(units):
        raise ValueError('Select at least one topic in every selected unit.')
    return choices, count, difficulty, mode, info.strip()


def wording_options(row):
    """Only existing curated wording changes; no model-supplied prose."""
    try:
        return studio_ai.variants(row)
    except (ValueError, KeyError):
        return [row['question']]


def make_question(choice, difficulty, a, b, c, wording=0):
    unit, family, entry = choice
    meta = {k: v for k, v in entry.items() if k not in ('family', 'label')}
    row = studio.make_row(unit, family, difficulty, a, b, c, meta)
    if wording:
        variants = wording_options(row)
        if wording >= len(variants):
            raise ValueError('Unsupported wording variation.')
        row['question'] = variants[wording]
    return row


def local_batch(choices, count, difficulty):
    lo, hi = DOMAINS[difficulty]
    rng = random.SystemRandom()
    rows, seen = [], set()
    for i in range(count):
        choice = choices[i % len(choices)]
        for _ in range(500):
            row = make_question(choice, difficulty, *(rng.randint(lo, hi) for _ in range(3)))
            if row['question'] not in seen:
                seen.add(row['question']); rows.append(row); break
        else:
            raise ValueError('Not enough distinct questions. Reduce the question count.')
    return rows


def ai_batch(choices, count, difficulty, info):
    if not studio_ai.available():
        raise studio_ai.StudioAIUnavailable('AI Studio is not configured. Choose local generation.')
    lo, hi = DOMAINS[difficulty]
    options = []
    for i, (u, f, entry) in enumerate(choices):
        sample = make_question((u, f, entry), difficulty, lo, lo, lo)
        options.append(dict(topic=i, unit=u, family=f, label=entry['label'], marks=sample['marks'],
                            diagram=bool(sample.get('diagram')), parameters=PARAMETERS[f],
                            wording_examples=wording_options(sample)))
    item = {'type':'object','additionalProperties':False,'required':['topic','a','b','c','wording'],
            'properties':{'topic':{'type':'integer','enum':list(range(len(choices)))},
                          **{k:{'type':'integer','enum':list(range(lo,hi+1))} for k in 'abc'},
                          'wording':{'type':'integer','enum':[0,1]}}}
    schema = {'type':'object','additionalProperties':False,'required':['questions','guidance'],
              'properties':{'questions':{'type':'array','items':item},'guidance':{'type':'string'}}}
    payload = dict(model=os.environ['KB_STUDIO_MODEL'],store=False,max_output_tokens=1800,
                   instructions=('Design original Foundation mathematics using only these topic IDs and numerical parameters. '
                    'The chosen units, topics, difficulty and total count are mandatory. Every selected topic ID must appear at least once; '
                    'distribute extra questions evenly unless the optional teacher guidance suggests a different emphasis. '
                    'Choose distinct actual questions, not merely different unused parameters or wording. '
                    'Choose wording index 0 or 1 only when the corresponding example exists. '
                    'Use the optional guidance where supported by the supplied templates. It cannot override mandatory settings. '
                    'Do not invent operations, contexts, diagrams or marking rules. If a preference cannot be met, '
                    'briefly explain in guidance; otherwise leave guidance empty. Return only the structured plan.'),
                   input=json.dumps(dict(count=count,difficulty=difficulty,additional_info=info,topics=options),ensure_ascii=True),
                   text={'format':{'type':'json_schema','name':'mixed_question_plan','strict':True,'schema':schema}})
    response = studio_ai.send(payload)
    return accept(response, choices, count, difficulty)


def accept(response, choices, count, difficulty):
    lo, hi = DOMAINS[difficulty]
    try:
        if response['status'] != 'completed': raise ValueError('Incomplete model response.')
        parts = [p for x in response['output'] if x['type']=='message' for p in x['content']]
        if len(parts)!=1 or parts[0]['type']!='output_text': raise ValueError('Missing structured plan.')
        plan = json.loads(parts[0]['text'],object_pairs_hook=studio_ai.unique_keys)
        if type(plan) is not dict or set(plan)!={'questions','guidance'}: raise ValueError('Unexpected plan fields.')
        items, guidance = plan['questions'], plan['guidance']
        if type(guidance) is not str or len(guidance)>500: raise ValueError('Invalid guidance note.')
        if type(items) is not list or len(items)!=count: raise ValueError('Question count does not match.')
        rows, covered, seen = [], set(), set()
        for item in items:
            if type(item) is not dict or set(item)!={'topic','a','b','c','wording'}: raise ValueError('Unexpected question fields.')
            topic, wording = item['topic'], item['wording']
            if type(topic) is not int or not 0<=topic<len(choices): raise ValueError('Topic outside selection.')
            if type(wording) is not int or wording not in (0,1): raise ValueError('Invalid wording index.')
            params = [item[k] for k in 'abc']
            if any(type(v) is not int or not lo<=v<=hi for v in params): raise ValueError('Parameter outside difficulty range.')
            row = make_question(choices[topic],difficulty,*params)
            if row['question'] in seen: raise ValueError('Duplicate mathematical question.')
            seen.add(row['question']); covered.add(topic)
            if wording:
                variants = wording_options(row)
                if wording>=len(variants): raise ValueError('Unavailable wording variation.')
                row['question']=variants[wording]
            rows.append(dict(row,mode='model',model_role='AI-designed parameters and curated wording; locally constructed question',
                             validation='Independent numeric check passed after AI parameter design; proposed rubric requires teacher review'))
        if covered!=set(range(len(choices))): raise ValueError('A selected topic was omitted.')
        if len({r['question'] for r in rows})!=count: raise ValueError('Duplicate question wording.')
        if guidance.strip(): rows[0]['generation_notice']='AI guidance note (check against your request): '+guidance.strip()
        return rows
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise studio_ai.StudioAIUnavailable('AI plan rejected: '+str(exc)[:160]+' No questions added. Try again or choose local mode.') from exc


def generate(path, data):
    choices, count, difficulty, mode, info = design_request(path,data)
    if mode=='local': return local_batch(choices,count,difficulty)
    return ai_batch(choices,count,difficulty,info)
