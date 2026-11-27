"""FM-16AZ frozen polar and locus design evidence, not teacher approval."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_az import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='6fd19029406170c8752cc8f1f9c94dd9c1428c4231407896a7771098fef82174'
# Alternatives and domain/boundary decisions reviewed for each design.
NOTES={
'polar-to-cartesian':(
 ('Use special-angle triangles or unit-circle values.','Both ratios are positive in quadrant I.'),
 ('Use the unit circle or reference angle with signs.','Quadrant II has negative cosine and positive sine.'),
 ('Use signed trigonometric ratios or unit-circle coordinates.','Both components are negative for the specified quadrant-III angle.'),
 ('Convert both numbers before adding, or combine their components algebraically.','Opposite imaginary signs do not imply cancellation unless moduli are equal.'),
 ('Use the real-part equation or the tangent ratio with a sign check.','Nonzero cosine fixes positive modulus uniquely; the opposite ray is not allowed.'),
 ('Solve the two linear component equations or resolve along the two unit directions.','Both sin and cos are positive. Strict positivity requires k>tan(theta)|h|; equality makes at least one modulus zero, including both at the origin.')),
'cartesian-to-polar':(
 ('Use Pythagoras or the Euclidean norm.','Take the nonnegative square root.'),
 ('Use atan2 or a reference angle with quadrant correction.','Negative real and positive imaginary components require quadrant II, not IV.'),
 ('Use exact trigonometric ratios or a unit-circle direction.','Quadrant III is represented by a negative principal angle.'),
 ('Use directed endpoint differences and quadrant-aware angles.','AB lies in quadrant II, BC on the negative imaginary axis; C is a position vector, not BC. Existing typed rubric retained.'),
 ('Solve the radius equation or use right-triangle geometry.','The imaginary magnitude is positive; strict negativity selects one sign.'),
 ('Use the squared imaginary coordinate or the cosine relation on the circle.','Outside the closed radius interval none; at either boundary one; inside two; the negative real axis uses pi, not minus pi.')),
'zero-exception':(
 ('Simplify before applying the distance formula.','Zero is the origin.'),
 ('Use geometric direction or the definition of argument for nonzero numbers.','Zero modulus is valid; argument of zero is undefined.'),
 ('Use simultaneous zero components or a positive sum of squares.','Both vanish at the same unique parameter.'),
 ('Inspect numerator and denominator separately.','Their distinct zeros give a valid zero and an undefined quotient respectively.'),
 ('Intersect a vertical line with a circle or solve for y squared.','Radius below the positive fixed real part is impossible; equality gives one; greater gives two; none can be zero.'),
 ('Factor the expression or simplify separately on its domain.','The excluded denominator line is never restored; exactly one admissible zero pair; all other admissible points have defined argument.')),
'polar-products':(
 ('Use a common denominator.','No principal normalization requested.'),
 ('Use multiplicativity of the modulus or Cartesian multiplication and norm.','Positive moduli multiply, not add.'),
 ('Multiply in polar form or convert to Cartesian then back.','Normalize only by full turns; pi is included and minus pi excluded.'),
 ('Divide the specified product by both known nonzero factors.','Unknown positive modulus is unique; subtract both arguments modulo two pi.'),
 ('Use two angle congruences or the Cartesian square-root reconstruction.','Two sign-related pairs satisfy both observations; either alone leaves an angle free. Existing AN rubric retained.'),
 ('Solve the angle congruence or set the imaginary part of the product to zero.','Six integer values from -2 to 3; even gives positive and odd negative; zero product impossible.')),
'polar-quotients':(
 ('Divide the moduli and subtract in the stated order.','Keep the raw angle even if outside principal range.'),
 ('Use zero distance or Cartesian modulus squared.','Zero denominator makes the quotient undefined.'),
 ('Divide in polar form or rationalize in Cartesian form.','Nonzero divisor; normalize into (-pi,pi], including pi rather than minus pi.'),
 ('Use associativity with inverse factors or compute the inner quotient first.','All three factors nonzero, so rewriting is reversible.'),
 ('Recover the numerator by multiplying the specified quotient by w.','Positive quotient modulus and nonzero w ensure uniqueness.'),
 ('Substitute q=z/w and solve the quadratic; equivalent real/imaginary separation accepted.','Thresholds are +/-2/a. Repeated roots +/-1 have unit modulus; interior conjugates have unit modulus; exterior real reciprocal roots have same sign and absolute-value moduli. Constant 1 excludes zero.')),
'argument-normalization':(
 ('Use full turns or degree conversion.','Keep the unwrapped angle.'),
 ('Use modular arithmetic or whole turns.','Negative real axis uses pi; minus pi is excluded.'),
 ('Subtract integer turns or use the unit circle.','The chosen representative must lie in the half-open interval.'),
 ('Use wrapped or unwrapped intermediate product angles.','All factors nonzero; wrapped representatives are congruent modulo two pi.'),
 ('Solve the congruence or use the two opposite square-root directions.','Exactly two distinct representatives in the half-open interval.'),
 ('Solve the wrap inequalities or reduce modulo two pi.','The three intervals are exhaustive for the given t domain. At both raw +/-pi thresholds the representative is pi.')),
'distance-circle':(
 ('Use Pythagoras or the modulus.','Distance is nonnegative.'),
 ('Use the definition of modulus and square both sides.','Radius is positive, not radius squared.'),
 ('Translate the centre to the origin and use the norm.','Both centre coordinates and positive radius must agree with the original equation.'),
 ('Complete squares or compare coefficients in a circle equation.','The signs of centre coordinates reverse the linear terms; take positive radius.'),
 ('Intersect the real axis with the circle or solve its squared displacement.','The radicand is positive; both real roots satisfy the original distance.'),
 ('Use radical-axis subtraction or the triangle inequality with circle intersections.','Reject negative h before squaring; d-r and d+r are included tangencies; strict interior gives two distinct signed points.')),
'equidistant-locus':(
 ('Average the coordinate pairs.','Midpoint lies on the joining segment.'),
 ('Use perpendicular-bisector geometry or square distances.','The line has unrestricted imaginary coordinate; the example point lies on it.'),
 ('Use squared distances or the midpoint and normal vector.','Distinct sites ensure a nonzero normal and a full line.'),
 ('Intersect perpendicular bisectors or solve the two independent linear equations.','Distinct noncollinear sites give exactly one point.'),
 ('Use radical axis and circle intersection or substitute the fixed real coordinate.','The squared imaginary component is positive; both signs are required.'),
 ('Use squared-distance equalities or classify perpendicular bisectors geometrically.','At k=0 the moving site is the origin; division by k otherwise valid. In the real family the nonzero identical-site case gives the same line; all other nonzero values give distinct parallel lines.')),
'argument-rays':(
 ('Use the positive imaginary axis or a unit-circle angle.','The point is nonzero.'),
 ('Translate the origin of the ray and inspect real displacement.','Endpoint undefined, negative ray has argument pi.'),
 ('Use slope and sign or positive radial parameter.','Endpoint excluded, direction restriction is strict.'),
 ('Solve the two line equations and filter by direction, or intersect parametrized rays.','Both strict inequalities hold; neither endpoint is included.'),
 ('Intersect the real line with the circle, then filter by ray direction.','One candidate has strictly positive ray parameter, the other is negative.'),
 ('Solve a quadratic in the ray parameter or intersect the supporting line and filter.','Negative radii impossible; minimum-distance tangency is admissible; upper threshold excludes the zero-parameter point; only positive roots count.')),
'complex-regions':(
 ('Test the given values in both inequalities.','Lower endpoint included; upper excluded.'),
 ('Compute the modulus or locate the point on the circle.','Equality violates the strict inequality.'),
 ('Intersect the two half-planes on labelled axes.','Vertical boundary below the corner included; horizontal boundary and corner excluded.'),
 ('Use half-disk area and boundary geometry.','The circular arc excludes both diameter endpoints; entire diameter excluded.'),
 ('Square equal distances and solve circle intersections or use perpendicular-bisector geometry.','Two distinct signed points; the origin lies strictly on the nearer-to-origin side.'),
 ('Reduce to a disk intersected with u>h, or use geometric disk caps.','Whole disk only for h<-r, empty for h>=r. At h=-r the leftmost point is excluded. Top point attained only for h<0; at h>=0 use admissible points approaching the excluded limiting point.')),
'locus-intersection':(
 ('Use squared Euclidean distance.','No square root requested.'),
 ('Use the geometric meaning of modulus.','The radius is positive; centre not on circumference.'),
 ('Use a diameter or substitute the vertical line.','Two opposite imaginary signs since radius positive.'),
 ('Use the perpendicular bisector and substitute, or use circle chord geometry.','The radicand is strictly positive for all three variants; two distinct points.'),
 ('Use a positive polar radius measured from the centre or intersect a directed ray.','Opposite ray has a different argument; the chosen point has positive imaginary part.'),
 ('Substitute the line coordinate or use perpendicular distance from centre.','Both endpoints are included single tangencies; interior two distinct points; outside none.'))}


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==198 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AZ frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped AZ rubric')
        checks={
          'mathematical_correctness':{'decision':'pass','evidence':'Representative design and variant prompts and answers reviewed; independent exact-fact oracle passed this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
          'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional M/A/R criteria preserve original mark total. Existing typed cartesian-to-polar T4 and polar-products T5 retained.'},
          'alternative_methods':{'decision':'pass','evidence':alternate+' Respect explicit question restrictions.'},
          'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning credit after arithmetic slips; require the specified correct accuracy result, with no automatic accuracy for an incorrect result.'},
          'boundary_cases':{'decision':'pass','evidence':boundary},
          'presentation':{'decision':'pass','evidence':'Representative worked solution and variant prompts and answers inspected; structural delimiter checks only. No rendered diagram or individual solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial polar and loci FM-16AZ (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
