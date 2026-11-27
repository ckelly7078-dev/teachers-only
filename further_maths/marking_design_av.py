"""Frozen shared-design review of advanced algebra; exact variant checks, not approval."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_av import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='d6c90518f6166c74654ddcaa49ec065612ec2fe74d52383ec3fcadf885fd0f49'
# Reviewed equivalent approaches and domain requirements for each tier.
NOTES={
 'combined-roots':('Invert then translate using invariants, or substitute the inverse map into the polynomial and normalise.','T5: nonzero reciprocal product and positive original discriminant. T6: h nonzero, original product strictly negative, translated product nonzero; both endpoints excluded.'),
 'cube-sums':('Factor the sum of cubes or use S cubed minus 3PS. For T6, strict monotonicity may be proved algebraically or by differentiation.','T5: nonzero sum fixes product; verify reality. T6: S squared at least 4P; disjoint cubic ranges, repeated roots at both included endpoints; enrichment only.'),
 'factor-connection':('Compare coefficients, eliminate either unknown, or use an equivalent scaled-factor argument.','T5: both distinct ordered pairs satisfy both coefficient constraints. T6: negative discriminant gives none, zero gives one, positive gives two distinct pairs.'),
 'quadratic-from-roots':('Use the squared-difference identity or equivalent coefficient discriminant reasoning without choosing a root ordering.','T5: positive prescribed difference fixes the product and reality. T6: zero sum is one equation, positive radicand yields two; each has the same strictly positive discriminant.'),
 'reciprocal':('Use reciprocal invariants or polynomial reversal for T5; for T6 classify fixed and swapped root permutations directly.','T5: nonzero original product. T6: exclude undefined denominators, repeated roots yield a separate family, complex conjugate roots are allowed; enrichment only.'),
 'reciprocal-sums':('Combine reciprocals or use the reversed polynomial and coefficient comparison.','T5: nonzero product and positive discriminant. T6: positive product excludes zero; absolute-value threshold includes repeated roots and the sign of the sum fixes the signs.'),
 'root-ratios':('Derive S squared over P minus two by combining fractions or use the squared-root identity.','T5: negative ratios force negative product; negative sum selects one branch. T6: exclude h=-2, distinguish denominator signs and include h=2 only for coincident ratios.'),
 'root-squares':('Use S squared minus 2P or expand the square of the sum.','T5: verify the computed discriminant. T6: both bounds on h included; zero sum at lower bound, zero root at h=0, repeated roots at upper bound.'),
 'root-sum-product':('Use a ratio parametrisation or Vieta and the positivity constraints; for T6 use sum, product and discriminant.','T5: positive square root only. T6: positive product excludes zero and opposite signs; include both repeated-root thresholds.'),
 'scaled-roots':('Use both scaled invariants or polynomial substitution, treating scale zero separately.','T5: both scale signs initially possible, coefficient sign selects one. T6: h negative impossible, zero gives repeated zero, positive gives two distinct equations with opposite root signs.'),
 'shifted-products':('Expand both translated products or evaluate the monic polynomial at the shifts.','T5: distinct shifts give independent equations; check discriminant. T6: do not divide by k=0; infinite family at zero, repeated-root endpoints included.'),
 'shifted-roots':('Use translated invariants or direct polynomial substitution and solve the product quadratic.','T5: product alone permits two shifts; positivity selects one. T6: minimum included, zero product excluded, two shifts strictly between minimum and zero.'),
 'squared-roots':('Recover squared magnitudes using coefficients or factorisation, then apply unordered sign branches.','T5: opposite signs and positive sum select the unique pair. T6: nonnegative squared roots; zero magnitude gives two equations, unequal positive gives four, equal gives three.'),
 'symmetric-parameter':('Use discriminant as squared root difference; solve by completing the square or an equivalent exact inequality method.','T5: both parameter branches give the specified positive discriminant. T6: h negative excluded, positivity eliminates negative branch, both interval endpoints included and h=0 gives a repeated root.'),
}


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in (5,6) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==84 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AV frozen batch changed; re-review required')
    for item in items:
        p=item['payload'];alternate,boundary=NOTES[p['path']];rubric=p['rubric']
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative mathematical design and parameter branches inspected. Independent exact-fact oracle passed this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Reviewed design-specific criteria, explicit M/A/R allocation, original mark total retained; AF typed criteria retained for its two cells.'},
            'alternative_methods':{'decision':'pass','evidence':alternate+' Respect explicit question restrictions.'},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated method or reasoning credit where valid after arithmetic errors. Require correct specified accuracy results and do not automatically award final accuracy for an incorrect result.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and all variant prompts and answers inspected; structural presentation checks passed. No rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial advanced algebra FM-16AV (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
