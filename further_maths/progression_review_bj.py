"""Validate version-bound representative demand reviews; never infer difficulty from marks."""
import collections
import json
from pathlib import Path
from active_difficulty import Resolver, require
from marking_review import fingerprint
from difficulty_revision_bj import TARGETS
from consolidation_audit import mark_transition

# One retained cubic transition and ten successor transitions, all from the BI priority queue.
PRIORITIES = {(p,t-1) for p,t in TARGETS}|{('solve-cubic',3)}
EQUAL_DECISIONS = {'role_contrast','linked_progression','inspect_demand','inspect_allocation'}


def bind(r,path,tier,decision,note,kind):
    require(type(tier) is int and 1<=tier<=5,'Invalid transition')
    require(isinstance(note,str) and note.strip(),'Demand review needs specific evidence')
    left=[r._resolve(path,tier,v) for v in (1,2,3)]
    right=[r._resolve(path,tier+1,v) for v in (1,2,3)]
    return {'path':path,'from_tier':tier,'to_tier':tier+1,'kind':kind,'decision':decision,'note':note,
            'left_fingerprints':[fingerprint(i) for i in left], 'right_fingerprints':[fingerprint(i) for i in right],
            'from_marks':[i['marks'] for i in left], 'to_marks':[i['marks'] for i in right],
            'teacher_approved':False,'empirical_calibration':False}


def validate(rows,old=None,current=None):
    old=old or Resolver(historical_through='bh');current=current or Resolver()
    seen=set();counts=collections.Counter();equal_keys=set();priority_keys=set();next_keys=set()
    for row in rows:
        p,t,k,d=row['path'],row['from_tier'],row['kind'],row['decision']
        require((p,t,k) not in seen,'Duplicate transition review');seen.add((p,t,k))
        require(row['teacher_approved'] is False and row['empirical_calibration'] is False,'Unjustified approval or calibration')
        r=current if k=='successor_neighbour_review' else old
        require(row==bind(r,p,t,d,row['note'],k),'Stale or invalid transition evidence')
        if k=='equal_mark_representative':
            require(d in EQUAL_DECISIONS and mark_transition(row['from_marks'],row['to_marks'])=='touching_marks','Not an original equal-mark transition')
            equal_keys.add((p,t))
        elif k=='priority_all_variants':
            require((p,t) in PRIORITIES and d==('retained_role_progression' if (p,t)==('solve-cubic',3) else 'successor_implemented'),'Invalid priority decision')
            priority_keys.add((p,t))
        elif k=='successor_neighbour_review':
            require((p,t) in TARGETS and d in ('linked_progression','inspect_allocation','inspect_demand'),'Invalid successor neighbour decision')
            next_keys.add((p,t))
        else:raise ValueError('Unknown transition review kind')
        counts[k+':'+d]+=1
    require(len(equal_keys)==233 and priority_keys==PRIORITIES and next_keys==set(TARGETS),'Transition coverage mismatch')
    return {'records':len(seen),'counts':dict(counts),'teacher_approved':0,'empirically_calibrated':0}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('ledger',type=Path)
    args=parser.parse_args(); print(json.dumps(validate([json.loads(x) for x in args.ledger.read_text().splitlines() if x.strip()]),indent=2,sort_keys=True))
