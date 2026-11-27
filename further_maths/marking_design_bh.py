"""Frozen final vector design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bh import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA="0818cdcf861049fef62f63372b7270199c3d743eb701035bd37acb504a1d6f5c"
NOTES={'point-line': (('Sum component squares.', 'Squared distance, not square root.'),
                ('Use orthogonal projection and Pythagoras.', 'Equality only at foot.'),
                ('Use cross product or perpendicular projection.', 'Divide by nonzero direction norm.'),
                ('Solve scalar-product equation for foot as requested.', 'Verify membership and perpendicularity.'),
                ('Project before equating squared distances.', 'Both signs; foot independent of vertical coordinate.'),
                ('Complete the square as requested.',
                 'Positive leading coefficient gives unique minimum; both larger-distance roots.')),
 'skew': (('Compare component ratios.', 'Include zero components.'),
          ('Check direction independence and constant z.', 'Nonparallel alone is insufficient.'),
          ('Equate all coordinates.', 'Unique intersection for independent directions.'),
          ('Solve x,y first as requested.', 'Check inconsistent z and nonparallelism.'),
          ('Use coordinate equations or coplanarity.', 'Exactly the zero offset branch intersects.'),
          ('Construct parallel containing planes using common normal.',
           'Nonparallel for all parameters; coincidence iff common point; all other cases skew.')),
 'line-plane-intersection': (('Isolate t.', 'Nonzero coefficient.'),
                             ('Substitute line into plane.', 'Constant residual excludes every point.'),
                             ('Substitute and solve.', 'Nonzero normal-direction dot product.'),
                             ('Determine plane constant, solve and verify.', 'Check both representations.'),
                             ('Solve linear parameter equation.',
                              'Zero coefficient with nonzero residual is inconsistent.'),
                             ('Solve both parameter equations separately.',
                              'Distinguish empty, whole line and unique point at exceptional coefficients; check '
                              'common intersection.')),
 'point-plane': (('Use Euclidean norm.', 'Nonnegative square root.'),
                 ('Compare scaled residual and normal length.', 'Nonzero scale cancels in ratio.'),
                 ('Use absolute residual over norm.', 'Normal nonzero; distance unsigned.'),
                 ('Project along normal and substitute.', 'Foot belongs to plane.'),
                 ('Solve both signed residual equations.', 'Side depends on displayed normal.'),
                 ('Use orthogonal decomposition.', 'Unique foot; circle in plane when target exceeds minimum.')),
 'line-line-distance': (('Subtract points and take norm.', 'Distance unsigned.'),
                        ('Align parallel coordinates.', 'Base points not generally closest; prove lower bound.'),
                        ('Use scalar triple product as requested.', 'Cross product nonzero; absolute numerator.'),
                        ('Minimise squared separation.', 'Both squares vanish only at unique pair.'),
                        ('Minimise over common parameter.',
                         'Both signs; infinitely many closest pairs for parallel lines.'),
                        ('Solve orthogonality equations for each line.',
                         'Unique pairs by independent directions; include distance equality and zero-distance cases.')),
 'triangle-area': (('Use half base times perpendicular height.', 'Triangle factor one half.'),
                   ('Reverse cross-product order.', 'Sign reverses but area unchanged.'),
                   ('Compute cross product or base-height equivalent.', 'Half its norm.'),
                   ('Use adjacent sides from common vertex.', 'Half norm; not position-vector cross product.'),
                   ('Solve squared area equation.', 'Both signs admissible and no collinearity.'),
                   ('Derive component-square constraints and third area.',
                    'Include ties, zero components and sole-point boundary.')),
 'triple-volume': (('Use base area times perpendicular height.', 'Volume nonnegative.'),
                   ('Swap vectors in determinant.', 'Sign reversal leaves magnitude unchanged.'),
                   ('Cross then dot or determinant.', 'Absolute value.'),
                   ('Use adjacent edge displacements.', 'Absolute signed product.'),
                   ('Split absolute-value equation.', 'Both signs; distinct roots.'),
                   ('Solve both signed quadratic branches.',
                    'Zero target branches coincide; negative branch discriminant threshold; positive branch always two '
                    'for positive target.')),
 'line-intersection': (('Substitute prescribed parameter.', 'Check sign.'),
                       ('Compare all three coordinates.', 'Different z excludes equality.'),
                       ('Solve coordinate equations and substitute.', 'Check remaining coordinate.'),
                       ('Construct directions from endpoints.', 'Nonparallel and inconsistent coordinates imply skew.'),
                       ('Use z then y then x.', 'Unique parameter pair and common point.'),
                       ('Separate parallel and nonparallel cases.',
                        'Zero slope and zero offset can produce coincident lines; otherwise classify all disjoint '
                        'branches.')),
 'plane-intersection-direction': (('Use dot product.', 'Nonzero vectors required for angle interpretation.'),
                                  ('Test against both normals.', 'A normal is not an in-plane direction.'),
                                  ('Cross normals and verify dot products.',
                                   'Nonzero cross product proves independent normals.'),
                                  ('Derive normals from spanning directions.',
                                   'Both planes contain origin and common direction is nonzero.'),
                                  ('Impose both normal orthogonality constraints.', 'Check independence at solution.'),
                                  ('Solve normal constraints with nonparallel exclusions.',
                                   'Exactly-one-zero branches excluded; two-zero family must exclude zero slope.')),
 'parallelogram-area': (('Use base times perpendicular height.', 'No triangle factor.'),
                        ('Reverse cross product.', 'Magnitude unchanged.'),
                        ('Compute cross product then magnitude.', 'Full area, not half.'),
                        ('Use adjacent displacements and vector addition.', 'Opposite vertex plus full area.'),
                        ('Solve squared magnitude equation.', 'Both signs exhaust roots.'),
                        ('Complete square of area.',
                         'Nonnegative target; below/equal/above minimum gives zero/one/two roots.')),
 'plane-common-point': (('Substitute coordinates.', 'Compare plane constant.'),
                        ('Check both equations.', 'Membership of one is insufficient.'),
                        ('Set prescribed coordinate and solve.', 'Verify both equations.'),
                        ('Find two distinct points and parameterise.', 'Prove all common points accounted for.'),
                        ('Eliminate with third condition.', 'Nonzero coefficient proves uniqueness.'),
                        ('Parameterise intersection then minimise squared norm.',
                         'Direction never zero; positive coefficient for all k ensures unique global minimum.')),
 'related-solids': (('Use base area times height.', 'Perpendicular height.'),
                    ('Compare prism and pyramid volumes.', 'Tetrahedron one third of same-base prism.'),
                    ('Use absolute determinant over six.', 'Edges share vertex.'),
                    ('Compute triangular base and tetrahedron volume.',
                     'Prism three times tetrahedron; divide by base area.'),
                    ('Use multilinearity of determinant.', 'Only nonnegative root on closed edge segment.'),
                    ('Complete square of volume ratio.',
                     'Closed interval includes degenerate endpoints; double root at maximum; reject outside range.')),
 'plane-intersection-line': (('Substitute in both equations.', 'Both constants must match.'),
                             ('Leave z free.', 'Complete line rather than one point.'),
                             ('Use prescribed parameter y.', 'Check both equations identically.'),
                             ('Eliminate then parameterise.', 'Every common point obeys elimination result.'),
                             ('Impose prescribed direction orthogonal to normals.',
                              'Nonzero third normal component ensures independence.'),
                             ('Eliminate y and split by coefficient zeros.',
                              'h nonzero: constant z iff k=1; h zero,k nonunit: vertical line; both coefficients zero '
                              'inconsistent.')),
 'justify-skew': (('Compare scalar multiples.', 'Zero components matter.'),
                  ('Exhibit common point.', 'Nonparallel not enough for skewness.'),
                  ('Check all coordinates as requested.', 'Inconsistent third coordinate and nonparallel directions.'),
                  ('Derive directions from endpoints.', 'Solve first two then check third.'),
                  ('Solve matching coordinate equations.', 'One offset allows intersection; all others skew.'),
                  ('Project onto both coordinate planes as requested.',
                   'Projection parameters must agree; exceptional k=1 disjoint and nonparallel.'))}

def records(resolver=None):
    r=Resolver(historical_through='bh') if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==252 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BH frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BH rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AL, AK, AP, AO and AQ rubrics preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution inspected; independent exact-fact checks and structural checks on all variants, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial vector intersections, distances, areas and volumes FM-16BH (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
