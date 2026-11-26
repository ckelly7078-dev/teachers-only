"""FM-16AG original complex-number revisions."""
import sympy as s
from calibration_bank import L
from calibration_aa_bank import make as sums
from calibration_r_bank import make as polar
TARGETS={('cartesian-sums',6),('cartesian-to-polar',4)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not an FM-16AG revision')
    a=s.Integer(v+1); b=a+2; h=s.Symbol('h',real=True)
    if path=='cartesian-sums':
        p=sums(path,tier,v); S=a+b*s.I; r=s.sqrt(a*a+b*b); D=h*(-b+a*s.I)/r; U=s.expand((S+D)/2); V=s.expand((S-D)/2)
        q=f'For each real h, find every ordered pair of complex numbers u,v with u+v={L(S)}, equal moduli, and |u-v|=h. Classify the number of ordered pairs and prove completeness.'
        ans=f'h negative: none. h=0: u=v={L(S/2)}. h positive: (u,v)=({L(U)}, {L(V)}) or the reversed pair.'
        steps=[f'Write D=u-v. Then u=(S+D)/2 and v=(S-D)/2, with S={L(S)}.',f'Writing D=x+iy, equality of squared moduli gives $(a+x)^2+(b+y)^2=(a-x)^2+(b-y)^2$ with a={a}, b={b}; hence {a}x+{b}y=0.',f'All solutions of this linear condition have (x,y)=t(-{b},{a}). Their modulus is |t| times {L(r)}. Negative h is impossible; h=0 forces t=0.',f'For h positive, t is plus or minus {L(h/r)}. Substitution gives the ordered pair ({L(U)}, {L(V)}) or its reverse. They are distinct because D is nonzero.', 'All steps are reversible, so each pair satisfies the sum, equal moduli and prescribed distance; no other pair exists.']
        facts=[*map(s.simplify,[s.re(U),s.im(U),s.re(V),s.im(V)]),0,1,2]; hints=['Introduce the sum and difference as new variables.','Expand the two squared moduli; then use the distance condition.']; mistake='Treating the two ordered pairs as identical, or losing the zero-distance case.'
        rationale='Reconstruct ordered complex pairs from addition, subtraction, equal norms and distance, avoiding another singular-system template.'
        rub=[('M',1,'Express u and v in terms of the known sum and unknown difference.'),('M',1,'Derive the linear orthogonality condition from equal moduli.'),('A',2,'Obtain both ordered pairs for positive distance.'),('R',2,'Classify negative and zero distances and prove completeness.')]
    else:
        p=polar(path,tier,v); A=a+b*s.I; B=A-a*s.sqrt(3)+a*s.I; C=A-a*s.sqrt(3)-a*s.I; D=s.expand(B-A); E=s.expand(C-B)
        q=f'Points A, B and C represent {L(A)}, {L(s.expand(B))} and {L(s.expand(C))} respectively. Find the exact modulus and principal argument in (-pi,pi] of the displacements from A to B and from B to C. Explain why converting the position of C is not the same as converting the second displacement.'
        ans=f'AB: modulus {2*a}, argument {L(5*s.pi/6)}. BC: modulus {2*a}, argument {L(-s.pi/2)}.'
        steps=[f'Subtract the position of A from B, giving {L(D)}. Its modulus is {2*a}.',f'The real component is negative and imaginary component positive, so the reference angle pi/6 gives principal argument {L(5*s.pi/6)}.',f'Subtract B from C, giving {L(E)}. Its modulus is {2*a} and it lies on the negative imaginary axis, so its argument is {L(-s.pi/2)}.', 'The position of C is measured from the origin; the displacement BC is measured from B, which is nonzero. They are different vectors.']
        facts=[D,E,2*a,5*s.pi/6,2*a,-s.pi/2]; hints=['Subtract the starting position for each arrow.','Check the quadrant or axis before giving the principal angle.']; mistake='Converting endpoints instead of displacements, or choosing the wrong quadrant.'
        rationale='Link Cartesian subtraction to exact polar conversion of two successive displacements, including an axis case.'
        rub=[('M',1,'Determine both directed Cartesian displacements.'),('A',2,'Give both exact moduli and principal arguments.'),('R',1,'Distinguish an endpoint position from a directed displacement.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(x) for x in facts],rubric=[{'type':t,'marks':m,'criterion':r} for t,m,r in rub]);return p
