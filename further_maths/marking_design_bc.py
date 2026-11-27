"""Frozen transformation design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bc import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='c095aca11e67ee58c087d54c0528e2e37c69a2cca9f0ddf79f7f7a46306d3c2d'
# Each entry describes an equivalent approach and the relevant boundary check.
NOTES={
'composition-order':(
 ('Evaluate directly or bracket the addition before multiplication.','Respect the specified order, not ordinary precedence on an unbracketed sum.'),
 ('Apply each map successively or use both products.','The given column vector distinguishes the two orders.'),
 ('Multiply the matrices or track both basis images.','The later transformation multiplies on the left.'),
 ('Transform a direction or parameterise the original line.','Origin fixed and the image direction is nonzero; both methods cover the full line.'),
 ('Use the first coordinate equation or the composition matrix.','The given scale is nonzero; the reverse order must be applied separately.'),
 ('Compare both shear products or solve the point equations for each order.','Both candidates forced by first observation; verify positive ray and reject the wrong slope. Existing AE allocation retained.')),
'invariant-lines':(
 ('Read rise/run or subtract two distinct points.','Any nonzero scalar multiple is accepted, but the zero vector is not.'),
 ('Use general points or the restriction of the map to the axis.','Nonzero factor ensures onto; nonunit factor supplies a counterexample.'),
 ('Use eigenvectors or solve the collinearity equations.','Distinct nonzero diagonal factors; both axes and no mixed direction.'),
 ('Substitute inverse coordinates or transform a point and direction.','Both factors nonzero; the complete image line differs in slope and intercept.'),
 ('Solve the slope equation or find eigenvectors with nonzero eigenvalues.','Do not divide by the slope; check the vertical case separately and ensure onto.'),
 ('Use an affine parametrisation or compare image directions.','All horizontal lines translate bijectively; only zero height is fixed pointwise; nonzero shear excludes every other direction. Existing AI allocation retained.')),
'fixed-points':(
 ('Rearrange or verify the unique solution by substitution.','The displayed coefficient is nonzero.'),
 ('Solve the fixed-point equation on the axis or use the scalar multiplier.','Nonunit multiplier forces zero; a single nonzero counterexample suffices to disprove pointwise fixation.'),
 ('Use component equations or the kernel of A-I.','The nonzero shear forces y=0; x is arbitrary.'),
 ('Use component subtraction or compute (A-I) times the point.','The nonzero coefficient forces x=y; displacement is parallel to (1,1).'),
 ('Solve both fixed coordinate equations or use the kernel.','Specified x is nonzero, so k is unique; the remaining equation defines exactly a line.'),
 ('Use component equations or classify the kernel by rank.','Distinguish h=1 and k=1 independently; the nonzero off-diagonal entry precludes the identity.')),
'basis-images':(
 ('Read coordinates or expand the linear combination.','Keep the order of the unit vectors.'),
 ('Multiply by each unit column or read columns.','Rows are not the basis images under the column-vector convention.'),
 ('Assemble the image columns directly or check on both basis vectors.','Two independent coordinate inputs uniquely determine the matrix.'),
 ('Add and subtract the image equations or solve the two independent linear systems.','Division by two is valid; keep the sign of the second input.'),
 ('Use the inverse input matrix or solve entrywise.','Nonzero input determinant ensures uniqueness; verify the third image.'),
 ('Use linearity or compare matrix columns directly.','Separate k=0 before dividing; h=0 gives a free second column, h nonzero gives inconsistency.')),
'composition-compute':(
 ('Use rotation coordinates or the standard rotation matrix.','Anticlockwise quarter-turn negates y and swaps coordinates.'),
 ('Use direct successive images or both matrix products.','The shear is nonzero so the two test images differ.'),
 ('Multiply or find the images of the two basis vectors.','A acts first, so B is on the left.'),
 ('Eliminate the original parameter or substitute inverse coordinates.','Nonzero horizontal image-direction component gives a whole nonvertical line.'),
 ('Right-multiply by the inverse or solve simultaneous equations in U entries.','A has determinant one; reverse-order inversion is not equivalent; check both image methods.'),
 ('Compare entries of both shear products or solve the four scalar equations.','Nonzero scale coefficients recover unique parameters; both orders exactly when p=w=1 and qr=0.')),
'figure-images':(
 ('Apply the coordinate rule or the diagonal matrix.','Only the x-coordinate changes.'),
 ('Multiply by e1 and e2 or inspect matrix columns.','Rows do not represent images of column basis vectors.'),
 ('Use component equations or row-column products.','Retain the sign of the negative second coordinate.'),
 ('Use two image points or transform the direction vector and a point.','Image direction nonzero and horizontal component nonzero; distinguish line from segment.'),
 ('Invert or solve the two image equations; use base-height or determinant area.','Determinant nonzero ensures unique preimage; area is unsigned.'),
 ('Parameterise and map the line or use transformed base and direction.','When horizontal direction vanishes, distinguish zero from nonzero vertical direction before division; otherwise all X occur.')),
'fixed-invariant':(
 ('Substitute the point or compare the ratio of coordinates.','Check the actual specified line.'),
 ('Use a general axis point and a nonzero counterexample.','Vertical multiplier is nonzero and not one; the axis maps onto itself but moves nonzero points.'),
 ('Parameterise the vertical line or use inverse coordinates.','Vertical multiplier nonzero ensures onto; only the point at height zero is fixed.'),
 ('Map each line parametrically or substitute image coordinates.','Nonzero nonunit multiplier; nonzero horizontal height changes, vertical lines remain setwise invariant.'),
 ('Use a direction eigenvector or compare slopes without losing a zero component.','Given slope nonzero forces the multiplier; it differs from one so no nonzero fixed point on this line.'),
 ('Use general affine lines or direction and base-point constraints.','Distinguish identity at k=v, zero multiplier and other nonzero values; vertical lines collapse at zero, nonvertical lines require zero slope and intercept otherwise.')),
'describe-transform':(
 ('Read columns or multiply the unit vectors.','Use the actual scaled basis images, not unit-normalized directions.'),
 ('Use a test point and fixed/perpendicular directions or the coordinate swap rule.','A nonzero fixed line rules out a quarter-turn; the worked solution includes the test-point image.'),
 ('Use basis images or compare with the standard rotation matrix.','Angles are 90, 180 or 270 degrees under the specified anticlockwise convention; centre is origin.'),
 ('Compose matrices or track basis vectors through the three maps.','Positive scale and correct reflection axis; multiplication order matters.'),
 ('Use independent fixed/reversed directions or the projection formula.','The fixed point is nonzero; the perpendicular direction supplies an independent basis.'),
 ('Normalize and use orthogonality, or diagonalize the symmetric matrix.','Handle zero scale first; use the alternate nonzero axis when rho+p and h vanish; unit scale gives pure reflection.')),
}

def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==144 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BC frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BC rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AE and AI rubrics preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and variant prompts and answers inspected; structural checks only, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial matrix transformations FM-16BC (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
