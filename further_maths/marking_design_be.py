"""Frozen matrix system design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_be import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA="412f8771373f3bc2f81f16cbaadedf907e5173397aca664249e6a3543a3e814e"
NOTES={'system-consistency': (('Use elimination as requested; back-substitute or eliminate again.',
                         'Both equations must hold.'),
                        ('Compare proportional augmented rows or parallel and coincident lines.',
                         'A zero coefficient row is not sufficient to imply inconsistency.'),
                        ('Eliminate or compare the two lines.',
                         'Do not divide by the parameter difference at its zero.'),
                        ('Use row reduction or substitute the first two equations into the third.',
                         'At k=1 the remaining equation contradicts a nonzero constant.'),
                        ('Eliminate or use a determinant plus direct substitution in each branch.',
                         'The singular equation is redundant, not contradictory.'),
                        ('Use row subtraction or rank and nullspace with explicit spanning sets.',
                         'The homogeneous system always contains zero; the two vanishing coefficients give four '
                         'disjoint cases. Existing AE rubric retained.')),
 'system-classification': (('Substitute the forced value or compare constants.',
                            'The two constants are not proportional.'),
                           ('Compare augmented ranks or coincident versus parallel lines.',
                            'Zero determinant alone cannot distinguish none from infinitely many.'),
                           ('Use elimination or substitution.', 'Free parameter unrestricted in I; no solution in II.'),
                           ('Use augmented matrix reduction or compare the plane equations.',
                            'The first two independent equations leave one free coordinate.'),
                           ('Compare augmented row dependence or substitute the entire line.',
                            'No choice of right side can increase coefficient rank.'),
                           ('Use rank and augmented rank or solve the reduced equation.',
                            'Do not divide by k before splitting k=0; equality of constants is exact.')),
 'nonunique-set': (('Substitute or subtract.', 'Use the actual given value of y.'),
                   ('Show line coincidence or compare rows.', 'Examples must be distinct and satisfy both equations.'),
                   ('Substitute z=t as requested.', 'Every real t is allowed and every solution has such a t.'),
                   ('Use row reduction or choose the free z-coordinate directly.',
                    'The direction is nonzero and all real parameters occur.'),
                   ('Use vector norm or substitute into the sphere equation.',
                    'Positive distance gives two distinct roots; neither sign may be lost.'),
                   ('Intersect the parameter inequalities or use the feasible triangle and affine range.',
                    'Include equality at both extremes; interior interval has positive length.')),
 'three-plane-unique': (('Substitute the three coordinates.', 'Membership requires exact equality.'),
                        ('Use row reduction or geometric intersection.', 'The free coordinate ranges over all reals.'),
                        ('Use elimination or a nonzero determinant and substitution.',
                         'All coordinates forced; verify existence as well as uniqueness.'),
                        ('Use elimination as specified, then compute determinant.',
                         'Determinant must be nonzero; correct sign matters.'),
                        ('Substitute the fixed coordinate, then solve the third plane equation.',
                         'Fixed x is nonzero; recovered parameter is not the singular value.'),
                        ('Use the common line and sphere intersection, then impose the extra plane point.',
                         'Both signed distance parameters nonzero; resulting planes meet line uniquely and both '
                         'candidates exhaust possibilities. Existing AE rubric retained.')),
 'two-variable-system': (('Subtract and divide by nonzero coefficient.', 'Check original equation.'),
                         ('Compare proportional rows or coincident lines.',
                          'Both examples must satisfy both equations.'),
                         ('Use elimination as specified.', 'A nonzero pivot guarantees a unique pair.'),
                         ('Use elimination or substitution.',
                          'Counts are nonnegative integers, not arbitrary real solutions.'),
                         ('Parameterise ratio then substitute.',
                          'The fixed x is nonzero and recovered determinant is nonzero.'),
                         ('Use affine range on the segment or solve inequalities with sign reversal where necessary.',
                          'Include both endpoints; k=1 must be treated separately.')),
 'inverse-systems': (('Multiply by the reciprocal as requested.', 'Coefficient nonzero.'),
                     ('Use proportional augmented rows or a determinant and substitution.',
                      'Singularity alone does not imply inconsistency.'),
                     ('Use adjugate or row reduction to compute inverse.',
                      'Nonzero determinant required; verify the original system.'),
                     ('Use cofactor or augmented-identity inversion as required.',
                      'Nonzero determinant, correct multiplication order.'),
                     ('Use matrix inversion as required then solve the scalar condition.',
                      'Nonzero determinant and nonzero coefficient in the scalar equation.'),
                     ('Use inverse for both right sides, determinant multiplicativity for independence, then row '
                      'proportionality in singular case.',
                      'The two singular compatibility constants differ by one half; never both compatible. Existing AJ '
                      'rubric retained.')),
 'three-system': (('Use the specified back-substitution.', 'All coordinates must match original equations.'),
                  ('Compare augmented rows or substitute the first equation into the second.',
                   'Three equations do not guarantee rank three.'),
                  ('Use elimination as requested.', 'Check original rather than only reduced equations.'),
                  ('Use substitution or elimination.',
                   'Quantities are signed, not restricted to nonnegative integers.'),
                  ('Use elimination or solve the three independent fixed constraints first.',
                   'Reduced determinant is nonzero, and k is then forced.'),
                  ('Use reversible elimination and factor the reduced determinant, then split both singular cases.',
                   'Two distinct singular values have different compatibility constants; the other reduced row still '
                   'has a nonzero coefficient. Existing AE rubric retained.')),
 'inconsistent-geometry': (('Compare normals and intercepts.',
                            'Equal normals alone do not imply disjointness; constants differ.'),
                           ('Use substitution or augmented ranks and pairwise normal independence.',
                            'All three pairs intersect but the total intersection is empty.'),
                           ('Use elimination as specified.',
                            'Zero left side with nonzero right side, not merely zero determinant.'),
                           ('Solve each pair separately or use normals and fixed coordinates.',
                            'All directions parallel to z-axis; fixed coordinate pairs distinct.'),
                           ('Use row dependence and pairwise rank or substitute line.',
                            'Compatibility occurs at exactly one parameter; no two normals proportional.'),
                           ('Use pairwise elimination with explicit split on the parameter difference.',
                            'At zero parameter difference the second and third planes are parallel disjoint only when '
                            'constants differ; otherwise the common line exists.')),
 'nonunique-geometry': (('Parameterise the free coordinate.', 'Parameter arbitrary real.'),
                        ('Reduce proportional equations or compare normals and constants.',
                         'Two independent unrestricted coordinates.'),
                        ('Use row reduction or substitution.',
                         'Independent first two constraints; every real parameter works.'),
                        ('Use rank one or solve for x in terms of y,z.',
                         'Both parameters independently arbitrary; verify direction independence.'),
                        ('Use coefficient matching or require the plane contain one point and the direction.',
                         'The two equations for k,h have nonzero determinant; containment is for every parameter, not '
                         'a single point.'),
                        ('Compare augmented ranks or substitute first coordinate.',
                         'Free z in every compatible case; at vanishing parameter difference y is also free.'))}

def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==162 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BE frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BE rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AE and AJ rubrics preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and variant prompts and answers inspected; structural checks only, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial matrix systems and geometry FM-16BE (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
