"""FM-16AL: classify skew lines by constructing parallel planes."""
import sympy as s
from calibration_bank import L,make
TARGETS={('skew',6)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not FM-16AL')
    a=s.Integer(v+1); b=a+2; h,k=s.symbols('h k',real=True)
    p=make(path,tier,v); N=s.Matrix([a,-1,k-a]); C=b*(k-a)-h; P=s.Matrix([-b,-a*b,0])
    q=f'For real h,k let L have points (t,{a}t,0) and M have points (u,h+ku,{b}+u), with t,u real. Construct the unique plane containing L whose direction space contains the direction of M. Construct the parallel plane containing M. Determine exactly when these planes coincide, classify the lines, and give their common point when it exists. Prove your classification.'
    ans=f'The planes are {a}x-y+(k-{a})z=0 and {a}x-y+(k-{a})z={L(C)}. They coincide precisely when h={L(b*(k-a))}; then L and M intersect at {L(P)}. Otherwise the lines are skew.'
    steps=[f'The direction vectors (1,{a},0) and (1,k,1) are independent because the second has nonzero third component. Their cross product is {L(N)}, nonzero, so it determines a unique normal direction.',f'The plane through L contains the origin, so its equation is {a}x-y+(k-{a})z=0. The parallel plane through (0,h,{b}) has constant {L(C)}; every point of M satisfies it because its direction is perpendicular to the normal.',f'The planes coincide if and only if {L(C)}=0. If distinct, they are disjoint and the nonparallel lines are skew.',f'If coincident, the third coordinate forces u=-{b}, and the first gives t=-{b}. The second coordinates agree exactly when h={L(b*(k-a))}. Thus the unique intersection is {L(P)}.', 'These cases exhaust the parameters: neither direction can vanish or become parallel, and the constructed point satisfies both lines exactly in the coincident-plane case.']
    facts=[*N,C,b*(k-a),*P]; hints=['Cross the two direction vectors to obtain a normal.','Use the base points to obtain the two plane constants; verify intersection independently.']; mistake='Assuming nonparallel directions guarantee intersection, or confusing parallel planes with parallel lines.'
    rationale='Differentiate skew classification from direct coordinate elimination by reconstructing parallel supporting planes and proving coplanarity and uniqueness.'
    rub=[('M',1,'Obtain independent directions and their nonzero common normal.'),('A',2,'Construct both plane equations.'),('R',1,'Derive coincidence condition and explain skewness otherwise.'),('A',1,'Find the intersection point in the coplanar case.'),('R',1,'Prove completeness and uniqueness.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(s.simplify(f)) for f in facts],rubric=[{'type':t,'marks':m,'criterion':c} for t,m,c in rub]);return p
