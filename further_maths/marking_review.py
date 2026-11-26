"""Version-bound marking review inventory; never grants teacher approval."""
import hashlib
import json
from active_difficulty import require

DIMENSIONS=('mathematical_correctness','criterion_allocation','alternative_methods','consequential_errors','boundary_cases','presentation')
TYPES={'M','A','R'}

def fingerprint(item):
    data={k:item[k] for k in ('id','revision','scope','marks','payload')}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def inventory_entry(item):
    require(item['teacher_approved'] is False,'Teacher approval must remain separate')
    rub=item['payload']['rubric']
    require(bool(rub) and all(type(r['marks']) is int and r['marks']>0 and isinstance(r['criterion'],str) and r['criterion'].strip() for r in rub),'Invalid rubric')
    require(sum(r['marks'] for r in rub)==item['marks'],'Mark total mismatch')
    require(all('type' not in r or r['type'] in TYPES for r in rub),'Unknown criterion type')
    typed=sum('type' in r for r in rub)
    return {'id':item['id'],'revision':item['revision'],'scope':item['scope'],'fingerprint':fingerprint(item),'marks':item['marks'],'criteria':len(rub),'typed_criteria':typed,'status':'typed_provisional' if typed==len(rub) else 'needs_type_review','teacher_approved':False}

def validate_review(item,review):
    """Validate evidence shape, not the mathematical correctness of reviewer judgments."""
    entry=inventory_entry(item)
    require(review.get('id')==entry['id'] and review.get('fingerprint')==entry['fingerprint'],'Stale or mismatched review')
    require(review.get('teacher_approved') is False,'Approval not supported by this framework')
    require(isinstance(review.get('reviewer'),str) and bool(review['reviewer'].strip()),'Reviewer required')
    checks=review.get('checks',{})
    require(set(checks)==set(DIMENSIONS),'Incomplete review dimensions')
    for dimension,value in checks.items():
        require(isinstance(value,dict) and value.get('decision') in ('pass','revise','not_applicable') and isinstance(value.get('evidence'),str) and bool(value['evidence'].strip()),'Each decision requires evidence')
        require(dimension not in ('mathematical_correctness','criterion_allocation','presentation') or value['decision']!='not_applicable','Essential review dimension cannot be waived')
    allocation=review.get('allocation',[]);rub=item['payload']['rubric']
    require(len(allocation)==len(rub),'Each criterion needs explicit allocation')
    for i,(row,criterion) in enumerate(zip(allocation,rub)):
        require(row.get('criterion_index')==i and isinstance(row.get('marks'),dict) and set(row['marks'])==TYPES and all(type(n) is int and n>=0 for n in row['marks'].values()) and sum(row['marks'].values())==criterion['marks'],'Criterion allocation mismatch')
        require(isinstance(row.get('evidence'),str) and bool(row['evidence'].strip()),'Allocation evidence required')
    return 'changes_requested' if any(x['decision']=='revise' for x in checks.values()) else 'editorial_review_recorded'
