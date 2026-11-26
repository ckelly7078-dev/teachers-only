"""FM-16AH: distinct modulus and conjugate-factor challenges."""
import sympy as s
from calibration_bank import L
from calibration_t_bank import make as modulus
from calibration_x_bank import make as factor
TARGETS={('modulus-constraints',6),('conjugate-factor',6)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not an FM-16AH revision')
    a=s.Integer(v+1); b=a+2; h=s.Symbol('h',real=True); x=s.Symbol('x',real=True)
    if path=='modulus-constraints':
        p=modulus(path,tier,v); lo=a; hi=a*s.sqrt(2); A=(h+s.sqrt(2*a*a-h*h))/2; B=(h-s.sqrt(2*a*a-h*h))/2
        q=f'For every real h find all complex z such that |z|={a} and |Re(z)|+|Im(z)|=h. Give exact Cartesian forms, count the distinct solutions and justify the boundary cases.'
        ans=f'None outside [{L(lo)}, {L(hi)}]. At h={a}: four axis points, z=+/-{a} or +/-{a}i. At h={L(hi)}: four diagonal points with both component magnitudes {L(a/s.sqrt(2))}. Inside the interval: eight points, with component magnitudes {L(A)}, {L(B)} in either order and independent signs.'
        steps=[f'Write U=|Re(z)| and V=|Im(z)|, so U,V are nonnegative, U+V=h and U squared+V squared={a*a}. Hence h is nonnegative.',f'The product UV=(h squared-{a*a})/2 must be nonnegative, and (U-V) squared={2*a*a}-h squared must be nonnegative. Thus {a} <= h <= {L(hi)}.',f'U and V are roots of the monic quadratic with sum h and product (h squared-{a*a})/2, giving {L(A)} and {L(B)}. Both are nonnegative throughout the interval.',f'At the lower endpoint one magnitude is zero, giving four axis points. At the upper endpoint the magnitudes coincide, giving four diagonal points. In the interior the two magnitudes are positive and distinct, so two orders and four sign choices give eight distinct points.', 'Each listed point has the given modulus and absolute-component sum; the magnitude equation and sign choices exhaust all possibilities.']
        facts=[lo,hi,A,B,0,4,8,4]; hints=['Introduce nonnegative component magnitudes.','Use both their product and squared difference to bound h.']; mistake='Counting eight sign/order choices even when a component is zero or both magnitudes agree.'
        rationale='Combine modulus with absolute Cartesian components; derive sharp bounds and classify axis, diagonal and general symmetry orbits.'
        rub=[('M',1,'Introduce nonnegative magnitudes and derive sum and squared sum.'),('R',2,'Derive both sharp bounds including nonnegativity.'),('A',2,'Find both exact component magnitudes.'),('R',2,'Count axis, diagonal and interior solutions and prove completeness.')]
    else:
        p=factor(path,tier,v); N=a*a+b*b; low=N*b*b; collision=N*N; U=s.sqrt(h/N-b*b); F=(x-a)**2+b*b; G=(x-U)**2+b*b; H=(x+U)**2+b*b
        q=f'A monic real quartic P has root {L(a+b*s.I)} and its other conjugate pair (counting multiplicity) has imaginary-part magnitude {b}. Given P(0)=h, find every possible factorisation into monic irreducible real quadratics for each real h. Count the distinct quartics and determine exactly when roots repeat.'
        ans=f'None for h below {low}. At h={low}: one quartic, ({L(F)})({L(x*x+b*b)}). For h above {low}: two quartics, ({L(F)})({L(G)}) or ({L(F)})({L(H)}). Repeated roots only for h={collision} in the positive-real-part branch, when P=({L(F)}) squared and both conjugate roots have multiplicity two.'
        steps=[f'Real coefficients force the conjugate {L(a-b*s.I)}, so the first monic factor is {L(F)}. The other pair must be u +/- {b}i for real u, giving the factor (x-u) squared+{b*b}.',f'At x=0 the product is {N}(u squared+{b*b}), so u squared=h/{N}-{b*b}. A real u exists exactly for h >= {low}.',f'At equality u=0 gives one quartic. Above it, u=+/- {L(U)} gives two different monic quadratics and hence two different quartics.',f'Each quadratic is irreducible since {b} is nonzero. A shared root requires the two conjugate pairs to coincide, so u={a}, forcing h={collision}. The positive branch then gives two double roots; the negative branch still has four simple roots.', 'Conversely both constructed factors have the required roots and constant, so the classification is exhaustive.']
        facts=[low,collision,U,s.expand(F),s.expand(G),s.expand(H),1,2]; hints=['Factor out the given conjugate pair first.','Use the constant term to constrain the real part of the other pair; check when the factors coincide.']; mistake='Counting the two signs as different at u=0 or assuming every quartic at the collision parameter has repeated roots.'
        rationale='Reconstruct all quartic conjugate factors from a constant constraint and classify branch-specific multiplicities.'
        rub=[('M',1,'Derive the forced conjugate factor and parameterise the second.'),('M',1,'Use the constant term to derive the constraint.'),('A',2,'Give all factorisations and correct counts.'),('R',2,'Identify the unique repeated-root branch and justify completeness.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(f) for f in facts],rubric=[{'type':t,'marks':m,'criterion':r} for t,m,r in rub]);return p
