"""Bounded method/proof certificates for original AS1 rubrics, not raw scripts."""
import copy
import hashlib
import json
from pathlib import Path
from active_difficulty import require
from engine_fm17d import reconcile_proposal
from marking_batch import read_batch
from marking_review import fingerprint
from profile_marking_fm17h import numbers, proportional
from profile_marking_fm17i import TierMarking, tier_matches
from structured_math_fm17d import rational


def certificate(spec, value):
    """A trusted observer transcribes actual working, never infers it from an answer."""
    if value is None:
        return 'uncertain'
    rule, target = spec['rule'], spec['target']
    if rule == 'alternatives':
        require(isinstance(value, dict) and set(value) == {'method', 'evidence'}, 'Invalid method observation')
        require(isinstance(value['method'], str), 'Invalid method name')
        if value['method'] == 'other':
            require(value['evidence'] is None, 'Unrecognised method must be unresolved')
            return 'uncertain'
        require(value['method'] in target, 'Unknown method representation')
        rule, expected = target[value['method']]
        valid = tier_matches(rule, value['evidence'], expected)
    elif rule == 'row_combination':
        # Actual linear combination and its stated resulting augmented equation.
        require(isinstance(value, dict) and set(value) == {'multipliers', 'row'}, 'Invalid elimination evidence')
        rows = target['rows']; n = len(rows[0]); m = len(rows)
        weights = numbers(value['multipliers'], m)
        result = numbers(value['row'], n)
        calculated = tuple(sum(w*rational(row[j]) for w, row in zip(weights, rows)) for j in range(n))
        valid = (sum(w != 0 for w in weights) >= 2 and result == calculated
                 and proportional(result, numbers(target['row'], n)))
    elif rule == 'row_dependency':
        # Actual coefficients of a dependence; including the constant distinguishes
        # redundancy from inconsistency. A nonzero combination is mandatory.
        require(isinstance(value, dict) and set(value) == {'multipliers', 'residual', 'conclusion'}, 'Invalid dependence evidence')
        rows = target['rows']; n = len(rows[0]); m = len(rows)
        weights = numbers(value['multipliers'], m)
        residual = rational(value['residual'])
        calculated = tuple(sum(w*rational(row[j]) for w, row in zip(weights, rows)) for j in range(n))
        valid = (sum(w != 0 for w in weights) >= 2 and not any(calculated[:-1])
                 and calculated[-1] == residual and (residual == 0) == target['consistent']
                 and value['conclusion'] == target['conclusion'])
    elif rule == 'row_addition':
        require(isinstance(value, dict) and set(value) == {'destination', 'source', 'scale', 'matrix'}, 'Invalid row-addition observation')
        rows = [numbers(row, len(target[0])) for row in target]; n = len(rows)
        i,j=value['destination'],value['source']
        require(type(i) is int and type(j) is int and 0 <= i < n and 0 <= j < n and i != j, 'Invalid row indices')
        m=rational(value['scale']); require(isinstance(value['matrix'],list) and len(value['matrix'])==n,'Invalid matrix size')
        actual=[numbers(row,len(rows[0])) for row in value['matrix']]
        changed=list(rows); changed[i]=tuple(a+m*b for a,b in zip(rows[i],rows[j]))
        valid=bool(rows[i][0] and m and changed[i][0]==0 and actual==changed)
    elif rule == 'affine_line_proof':
        # Two independent equations in three unknowns: exact substitution and
        # a nonzero direction establish the whole line, not just sample points.
        require(isinstance(value,dict) and set(value)=={'point','direction','substitutions','conclusion'}, 'Invalid line proof')
        rows=[numbers(row,4) for row in target]; require(len(rows)==2 and not proportional(rows[0][:3],rows[1][:3]) and all(any(r[:3]) for r in rows),'Invalid independent equations')
        p,d=numbers(value['point'],3),numbers(value['direction'],3)
        require(isinstance(value['substitutions'],list) and len(value['substitutions'])==2,'Two substitutions required')
        observed=[numbers(row,2) for row in value['substitutions']]
        computed=[(sum(a*b for a,b in zip(row[:3],p)),sum(a*b for a,b in zip(row[:3],d))) for row in rows]
        valid=bool(any(d) and observed==computed and all(pair==(row[3],0) for pair,row in zip(computed,rows)) and value['conclusion']=='complete_line_two_independent_equations')
    else:
        raise ValueError('Unsupported certificate rule')
    return 'met' if valid else 'not_met'


def product_followthrough(spec, value, earlier):
    """Specific symbolic elimination with one permitted earlier constant-product slip.

    c1 evidence encodes the real equation -b*x+a*y=h and imaginary xy+c=k.
    c2 evidence is the retained variable and coefficients of
    A*v^2 + B*h*v + C*k + D = 0, with a nonzero common scale permitted.
    """
    if value is None:
        return 'uncertain', False
    require(isinstance(value, dict) and set(value) == {'variable', 'coefficients'}, 'Invalid quadratic evidence')
    require(value['variable'] in ('x', 'y'), 'Unknown eliminated variable')
    actual = numbers(value['coefficients'], 4)
    if earlier is None:
        return 'uncertain', False
    a, b = numbers(spec['target'], 2)
    e = numbers(earlier, 3)
    if e[:2] != (a, b):
        # Other component errors are outside this specifically supported route.
        return 'uncertain', False
    c = e[2]
    wanted = (b, 1, -a, a*c) if value['variable'] == 'x' else (a, -1, -b, b*c)
    valid = proportional(actual, wanted)
    return ('met' if valid else 'not_met'), bool(valid and c != a*b)


