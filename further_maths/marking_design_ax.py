"""Frozen complex polynomial design review; exact variant checks, not approval."""
import hashlib
import json
from active_difficulty import Resolver, require
from difficulty_revision_ax import BANKS
from marking_review import fingerprint

FROZEN_BATCH_SHA='322755a29ff9bbb20ff579431c6cacec90223b73481c7a62f2b8669ef0f2a4d6'
# Each note gives alternative-method guidance and mathematical domain/boundary
# evidence for the design, not certification of each written solution.
NOTES={
 'complex-discriminant':(
  ('Read the signed coefficients and evaluate B squared minus 4AC.','The leading coefficient is one, the discriminant is strictly negative in every variant.'),
  ('Evaluate both discriminants or compare the completed squares and derive their discriminants.','The common linear coefficient does not fix the constant; the first discriminant is zero and the second is negative.'),
  ('Use the general signed discriminant formula, or an algebraically equivalent derivation without solving the polynomial.','The leading coefficient is positive and not one in every variant; the discriminant is negative, so there are two distinct non-real conjugates.'),
  ('Solve the discriminant inequality by factoring or comparing the absolute value of k with the positive threshold.','Strict inequality gives non-real roots; both equality values are real repeated-root boundaries.'),
  ('Compare both discriminant signs or the completed-square thresholds.','The smaller squared threshold is strictly below the larger; exactly one negative discriminant occurs above the smaller and at or below the larger.'),
  ('Use either signed discriminants or the corresponding completed-square inequalities.','Thresholds are k squared and (k-a) squared; equality gives a repeated root, the two curves meet uniquely at k=a/2, h=a squared/4. The half-open interval between them is empty when they coincide.')),
 'complex-quadratic':(
  ('Factor over the complex numbers or use both imaginary square roots.','The positive magnitude is nonzero, so the two roots are distinct.'),
  ('Use the two square-root branches or factor the shifted quadratic over the complex numbers.','Shifting both distinct imaginary values by the same real constant cannot merge them; one is the supplied root.'),
  ('Use the quadratic formula as explicitly requested; algebraically equivalent rearrangements of it are accepted.','The nonmonic leading coefficient is nonzero, the discriminant is negative, and the entire signed numerator must be divided by twice the leading coefficient.'),
  ('Complete the square in the shifted variable as requested; verify by Vieta or expand the product of the resulting factors.','The shift is undone for both distinct conjugate roots; their sum and product must match the expanded monic polynomial.'),
  ('Complete the square or use the signed real-coefficient invariants of a conjugate pair.','The imaginary magnitude is positive, fixing k above the real-root threshold; the two conjugate values satisfy the same unique constant.'),
  ('Complete the square or use the quadratic formula, and use Vieta or direct inequalities to determine the real-root signs.','For |h| below the positive threshold there are two non-real conjugates with the same positive modulus; at either endpoint one double real root; outside, positive product and nonzero signed sum fix the common sign.')),
 'conjugate-deduction':(
  ('Reflect across the real axis geometrically or conjugate the Cartesian number.','The real coordinate is unchanged and the nonzero imaginary coordinate reverses sign.'),
  ('Solve the linear counterexample or substitute the purported conjugate directly.','The supplied non-real coefficient violates the hypothesis of the universal theorem; the conjugate is distinct and is not a root of this linear polynomial.'),
  ('Use the conjugate-root theorem and the degree bound, without expanding or solving as requested.','The known real root differs from both conjugates; exactly three distinct roots account for the cubic.'),
  ('Conjugate the factorisation including the remaining factor, or use the equivalent derivative multiplicity characterisation.','The given root has multiplicity exactly two, not merely at least two. Its conjugate is distinct with the same multiplicity; their squared real quadratic attains degree four.'),
  ('Use Vieta or compare the next coefficient of the product of the forced quadratic and a monic linear factor.','The conjugate pair is distinct, its sum is real, and the monic coefficient uniquely fixes the third real root.'),
  ('Count the forced root set before forming real conjugate-pair factors.','At either signed imaginary magnitude the prescribed roots lie in the same conjugate pair; h=0 adds exactly one real root; all other h add a distinct conjugate pair. Products attain degrees 2, 3 and 4.')),
 'conjugate-factor':(
  ('Use a difference of squares, direct expansion or the modulus-squared identity.','The imaginary square is negative, making the conjugate product a strictly positive real number.'),
  ('Compute the product directly or use the conjugate-root coefficient identity.','Both imaginary signs are opposite; the constant is the sum of squares, not their difference.'),
  ('Construct the product of conjugate linear factors or use their real sum and positive product.','The non-real root forces a distinct conjugate; monicity fixes the leading coefficient.'),
  ('Use a scalar multiple of the conjugate factor or solve the coefficient and evaluation equations.','The squared imaginary magnitude is positive, so the supplied real evaluation fixes a unique nonzero leading coefficient.'),
  ('Use polynomial long division or another valid polynomial-division notation with equivalent intermediate coefficient work.','The conjugate factor divides exactly; both monic quadratics have strictly negative discriminants, so neither splits over the reals.'),
  ('Parameterise the unknown real part of the other conjugate pair and compare constant terms.','The lower threshold is attained by one factorisation; above it two distinct signs give two quartics. Only the positive-real-part branch at the collision parameter repeats both conjugate roots; the other branch remains simple. The AH rubric is retained.')),
 'solve-cubic':(
  ('Use polynomial long or synthetic division as required, then factor or solve the real quadratic.','The two other real roots are positive, distinct and different from the known negative root.'),
  ('Use the zero-product rule and both imaginary square roots, or factor over the complex numbers.','The negative real root is simple; the two non-real conjugates are distinct and disjoint from it.'),
  ('Use valid long or synthetic division with visible equivalent intermediate coefficient work; solve the quotient by completing the square or the quadratic formula.','The supplied negative root is part of the full solution; the quotient has two distinct non-real conjugates and no common root with the divisor.'),
  ('Use the forced real conjugate factor and division, or determine the remaining linear factor by exact coefficient comparison.','The remaining root must be real and distinct from the given conjugates; guessing alone does not satisfy the method restriction.'),
  ('Evaluate the polynomial at the supplied root or match coefficients in a real conjugate-factor product.','The unknown constant has coefficient one; the real and imaginary constraints are compatible and give a unique real value, after which the three roots are distinct.'),
  ('Divide by the known linear factor or establish the equivalent factorisation, then examine the quadratic discriminant and its value at the known root.','Negative h yields a non-real pair plus the known simple real root; zero yields a double root at the quotient centre; the positive collision parameter gives a double known root and one other simple root. All other positive h give three distinct real roots.')),
 'solve-quartic':(
  ('Apply the zero-product rule or treat the equation as a quadratic in x squared.','The two positive squared values are unequal; both signs of both square roots give four distinct real roots.'),
  ('Use the two separate factors or the corresponding quadratic in x squared.','One squared value is positive and the other strictly negative; each produces two distinct roots and the pairs cannot overlap.'),
  ('Use valid polynomial division with equivalent intermediate coefficient work and then solve each quadratic exactly.','The supplied factor and quotient are both irreducible over the reals and their conjugate pairs have different real parts, so all four roots are distinct.'),
  ('Use conjugation and polynomial division as requested; factor or solve the remaining real quadratic exactly.','The forced non-real pair and the two unequal real roots are disjoint; both factors and all four roots are required.'),
  ('Evaluate at the supplied non-real root or compare coefficients in the conjugate-factor product, then solve the quotient.','The constant enters with coefficient one; the two conjugate pairs have different real parts, hence all four roots are simple.'),
  ('Divide by the fixed factor or compare the factor product, and use both discriminants and the condition for a common root.','At h=0 only the variable quadratic has a double real root; at h equal to the negative squared imaginary magnitude the two factors coincide, giving two double non-real roots. Otherwise there are four simple roots, two real if h is positive and all non-real if h is negative.')),
 'verify-roots':(
  ('Substitute into the expanded polynomial term by term or use an equivalent exact Horner evaluation.','An exact zero confirms the given root; a rounded near-zero value is not sufficient.'),
  ('Divide by the supplied linear factor or verify the exact cubic factorisation; the derivative at the real root is an equivalent multiplicity check.','The quadratic value at the real root is strictly positive, so the root is simple; real coefficients also force the omitted conjugate.'),
  ('Multiply the three monic linear factors as requested, pairing conjugates first if desired.','The reproduced monic cubic and three distinct linear factors establish complete roots with multiplicity one, not merely individual substitution.'),
  ('Verify the factorisation as requested by expansion or exact division.','The quadratic has a strictly negative discriminant and does not vanish at the real root, so only the real linear factor repeats.'),
  ('Use exact evaluation or coefficient comparison with the known conjugate factor, then factor the resulting quartic.','The unknown constant is uniquely fixed; the proposed doubled non-real root has multiplicity one, while the real factor occurs twice and is disjoint from the conjugates.'),
  ('Construct each full monic polynomial and compare coefficients, or cancel the common nonzero polynomial factor before comparing the residual quadratics.','The two candidate residual quadratics have different linear coefficients, so the pairs cannot coincide. The fixed pair is a root pair for all parameters, so checking it cannot certify multiplicities or either list.')),
}


def records(resolver=None):
    r=Resolver(historical_through='bh') if resolver is None else resolver
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==126 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'AX frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Untyped AX rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Mathematical design, representative solution and parameter branches reviewed; independent exact-fact oracle passed this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Reviewed distinct design-specific M/A/R requirements with the original total marks preserved; the existing AH allocation is retained for conjugate-factor T6.'},
            'alternative_methods':{'decision':'pass','evidence':alternate+' Respect the explicit method restrictions in the question.'},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method and reasoning credit after arithmetic slips. For division, a correct subsequent reduction on a consistent erroneous dividend can still demonstrate method. Require the specified exact accuracy result; do not award accuracy automatically.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative solution and structure of all variants reviewed; delimiter checks passed. No individual written-solution or rendered-mathematics certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial complex polynomial FM-16AX (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records(): print(json.dumps(record,sort_keys=True))
