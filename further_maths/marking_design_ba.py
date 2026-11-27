"""Frozen individual re-review of the three AD angle congruence variants."""
import hashlib
import json
from active_difficulty import Resolver, require
from marking_review import fingerprint

FROZEN_BATCH_SHA='347d6eff6b57540966adcb6058c8e31f5bac9830291bd0c7f9160642157abcfa'
PRIOR=('7950cc9464d4c2664cf5fc2598d7d211b957afed55f52ab8f10ae303a8dcbe12','f9868e630502a6aee385a0bfd7a273d7445dcc0bef2b4e20c7806b4efc17304c','4bf39e56d5498233af46655141830aed2bb901ad4b7f56c2dd69fd2522185d6e')

def records(resolver=None):
    r=resolver or Resolver()
    items=[r._resolve('angle-units',6,v) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BA frozen batch changed')
    for item,prior in zip(items,PRIOR):
        p=item['payload'];v=p['variant'];alpha=30*(v+1)
        old=r._resolve_version('angle-units',6,v,'ad')
        require(fingerprint(old)==prior and {k for k in p if p[k]!=old['payload'][k]}=={'rubric'},'BA predecessor or payload changed')
        checks={
          'mathematical_correctness':{'decision':'pass','evidence':f'Individual text and exact degree enumeration reviewed: [{alpha}, {alpha+360}, {alpha+720}], stricter modulus retains [{alpha}, {alpha+720}]. Original prompt, answer, facts and worked solution unchanged.'},
          'criterion_allocation':{'decision':'pass','evidence':'The four one-mark criteria now explicitly award M, R, A, R; the previously proposed AY allocations are applied to the active BA version.'},
          'alternative_methods':{'decision':'pass','evidence':'Accept consistent radian or degree congruences and equivalent integer reasoning.'},
          'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated method credit after a later arithmetic slip; reasoning must establish the relevant congruence; exact listed values are required for accuracy.'},
          'boundary_cases':{'decision':'pass','evidence':f'Inclusive degree interval [-180,900] admits n=0,1,2 for alpha={alpha}; n=-1 and n=3 are excluded. Modulo pi the half-angle constraint is automatic; modulo 2pi only even n survive.'},
          'presentation':{'decision':'pass','evidence':'Individual prompt, answer and solution text inspected; no rendered mathematics certification. Enrichment-only scope retained.'}}
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if t==row['type'] else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(p['rubric'])]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'supersedes_fingerprint':prior,'review_basis':'individual_item_rereview','reviewer':'AI editorial re-review FM-16BA (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for row in records():print(json.dumps(row,sort_keys=True))
