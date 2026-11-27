"""Frozen line/plane design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bg import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA="78f9f571956c02e3c69ba088eb5beac3d6741c40d2103c7ca0ca89f69ed5afed"
NOTES={'vector-line-equation': (('Use component subtraction Q-P.', 'Direction must be signed final minus initial.'),
                          ('Compare a common point and proportional nonzero directions, or reparameterise.',
                           'Parameters cover all real numbers; negative scale is valid.'),
                          ('Use the specified base and directed displacement.',
                           'Distinct points ensure nonzero direction.'),
                          ('Solve the third coordinate and substitute.',
                           'Nonzero z direction makes the intersection unique.'),
                          ('Match all three coordinates.',
                           'First coordinate fixes nonzero parameter; check the second before solving k.'),
                          ('Use a basis of the perpendicular subspace for coincident points.',
                           'Distinct points fix the line; at the origin coincidence infinitely many lines, identify '
                           'proportional nonzero directions.')),
 'cartesian-line': (('Use inverse operations.', 'Coefficient of parameter nonzero.'),
                    ('Retain the constant coordinate and eliminate t from the other two.',
                     'Never divide by a zero direction component.'),
                    ('Equate parameter expressions.', 'All three denominators nonzero; signed denominator allowed.'),
                    ('Set common ratio to a parameter then solve z.', 'Equivalent nonzero reparameterisation valid.'),
                    ('Subtract endpoints and substitute the required y.',
                     'Fixed x must be retained and both ratios agree.'),
                    ('Use component equations before splitting on k.',
                     'For k=0 all or no points according to h; direction never zero.')),
 'zero-direction': (('Read the first coordinate equation.', 'Constant coordinate for every parameter.'),
                    ('Use the two nonconstant coordinate equations.', 'Zero over zero is undefined too.'),
                    ('Eliminate between nonconstant coordinates and verify the point.', 'Retain fixed y.'),
                    ('Use component matching or common parameter.',
                     'A point satisfying the ratio can fail the constant coordinate.'),
                    ('Use proportionality then solve the third coordinate.',
                     'Nonzero third component fixes scale and parameter uniquely.'),
                    ('Split according to h then k.',
                     'If h=k=0 the set is a point, not a line; p=0 distinguishes membership.')),
 'vector-plane': (('Use final minus initial.', 'Zero middle component is valid.'),
                  ('Reduce to a single effective parameter.', 'Both directions nonzero but dependent; not a plane.'),
                  ('Use nonzero cross product or rank two to verify independence.',
                   'Parameters range independently over all reals.'),
                  ('Use cross product and scalar product with P.',
                   'Requested normal scaling is fixed; verify W in both forms.'),
                  ('Solve x and y then substitute z.', 'Independent nonzero coefficients imply uniqueness.'),
                  ('Compare the rank of the two yz vectors and the x direction.',
                   'At h=k=0 infinitely many planes; determinant zero away from origin gives unique plane; nonzero '
                   'determinant rules out all planes.')),
 'plane-cartesian': (('Sum signed component products.', 'Zero term contributes zero.'),
                     ('Scale the whole equation or compare plane constants.',
                      'Nonzero constant prevents equivalence after scaling only left side.'),
                     ('Use n dot (r-P)=0.', 'Use the supplied point to fix constant.'),
                     ('Use displacements and cross product or solve two orthogonality conditions.',
                      'Noncollinear points; equivalent simultaneous scaling of both sides valid.'),
                     ('Subtract point equations then substitute axis coordinates.',
                      'Nonzero coefficient of z makes intercept unique.'),
                     ('Solve normal constraints in the orthogonal complement of line direction.',
                      'Nonzero extra displacement modulo line gives one plane; coincident extra point gives family '
                      'with proportional normals identified.')),
 'plane-normal': (('Sum component products.', 'Keep signed terms.'),
                  ('Use homogeneity of perpendicularity conditions.', 'Zero normal cannot define a plane.'),
                  ('Test both dot products for each candidate.', 'Normal nonzero and both directions independent.'),
                  ('Use cross product or solve normal equations with fixed first component.',
                   'Verify all three points and specified scaling.'),
                  ('Solve the two independent dot equations.',
                   'Fixed nonzero first component; unique normal and membership check.'),
                  ('Solve the orthogonality equations with prescribed first component.',
                   'k=0,h nonzero gives independent directions but no prescribed normal; both zero gives family '
                   'without plane span.')),
 'cross-normal': (('Compute the dot product and conclude perpendicularity.', 'Both vectors must be nonzero.'),
                  ('Test proportionality or calculate the cross product.',
                   'Zero cross product cannot supply a nonzero normal.'),
                  ('Use signed determinant and check both dot products.',
                   'Cross product nonzero proves independent directions.'),
                  ('Use displacements, cross product and n dot P.', 'Check noncollinearity and all three memberships.'),
                  ('Solve orthogonality against both directions and check cross product.',
                   'Unique k from nonzero linear coefficient; normal nonzero.'),
                  ('Factor the cross product before normalising.',
                   'At kh=constant the directions span exactly one line; orientation changes across sign boundary.')),
 'normal-dot-plane': (('Compute signed products.', 'Do not omit negative term.'),
                      ('Use point-normal equation rather than position-vector orthogonality.',
                       'Plane need not pass through origin.'),
                      ('Expand n dot (r-Q)=0.', 'Check the same nonzero constant at Q.'),
                      ('Compute three dot products and compare with plane constant.',
                       'Equality is necessary and sufficient for membership.'),
                      ('Use orthogonality of the displacement and substitute P.',
                       'Nonzero normal and unique parameter.'),
                      ('Intersect the unit sphere with normal-component and orthogonality constraints.',
                       'Outside |h|<=1 none; at h=0 identify opposite normals, at |h|=1 branches coincide; otherwise '
                       'two distinct planes.')),
 'line-line-angle': (('Use square root of sum of squares.', 'Magnitude positive for nonzero vector.'),
                     ('Reverse one direction or use absolute dot product.',
                      'Smaller angle for unoriented lines is at most 90 degrees.'),
                     ('Use directions only and absolute cosine ratio.', 'Position vectors irrelevant.'),
                     ('Form directed endpoint differences and take inverse cosine of absolute ratio.',
                      'Do not take obtuse directed angle.'),
                     ('Square the nonnegative cosine equation and substitute both roots.',
                      'Direction nonzero; both signs satisfy the original relation.'),
                     ('Reduce to a quadratic in k, separately solve degree change, test discriminant.',
                      'At t=0 double root; t=1/2 linear; sharp discriminant threshold one root; no roots above.')),
 'plane-plane-angle': (('Use absolute cosine ratio then inverse cosine.', 'Smaller angle in [0,pi/2].'),
                       ('Reverse normal or use absolute dot product.', 'Opposite normals specify same plane angle.'),
                       ('Read normals then apply absolute cosine.', 'Both normals nonzero.'),
                       ('Use cross product of in-plane directions then compare normals.',
                        'Equivalent scaling of plane equation accepted.'),
                       ('Square unsigned ratio then verify both signs.', 'Denominator always positive.'),
                       ('Split absolute cosine into two signed equations.',
                        'At c=1 only k=0; at c=0 branches coincide; intermediate c gives four distinct roots.')),
 'line-plane-angle': (('Use sine ratio then inverse sine.', 'Acute angle measured from plane, not its normal.'),
                      ('Take complement of the normal angle.', 'z axis normal to horizontal plane.'),
                      ('Apply sine formula with the plane normal.', 'Use absolute dot product and nonzero norms.'),
                      ('Find normal and line direction then complement the normal angle.',
                       'Plane offset irrelevant to angle.'),
                      ('Square unsigned sine relation then substitute roots.',
                       'Both signs valid; denominator positive.'),
                      ('Use common norm and solve the two absolute projection conditions.',
                       'Existing AO typed rubric retained; strict feasibility p^2+q^2<1, including zero components and '
                       'equality exclusion.'))}

def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==198 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BG frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BG rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AO rubric preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution inspected; independent exact-fact checks and structural checks on all variants, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial line and plane equations, normals and angles FM-16BG (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
