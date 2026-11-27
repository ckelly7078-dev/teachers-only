"""FM-16AU: reviewed algebra T1-T4 marking designs; not teacher-approved."""
import importlib

BANKS = {
    'root-squares':'', 'reciprocal':'', 'root-sum-product':'r',
    'quadratic-from-roots':'r', 'scaled-roots':'s', 'shifted-roots':'s',
    'squared-roots':'t', 'root-ratios':'t', 'reciprocal-sums':'u', 'cube-sums':'u',
    'combined-roots':'v', 'shifted-products':'v', 'factor-connection':'w', 'symmetric-parameter':'w',
}
# One explicitly reviewed allocation per design. Existing AS and AF cells remain intact.
# Entries are (type, requirement); original numerical work is retained as an example,
# not as a requirement to reproduce a particular sequence of solution steps.
DESIGNS = {
    'combined-roots': (
        ('A:Correct reciprocal of the difference.',),
        ('A:Identify the root that gives a zero denominator.','R:Explain that division by zero rules out a finite pair of transformed roots.'),
        ('M:Apply translated sum and product identities.','M:Use both reciprocal invariants with nonzero translated product.','A:Give the exact monic equation.'),
        ('M:Scale then translate both invariants, allowing zero product.','M:Apply square-sum and squared-product identities.','A:Give the exact monic equation including a zero constant if applicable.')),
    'cube-sums': (
        ('A:Correct signed sum of cubes.',),
        ('R:Identify the mixed term 3PS and explain why cubing the sum is not equivalent.','A:Give the correct cube sum.'),
        ('M:Obtain the signed sum and product.','M:Apply the cube-sum identity.','A:Give the exact cube sum.'),
        ('M:Apply translation and the cube-sum identity to the translated invariants.','A:Give the correct exact cube sum.')),
    'factor-connection': (
        ('A:Correct complete expanded polynomial.',),
        ('A:Correct linear coefficient with explanation from both cross terms.','A:Correct constant with explanation from the signed product.'),
        ('A:Correct leading coefficient.','A:Correct signed mixed coefficient.','A:Correct constant coefficient.'),
        ('A:Recover u by coefficient comparison or equivalent identity reasoning.','A:Recover w by coefficient comparison or equivalent identity reasoning.','R:Verify the middle coefficient using both recovered values.')),
    'quadratic-from-roots': (
        ('M:Form the two correct linear factors.','A:Give the expanded monic equation.'),
        ('A:Give the correct monic equation.','R:Explain invariance of roots under nonzero scalar multiplication.','R:Distinguish monic uniqueness from nonmonic alternatives.'),
        ('M:Use the sum-product monic identity.','A:Give the exact monic equation.'),
        ('M:Use the square-sum identity to recover the product.','A:Give the monic equation.','R:Verify the positive discriminant and hence reality.')),
    'reciprocal': (
        ('M:Use a valid common denominator and equivalent numerators.','A:Give the correct simplified fraction.'),
        ('R:Explain the error by combining fractions and derive the general identity.','R:State both original roots must be nonzero, since uv is the denominator.'),
        ('M:Use both reciprocal invariants with nonzero original product, or equivalent reversed-polynomial method.','A:Give the exact monic equation.'),
        ('M:Translate then reciprocate using both new invariants with a nonzero shifted product, or equivalent substitution.','A:Give the exact monic equation.')),
    'reciprocal-sums': (
        ('A:Correct simplified fraction.',),
        ('A:Identify zero as an original root.','R:Explain why the reciprocal sum is undefined.'),
        ('M:Recover the signed root invariants.','M:Combine reciprocals over the nonzero product.','A:Give the exact sum.'),
        ('M:Obtain the shifted sum.','M:Obtain the shifted product by expansion or polynomial evaluation.','A:Give the exact reciprocal sum with nonzero denominator.')),
    'root-ratios': (
        ('A:Both ordered ratios correct and simplified.',),
        ('R:Explain the repeated root gives two equal ratios, both one.','R:Explain that a zero root makes the second construction undefined.'),
        ('M:Use the ratio sum S squared over P minus two.','M:Establish product one using nonzero roots.','A:Give the exact monic equation.'),
        ('M:Form the ratio-sum equation with nonzero product.','A:Recover the exact product.','A:Give the original monic equation.')),
    'root-squares': (
        ('M:Expand the square as a product or use the binomial identity.','A:Give the complete polynomial and identify the middle term.'),
        ('A:Correct numerical comparison of both sides.','R:Derive the identity by accounting for the cross term.'),
        ('M:Use signed coefficient ratios and the square-sum identity.','A:Give the exact square sum.'),
        ('M:Translate both invariants and apply the square-sum identity.','A:Give the exact shifted square sum.')),
    'root-sum-product': (
        ('M:Expand all four signed products or equivalent identity.','A:Give the complete collected polynomial.'),
        ('M:Compare with a times the product of linear factors or use Vieta identities.','R:Explain the sign of the sum and division by leading coefficient.','A:Correct both numerical invariants.'),
        None,
        ('M:Use the squared-difference identity.','A:Recover the exact product.','A:Give both signed monic coefficients.')),
    'scaled-roots': (
        ('A:Both scaled numbers correct.',),
        ('M:Recover original sum and product.','A:Correct both scaled invariants and explain why the product scales twice.'),
        ('M:Recover original invariants.','M:Scale the sum once and product twice with signs.','A:Give the exact monic equation.'),
        None),
    'shifted-products': (
        ('A:Correct signed product of the shifted numbers.',),
        ('R:Identify the missing signed mixed term.','A:Give the exact corrected product.'),
        ('M:Recover original invariants.','M:Apply the shifted-product identity or evaluate the original monic polynomial at the shift.','A:Give the exact signed result.'),
        ('M:Form the equivalent quadratic in the shift.','M:Solve the quadratic by factorisation or equivalent exact method.','A:Give both distinct real shifts; no additional values satisfy the equivalent equation.')),
    'shifted-roots': (
        ('A:Both shifted numbers correct.',),
        ('R:Explain the reverse sign in the argument of the polynomial.','A:Give the corrected expanded polynomial.'),
        ('M:Use both shifted invariants or equivalent polynomial substitution.','A:Give the exact monic equation.'),
        ('A:Recover the unique shift from the new sum.','A:Give the exact shifted equation.','R:Verify discriminant invariance by calculation or unchanged root difference.')),
    'squared-roots': (
        ('A:Correct square of the negative number.','A:Correct square of the other number.'),
        ('M:Recover original sum and product.','A:Correct the squared-root sum using the mixed term.','A:Correct the squared-root product.'),
        ('M:Recover original invariants.','M:Apply both squared-root identities.','A:Give the exact monic equation.'),
        ('M:Obtain translated invariants.','M:Apply both squared-root identities to the translated roots.','A:Give the exact monic equation.')),
    'symmetric-parameter': (
        ('A:Correct solution for the linear unknown.',),
        ('M:Set the discriminant equal to zero.','A:Give both real parameter values.'),
        ('M:Derive the parameter equation using the square-sum identity.','A:Give both signs of the parameter.','R:Verify reality by the discriminant and completeness.'),
        ('M:Form the equation equating sum and product.','A:Recover the unique parameter.','R:Evaluate the discriminant and correctly classify the roots.')),
}
TARGETS = {(p,t) for p, rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    suffix = BANKS[path]
    return importlib.import_module('calibration' + ('_' + suffix if suffix else '') + '_bank')


def revise(path,tier,v):
    if (path,tier) not in TARGETS or type(v) is not int or v not in (1,2,3):
        raise ValueError('Not FM-16AU')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    if path=='factor-connection' and tier==3:
        p['likely_mistake']='Omitting a cross term or giving the mixed coefficient or constant the wrong sign.'
    if path=='root-squares':
        p['likely_mistake']='Omitting the cross term in a squared sum.'
    if path=='reciprocal' and tier==2:
        steps[0]='For nonzero u,v, combining fractions gives 1/u+1/v=(u+v)/(uv), not 1/(u+v).'
    if path=='reciprocal' and tier==3:
        steps[0]+=' The product is nonzero, so both roots are nonzero. Use reciprocal sum S/P and reciprocal product 1/P.'
    if path=='shifted-roots' and tier==3:
        a=v+1; b=2*a+2; d=2*a+3; S=a+b; P=a*b
        steps[0]=f'Original sum {S}, product {P}. Subtracting {d} from each root gives new sum {S}-2({d})={S-2*d}; expanding the shifted product gives {P}-{d}({S})+{d*d}={P-d*S+d*d}.'
    if path=='root-squares' and tier==2:
        steps[1]+=' Thus u^2+v^2=(u+v)^2-2uv.'
    if path=='cube-sums' and tier==4:
        steps[0]='For a decrease by d, the shifted sum is S-2d and the shifted product is P-dS+d^2. '+steps[0]
    if path=='combined-roots' and tier==4:
        steps[0]='For roots c*alpha-d and c*beta-d, use sum cS-2d and product c^2 P-cdS+d^2. '+steps[0]
        steps[1]='For the shifted invariants U,V, the squared-root sum is U^2-2V and product V^2. '+steps[1]
    if path=='root-squares' and tier==4:
        steps[0]='For an increase by d, use shifted sum S+2d and product P+dS+d^2. '+steps[0]
    if path=='scaled-roots' and tier==3:
        steps[1]='Scaling by c changes the sum to cS and product to c^2 P. '+steps[1]
    if path=='squared-roots' and tier in (3,4):
        if tier==4:
            steps[0]='For a decrease by d, use translated sum S-2d and product P-dS+d^2. '+steps[0]
        steps[1]='Squaring the roots: for original invariants U,V, the sum of the squared roots is U^2-2V and product V^2. '+steps[1]
    if path=='symmetric-parameter' and tier==4:
        steps[-1]+=' The discriminant is positive, so the roots are distinct and real.' if v==3 else ' The discriminant is negative, so the roots are nonreal.'
    # Preserve the number of marks and their original per-criterion weights.
    design=DESIGNS[path][tier-1]
    old=p['rubric']
    if len(design)!=len(old) or any(r['marks']!=1 for r in old):
        raise ValueError('Unreviewed rubric structure')
    rub=[]
    for spec in design:
        kind, criterion=spec.split(':',1)
        # Worked examples remain separate from the marking requirements.
        if kind=='M':
            criterion+=' Accept a valid equivalent method respecting the question restrictions; retain demonstrated method credit after a subsequent arithmetic slip.'
        elif kind=='A':
            criterion+=' Require the correct result for this criterion; do not automatically credit an incorrect result.'
        else:
            criterion+=' Accept equivalent valid reasoning; the conclusion must follow from the stated constraints.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
