"""Generate a temporary mixed-unit batch with explicit curriculum constraints."""
import json
import os
import random
from . import studio, studio_ai, geometry
import re
from itertools import product
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
    if difficulty not in studio.DIFFICULTIES or mode not in ('local', 'model', 'hybrid'):
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


def make_question(choice, difficulty, a, b, c, wording=0, layout=None):
    unit, family, entry = choice
    meta = {k: v for k, v in entry.items() if k not in ('family', 'label')}
    row = studio.make_row(unit, family, difficulty, a, b, c, meta)
    if wording:
        variants = wording_options(row)
        if wording >= len(variants):
            raise ValueError('Unsupported wording variation.')
        row['question'] = variants[wording]
    if row.get('diagram'):
        row['diagram'] = geometry.diagram(family,a,b,c,layout)
        row['_diagram_seed'] = (a,b,c,wording,geometry.default_layout(a,b,c) if layout is None else layout)
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
                            layouts=(list(geometry.LAYOUTS) if sample.get('diagram') else [0]),
                            wording_examples=wording_options(sample)))
    item = {'type':'object','additionalProperties':False,'required':['topic','a','b','c','wording','layout'],
            'properties':{'topic':{'type':'integer','enum':list(range(len(choices)))},
                          **{k:{'type':'integer','enum':list(range(lo,hi+1))} for k in 'abc'},
                          'wording':{'type':'integer','enum':[0,1]}, 'layout':{'type':'integer','enum':list(geometry.LAYOUTS)}}}
    schema = {'type':'object','additionalProperties':False,'required':['questions','guidance'],
              'properties':{'questions':{'type':'array','items':item},'guidance':{'type':'string'}}}
    payload = dict(model=os.environ['KB_STUDIO_MODEL'],store=False,max_output_tokens=1800,
                   instructions=('Design original Foundation mathematics using only these topic IDs and numerical parameters. '
                    'The chosen units, topics, difficulty and total count are mandatory. Every selected topic ID must appear at least once; '
                    'distribute extra questions evenly unless the optional teacher guidance suggests a different emphasis. '
                    'Choose distinct actual questions, not merely different unused parameters or wording. For diagram topics, '
                    'vary the ratios of side lengths and layout indices (0 to 7) rather than repeating the same outline. '
                    'For L shapes, layouts rotate or reflect the cutout; for trapezia they shift the short base and invert it; '
                    'for Pythagoras they change diagonal direction and dimension placement. For non-diagram topics layout must be 0. '
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
            if type(item) is not dict or set(item) not in ({'topic','a','b','c','wording'}, {'topic','a','b','c','wording','layout'}): raise ValueError('Unexpected question fields.')
            topic, wording = item['topic'], item['wording']
            if type(topic) is not int or not 0<=topic<len(choices): raise ValueError('Topic outside selection.')
            if type(wording) is not int or wording not in (0,1): raise ValueError('Invalid wording index.')
            params = [item[k] for k in 'abc']
            if any(type(v) is not int or not lo<=v<=hi for v in params): raise ValueError('Parameter outside difficulty range.')
            layout = item.get('layout')
            if layout is not None and (type(layout) is not int or layout not in geometry.LAYOUTS): raise ValueError('Unsupported diagram layout.')
            if choices[topic][1] not in geometry.FAMILIES and layout not in (None,0): raise ValueError('Layout is only valid for diagram topics.')
            row = make_question(choices[topic],difficulty,*params,layout=layout) if layout is not None else make_question(choices[topic],difficulty,*params)
            if row['question'] in seen: raise ValueError('Duplicate mathematical question.')
            seen.add(row['question']); covered.add(topic)
            if wording:
                variants = wording_options(row)
                if wording>=len(variants): raise ValueError('Unavailable wording variation.')
                row['question']=variants[wording]
            if '_diagram_seed' in row:
                a,b,c,_,layout = row['_diagram_seed']
                row['_diagram_seed'] = (a,b,c,wording,layout)
            rows.append(dict(row,mode='model',model_role='AI-designed parameters and curated wording; locally constructed question',
                             validation='Independent numeric check passed after AI parameter design; proposed rubric requires teacher review'))
        if covered!=set(range(len(choices))): raise ValueError('A selected topic was omitted.')
        if len({r['question'] for r in rows})!=count: raise ValueError('Duplicate question wording.')
        if guidance.strip(): rows[0]['generation_notice']='AI guidance note (check against your request): '+guidance.strip()
        return rows
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise studio_ai.StudioAIUnavailable('AI plan rejected: '+str(exc)[:160]+' No questions added. Try again or choose local mode.') from exc


def hybrid_batch(choices, count, difficulty, info):
    """One optional AI call, exclusively for families with schematic diagrams.

    Round-robin allocation fixes the number of diagram and non-diagram slots
    before sending anything to the model. Every chosen unit/topic is covered.
    """
    lo, _ = DOMAINS[difficulty]
    diagram_flags = [bool(make_question(choice,difficulty,lo,lo,lo).get('diagram'))
                     for choice in choices]
    slots = [diagram_flags[i % len(choices)] for i in range(count)]
    diagram_count = sum(slots)
    local_count = count - diagram_count
    diagram_choices = [c for c, flag in zip(choices,diagram_flags) if flag]
    local_choices = [c for c, flag in zip(choices,diagram_flags) if not flag]
    # No availability check or API call at all for an entirely text-only batch.
    # If a diagram plan fails, the batch fails atomically, not silently partially.
    local = local_batch(local_choices,local_count,difficulty) if local_count else []
    model = ai_batch(diagram_choices,diagram_count,difficulty,info) if diagram_count else []
    if len(local)!=local_count or len(model)!=diagram_count or any(r.get('diagram') for r in local) or any(not r.get('diagram') for r in model):
        raise ValueError('Hybrid diagram classification changed; no questions added.')
    local_iter, model_iter = iter(local), iter(model)
    rows = [next(model_iter) if flag else next(local_iter) for flag in slots]
    if len({r['question'] for r in rows})!=count or {(r['unit'],r['family']) for r in rows}!={(u,f) for u,f,_ in choices}:
        raise ValueError('Hybrid batch did not meet topic coverage or uniqueness; no questions added.')
    note = f'Hybrid: {local_count} local question(s), {diagram_count} AI-designed diagram question(s); '
    note += 'one model request.' if diagram_count else 'no API request.'
    if info and local_count:
        note += ' Additional guidance applies only to the AI-designed diagram questions.' if diagram_count else ' Additional guidance was not used because no diagram topics were selected.'
    guidance = [r.pop('generation_notice') for r in rows if r.get('generation_notice')]
    rows[0]['generation_notice'] = ' '.join([note,*guidance])
    return rows


def diagram_history(data, field='diagram_history', maximum=300):
    history=data.get(field,[])
    if (type(history) is not list or len(history)>maximum or any(type(k) is not str or not re.fullmatch(r'[0-9a-f]{24}',k) for k in history)):
        raise ValueError('Invalid or excessive diagram history. Export and start a new worksheet.')
    return set(history)


def diversify(rows, choices, difficulty, used, shapes=None):
    """Keep every actual diagram distinct; prefer new silhouettes in a batch.

    First try all orientations of the original question. If these repeat a
    silhouette, search new parameters and validate the whole replacement row.
    Never change just the picture while leaving mismatched answers behind.
    """
    lo,hi=DOMAINS[difficulty]
    by_topic={(u,f):choice for choice in choices for u,f,_ in [choice]}
    shapes=set(shapes or ())
    seen={r['question'] for r in rows}
    for i, original in enumerate(rows):
        seed=original.get('_diagram_seed')
        if seed is None:
            continue
        a,b,c,wording,layout=seed
        family=original['family']
        choice=by_topic[(original['unit'],family)]
        best=None; fallback=None
        def try_layouts(row, params, preferred):
            nonlocal fallback
            for l in [preferred]+[v for v in geometry.LAYOUTS if v!=preferred]:
                d=geometry.diagram(family,*params,l)
                key=geometry.diagram_key(d); shape=geometry.shape_key(d)
                if key in used: continue
                candidate=(row,d,key,shape)
                if shape not in shapes: return candidate
                if fallback is None: fallback=candidate
            return None
        best=try_layouts(original,(a,b,c),layout)
        if best is None:
            # Deterministic exhaustive domain search, so repetitive model
            # parameters cannot force repetitive drawings or extra API calls.
            for params in product(range(lo,hi+1),repeat=3):
                if params==(a,b,c): continue
                candidate=make_question(choice,difficulty,*params,wording=wording)
                if candidate['question'] in seen: continue
                best=try_layouts(candidate,params,geometry.default_layout(*params))
                if best is not None: break
        best=best or fallback
        if best is None:
            raise ValueError('Could not find a distinct diagram for the selected topics. Reduce the count or choose another topic. No questions added.')
        row,d,key,shape=best
        if row is not original:
            seen.discard(original['question']);seen.add(row['question'])
            # Do not misrepresent locally repaired mathematical parameters as
            # having been directly chosen by the model.
            if original.get('mode')=='model':
                row.update(mode='model',model_role='AI-selected topic; locally varied and revalidated parameters for diagram diversity',
                           validation='Independent numeric check passed after local diagram-diversity adjustment; proposed rubric requires teacher review')
            if original.get('generation_notice'): row['generation_notice']=original['generation_notice']
        row['diagram']=d; row['diagram_key']=key; row['diagram_shape']=shape
        row.pop('_diagram_seed',None)
        rows[i]=row;used.add(key);shapes.add(shape)
    return rows


def generate(path, data):
    choices, count, difficulty, mode, info = design_request(path,data)
    history=diagram_history(data)
    shapes=diagram_history(data,'shape_history',150)
    if mode=='local': rows=local_batch(choices,count,difficulty)
    elif mode=='hybrid': rows=hybrid_batch(choices,count,difficulty,info)
    else: rows=ai_batch(choices,count,difficulty,info)
    return diversify(rows,choices,difficulty,history,shapes)
