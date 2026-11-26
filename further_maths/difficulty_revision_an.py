"""FM-16AN: distinct complex-number reconstruction challenges."""
import sympy as s
from calibration_bank import L
from calibration_v_bank import make as polar
from calibration_w_bank import make as conjugate
from calibration_z_bank import make as product
TARGETS={('polar-products',5),('conjugate-find',6),('cartesian-product',6)}


def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not FM-16AN')
    a=s.Integer(v+1); b=a+2; h,k=s.symbols('h k',real=True)
    if path=='polar-products':
        p=polar(path,tier,v); A=5*s.pi/6; B=-s.pi/2; T=s.pi/6; U=2*s.pi/3
        q=f'Nonzero complex numbers z,w satisfy |z|={a}, and zw has modulus {a*b} and argument 5pi/6, while z conjugate(w) has modulus {a*b} and argument -pi/2. Find every ordered pair (z,w) in polar form with principal arguments in (-pi,pi]. Explain why neither observation alone determines the pair.'
        ans=f'|z|={a}, |w|={b}; (arg z,arg w) is ({L(T)},{L(U)}) or ({L(T-s.pi)},{L(U-s.pi)}).'
        steps=[f'Both product moduli equal |z||w|, so |w|={b}. Write theta=arg z, phi=arg w.', 'The product arguments give theta+phi congruent to 5pi/6 and theta-phi congruent to -pi/2, modulo 2pi.', 'Adding gives 2theta congruent to pi/3 modulo 2pi. In the principal interval theta=pi/6 or -5pi/6. Substituting into the first congruence gives phi=2pi/3 or -pi/3 respectively.', 'Each pair satisfies both original congruences and the moduli. Either observation alone leaves one angle arbitrary; together they leave exactly two pairs, related by simultaneous negation.']
        facts=[a,b,T,U,T-s.pi,U-s.pi]; hints=['Use the sign reversal of the argument under conjugation.','Add the congruences, but keep both solutions when dividing the angle by two.']; mistake='Dividing a congruence by two and discarding the second principal-angle pair.'; rationale='Reconstruct two unknown polar factors from independent product observations and explain the remaining sign ambiguity.'
        rub=[('M',1,'Use both product observations to obtain the modulus and angle congruences.'),('M',1,'Eliminate one angle without losing the second branch; equivalent Cartesian square-root method accepted.'),('A',2,'Give both complete ordered pairs with principal angles (one mark per pair).'),('R',1,'Verify both observations and explain why either alone is insufficient.')]
    elif path=='conjugate-find':
        p=conjugate(path,tier,v); lo=(a+1)*(a-3)/4; hi=(a-1)**2/4; X=-(a+1)/2; R=s.sqrt(hi-h); Y=s.sqrt(h-lo); C=-(a-1)/2
        q=f'For each real h find all complex z satisfying conjugate(z)=z squared+{a}z+h. Separate real and nonreal solutions, count all distinct solutions including boundary values, and prove completeness.'
        ans=f'Real solutions z={L(C)} +/- {L(R)} for h <= {L(hi)}, with one at equality. Nonreal solutions z={L(X)} +/- i times {L(Y)} for h > {L(lo)}. Counts: 2 for h <= {L(lo)}, 4 for {L(lo)} < h < {L(hi)}, 3 at h={L(hi)}, 2 for h > {L(hi)}.'
        steps=[f'Put z=x+iy. Equating components gives x squared-y squared+({a}-1)x+h=0 and y(2x+{a}+1)=0.',f'If y=0, complete the square to obtain (x+{L((a-1)/2)}) squared={L(hi-h)}. There are two, one or no real roots as h is below, equal to or above {L(hi)}.',f'If y is nonzero, x={L(X)} and substitution gives y squared={L(h-lo)}. There are exactly two nonreal roots when h>{L(lo)} and none otherwise.',f'The thresholds satisfy {L(hi)}-{L(lo)}=1. The real and nonreal families are disjoint. Hence there are 2, 4, 3, 2 solutions over the successive regions listed; the lower endpoint has two real roots and no nonreal roots.', 'Each branch solves both component equations and every solution must satisfy one of the branches.']
        facts=[lo,hi,C,R,X,Y,2,4,3,2]; hints=['Equate imaginary components and factor out y.','Treat y=0 separately from y nonzero; compare the two thresholds.']; mistake='Dividing by the imaginary component and losing all real roots.'; rationale='Classify nonlinear conjugate equations through disjoint real and nonreal branches, not a singular linear system.'
        rub=[('M',1,'Obtain both component equations and factor the imaginary equation.'),('A',2,'Find the real-root formula and the discriminant boundary (one mark each).'),('A',2,'Find the forced real component and imaginary-component formula with strict threshold (one mark each).'),('R',2,'Count distinct solutions across the thresholds (one mark); prove both branches exhaust the original equation (one mark).')]
    else:
        p=product(path,tier,v); D=h*h-4*a*b*(a*b-k); X=(-h-s.sqrt(D))/(2*b); Y=(h+b*X)/a; U=(-h+s.sqrt(D))/(2*b); V=(h+b*U)/a
        q=f'For each real pair (h,k), find every ordered pair of complex numbers z,w with Re(z)={a}, Im(w)={b} and zw=h+ki. Classify zero, one and two possible pairs and prove completeness.'
        ans=f'Put D={L(D)}. For D<0 none. For D=0 one pair, and for D>0 two pairs: z={a}+ix, w=y+{b}i, where x={L(X)} or {L(U)} and y=(h+{b}x)/{a}.'
        steps=[f'Write z={a}+ix and w=y+{b}i. Expanding gives {a}y-{b}x=h and xy+{a*b}=k.',f'Eliminate y=(h+{b}x)/{a}, giving {b}x squared+hx+{a}({a*b}-k)=0.',f'Its discriminant is {L(D)}. A negative value gives no real x; zero gives one; positive gives two distinct roots {L(X)} and {L(U)}.',f'Each root determines exactly one y, and substitution into the product restores both components. The fixed nonzero components exclude zero factors. This proves the classification and completeness.']
        facts=[D,X,Y,U,V,0,1,2]; hints=['Expand the product and separate real and imaginary components.','Eliminate one component and classify the resulting quadratic.']; mistake='Solving only one product component or assuming two roots remain distinct at zero discriminant.'; rationale='Reconstruct both factors from nonlinear product constraints, including a discriminant boundary and proof of sufficiency.'
        rub=[('M',1,'Obtain both product component equations.'),('M',1,'Eliminate either unknown to form an equivalent quadratic; allow follow-through from a single earlier arithmetic slip.'),('A',2,'Find both parameterised factor pairs (one mark for roots, one for reconstruction; follow through a consistent quadratic).'),('R',2,'Classify discriminant cases (one mark); prove sufficiency and completeness for the original constraints (one mark).')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(s.simplify(f)) for f in facts],rubric=[{'type':t,'marks':m,'criterion':c} for t,m,c in rub]);return p
