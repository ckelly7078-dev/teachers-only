"""FM-16AV: explicit marking requirements for algebra tiers 5 and 6."""
from difficulty_revision_au import BANKS,base

DESIGNS={
 'combined-roots':(
  ('R:Establish that the reciprocal product is nonzero, making inversion valid.','M:Invert both root invariants and translate back to the original roots.','A:Give the exact original monic equation.','R:Check reality by discriminant and justify uniqueness by reversibility.'),
  ('R:Exclude zero reciprocal product.','M:Invert and translate both invariants.','A:Derive the exact open interval for h from negative original product, accounting for the sign of h.','R:Verify real opposite-sign roots and nonzero translated product.','R:Construct the equation and establish uniqueness and exclusion of both endpoints.')),
 'cube-sums':(
  ('M:Apply the cube-sum identity with the given sum.','A:Recover the exact product.','R:Give the monic equation and verify reality and uniqueness.'),
  ('M:Express the real-root constraint as S squared at least four times the product.','R:Establish strict monotonicity of the cubic on both admissible intervals.','A:Obtain the two exact endpoint cube sums and corresponding attainable ranges.','R:Construct the unique equation for each attainable value and identify repeated roots.','R:Justify exhaustion using the full admissible domain and disjoint ranges.')),
 'factor-connection':(
  ('M:Compare the mixed and constant coefficients.','M:Eliminate either constant using the linear relation.','A:Give both complete ordered pairs.','R:Verify both pairs and exclude additional solutions.'),
  ('M:Form both coefficient equations.','M:Eliminate one unknown to obtain an equivalent quadratic.','A:Derive the discriminant and exact thresholds.','A:Give all ordered pairs using the quadratic and linear relations.','R:Justify zero, one and two counts, including repeated boundary and sufficiency.')),
 'quadratic-from-roots':(
  ('A:Obtain the squared absolute difference.','M:Use the squared-sum minus squared-difference identity to determine product.','A:Give the exact monic equation.','R:Verify the discriminant and explain why the coefficients are unique.'),
  ('M:Relate the squared sum to product and prescribed squared difference.','R:Classify the impossible region and unique zero-sum boundary.','A:Give both distinct equations in the positive-radicand region.','R:Verify their discriminants and products.','R:Establish necessity and exhaustion of all possible sums.')),
 'reciprocal':(
  ('M:Use the reciprocal sum with nonzero product to determine the original constant.','A:Give the correct constant and complete monic reciprocal-root equation.'),None),
 'reciprocal-sums':(
  ('M:Use the nonzero-product reciprocal identity to recover product.','A:Give the exact monic quadratic.','R:Verify real nonzero roots and uniqueness.'),
  ('M:Recover the unique root sum from the prescribed reciprocal sum.','A:Give the monic equation.','A:Obtain the discriminant condition and exact admissible range.','R:Classify root signs and repeated roots, excluding zero.','R:Verify the original constraints and uniqueness.')),
 'root-ratios':(
  ('R:Deduce opposite signs and hence the signed product.','M:Apply the ratio-sum identity to obtain the squared sum.','A:Select the correct negative sum.','R:Give the equation and verify both ratios and uniqueness.'),
  ('M:Use the ratio-sum identity, exclude h=-2 and solve for product.','R:Analyse the rational discriminant inequality with its denominator sign.','A:Give the exact equation for all admissible values.','R:Identify the repeated ratio boundary and prove sufficiency and uniqueness.')),
 'root-squares':(
  ('M:Use the square-sum identity to form the equation in the unknown product.','A:Give the correct product and verify reality by its discriminant.'),None),
 'root-sum-product':(
  ('M:Parameterise the positive roots using the prescribed ratio.','A:Recover the positive smaller root from the product.','A:Give both roots and the coefficient from their sum.','R:Verify both conditions and uniqueness under positivity.'),
  ('R:Use positive product to exclude zero and opposite signs.','M:Compute the discriminant and both zero thresholds.','A:Identify the nonreal interval.','A:Classify both distinct-real regions using the sum.','R:Identify both repeated roots and justify exhaustive disjoint cases.')),
 'scaled-roots':(
  ('M:Use the squared scale on the product and find both candidate scales.','R:Use the sign of the linear coefficient to select the unique scale.','A:Give the exact equation and verify both conditions.'),
  ('M:Form the scaled root invariants.','A:Derive the scaled discriminant.','R:Classify negative h and the repeated zero-root case.','A:Give both scales and distinct equations for positive h.','R:Classify signs of the roots and justify exhaustion.')),
 'shifted-products':(
  ('M:Expand both shifted-product conditions as linear equations in sum and product.','A:Solve for both invariants.','R:Give the equation and verify reality and uniqueness of the linear system.'),
  ('M:Factor the shifted-product condition without dividing by k.','R:Give the entire infinite family for k=0, including its real-root constraint.','A:Give the unique candidate equation for nonzero k.','R:State its admissible range and all repeated-root cases, including k=0.','R:Verify both original conditions and completeness.')),
 'shifted-roots':(
  ('M:Form the shifted-product quadratic in m.','A:Obtain both candidate shifts.','R:Use positivity to reject the other shift and justify uniqueness.','A:Give the exact transformed equation and verify the constraints.'),
  ('M:Form the shifted-product quadratic.','A:Find its exact minimum and minimising shift.','R:Use strict opposite signs to exclude all nonnegative products.','A:Give both shifts in the open admissible interval and the single minimum shift.','R:Verify all allowed shifts and justify the excluded regions.')),
 'squared-roots':(
  ('M:Find both squared-root values by factorisation or equivalent method.','R:Use both sign restrictions to establish the unique unordered root pair.','A:Give the exact original equation.'),
  ('M:Form the quadratic satisfied by the nonnegative squared roots.','R:Derive the exact range of product for nonnegative real squared roots.','A:Obtain both squared magnitudes and construct equations from their signed roots.','R:Count the zero-product and unequal-positive-magnitude cases without double counting.','R:Count the equal-magnitude boundary and prove exhaustion of unordered pairs.')),
 'symmetric-parameter':(
  ('M:Express squared root difference using the discriminant.','M:Equate to the prescribed squared difference and solve the resulting quadratic.','A:Give both exact parameter values and verify their discriminants.'),
  ('R:Exclude negative h.','R:Establish the sum and product conditions for positivity.','M:Form the two-sided discriminant inequality.','R:Reject the negative branch using the sign of the sum.','A:Give the exact closed interval, justify sufficiency and the repeated-root boundary.')),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in zip((5,6),rows) if row is not None}


def revise(path,tier,v):
    if (path,tier) not in TARGETS or type(v) is not int or v not in (1,2,3):
        raise ValueError('Not FM-16AV')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    if path=='combined-roots' and tier==5:
        steps[1]='For reciprocal-root sum U and product V, inversion gives sum U/V and product 1/V. Adding the original shift d gives sum U/V+2d and product 1/V+d*U/V+d^2.'
    if path=='shifted-roots' and tier==5:
        steps[1]+=' The two candidates follow by factoring the product equation or the quadratic formula.'
    if path=='symmetric-parameter':
        steps[-1]=steps[-1].replace('$.;','$;').replace('$..','$.' )
    design=DESIGNS[path][tier-5]
    if len(design)!=len(p['rubric']) or any(x['marks']!=1 for x in p['rubric']):
        raise ValueError('Unreviewed mark structure')
    rules={'M':' Accept valid equivalent methods; retain demonstrated method credit after later arithmetic slips.',
           'A':' Require the correct specified result; do not automatically credit an incorrect result.',
           'R':' Accept equivalent valid reasoning with the necessary conditions and conclusions.'}
    p['rubric']=[{'type':spec[0],'marks':1,'criterion':spec[2:]+rules[spec[0]]} for spec in design]
    return p