def product_pair_credit(spec, value, components, elimination):
    """Two explicitly separable marks for parameterised roots and reconstruction.

    Root expressions are coefficient pairs for h and sqrt(D), where the
    discriminant has h^2 coefficient one. Reconstruction supplies the other
    variable's coefficients in the same order as the observed roots.
    """
    if value is None:
        return ['uncertain','uncertain'], False
    require(isinstance(value,dict) and set(value)=={'discriminant','roots','reconstruction'},'Invalid factor-pair evidence')
    a,b=numbers(spec['target'],2)
    # Validate observations even when prerequisites are missing.
    D=None if value['discriminant'] is None else numbers(value['discriminant'],3)
    def pairs(field):
        v=value[field]
        if v is None:return None
        require(isinstance(v,list) and len(v)==2,'Two symbolic branches required')
        return [numbers(p,2) for p in v]
    roots,other=pairs('roots'),pairs('reconstruction')
    earlier,follow=product_followthrough(spec,elimination,components)
    if earlier!='met':return ['uncertain','uncertain'],False
    c=numbers(components,3)[2]; wanted_D=(1,4*a*b,-4*a*b*c)
    is_x=elimination['variable']=='x'
    centre=-1/(2*b) if is_x else 1/(2*a); radius=1/(2*b) if is_x else 1/(2*a)
    wanted_roots={(centre,-radius),(centre,radius)}
    root_status='uncertain' if D is None or roots is None else 'met' if D==wanted_D and set(roots)==wanted_roots else 'not_met'
    # The reconstruction mark requires actual paired formulae and consistent
    # roots of the eligible quadratic, not merely a claimed second answer.
    if other is None or roots is None or D is None:
        reconstruction='uncertain'
    elif root_status!='met':
        reconstruction='uncertain'  # no invented follow-through of a root error
    else:
        wanted=[((1+b*r)/a,b*t/a) if is_x else ((a*r-1)/b,a*t/b) for r,t in roots]
        reconstruction='met' if wanted==other else 'not_met'
    return [root_status,reconstruction], bool(follow and 'met' in (root_status,reconstruction))


