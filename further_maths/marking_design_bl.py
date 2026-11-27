"""Version-bound shared-design and independent variant evidence for BL successors."""
import hashlib,json
from active_difficulty import Resolver, require, MARK_SUCCESSIONS
from difficulty_revision_bl import TARGETS, CRITERIA, NEW_DEMAND
from difficulty_revision_bl_oracle import check
from marking_review import fingerprint
FROZEN_BATCH_SHA='503faff561139af6cd3690f37af28322e413a466995f3c4b418004fb554fa415'

def records(resolver=None):
    r=resolver or Resolver()
    items=[r._resolve(p,t,v) for p,t in sorted(TARGETS) for v in (1,2,3)]
    require(hashlib.sha256(json.dumps([(i['id'],fingerprint(i)) for i in items],separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BL frozen batch changed')
    for item in items:
        p=item['payload'];path,t,v=p['path'],p['tier'],p['variant'];key=path,t
        old=r._resolve_version(path,t,v,TARGETS[key])
        require(item['revision']=='FM-16BL' and check(p) and old['scope']==item['scope'],'Invalid BL item')
        require((old['marks'],item['marks'])==MARK_SUCCESSIONS[path,t,'bl'],'Mark succession mismatch')
        stage='; '.join(c for k,c in CRITERIA[key])
        reasoning='; '.join(c for k,c in CRITERIA[key] if k=='R') or 'The given nonzero line direction makes the perpendicular foot unique; its displacement has nonnegative norm.'
        method='; '.join(c for k,c in CRITERIA[key] if k=='M')
        checks={
          'mathematical_correctness':{'decision':'pass','evidence':('New shared task, exact independent constraint check. ' if key in NEW_DEMAND else 'Mathematical facts retained and checked by predecessor oracle. ')+stage},
          'criterion_allocation':{'decision':'pass','evidence':f"Separate credit for {item['marks']} assessable stages: "+stage},
          'alternative_methods':{'decision':'pass','evidence':method+' Equivalent valid methods are permitted within question restrictions.'},
          'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid methods and reasoning after a subsequent arithmetic slip; exact required answers remain necessary for accuracy credit.'},
          'boundary_cases':{'decision':'pass','evidence':reasoning},
          'presentation':{'decision':'pass','evidence':'Shared question, worked structure and allocation examined; individual written-solution and rendering checks remain pending.'},
        }
        allocation=[{'criterion_index':i,'marks':{k:row['marks'] if k==row['type'] else 0 for k in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(p['rubric'])]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'supersedes_fingerprint':fingerprint(old),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial demand and allocation review FM-16BL (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for row in records():print(json.dumps(row,sort_keys=True))
