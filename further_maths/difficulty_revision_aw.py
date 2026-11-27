"""FM-16AW: reviewed Cartesian and conjugate marking designs; not teacher-approved."""
import importlib
import sympy as s
from calibration_bank import L

BANKS={'identify-components':'ab','standard-cartesian':'ab','cartesian-sums':'aa',
       'cartesian-product':'z','complex-division':'','conjugate-find':'w','conjugate-product':'w'}
# None denotes an existing typed design: preserve its overlay and evidence.
DESIGNS={
 'identify-components':(
  ('A:Correct constant.','A:Correct signed coefficient.'),
  ('R:Explain that the imaginary part is the real coefficient of i, not the imaginary term.','A:Correct both components including zero real part.'),
  ('A:Correct signed real component.','A:Correct signed imaginary coefficient.'),
  ('A:Correct two expanded component expressions.','M:Equate the real coefficients and solve the resulting linear equation.','A:Correct unique t.'),
  ('M:Form both component equations.','M:Eliminate either unknown using both equations or use an equivalent invertible system.','A:Correct p and q.','R:Establish existence and uniqueness using the nonzero determinant or equivalent reversible reasoning.'),
  ('M:Express the two components using the shifted variable.','M:Split the absolute-value equation into both sign cases, retaining the nonnegative radius.','A:Find the first admissible positive radius.','A:Find the second admissible positive radius.','A:Recover all four t values.','A:Give the correct paired component signs for all four values.','R:Prove both branches exhausted and that no negative radii or duplicate roots remain.')),
 'standard-cartesian':(
  ('A:Correct first power of i.','A:Correct second power of i.'),
  ('R:Explain why the proposed real roots do not square to the negative number.','A:Give both imaginary roots in Cartesian form, with zero real part.'),
  ('M:Rationalise the nonzero denominator or solve an equivalent complex product equation.','A:Obtain correct numerator and real denominator or equivalent component relations.','A:Give exact Cartesian coefficients.'),
  ('M:Combine the two fractions using the nonzero conjugate product.','A:Obtain the exact real fraction sum.','A:Give the full Cartesian result including the extra imaginary term.'),
  ('M:Rationalise the quotient.','M:Square the quotient retaining the cross term.','A:Give the exact Cartesian square.','R:Verify its modulus from the original moduli and the Cartesian result.'),
  ('M:Rationalise the quotient on its nonzero denominator domain.','A:Give both exact Cartesian component functions.','R:Obtain the real-part equation and justify h=-1 and h=1 separately.','A:Give both t branches in the open admissible interval and exclude outside values.','A:Give corresponding signed imaginary components including zero at h=-1.','R:Prove completeness and reversibility on the original domain.')),
 'cartesian-sums':(
  ('A:Correct first signed difference.','A:Correct second signed sum.'),
  ('M:Apply the subtraction to both real and imaginary terms.','A:Give the corrected Cartesian expression.'),
  ('A:Correct Cartesian sum.','A:Correct Cartesian difference.'),
  ('M:Expand the bracket with the correct signs and isolate the unknown.','A:Give the exact complex solution.'),
  ('M:Eliminate either unknown using both complex equations.','A:Give both exact complex solutions.','R:Verify both equations and establish uniqueness by the nonzero elimination coefficient or determinant.'),None),
 'cartesian-product':(
  ('A:Correct reduced power of i using its four-term cycle.',),
  ('R:Explain that multiplying the imaginary terms introduces i squared, equal to minus one.','A:Give the correct signed real product.'),None,None,
  ('M:Expand the Cartesian product and equate both coefficients.','A:Give both exact real unknowns.','R:Prove uniqueness through invertibility and verify the original product.'),None),
 'complex-division':(
  ('M:Expand or use the difference-of-squares identity with i squared equal to minus one.','A:Correct real product.'),
  ('R:Explain that the conjugate product is real and nonzero and that multiplying by the conjugate ratio preserves value.','A:Correct exact Cartesian reciprocal.'),
  ('M:Rationalise the nonzero denominator or use equivalent component comparison.','A:Correct exact Cartesian quotient.'),
  ('A:Correct exact Cartesian quotient.','M:Determine its modulus from the Cartesian components.','R:Independently obtain the same exact modulus using the quotient-of-moduli rule.'),
  ('M:Obtain the imaginary-component condition for a real quotient using the nonzero denominator.','A:Give the unique k and real quotient.'),None),
 'conjugate-find':(
  ('A:Correct reflected complex coordinate, retaining the real part and reversing the imaginary part.',),
  ('R:Explain that conjugation preserves the real coefficient and reverses only the imaginary coefficient.','A:Give the correct conjugate.'),
  ('M:Expand the product using i squared equal to minus one.','A:Give its exact conjugate in Cartesian form.'),
  ('M:Express z and its conjugate in real components and equate coefficients.','A:Give the exact complex solution.','R:Verify by substitution into the original equation.'),
  ('M:Expand and form both real component equations.','R:Show the coefficient determinant is nonzero or otherwise establish invertibility.','A:Give the correct unique Cartesian solution.','R:Verify both components in the original equation.'),None),
 'conjugate-product':(
  ('A:Correct sum of both squares.',),
  ('R:Explain the conjugate product is the sum of squares, not the complex square in this nonreal example.','A:Correct real conjugate product.'),
  ('M:Use the nonzero conjugate product to rationalise.','A:Correct expanded numerator and real denominator or equivalent component values.','A:Exact Cartesian quotient.'),
  ('M:Form the conjugate-product equation and recover the squared imaginary coefficient.','A:Give both distinct signed y values with justification that both satisfy the equation.'),
  ('M:Form both squared-norm equations in real components.','M:Eliminate the squared imaginary term to fix the real component.','A:Give both exact complex solutions.','R:Verify both constraints and prove completeness.'),
  ('R:Establish both shifted factors are nonzero on the norm circle and that the ratio is positive.','M:Express the ratio in terms of the real component using the fixed squared norm.','A:Recover the real component for admissible h.','R:Derive the exact closed attainable range using monotonicity or equivalent inequality reasoning.','A:Give both complex branches and the one-solution endpoint cases.','R:Prove completeness, excluding outside values and undefined denominators.')),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    suffix=BANKS[path]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_bank')


def revise(path,tier,v):
    if (path,tier) not in TARGETS or type(tier) is not int or type(v) is not int or v not in (1,2,3):
        raise ValueError('Not FM-16AW')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    a,b,d=map(s.Integer,(v+1,v+3,3*v+5))
    if path=='standard-cartesian' and tier==5:
        n=s.expand((a-b*s.I)*(d-a*s.I));den=d*d+a*a
        steps[0]=f'Rationalise the quotient to {L(n)}/{den}, which simplifies to {L(s.expand(n/den))}.'
        steps[1]=f'Square the unsimplified numerator and denominator: {L(s.expand(n**2))} over {den**2}; this is equivalent to squaring the simplified quotient.'
    if path=='cartesian-sums' and tier==4:
        steps[0]='Write w for the given complex number inside the bracket. Expanding u-(w-u) gives 2u-w.'
    if path=='conjugate-product' and tier==2:
        steps[-1]+=' This is not the complex square: a nonzero nonreal number is not equal to its conjugate, so multiplying each by that same nonzero number gives different products.'
    if path=='conjugate-product' and tier==4:
        steps[-1]+=' Since the squared value is strictly positive, the two roots are distinct and exhaust the real solutions.'
    design=DESIGNS[path][tier-1]
    if len(design)!=len(p['rubric']) or any(x['marks']!=1 or 'type' in x for x in p['rubric']):
        raise ValueError('Unreviewed mark structure')
    rules={'M':' Accept a valid equivalent method respecting explicit restrictions; retain demonstrated method credit after a subsequent arithmetic slip.',
           'A':' Require the correct specified result; do not automatically award accuracy for an incorrect result.',
           'R':' Accept equivalent valid reasoning supported by the necessary conditions.'}
    p['rubric']=[{'type':spec[0],'marks':1,'criterion':spec[2:]+rules[spec[0]]} for spec in design]
    return p
