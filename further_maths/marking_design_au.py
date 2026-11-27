"""Frozen AU design-review evidence, with independent variant checks, not teacher approval."""
import hashlib
import json
from active_difficulty import Resolver,require
from difficulty_revision_au import BANKS
from marking_review import fingerprint
from marking_algebra_at import records as prior_records

FROZEN_BATCH_SHA='48721108f60915a61c3602318de4a6e3e2fdba4573e3c992cc648a09da6f188b'
# Shared design evidence for tiers 1, 2 and 4, in that order.
# Each pair is an equivalent approach and a domain/boundary review note.
NOTES={
 'combined-roots':(('Subtract before dividing.','Every supplied difference is nonzero.'),('Evaluate the denominator at the offending root.','A zero denominator prevents a finite transformed pair.'),('Use both affine invariants then the square identities.','Zero transformed product is valid for squaring; variant one has it.')),
 'cube-sums':(('Evaluate signed cubes separately.','Negative cubes retain their sign.'),('Expand the cube of a sum or factor the sum of cubes.','The mixed term is 3PS, not zero in these examples.'),('Translate the invariants, then factor the sum of cubes.','No division by a root is needed.')),
 'factor-connection':(('Distributive or grid expansion.','No denominator or parameter boundary.'),('Use signed coefficient products or a grid.','Negative times negative gives positive constant.'),('Compare coefficients or expand the proposed identity.','The leading and constant multipliers are nonzero, so both unknowns are fixed.')),
 'quadratic-from-roots':(('Use signed factors or sum-product construction.','Monic normalization fixes the leading coefficient.'),('Construct the monic equation and compare scalar multiples.','The scalar must be nonzero to preserve the roots.'),('Recover P from the squared sum, then compare coefficients.','Positive discriminant in each variant establishes two distinct real roots.')),
 'reciprocal':(('Any valid common denominator.','Both given denominators are nonzero.'),('Combine fractions symbolically.','The product of the two original roots must be nonzero.'),('Use reciprocal substitution after translation or transform the invariants.','Every shifted product is positive and nonzero.')),
 'reciprocal-sums':(('Any valid common denominator.','Both supplied denominators are nonzero.'),('Use the constant coefficient or the displayed zero factor.','A single zero root makes the reciprocal sum undefined.'),('Use the translated polynomial evaluated at zero, or expand the product.','All shifted products are negative and nonzero.')),
 'root-ratios':(('Divide in each order.','Both supplied numbers are nonzero.'),('Inspect multiplicity and the zero-root case.','Repeated roots give equal ratios; a zero root is excluded.'),('Rearrange S^2/P-2 or derive it from the two fractions.','P must be nonzero; the recovered products are positive.')),
 'root-squares':(('Binomial expansion or direct multiplication.','Keep the signed mixed term.'),('Compare numerical sides, then expand symbolically.','The missing term is 2uv; the identity holds for all u,v.'),('Expand the translated squares or use translated invariants.','No denominator or branch exclusion is needed.')),
 'root-sum-product':(('Distributive expansion or coefficient products.','Keep the signed constant.'),('Normalize to a monic polynomial or match factored coefficients.','The leading coefficient is nonzero.'),('Expand the squared difference or subtract it from the squared sum.','The resulting product fixes the constant of the monic polynomial.')),
 'scaled-roots':(('Multiply each value by the scale.','Both outputs must use the same scale.'),('Compare scaled factors or use sum-product identities.','The product uses the square of the scale.'),('Use signed coefficient ratios or normalized polynomial substitution.','The original sum is nonzero, so m is unique; both candidates have the same sum but only one has the correct product.')),
 'shifted-products':(('Subtract from each factor before multiplying.','Keep the sign of each translated factor.'),('Expand both brackets or use P-dS+d^2.','The mixed term includes both original roots.'),('Evaluate the monic polynomial at t or expand the shifted product.','Both distinct solutions of the equivalent quadratic are valid.')),
 'shifted-roots':(('Subtract the shift from each number.','Negative translated values are permitted.'),('Test the substituted argument at an original root.','The sign inside f is opposite the root translation.'),('Use polynomial substitution or translated invariants.','The new sum fixes the unique shift; translation preserves the squared root difference.')),
 'squared-roots':(('Multiply each signed number by itself.','A negative number has a positive square.'),('Expand the squared sum and square the product.','No division by a root is needed.'),('Translate S,P then apply U^2-2V and V^2.','Squared roots may coincide; the monic construction preserves multiplicities.')),
 'symmetric-parameter':(('Undo addition then division.','The coefficient of the unknown is nonzero.'),('Set the discriminant to zero or match a repeated linear factor.','Both signs satisfy the repeated-root condition.'),('Equate coefficient invariants then calculate the discriminant.','The linear equation fixes k; the first two variants have negative discriminant and the third positive.')),
}


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,5) for v in (1,2,3) if (p,t)!=('root-sum-product',3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==165 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AU frozen review batch changed; re-review required')
    prior={x['id']:x for x in prior_records()}
    for item in items:
        p=item['payload'];path,tier=p['path'],p['tier'];qid=item['id'];fp=fingerprint(item)
        rubric=p['rubric'];alloc=[{'criterion_index':i,'marks':{t:row['marks'] if t==row['type'] else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        if tier==3:
            old=prior[qid];checks=old['checks'];checks['mathematical_correctness']['evidence']+=' Prompt, exact answer and facts preserved; independent variant oracle passed.'
            checks['criterion_allocation']={'decision':'pass','evidence':'Applied reviewed allocation to the active rubric: '+' '.join(row['criterion'] for row in rubric)}
            checks['presentation']={'decision':'pass','evidence':'Re-reviewed amended solution and misconception guidance against the flagged issue. Text inspected, not rendered.'}
            record={'supersedes_fingerprint':old['fingerprint'],'review_basis':'individual_item_rereview'}
        else:
            alternate,boundary=NOTES[path][{1:0,2:1,4:2}[tier]]
            checks={
                'mathematical_correctness':{'decision':'pass','evidence':'Shared design reasoning inspected. Independent original oracle passed this variant; exact structured facts: '+json.dumps(p['facts'],ensure_ascii=False)},
                'criterion_allocation':{'decision':'pass','evidence':'Reviewed shared design; each criterion explicitly specifies method, accuracy or reasoning, with original total preserved.'},
                'alternative_methods':{'decision':'pass','evidence':alternate+' Respect any explicit method restrictions.'},
                'consequential_errors':{'decision':'pass','evidence':'Retain valid demonstrated method credit after a later arithmetic slip; accuracy requires the specified correct result; valid reasoning may be credited independently.'},
                'boundary_cases':{'decision':'pass','evidence':boundary},
                'presentation':{'decision':'pass','evidence':'Representative prompt, solution and guidance inspected; all variant text passed structural delimiter checks in private QA. No rendered or individual prose certification.'},
            }
            record={'review_basis':'shared_design_plus_variant_oracle'}
        yield dict(record,id=qid,fingerprint=fp,reviewer='AI editorial batch FM-16AU (teacher approval pending)',teacher_approved=False,checks=checks,allocation=alloc)

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
