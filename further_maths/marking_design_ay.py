"""Version-bound Argand and angle review; proposed AD allocations remain pending."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_ay import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='73d53cad40d23eb30c2ee1b38e8fe481b47f47737ac878b5b0893bb3cdfcca2a'
# Each pair gives permitted methods and the relevant domain or boundary conditions.
NOTES={
 'argand-coordinates':(
  ('Read a labelled Cartesian grid or use the coordinate convention.','Horizontal first, signed vertical second.'),
  ('Read the real part and the coefficient of i directly or use an Argand diagram.','The imaginary component is a real coefficient; axes cannot be interchanged.'),
  ('Plot on a correctly oriented, labelled Argand diagram.','Negative real and positive imaginary coordinates place the point in quadrant II; neither is zero.'),
  ('Use geometric reflection or change the relevant coordinate sign.','The real-axis reflection changes the vertical sign; imaginary-axis reflection changes the horizontal sign; both commute.'),
  ('Use the midpoint equation componentwise or in complex notation.','The recovered point has two negative coordinates, is unique and must be plotted along with A.'),
  ('Eliminate t or use component signs and the corresponding axis crossings.','The two distinct component zeros split the real line into III, negative imaginary axis, IV, positive real axis and I. Neither origin nor quadrant II occurs.')),
 'argand-displacement':(
  ('Use the coordinate convention or draw the directed movement.','Right and down have opposite signs.'),
  ('Subtract position vectors or obtain the directed arrow geometrically.','The displacement is B-A, not the position B or the reverse displacement.'),
  ('Use the tip-to-tail construction or add/subtract components.','The requested second-to-first displacement is first minus second.'),
  ('Use the parallelogram law or equal opposite directed sides.','C=A+B, but the A-to-B diagonal is B-A.'),
  ('Solve the two vector equations by addition and subtraction or construct their half-sum and half-difference.','The given difference is directed; halving the two combinations uniquely recovers the ordered endpoints.'),
  ('Use a 2D determinant and dot product or equivalent exact tests for parallel and perpendicular directions.','Both sides are nonzero. The parallel and perpendicular parameter values are distinct; all remaining values give a nondegenerate nonrectangular parallelogram.')),
 'angle-units':(
  ('Use pi/180 or the fraction of a full turn.','Retain exact radians.'),
  ('Use 180/pi or the fraction of a full turn.','A fractional degree measure is valid; no rounding needed.'),
  ('Convert directly using 180/pi.','The negative signed rotation is not reduced modulo 360.'),
  ('Convert either angle to the other unit before adding.','Retain the negative rotation and report both exact units without normalization.'),
  ('Convert interval bounds or convert the entire family to radians, then solve the integer inequality.','The lower bound is inclusive and upper exclusive; the offsets lie strictly inside a full turn.'),
  ('Work consistently in either degrees or radians and substitute the general congruence into the half-angle condition.','The interval admits exactly n=0,1,2. Modulo pi the second condition is automatic; modulo 2pi it restricts n to even values. Existing AD payload retained pending version-history migration.')),
 'exact-radians':(
  ('Use a special-angle triangle or known exact unit-circle values.','Both sine and cosine are positive in quadrant I.'),
  ('Use reference angles or unit-circle symmetry.','Quadrant II has negative cosine and positive sine.'),
  ('Substitute special-angle values and simplify radicals.','Preserve the signed difference and exact form.'),
  ('Use polar multiplication and the angle-addition identity as required.','The arguments sum to pi/2, so cosine vanishes and sine is one.'),
  ('Use the unit circle or solve the sine equation then filter by cosine sign.','The sine is strictly positive and below one; cosine must be strictly negative, leaving only quadrant II.'),
  ('Use the supplied identity to combine terms into a shifted cosine, or an equivalent exact phase construction.','Outside the amplitude range none; at each endpoint one representative; inside two distinct modulo 2pi. Normalize into [0,2pi), excluding 2pi itself.')),
 'polar-geometry':(
  ('Use the geometric distance and quarter-turn angle.','The radius is positive and the point is above the origin.'),
  ('Use an Argand diagram or the definitions of modulus and argument.','Distance is positive and the principal argument of a negative imaginary-axis point is -pi/2.'),
  ('Use polar-to-Cartesian conversion or right-triangle geometry.','The two points are distinct reflections; twice their positive angle is less than pi.'),
  ('Use symmetry and right-triangle geometry as explicitly requested.','The midpoint is real; the half-chord is perpendicular to the radius. Do not expand a modulus squared.'),
  ('Use the perpendicular bisector of a chord or equivalent exact component reasoning.','The midpoint is nonzero and strictly inside the circle. Exactly two distinct points with opposite imaginary signs form one unordered pair.'),
  ('Use midpoint/chord geometry or subtract the squared Cartesian radius equations.','Outside |h|<=2r no pair; extreme h gives one coincident pair; h=0 gives all antipodal pairs; nonzero interior h gives exactly two ordered pairs.')),
 'modulus-constraints':(
  ('Use Pythagoras or the distance formula.','Take the positive square root of the sum of squares.'),
  ('Use Euclidean distance or the modulus-squared identity.','The sum of absolute components is not the Euclidean norm for these two nonzero components.'),
  ('Use Pythagoras or z times its conjugate.','Both results must be nonnegative exact moduli, simplified where possible.'),
  ('Solve the squared-distance equation or use a right triangle.','The positive and negative imaginary possibilities are distinct; strict negativity selects only one.'),
  ('Subtract the two circle equations or use their radical axis and intersections.','Centres are distinct and the remaining squared imaginary component is strictly positive. Both signed solutions satisfy the original nonnegative distances.'),
  ('Solve for nonnegative component magnitudes using their sum and product, or intersect the circle with the absolute-value diamond.','The closed bounds are r and r sqrt(2); one zero magnitude at the lower boundary, equal magnitudes at the upper boundary. Four points at either endpoint, eight in the interior, none outside. AH rubric retained.')),
 'argument-range':(
  ('Read the positive real axis geometrically.','Its principal angle is zero; the point is nonzero.'),
  ('Use a quadrant-aware argument or adjust the inverse tangent of the component ratio.','Both components are negative, so use quadrant III and subtract pi from the positive reference angle.'),
  ('Use a reference angle or quadrant-aware inverse tangent.','Negative real and positive imaginary components require quadrant II and an angle in (-pi,pi].'),
  ('Use B-A and a quadrant-aware angle, then normalize.','The displacement is nonzero in quadrant IV; add 2pi to its negative principal angle.'),
  ('Use the tangent relation or a positive radial multiple of the unit direction.','The fixed negative real part is compatible with the third-quadrant ray; the opposite ray is excluded.'),
  ('Use component signs and exact tangent with quadrant checks.','At the smaller component zero z=0 and argument is undefined. The larger zero gives a positive real point. The two requested angles share tangent -1, but only the quadrant-IV branch is attained. AD typed rubric retained.')),
}
PROPOSED_AD=(('M','Convert interval bounds and express T as a general congruence.'),
             ('R','Show the original half-angle condition modulo pi is automatic.'),
             ('A','Give all three admissible degree values, checking interval endpoints.'),
             ('R','Derive the even-integer condition for the stricter modulus and give exactly the two surviving values.'))


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve_version(p,t,v,'ad') if (p,t)==('angle-units',6) else r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==126 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AY frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        pending=(p['path'],p['tier'])==('angle-units',6)
        require(pending or all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped AY rubric')
        checks={
          'mathematical_correctness':{'decision':'pass','evidence':'Representative design and numerical prompts and answers reviewed; independent exact-fact oracle passed this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
          'criterion_allocation':{'decision':'revise' if pending else 'pass','evidence':('Proposed four explicit types; retain AD history and active payload until a multi-version migration is reviewed.' if pending else 'Design-specific provisional marking criteria reviewed; original total preserved. Existing AD argument and AH modulus allocations retained.')},
          'alternative_methods':{'decision':'pass','evidence':alternate+' Respect explicit question restrictions.'},
          'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning credit after arithmetic slips. Require the correct stated accuracy result; do not award accuracy automatically.'},
          'boundary_cases':{'decision':'pass','evidence':boundary},
          'presentation':{'decision':'pass','evidence':'Representative worked solution and variant text inspected; delimiter checks only. Plotting requirements are explicit where needed; no rendered diagram or individual solution certification.'},
        }
        allocations=PROPOSED_AD if pending else tuple((row['type'],row['criterion']) for row in rubric)
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if kind==t else 0 for t in ('M','A','R')},'evidence':criterion} for i,(row,(kind,criterion)) in enumerate(zip(rubric,allocations))]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial Argand and angle FM-16AY (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
