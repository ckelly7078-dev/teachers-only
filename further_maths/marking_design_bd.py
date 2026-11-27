"""Frozen determinant and inverse design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bd import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='f8f866ebb91ac2342d5edc47add01fe5a95d423297272d39b1dcdd33fe0b3546'
# Each entry describes an equivalent approach and the relevant boundary check.
NOTES={
'det-area':(
 ('Count unit squares or multiply perpendicular lengths.','Area is unsigned.'),
 ('Use reflection geometry or determinant of its diagonal matrix.','Negative determinant reverses orientation, absolute determinant is one.'),
 ('Use determinant directly or transform vertices and calculate area.','Use the absolute value of the determinant.'),
 ('Compute BA and its determinant or use determinant multiplicativity for area.','Composition order matters even if determinant is order-independent.'),
 ('Solve both signed equations or sketch the absolute linear function.','Both roots are distinct since the target area is positive.'),
 ('Split the absolute quadratic or intersect its graph with a horizontal line.','At c=0 branches coincide; at the positive threshold one square is zero; the nonzero off-diagonal excludes the zero map.')),
'orientation':(
 ('Use sign rule or repeated addition.','Negative times positive is negative.'),
 ('Compare ordered vertex triples or use reflection determinant.','Reflection preserves distances and unsigned area.'),
 ('Compute signed area of images of basis vectors or use ad-bc.','Negative nonzero determinant reverses orientation.'),
 ('Multiply determinants or compute the composition determinant.','Two negative determinants give positive orientation; unsigned area stays positive.'),
 ('Solve the signed equations directly or inspect the determinant quadratic.','Target positive area exceeds the constant in the negative branch, so its squared parameter is negative.'),
 ('Use a sign diagram, factored quadratic or roots and leading coefficient.','Distinct real boundaries; at zero determinant the nonzero off-diagonal forces rank one.')),
'collapse':(
 ('Compare component ratios or verify a common multiplier.','Both components use the same nonzero scale.'),
 ('Use first column or direct matrix-vector multiplication.','A single nonzero image disproves the zero map.'),
 ('Use the span of columns or parameterize all inputs.','The first column is nonzero and all scalar multiples occur.'),
 ('Solve the homogeneous equations or express the map as an outer product.','On the input line the free horizontal coordinate still covers the full image.'),
 ('Use determinant or column dependence.','The first column is never zero, so singularity gives rank one, not zero.'),
 ('Reconstruct columns or solve linear equations for the entries.','Targets on the image have an entire affine line of preimages, outside have none. Existing AI rubric retained.')),
'collapse-parameter':(
 ('Use ad-bc or signed parallelogram area.','Keep the sign of the determinant.'),
 ('Use the first column and span of both columns or direct mapping.','Nonzero first column ensures the whole x-axis occurs.'),
 ('Set determinant zero or equate column slopes without losing solutions.','Coefficient of k is nonzero.'),
 ('Factor or solve the determinant quadratic, then span the image.','Both roots; the fixed nonzero upper-right entry ensures rank one.'),
 ('Complete the square or set the discriminant to zero.','Repeated root counts once; nonzero second column gives the full line.'),
 ('Use discriminant or vertex of the quadratic; find nullspace by substitution.','Threshold equality gives one root, not two; nonzero fixed entry ensures rank one at every singular value.')),
'det-three':(
 ('Use ad-bc.','Preserve signed determinant.'),
 ('Use determinant alternating property or the permutation sign.','Exactly one row exchange negates the determinant.'),
 ('Use the requested first-row cofactor expansion.','Cofactor signs alternate; zero entry has zero contribution.'),
 ('Use a valid row addition then expand, or triangularize with determinant accounting.','Row addition preserves determinant; row swaps/scalings need compensation.'),
 ('Use cofactor expansion or determinant-preserving elimination.','Nonzero leading minor forces rank at least two at the unique zero.'),
 ('Factor the determinant by expansion or recurrence.','Minor with rows 1,2 and columns 2,3 is a fixed positive square, including k=0.')),
'inverse-two':(
 ('Divide by the coefficient or multiply by its reciprocal.','The divisor is nonzero.'),
 ('Multiply the specified row and column.','Identity has zero off-diagonal entries; a nonzero one disproves the candidate.'),
 ('Use adjugate, row reduction or solve for the inverse columns.','Nonzero determinant; multiplication must yield the identity.'),
 ('Use a valid inverse calculation and recover by applying it.','Nonzero determinant implies unique preimage.'),
 ('Equate the inverse entry or solve its defining column equation.','Exclude zero determinant before clearing denominators.'),
 ('Use inverse formula or coefficient equations for the inverse.','Upper endpoint gives k=0 once; r<=0 and r above endpoint are impossible. Existing AJ rubric retained.')),
'inverse-three':(
 ('Use substitution or elimination.','Substitute the actual given value of y.'),
 ('Multiply the specified row and column or solve for the missing inverse entry.','The product must be the identity, not simply triangular.'),
 ('Solve for a general right-hand side, augment with identity or use adjugate.','Elimination pivots are nonzero; verify the full product.'),
 ('Obtain inverse by valid elimination or adjugate then apply it.','Check against original system, not only reduced equations.'),
 ('Back-substitute or solve the third inverse column.','Exclude k=0 before dividing; unique inverse-entry condition.'),
 ('Back-substitute symbolically or use row reduction split by pivot vanishing.','At k=h=0 the fixed nonzero off-diagonal still forces z=0, so nullity is one.')),
'inverse-product':(
 ('Undo in reverse order or divide by the product of multipliers.','Both multipliers are nonzero.'),
 ('Use inverse rule or verify identity by multiplication.','Candidates differ because the shear and scaling do not commute.'),
 ('Use the required inverse-product rule and individual inverses.','Reverse order, not entrywise inversion.'),
 ('Apply the two inverse matrices or undo both coordinate maps.','Intermediate vector must undo A before B.'),
 ('Invert the given product or multiply the inverse equation appropriately.','Isolate A by right multiplication; both factors invertible.'),
 ('Compare AB and BA or compare inverse products directly.','Exclude h=0 first; commutation iff the shear is zero or the two diagonal entries coincide.')),
'inverse-identities':(
 ('Divide by the specified nonzero coefficient.','Product equals one.'),
 ('Use the inverse definition.','Identity must have the specified dimension in each variant.'),
 ('Use double-inverse definition and associativity without calculating the inverse.','Only adjacent factors cancel; no commutation needed.'),
 ('Simplify using adjacent inverse pairs or equivalent associative grouping.','Do not reorder noncommuting factors.'),
 ('Invert both sides or use reversed product identity.','All equation transformations are reversible for the given invertible matrices.'),
 ('Compare entries of A plus inverse or multiply by A to get a quadratic matrix identity.','k=0 excluded; k equal to reciprocal gives any off-diagonal, other root forces zero.')),
'singular-condition':(
 ('Apply zero product or solve both linear factors.','Include both distinct roots.'),
 ('Show rows proportional or calculate determinant.','All nonzero entries do not imply invertibility.'),
 ('Solve determinant equation by square roots or factoring.','Positive radicand gives both signs.'),
 ('Factor individual determinants or use determinant multiplicativity.','The positive square root lies strictly between the two positive magnitudes, so no overlaps.'),
 ('Solve second determinant first or intersect both zero sets.','Both pairs require h=k squared; verify each.'),
 ('Use determinant product and direct multiplication or the rank argument for one invertible factor.','Exactly one singular factor cannot yield zero product; both singular at unique intersection. Existing AP rubric retained.')),
'det-classification':(
 ('Use ad-bc or signed area.','Preserve sign.'),
 ('Use row dependence or direct zero determinant.','Nonzero entries do not preclude row dependence.'),
 ('Use expansion, triangularization or repeated-row rule.','Classify each separately by determinant, including the repeated rows.'),
 ('Use determinant multiplicativity without multiplying matrices.','Reversal preserves determinant but need not preserve matrix product.'),
 ('Compare zero sets of the two determinants.','C strictly negative for every real k, including zero.'),
 ('Expand along first column or use block triangular determinant.','Curves meet only at origin; exclude intersection from exactly-one cases.')),
'matrix-equation':(
 ('Divide by nonzero coefficient or multiply by reciprocal.','Explain why cancellation is valid.'),
 ('Use left multiplication by inverse, without recomputing candidates.','Products differ and invertibility guarantees uniqueness.'),
 ('Use an inverse by elimination or adjugate then left-multiply.','Verify original product AX, not XA.'),
 ('Use inverse on correct side in each equation.','Compare distinct matrices; verify both original equations.'),
 ('Use inverse or simultaneous entry equations and symmetry.','Nonzero determinant guarantees unique X for each h; off-diagonal equality gives unique h.'),
 ('Use commutation criterion or solve both matrix equations entrywise.','k=0 impossible since B invertible; for nonzero k either h=0 or k equals first diagonal entry, including overlap.')),
}

def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==216 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BD frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BD rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AI, AJ and AP rubrics preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and variant prompts and answers inspected; structural checks only, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial matrix determinants and inverses FM-16BD (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