class ReasoningMarking:
    def __init__(self, engine, prior, records):
        self.engine, self.prior, self._profiles = engine, prior, {}
        for row in records:
            key = row['id']
            require(key in engine.bank.items and key not in self._profiles, 'Unknown or duplicate reasoning profile')
            item = engine.bank.items[key]; p = item['payload']
            require(p['tier'] != 3 and row['revision'] == item['revision'] and row['fingerprint'] == fingerprint(item)
                    and row['basis'] == 'prompt_bound_method_certificates', 'Stale reasoning profile')
            seen = set()
            for s in row['criteria']:
                i = s['index']; require(type(i) is int and 1 <= i <= len(p['rubric']) and i not in seen, 'Invalid criterion index')
                r = p['rubric'][i-1]
                require(set(s) == {'index', 'type', 'marks', 'rule', 'target', 'reference'}
                        and s['type'] == r['type'] and s['marks'] == r['marks']
                        and ((r['marks']==1 and r['type'] in ('M','R')) or (r['marks']==2 and r['type']=='A' and s['rule']=='product_pair_credit')), 'Unsupported criterion')
                if s['rule'] == 'product_components':
                    require(p['path'] == 'cartesian-product' and p['tier'] == 6 and i == 1, 'Invalid component scope')
                    a,b = numbers(s['target'],2); require(a and b and numbers(s['reference'],3)==(a,b,a*b), 'Invalid components')
                elif s['rule'] == 'product_followthrough':
                    require(p['path'] == 'cartesian-product' and p['tier'] == 6 and i == 2 and 1 in seen
                            and 'follow-through' in r['criterion'], 'Follow-through not authorised by rubric')
                    previous = next(x for x in row['criteria'] if x['index']==1)
                    require(previous['rule']=='product_components' and previous['target']==s['target']
                            and product_followthrough(s,s['reference'],previous['reference'])==('met',False), 'Invalid follow-through reference')
                elif s['rule']=='product_pair_credit':
                    require(p['path']=='cartesian-product' and p['tier']==6 and i==3 and {1,2}<=seen
                            and 'one mark for roots, one for reconstruction' in r['criterion'] and 'follow through' in r['criterion'], 'Partial credit not authorised by rubric')
                    earlier={x['index']:x for x in row['criteria'] if x['index'] in (1,2)}
                    require(all(x['target']==s['target'] for x in earlier.values()) and earlier[1]['rule']=='product_components' and earlier[2]['rule']=='product_followthrough'
                            and product_pair_credit(s,s['reference'],earlier[1]['reference'],earlier[2]['reference'])==(['met','met'],False),'Invalid partial-credit reference')
                else:
                    require(certificate(s,s['reference'])=='met','Invalid reference certificate')
                seen.add(i)
            require(bool(seen), 'Empty profile')
            self._profiles[key] = copy.deepcopy(row)

    @classmethod
    def from_bundle(cls, engine, root):
        prior = TierMarking.from_bundle(engine, root)
        folder = Path(root)/'FM17J'; path = folder/'profiles.jsonl'
        manifest = json.loads((folder/'runtime-manifest.json').read_text())
        require(manifest['checkpoint']=='FM-17J','Invalid manifest')
        with path.open('rb') as stream:
            require(hashlib.file_digest(stream,'sha256').hexdigest()==manifest['sha256']['profiles.jsonl'],'Profile hash mismatch')
        rows=read_batch(path); require(len(rows)==manifest['profile_count'],'Profile count mismatch')
        return cls(engine,prior,rows)

    def capability(self,item_id,*,mode,item_fingerprint):
        result=self.prior.capability(item_id,mode=mode,item_fingerprint=item_fingerprint)
        if item_id in self._profiles:
            ids=[f"c{s['index']}" for s in self._profiles[item_id]['criteria']]
            old=result.get('checked_criteria',[]); total=len(self.engine.bank.items[item_id]['payload']['rubric'])
            result.update(reasoning_criteria=ids, accuracy_criteria=old, checked_criteria=sorted(set(ids+old),key=lambda x:int(x[1:])),
                          structured_checks_available=True,total_criteria=total,coverage='full' if len(set(ids+old))==total else 'partial',
                          basis='bounded_method_and_accuracy_observations')
        return result

    def check_work(self,item_id,*,mode,item_fingerprint,work):
        args=dict(mode=mode,item_fingerprint=item_fingerprint)
        # Preserve the existing direct-work API exactly. The new explicit envelope
        # is needed to request method marking; accuracy-only callers are unchanged.
        if item_id not in self._profiles or not isinstance(work,dict) or 'reasoning' not in work:
            return self.prior.check_work(item_id,work=work,**args)
        context=self.engine.marking_context(item_id,**args)
        require(set(work)=={'accuracy','reasoning'},'Invalid reasoning envelope')
        old=self.prior.capability(item_id,**args); accuracy=work['accuracy']; observed=work['reasoning']
        specs={f"c{s['index']}":s for s in self._profiles[item_id]['criteria']}
        require(isinstance(observed,dict) and set(observed)==set(specs),'Unexpected reasoning fields')
        require(isinstance(accuracy,dict) and set(accuracy)==set(old.get('checked_criteria',[])),'Unexpected accuracy fields')
        prior_rows={}
        if old['structured_checks_available']:
            prior_rows={r['criterion_id']:r for r in self.prior.check_work(item_id,work=accuracy,**args)['criteria']}
        decisions=[]; ft=[]; split={}
        for c in context['criteria']:
            k=c['id']; status='uncertain'; detail='No supported observed evidence.'
            if k in specs:
                spec=specs[k]; val=observed[k]; follow=False
                if spec['rule']=='product_components':
                    a,b=numbers(spec['target'],2)
                    status='uncertain' if val is None else 'met' if numbers(val,3)==(a,b,a*b) else 'not_met'
                elif spec['rule']=='product_followthrough':
                    status,follow=product_followthrough(spec,val,observed['c1'])
                elif spec['rule']=='product_pair_credit':
                    subs,follow=product_pair_credit(spec,val,observed['c1'],observed['c2']); split[k]=subs
                    status='uncertain'  # separately resolve the expressly split mark below
                else:
                    status=certificate(spec,val)
                if follow:
                    ft.append(k); detail='Consistent elimination after the specifically permitted earlier constant-product slip.'
                elif status!='uncertain':
                    detail='Compared actual structured method or proof evidence with the rubric-bound certificate.'
            elif k in prior_rows:
                status=prior_rows[k]['status']; detail=prior_rows[k]['evidence']
            decisions.append(dict(criterion_id=k,status=status,evidence=detail))
        result=reconcile_proposal(context,decisions)
        for row in result['criteria']:
            if row['criterion_id'] not in split:continue
            subs=split[row['criterion_id']]; low=subs.count('met'); high=2-subs.count('not_met')
            row['possible_marks']=[low,high];row['status']='met' if low==2 else 'not_met' if high==0 else 'partial' if low==high else 'uncertain'
            row['subcriteria']=[{'id':name,'status':status} for name,status in zip(('roots','reconstruction'),subs)]
            row['evidence']='Two separately specified rubric marks: parameterised roots and paired reconstruction.'
            result['possible_total'][0]+=low;result['possible_total'][1]+=high-2
        result.update(basis='bounded_method_certificates_and_accuracy_observations',followthrough_criteria=ft)
        return result
