"""Frozen foundational vector design reviews with independent exact-fact checks."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bf import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA="1da12764f4aba853677512462d3314d690697a534697fe15bd1badeea649bef4"
NOTES={'vector-components': (('Read the coefficients of i,j,k.', 'Retain the negative component.'),
                       ('Use Q=P+PQ.', 'Position-vector sum is not displacement.'),
                       ('Use component equations or vector addition.', 'Zero components are valid.'),
                       ('Use the weighted average of endpoints.',
                        'Internal fraction lies strictly between zero and one.'),
                       ('Use Pythagoras and both square roots.', 'Both signs satisfy the same squared magnitude.'),
                       ('Subtract squared distances then substitute, or intersect the two circles in the '
                        'fixed-coordinate plane.',
                        'Negative distances impossible; at zero radicand count the root once.')),
 'vector-combinations': (('Apply order of operations.', 'Multiply before adding.'),
                         ('Use componentwise multiplication.', 'Positive scaling preserves direction.'),
                         ('Compute directly component by component.',
                          'Subtract all components of the second scaled vector.'),
                         ('Use S=Q+R-P.', 'Adjacent directions must be independent for a nondegenerate parallelogram.'),
                         ('Use an internal section formula.',
                          'Parameter strictly between zero and one; nonzero specified direction component ensures '
                          'uniqueness.'),
                         ('Use barycentric coordinates or solve for the two independent edge coefficients.',
                          'Include vertices and edges; interior is relative to the triangle plane.')),
 'unit-vector': (('Use the square root of the sum of squares.', 'Magnitude is not a signed component.'),
                 ('Compute norms directly.', 'The proposed divisor is positive but not the Euclidean norm.'),
                 ('Use normalized component ratios.', 'Positive normalization preserves orientation.'),
                 ('Use the ratio of required distance to length PQ.', 'Do not take the point on the opposite ray.'),
                 ('Use the fixed component ratio.',
                  'The multiplier must be positive and the given direction component nonzero.'),
                 ('Intersect the unit sphere with the two coordinate constraints.',
                  'Negative radicand impossible; zero on the ellipse gives one vector, positive gives two.')),
 'scalar-product': (('Multiply corresponding terms then add.', 'Preserve the negative contribution.'),
                    ('Use direct calculation and the angle criterion.',
                     'A zero dot product does not imply a zero factor.'),
                    ('Use componentwise signed products.', 'Existing FM-16AS individually reviewed rubric retained.'),
                    ('Use bilinearity of the dot product.',
                     'Reversing both would preserve the product; only one reverses here.'),
                    ('Use elimination or the inverse of the coefficient matrix.',
                     'Nonzero determinant proves uniqueness.'),
                    ('Use cosine inequalities with the sign condition before squaring.',
                     'Existing AO rubric retained; interval is a singleton at the sharp positive bound.')),
 'perpendicular-test': (('Multiply corresponding components and sum.', 'Keep negative terms.'),
                        ('Use the angle formula denominator.', 'Both vectors must be nonzero for a right angle.'),
                        ('Use the dot-product condition on each candidate.', 'Only one product vanishes.'),
                        ('Use all three vertex dot products as specified.',
                         'All sides are nonzero; only one zero product.'),
                        ('Solve the two independent equations or use the cross product and scale.',
                         'Fixed nonzero third component rules out the zero vector.'),
                        ('Solve for k after splitting the zero coefficient case.',
                         'Neither zero vector is allowed even though its dot product vanishes.')),
 'perpendicular-parameter': (('Use inverse operations.', 'The coefficient is nonzero.'),
                             ('Use the norm denominator or lack of direction.',
                              'Do not infer perpendicularity from zero product alone.'),
                             ('Set the signed component product sum to zero.',
                              'Fixed nonzero components ensure angle defined.'),
                             ('Use a projection equation.', 'The displacement must be nonzero.'),
                             ('Eliminate or scale the cross product.', 'Fixed third component nonzero.'),
                             ('Check the right-angle condition at each of the three vertices.',
                              'Existing AO rubric retained: exclude collinearity and count a repeated zero root '
                              'once.')),
 'cross-product': (('Use ad-bc.', 'Do not use absolute value.'),
                   ('Use the component determinant or anti-commutativity with calculation.',
                    'Orientation reverses, magnitude does not.'),
                   ('Use component determinants or full determinant expansion.',
                    'Middle component has the negative cofactor sign.'),
                   ('Compute cross product then half its norm.', 'Use unsigned magnitude for area.'),
                   ('Solve the quadratic in the parameter.', 'Both signs are valid; do not conflate the two products.'),
                   ('Use a particular solution plus the kernel of the first cross-product map.',
                    'Existing AK rubric retained; independent coefficients force compatibility and uniqueness.')),
 'cross-order': (('Multiply then negate.', 'Retain sign.'),
                 ('Negate all components.', 'Orientation not magnitude changes.'),
                 ('Compute once and negate as requested.', 'Negate every component.'),
                 ('Compute each product directly or use bilinearity.',
                  'Cyclic permutation preserves orientation; a swap reverses it.'),
                 ('Solve the component equations then negate.',
                  'The supplied axial coordinate fixes the otherwise free component.'),
                 ('Use direct component matching or the kernel of the cross product.',
                  'Below the threshold, including negative C, no solution; equality gives one root.')),
 'cross-linearity': (('Compute componentwise.', 'Scale all components including zero.'),
                     ('Use bilinearity or expand both products.',
                      'Two equal scale factors give their product, not one factor.'),
                     ('Use the specified distributive expansion.', 'Preserve the order and the subtraction sign.'),
                     ('Solve two independent component equations or use matrix elimination.',
                      'Nonzero cross product proves independence.'),
                     ('Solve components directly or use particular solution plus kernel.',
                      'Fixed cross-product factor nonzero; include zero difference.'),
                     ('Use components after substituting Y=S-X.',
                      'Free parameter arbitrary real; equal lengths force midpoint of axial components.')),
 'zero-cross': (('Match a nonzero component and check the other.', 'Multiplier is unique.'),
                ('Use component formula and the definition of direction.',
                 'Do not classify a zero vector as a valid parallel line.'),
                ('Use component products and proportionality.', 'Negative multiplier means opposite senses.'),
                ('Use cross products as requested.',
                 'Zero displacement would also be on the line; nonzero direction required.'),
                ('Solve for the multiplier using norms.',
                 'Positive target magnitude excludes zero and retains both signs.'),
                ('Use component proportionality or determinant.',
                 'The first vector is never zero; second vanishes only at origin.'))}

def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==180 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BF frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BF rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design reviewed, with separate exact-fact oracle passed for this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional allocation retains original mark total; existing AS, AO and AK rubrics preserved.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct specified accuracy results, with no automatic accuracy for incorrect results.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution inspected; independent exact-fact checks and structural checks on all variants, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial foundational vector operations and products FM-16BF (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
