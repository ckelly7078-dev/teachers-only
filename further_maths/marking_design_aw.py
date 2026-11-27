"""Frozen review of Cartesian/conjugate designs with independent variant fact checks."""
import hashlib
import json
from active_difficulty import Resolver, require
from difficulty_revision_aw import BANKS
from marking_review import fingerprint

# Keep the three individual AS reviews, not a lower-granularity replacement.
PRESERVE={('cartesian-product',3)}
FROZEN_BATCH_SHA='adc622c19e3c1f5e11e3f94f868ed9618ec0445b1d9cfdd5b424386698826d53'
# Boundary evidence is specific to each reviewed design and is not a claim of
# individual written-solution certification. Alternative methods respect the prompt.
NOTES={
 'identify-components':(
  ('Read the signed terms or compare with the general linear expression.','The negative multiplier includes its sign.'),
  ('Write the number as 0+bi or use the real/imaginary projection definitions.','Both components are real numbers; the missing real part is zero.'),
  ('Collect the components in either order or distribute first.','Negate both components of the subtracted bracket.'),
  ('Expand or compare coefficients through an equivalent product identity.','The coefficient difference is nonzero in all three variants, giving exactly one t.'),
  ('Use elimination, substitution or the inverse of the real coefficient matrix.','The determinant is a positive sum of two squares; verify both given components.'),
  ('Use nonnegative radius branches or solve the two signed component equations directly.','There are two positive distinct radii; negative radii are inadmissible, both signs of each radius occur and all four t values are distinct.')),
 'standard-cartesian':(
  ('Use the four-term cycle or repeated multiplication.','Reduce each exponent modulo four independently.'),
  ('Solve by factoring over the complex numbers or test both imaginary candidates.','The two imaginary roots are distinct and both have real part zero.'),
  ('Rationalise or solve the corresponding complex product equation.','The denominator modulus squared is positive; both coefficients must be exact.'),
  ('Combine over the conjugate product or rationalise each fraction separately.','The denominators are nonzero, the reciprocal sum is real and the added imaginary part remains.'),
  ('Square after rationalising, or square both original factors and rationalise.','The divisor is nonzero; include the cross term and verify the modulus as a positive ratio. The revised solution explicitly distinguishes reduced and unreduced numerators.'),
  ('Use rationalisation and the real-part equation, or the unit-circle relation with a direct sign check.','The denominator is always nonzero. h=-1 gives one t, h=1 is unattainable; -1<h<1 gives two matching sign branches; outside gives none.')),
 'cartesian-sums':(
  ('Use a number line or signed integer arithmetic.','Subtracting a negative is addition; the second signed result is negative.'),
  ('Distribute or subtract the components separately.','Both components of the second number are negated.'),
  ('Use component-wise calculation or an equivalent Argand displacement.','The sum and difference are separate results; preserve all signs.'),
  ('Expand the bracket or add the complex number and solve the linear equation.','The coefficient of the unknown is two, hence the complex solution is unique.'),
  ('Use elimination, substitution or separate real and imaginary linear systems.','The nonzero determinant guarantees existence and uniqueness; both equations must hold.'),
  ('Use midpoint and perpendicular displacement geometry or compare squared moduli algebraically.','Negative h is impossible, zero gives coincident factors, and positive h gives two ordered pairs related by swapping; all are exhaustive.')),
 'cartesian-product':(
  ('Use modular exponents or the four-term power cycle.','All variants have positive integer exponents; reduce modulo four.'),
  ('Expand or multiply coefficients first and use i squared.','The product is negative real, not positive.'),
  None,
  ('Use equal real and imaginary parts with a positivity test, or solve the ray equation directly.','Both components must be positive; the opposite ray and origin are excluded.'),
  ('Use Cartesian expansion as requested, then eliminate either unknown.','The determinant is a positive sum of squares, so the two real components are unique.'),
  ('Eliminate either unknown from the component equations and reconstruct the second factor.','The discriminant is negative, zero or positive, giving respectively zero, one or two distinct ordered pairs. Fixed nonzero components prevent zero factors.')),
 'complex-division':(
  ('Use difference of squares or direct expansion.','The imaginary cross terms cancel and the result is positive.'),
  ('Use the conjugate-product identity or expand the denominator directly.','The conjugate and denominator are nonzero; the ratio used to multiply is one.'),
  ('Rationalise or solve for the two components via multiplication.','The denominator has positive squared modulus, so the quotient exists uniquely.'),
  ('Rationalise or use component equations; compute modulus by Cartesian norm and by the quotient rule.','Both methods must give the same positive exact modulus; the divisor is nonzero.'),
  ('Rationalise and set the imaginary coefficient to zero, or set the quotient equal to a real unknown and compare components.','The imaginary numerator has a nonzero coefficient of k; the unique real quotient is verified by multiplication.'),
  ('Cross-multiply on the nonzero-denominator domain and use a determinant or rank argument.','Regular case requires h nonzero; at k equal to either signed threshold the compatible h=0 family excludes the origin. No solutions in other cases.')),
 'conjugate-find':(
  ('Reflect in the real axis or use the conjugate definition.','The real coordinate stays fixed and the imaginary coordinate changes sign.'),
  ('Use the Cartesian definition or real-axis reflection.','Do not negate the real coordinate.'),
  ('Expand then conjugate as requested, or use conjugation of products as a check.','The imaginary sign reverses after collecting the product; the real part stays fixed.'),
  ('Compare components or combine the equation with its conjugate.','Both linear component coefficients are nonzero in these variants; verify the original equation.'),
  ('Use real component elimination or an equivalent system involving z and its conjugate.','The determinant is nonzero in every variant; verify both components and uniqueness.'),
  ('Factor the imaginary-component equation and solve real and nonreal branches separately.','The lower threshold is strict for nonreal roots; the upper threshold includes a single real root. The thresholds differ by one; counts 2,4,3,2 are exhaustive.')),
 'conjugate-product':(
  ('Square each signed integer and add.','Both squares are nonnegative; the negative input is squared, not left negative.'),
  ('Use the difference of squares or expand the product.','The example is nonzero and nonreal, so its square differs from its conjugate product, which is strictly positive.'),
  ('Rationalise or use an equivalent real component system.','The denominator is a positive squared modulus, never zero.'),
  ('Use the squared-norm identity or the distance-circle intersection.','The computed squared imaginary component is positive; both distinct signs satisfy the equation and exhaust it.'),
  ('Subtract squared distance equations or intersect two circles geometrically.','The real component is uniquely fixed by the nonzero shift; positive squared imaginary component gives exactly two conjugate solutions.'),
  ('Use monotonicity of the rational expression or solve and impose the real-component interval.','Both shifted factors are nonzero on the circle; h is positive, the closed range is attained, endpoints give one solution, interior gives two. Enrichment scope unchanged.')),
}


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7)
           if (p,t) not in PRESERVE for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==123 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AW frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Untyped AW rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative design and solution inspected; variant prompt and answer inspected; independent exact-fact validator passed: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific M/A/R requirements and original mark total reviewed; existing typed criteria preserved where already registered.'},
            'alternative_methods':{'decision':'pass','evidence':alternate+' Respect explicit question restrictions.'},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method/reasoning after arithmetic slips. Require specified correct accuracy results unless the retained typed rubric explicitly provides consistent follow-through; do not award accuracy automatically.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and all three variant prompts and answers inspected; delimiters structurally checked. No individual written-solution or rendered-mathematics certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial Cartesian/conjugate FM-16AW (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records(): print(json.dumps(record,sort_keys=True))
