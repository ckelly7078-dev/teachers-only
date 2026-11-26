"""FM-16AE: four original difficulty designs, additive to FM-16AD."""
import sympy as s
from calibration_bank import L, make as base
from calibration_b_bank import make as composition
from calibration_l_bank import make as geometry
from calibration_p_bank import make as three

TARGETS={(p,6) for p in ('system-consistency','three-system','three-plane-unique','composition-order')}
FAMILIES={'system-consistency':'homogeneous-nullspace','three-system':'two-singular-values','three-plane-unique':'plane-reconstruction-distance','composition-order':'inverse-composition-order','system-classification':'parameter-system-reduction'}

def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not an FM-16AE revision')
    a=s.Integer(v+1); b=a+2; k,h,t=s.symbols('k h t',real=True)
    if path=='system-consistency':
        p=base(path,tier,v)
        U=s.Matrix([-a,-a,2]); V=s.Matrix([-a-1,1,1])
        q=f'For real k,h, solve the homogeneous system $x+y+{a}z=0$, $x+y+{a}z+(k-{a})(x-y)=0$, $x+y+{a}z+(h-{b})(y-z)=0$. Classify when there are zero, one or two independent free parameters and give the full solution set. Explain why no inconsistent case exists.'
        ans=f'If k differs from {a} and h differs from {b}, only the zero vector. If k differs from {a} and h={b}, all multiples of {L(U)}. If k={a} and h differs from {b}, all multiples of {L(V)}. If k={a}, h={b}, all real linear combinations of {L(U)} and {L(V)}.'
        steps=[f'Subtract the first equation from the other two: $(k-{a})(x-y)=0$ and $(h-{b})(y-z)=0$.',f'If both coefficients are nonzero, x=y=z and $({a+2})z=0$. Only the zero vector works.',f'If only the first coefficient is nonzero, x=y and the first equation gives the line spanned by {L(U)}. If only the second is nonzero, y=z and the line is spanned by {L(V)}.',f'If both vanish, the sole equation is $x+y+{a}z=0$. The two displayed vectors satisfy it and are independent (their first two components are equal for the first vector but unequal for the second). They therefore span its two-free-parameter solution plane.', 'The zero vector always satisfies a homogeneous system; the four disjoint cases exhaust the parameters.']
        f=[a,b,*U,*V,0,1,1,2]; hints=['Subtract the first equation before considering parameter values.','Find independent directions when both remaining equations vanish.']; mistake='Assuming every singular homogeneous system has exactly one free parameter.'
        rationale='Two independent singular switches; distinguish a zero solution, a line and a two-parameter family.'
        rubric=[('M',1,'Eliminate the common expression.'),('A',1,'Find the zero-only case.'),('A',2,'Find both one-parameter solution sets.'),('R',2,'Prove the two independent directions span the full plane.'),('R',1,'Explain consistency and exhaustive cases.')]
    elif path=='three-system':
        p=three(path,tier,v); d=k-a; D=(d-2)*(d+1); Y=(b*(d-1)-2*h)/D; Z=(d*h-b)/D; X=a-Y-Z
        q=f'For all real k,h solve $x+y+z={a}$, $x+(k-{a-1})y+3z={a+b}$ and $2x+3y+(k-{a-1})z={2*a}+h$. Classify every parameter pair, including both singular values, and give every solution.'
        ans=f'For k not equal to {a-1} or {a+2}: x={L(X)}, y={L(Y)}, z={L(Z)}. For k={a-1}, require h={-b}; for k={a+2}, require h={L(b/2)}. In either compatible singular case z=t, y=h-(k-{a+1})t, x={a}-y-t, t real. Otherwise no solution.'
        steps=[f'Subtract the first equation from the second, and twice the first from the third. With d=k-{a}, obtain $dy+2z={b}$ and $y+(d-1)z=h$.','The reduced determinant is $d(d-1)-2=(d-2)(d+1)$. Its two zeros must be treated separately.',f'For nonzero determinant eliminate y and z to obtain y={L(Y)}, z={L(Z)}; back-substitute x={L(X)}.',f'At d=-1 the rows are proportional with factor -1, requiring h={-b}; at d=2 the factor is one half, requiring h={L(b/2)}.',f'For each compatible singular case choose z=t and use the second reduced equation, then x={a}-y-t. For incompatible constants the reduced rows contradict each other. All row operations are reversible, so the classification is complete.']
        f=[a-1,a+2,-b,b/2,X,Y,Z]; hints=['Eliminate x from both remaining equations.','Factor the reduced determinant and compare the right sides at each zero.']; mistake='Checking only one determinant zero or using the same compatibility condition at both.'
        rationale='Coupled elimination leaves a two-variable system with two distinct singular branches and different compatibility conditions.'
        rubric=[('M',1,'Obtain both reduced equations.'),('M',1,'Factor determinant and identify both singular values.'),('A',2,'Obtain all three regular-case coordinates.'),('R',2,'Derive both distinct compatibility conditions.'),('A',1,'Give full singular families and exclude incompatible cases.')]
    elif path=='three-plane-unique':
        p=geometry(path,tier,v); P=s.Matrix([a,b,a+1]); Q=P+s.Matrix([a,0,0]); D=s.Matrix([1,-1,1]); km=2-a/b; kp=2+a/b; R=P+b*D; S=P-b*D; hm=Q[0]+km*Q[1]+Q[2]; hp=Q[0]+kp*Q[1]+Q[2]
        q=f'The planes $x+y={P[0]+P[1]}$ and $y+z={P[1]+P[2]}$ contain P={L(P)}. A third plane $x+ky+z=h$ contains Q={L(Q)}. Find every real pair (k,h) for which the three planes have a unique common point at distance {L(b*s.sqrt(3))} from P. Give the points and prove uniqueness and completeness.'
        ans=f'k={L(km)}, h={L(hm)}, point {L(R)}; or k={L(kp)}, h={L(hp)}, point {L(S)}.'
        steps=[f'The first two planes intersect along P+t(1,-1,1), with P={L(P)}. The distance from P is $|t|\\sqrt3$.',f'The required distance forces t={b} or t={-b}, giving {L(R)} and {L(S)}.',f'Containing Q forces $h={Q[0]}+{Q[1]}k+{Q[2]}$. Substitution of the line into the third plane then gives $(2-k)t={a}$.',f'For t={b} obtain k={L(km)}, h={L(hm)}; for t={-b} obtain k={L(kp)}, h={L(hp)}.', 'Both k values differ from 2, so the line equation has exactly one solution for each plane. No other t has the specified distance; both points satisfy all three equations.']
        f=[km,hm,*R,kp,hp,*S]; hints=['Find the common line of the first two planes.','The distance condition fixes two points; use Q to recover the plane.']; mistake='Finding a candidate common point without proving the intersection is unique.'
        rationale='Reconstruct plane coefficients from a line, prescribed distance and a second point; verify uniqueness for both branches.'
        rubric=[('M',1,'Parameterise the common line.'),('A',1,'Obtain both distance-constrained points.'),('M',1,'Use Q to relate the unknown coefficients.'),('A',2,'Find both coefficient pairs.'),('R',1,'Verify uniqueness and completeness.')]
    else:
        p=composition(path,tier,v); A=a+1; B=b+1; K=A-1; H=(B-1)/A; KR=(A-1)/B; HR=B-1; S=s.Matrix([[1,K],[0,1]]); T=s.Matrix([[1,0],[H,1]]); C=T*S; Cr=s.Matrix([[1,KR],[0,1]])*s.Matrix([[1,0],[HR,1]])
        q=f'The horizontal shear $S=\\begin{{pmatrix}}1&k\\\\0&1\\end{{pmatrix}}$ and vertical shear $T=\\begin{{pmatrix}}1&0\\\\h&1\\end{{pmatrix}}$ are applied once each in an unknown order. The point (1,1) maps to ({A},{B}), and the image of (1,0) lies on the ray $y={s.latex(H)}x$, x positive. Determine the order, k,h and the composition matrix; rule out the other order.'
        ans=f'S then T; k={K}, h={L(H)}, matrix {L(C)}.'
        steps=[f'For S then T, (1,1) maps to $(1+k,1+h(1+k))$. The observed image forces k={K}, h={L(H)}.',f'For T then S, the image is $(1+k(1+h),1+h)$. The observed image forces h={HR}, k={L(KR)}.',f'For the first candidate, (1,0) maps to {L(C[:,0])}, satisfying the positive ray.',f'For the second candidate, (1,0) maps to {L(Cr[:,0])}. Its slope is {L(Cr[1,0]/Cr[0,0])}, unequal to {L(H)}. Reject this order.',f'The valid composition is TS={L(C)}. Each order uniquely determined its candidate from the first image, and the second image selects exactly one.']
        f=[K,H,*C,KR,HR,False]; hints=['Determine the parameters separately for each possible order.','Test the second observed image before choosing the order.']; mistake='Assuming an order from a single observed image, or multiplying matrices in chronological order.'
        rationale='Inverse composition reconstruction with two competing orders and an independent ray observation.'
        rubric=[('M',1,'Construct the image equations for both orders.'),('A',2,'Recover both candidate parameter pairs.'),('R',2,'Use the second observation to accept and reject the respective candidates.'),('A',1,'State the valid composition matrix and order.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[x if type(x) is bool else str(x) for x in f],rubric=[{'type':c,'marks':m,'criterion':r} for c,m,r in rubric])
    return p
