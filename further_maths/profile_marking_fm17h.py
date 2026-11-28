"""Reusable, version-bound structured observations for the remaining AS1 Tier 3 designs."""
import copy
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from active_difficulty import require
from marking_review import fingerprint
from marking_batch import read_batch
from engine_fm17d import reconcile_proposal
from structured_math_fm17d import rational
import marking_dispatch_fm17g as prior


def radical_terms(value):
    require(isinstance(value,dict) and set(value)=={'radical_terms'},'Invalid exact radical')
    terms=value['radical_terms']; require(isinstance(terms,list) and len(terms)<=8,'Too many radical terms')
    result={}
    for term in terms:
        require(isinstance(term,list) and len(term)==2,'Invalid radical term')
        c=rational(term[0]); n=rational(term[1]); require(n.denominator==1 and 1<=n<=10000,'Invalid radicand')
        n=int(n); k=2
        while k*k<=n:
            while n%(k*k)==0: n//=k*k; c*=k
            k+=1
        result[n]=result.get(n,Fraction(0))+c
    return {k:v for k,v in result.items() if v}


def exact(actual,expected):
    if isinstance(expected,dict): return radical_terms(actual)==radical_terms(expected)
    if isinstance(expected,list):
        require(isinstance(actual,list) and len(actual)==len(expected),'Invalid observation shape')
        return all([exact(a,b) for a,b in zip(actual,expected)])
    require(isinstance(expected,str) and isinstance(actual,str) and len(actual)<=100,'Invalid observation value')
    return rational(actual)==rational(expected) if re.fullmatch(r'-?\d+(?:/[1-9]\d*)?',expected) else actual==expected


def numbers(value,n):
    require(isinstance(value,list) and len(value)==n,'Invalid numeric vector')
    return tuple(map(rational,value))


def proportional(a,b):
    return any(a) and any(b) and all(x*v==y*u for x,u in zip(a,b) for y,v in zip(a,b))


def matches(rule,value,target):
    if rule=='equal': return exact(value,target)
    if rule=='proportional': return proportional(numbers(value,len(target)),numbers(target,len(target)))
    if rule=='line':
        require(isinstance(value,list) and len(value)==3,'Invalid line representation')
        n=len(target[0]); a,d=numbers(value[0],n),numbers(value[1],n); b,e=numbers(target[0],n),numbers(target[1],n)
        delta=tuple(x-y for x,y in zip(a,b))
        return value[2]==target[2] and proportional(d,e) and (not any(delta) or proportional(delta,e))
    if rule=='line_with_checks':
        require(isinstance(value,list) and len(value)==len(target),'Invalid line verification')
        return matches('line',value[0],target[0]) and exact(value[1:],target[1:])
    if rule=='plane_check':
        require(isinstance(value,list) and len(value)==4,'Invalid plane verification')
        n=len(target[0]); a=numbers(value[0],n); b=numbers(target[0],n)
        c=rational(value[1]); point=numbers(value[2],n); evaluated=rational(value[3])
        return (any(a) and proportional((*a,c),(*b,rational(target[1]))) and exact(value[2],target[2])
                and sum(x*y for x,y in zip(a,point))==evaluated==c)
    if rule in ('unordered','directions'):
        require(isinstance(value,list) and len(value)==len(target) and len(target)<=6,'Invalid set representation')
        from itertools import permutations
        return any(all(matches('equal' if rule=='unordered' else 'proportional',a,b) for a,b in zip(value,p)) for p in permutations(target))
    raise ValueError('Unknown comparison rule')


class ProfileMarking:
    """Load private reviewed mathematical profiles, never caller-supplied reference values."""
    def __init__(self,engine,records):
        self.engine=engine; self._profiles={}
        for row in records:
            key=row['id']; require(key in engine.bank.items and key not in self._profiles,'Unknown or duplicate profile')
            item=engine.bank.items[key]; p=item['payload']
            require(p['tier']==3 and p['path'] not in prior.supported_designs() and row['fingerprint']==fingerprint(item)
                    and row['revision']==item['revision'] and row['basis']=='editorial_prompt_derived_observations','Stale or unsupported profile')
            criteria=row['criteria']; require(isinstance(criteria,list) and len(criteria)==len(p['rubric']),'Incomplete profile')
            fields=set()
            for spec,rubric in zip(criteria,p['rubric']):
                require(set(spec)=={'field','type','marks','rule','expected'} and spec['type']==rubric['type'] and spec['marks']==rubric['marks']
                        and isinstance(spec['field'],str) and re.fullmatch(r'[a-z][a-z0-9_]*',spec['field']) and spec['field'] not in fields,'Invalid criterion profile')
                require(matches(spec['rule'],spec['expected'],spec['expected']),'Invalid mathematical reference')
                fields.add(spec['field'])
            self._profiles[key]=copy.deepcopy(row)
        expected={key for key,item in engine.bank.items.items() if item['payload']['tier']==3 and item['payload']['path'] not in prior.supported_designs()}
        require(set(self._profiles)==expected,'Incomplete remaining Tier 3 profiles')

    @classmethod
    def from_bundle(cls,engine,root):
        root=Path(root)/'FM17H'; name='profiles.jsonl'
        manifest=json.loads((root/'runtime-manifest.json').read_text())
        require(manifest['checkpoint']=='FM-17H','Invalid profile manifest')
        with (root/name).open('rb') as stream:
            require(hashlib.file_digest(stream,'sha256').hexdigest()==manifest['sha256'][name],'Profile hash mismatch')
        return cls(engine,read_batch(root/name))

    def capability(self,item_id,*,mode,item_fingerprint):
        result=prior.capability(self.engine,item_id,mode=mode,item_fingerprint=item_fingerprint)
        if item_id in self._profiles:
            require(self._profiles[item_id]['fingerprint']==item_fingerprint,'Stale profile')
            result.update(structured_checks_available=True,basis='bounded_profile_observations')
        return result

    def check_work(self,item_id,*,mode,item_fingerprint,work):
        args=dict(mode=mode,item_fingerprint=item_fingerprint)
        if item_id not in self._profiles: return prior.check_work(self.engine,item_id,work=work,**args)
        context=self.engine.marking_context(item_id,**args); profile=self._profiles[item_id]
        require(profile['fingerprint']==item_fingerprint,'Stale profile')
        specs=profile['criteria']; require(isinstance(work,dict) and set(work)=={s['field'] for s in specs},'Unexpected observation fields')
        require([(c['type'],c['marks']) for c in context['criteria']]==[(s['type'],s['marks']) for s in specs],'Context rubric mismatch')
        decisions=[]
        for i,s in enumerate(specs,1):
            value=work[s['field']]; status='uncertain' if value is None else 'met' if matches(s['rule'],value,s['expected']) else 'not_met'
            decisions.append({'criterion_id':f'c{i}','status':status,'evidence':'Unrecognized or unavailable observation.' if status=='uncertain' else 'Compared bounded mathematical observation with the current private criterion profile.'})
        result=reconcile_proposal(context,decisions); result['basis']='exact_checks_on_supplied_structured_observations';return result
