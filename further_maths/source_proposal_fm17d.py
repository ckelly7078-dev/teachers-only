"""Arithmetic reconciliation of explicit observations on one official source route."""
from active_difficulty import require
from source_coverage_fm17c import route_signature


def source_bounds(coverage,key,*,signature,route_id,observations,exceptions=()):
    evidence=coverage.part(key)
    require(evidence['status']=='source_breakdown_available','Detailed source route unavailable')
    record=evidence['record']; require(signature==route_signature(record),'Stale source route')
    route=next((r for r in record['routes'] if r['id']==route_id),None)
    require(route is not None,'Unknown alternative route')
    stages={s['id']:s for s in route['stages']}; maximum=sum(s['marks'] for s in stages.values())
    require(isinstance(exceptions,(list,tuple)),'Invalid exception observations')
    allowed=set(stages); cap=maximum; seen=set()
    for e in exceptions:
        require(isinstance(e,dict) and set(e)=={'index','evidence'} and type(e['index']) is int
                and 0<=e['index']<len(route['exceptions']) and e['index'] not in seen
                and isinstance(e['evidence'],str) and 0<len(e['evidence'].strip())<=2000,'Invalid exception observation')
        seen.add(e['index']); rule=route['exceptions'][e['index']]
        if rule['kind']=='cap':
            allowed &= set(rule['stages']); cap=min(cap,rule['max_marks'])
        # Follow-through/acceptance/restriction notes do not award marks by themselves.
    require(isinstance(observations,list) and len(observations)==len(stages),'Complete stage observations required')
    checked=set(); rows=[]; low=high=0
    for row in observations:
        require(isinstance(row,dict) and set(row)=={'stage_id','status','partial_marks','evidence'},'Invalid stage observation')
        sid=row['stage_id']; status=row['status']; partial=row['partial_marks']
        require(isinstance(sid,str) and sid in stages and sid not in checked and isinstance(row['evidence'],str)
                and 0<len(row['evidence'].strip())<=2000,'Unknown stage or missing evidence')
        checked.add(sid); stage=stages[sid]; marks=stage['marks']
        if status=='partial':
            require(stage['partial_credit'] is not None and type(partial) is int and 0<partial<marks,'No explicit partial-credit basis')
            bounds=(partial,partial)
        else:
            require(status in ('met','not_met','uncertain') and partial is None,'Invalid award observation')
            bounds={'met':(marks,marks),'not_met':(0,0),'uncertain':(0,marks)}[status]
        if sid not in allowed:
            require(bounds[0]==0,'Observation conflicts with explicit cap')
            bounds=(0,0)
        low+=bounds[0]; high+=bounds[1]; rows.append({'stage_id':sid,'possible_marks':list(bounds)})
    require(low<=cap,'Observation conflicts with explicit cap')
    return {'source_part':list(key),'route_id':route_id,'signature':signature,'maximum_marks':maximum,
            'observed_cap':cap,'possible_total':[low,min(high,cap)],'stages':rows,
            'basis':'supplied_observations_not_verified_work','automatic_award':False,'teacher_approved':False,'release_allowed':False}
