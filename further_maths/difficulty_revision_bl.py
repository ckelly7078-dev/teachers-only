"""FM-16BL successors for the eleven BK demand/allocation observations."""
from copy import deepcopy
from importlib import import_module
import sympy as s
from active_difficulty import require

REGISTRY={
 ('inverse-three',5):('bd',3,7), ('locus-intersection',6):('az',3,6),
 ('plane-cartesian',6):('bg',3,6), ('point-line',6):('bh',3,6),
 ('symmetric-parameter',5):('av',3,6), ('system-consistency',5):('be',3,6),
 ('verify-roots',6):('ax',4,6), ('cube-sums',4):('au',2,4),
 ('matrix-equation',5):('bd',3,5), ('plane-plane-angle',5):('bg',3,4),
 ('scaled-roots',5):('av',3,4),
}
TARGETS={key:value[0] for key,value in REGISTRY.items()}
NEW_DEMAND={('inverse-three',5),('locus-intersection',6),('point-line',6),('symmetric-parameter',5),('system-consistency',5)}
CRITERIA={
 ('inverse-three',5):[('M','Find the determinant in terms of k and state its nonzero restriction.'),('M','Derive the (1,3) inverse entry by a cofactor or an equivalent solve.'),('A','Recover the unique admissible k.'),('M','Compute the full inverse by a valid method.'),('A','Give the exact inverse.'),('A','Apply it to obtain the exact solution vector.'),('R','Verify the inverse identity and the original system.')],
 ('locus-intersection',6):[('M','Express the line as x+y=k and substitute into the circle.'),('M','Complete the square or derive the equivalent quadratic discriminant.'),('A','Give both exact tangency thresholds.'),('R','Classify all three intersection counts with inclusive boundaries.'),('A','Give the paired exact Cartesian coordinates in each nonempty case.'),('R','Justify completeness and the coalescence at tangency.')],
 ('plane-cartesian',6):[('M','Use the given line direction to parameterise all normals.'),('A','Write the resulting general plane equation.'),('M','Impose the extra point condition on the two normal parameters.'),('A','Give the unique plane when the displacement is nonzero.'),('A','Give the entire family when both parameters vanish, excluding the zero normal.'),('R','Prove the cases exhaust all possibilities, identifying proportional normals.')],
 ('point-line',6):[('M','Form the squared distance as a quadratic in t.'),('M','Complete the square.'),('A','Give the unique closest point and exact minimum distance.'),('R','Prove uniqueness and classify the attainable squared levels.'),('A','Give the exact two points above the minimum and the singleton at equality.'),('R','Show no other points occur and exclude lower levels.')],
 ('symmetric-parameter',5):[('M','Relate the squared root difference to the discriminant.'),('M','Solve the parameter quadratic without losing either branch.'),('A','Give both exact parameters.'),('A','Recover the exact two roots for each parameter using their sum and gap.'),('R','Classify their signs using sum and product or exact inequalities.'),('R','Verify both gaps and explain completeness.')],
 ('system-consistency',5):[('M','Eliminate to obtain the single parameter-dependent scalar condition.'),('A','Give the unique point in the nonsingular case.'),('R','Identify the incompatible singular branch.'),('A','State the exact right-hand-side condition for the consistent singular branch.'),('A','Give the complete line in that branch.'),('R','Explain the three geometric possibilities and prove completeness.')],
 ('verify-roots',6):[('M','Identify the common conjugate-pair factor.'),('M','Reconstruct the other monic quadratic for each claimed list.'),('A','Give the exact parameter pair for list A.'),('A','Give the exact parameter pair for list B.'),('R','Prove both coefficient matches are necessary and sufficient and distinguish the pairs.'),('R','Explain why the common two roots alone cannot distinguish the lists.')],
 ('cube-sums',4):[('M','Obtain the original signed sum and product.'),('M','Translate both invariants with the correct signs.'),('M','Apply the cube-sum identity to the translated invariants.'),('A','Give the exact cube sum without solving the original equation.')],
 ('matrix-equation',5):[('M','Establish invertibility and set up X=A inverse B or equivalent equations.'),('M','Use symmetry to form the parameter equation.'),('A','Give the unique parameter.'),('A','Give the entire symmetric matrix.'),('R','Verify the original equation and justify uniqueness.')],
 ('plane-plane-angle',5):[('M','Use the absolute normal-vector cosine ratio.'),('M','Solve the resulting equation retaining both sign branches.'),('A','Give both exact parameter values.'),('R','Check both in the original equation and exclude other solutions.')],
 ('scaled-roots',5):[('M','Relate the scaled product to the given constant and recover both candidate scales.'),('R','Use the linear coefficient sign to select the unique scale.'),('A','Give the exact scale.'),('A','Give the full monic equation with both coefficients correct.')],
}
def tex(x): return '$'+s.latex(x)+'$'
def mf(m): return {'matrix':[[str(m[i,j]) for j in range(m.cols)] for i in range(m.rows)]}
def revise(path,tier,v):
    key=path,tier
    require(type(tier) is int and type(v) is int and v in (1,2,3) and key in TARGETS,'Unknown BL target')
    p=deepcopy(import_module('difficulty_revision_'+TARGETS[key]).revise(path,tier,v))
    require(sum(x['marks'] for x in p['rubric'])==REGISTRY[key][1] and len(CRITERIA[key])==REGISTRY[key][2],'BL allocation mismatch')
    p['rubric']=[{'type':t,'marks':1,'criterion':c+(' Accept equivalent valid methods respecting restrictions; retain independently demonstrated method credit after arithmetic slips.' if t=='M' else ' Require the specified correct result.' if t=='A' else ' Accept equivalent valid reasoning supported by the constraints.')} for t,c in CRITERIA[key]]
    if key not in NEW_DEMAND:return p
    k,h=s.symbols('k h',real=True); x=s.Symbol('x'); a=v+1;b=v+2
    if path=='inverse-three':
        A=s.Matrix([[1,a,0],[1,k,b],[0,1,1]]);det=k-a-b;K=a+2*b; B=s.Matrix([v+2,v+3,v+4]);Ai=A.subs(k,K).inv();sol=Ai*B
        q=f'The matrix {tex(A)} is invertible and its inverse has (1,3) entry {a}. Find k, determine the entire inverse, use it to solve A x = {tex(B)} and verify both the inverse and the solution.'
        ans=f'k={K}; inverse {tex(Ai)}; solution {tex(sol)}.'
        w=[f'The determinant is {tex(det)}, so k cannot equal {a+b}. The (3,1) cofactor is {a*b}; therefore the (1,3) inverse entry is {tex(a*b/det)}.',f'Equate this to {a}; since a is nonzero, the equation forces k={K}, with determinant {b}.',f'At this value, the adjugate is {tex(A.subs(k,K).adjugate())}. Dividing by {b} gives {tex(Ai)}.',f'Multiply by the right-hand side: {tex(Ai)} {tex(B)} = {tex(sol)}.',f'Direct multiplication gives {tex(A.subs(k,K)*Ai)} for the inverse check and {tex(A.subs(k,K)*sol)} for the solution check.']
        facts=[str(K),mf(Ai),mf(sol)]
    elif path=='locus-intersection':
        C=v+1;R=v+3;lo=C-s.sqrt(2)*R;hi=C+s.sqrt(2)*R;D=2*R**2-(k-C)**2;xp=(k+C+s.sqrt(D))/2;xm=(k+C-s.sqrt(D))/2;yp=k-xp;ym=k-xm
        q=f'For every real k, classify the intersections of |z-{C}|={R} and Re(z)+Im(z)=k. Give every intersection in exact Cartesian form, including tangencies, and justify completeness.'
        ans=f'No intersections outside [{tex(lo)}, {tex(hi)}]; one at either endpoint and two in the interior. In the nonempty cases z={tex(xp+s.I*yp)} or {tex(xm+s.I*ym)}; at either endpoint these coincide.'
        w=[f'Put z=x+iy; y=k-x, hence (x-{C}) squared +(k-x) squared ={R**2}.',f'Completing the square gives (2x-k-{C}) squared = {tex(D)}.',f'The right-hand side is positive precisely between {tex(lo)} and {tex(hi)}, zero at the endpoints and negative outside.',f'Take the paired square-root signs: x={tex(xp)} or {tex(xm)}; corresponding y=k-x is {tex(yp)} or {tex(ym)}. Both satisfy the original equations. At tangency the square root vanishes; outside the interval no real x is possible.']
        facts=[str(lo),str(hi),str(D),str(xp),str(yp),str(xm),str(ym)]
    elif path=='point-line':
        A=2*v+2;B=v+3;t=s.Symbol('t',real=True);P=s.Matrix([A,0,B]);foot=s.Matrix([A//2,A//2,0]);Dmin=s.Rational(A*A,2)+B*B;tp=s.Rational(A,2)+s.sqrt((h-Dmin)/2);tm=s.Rational(A,2)-s.sqrt((h-Dmin)/2)
        q=f'For P=({A},0,{B}) and line r=t(1,1,0), prove using squared distance that there is a unique closest point and give its distance. For every real h, classify and find every point on the line at squared distance h from P.'
        ans=f'Closest point {tex(foot)}, distance {tex(s.sqrt(Dmin))}. No points for h<{Dmin}, one at h={Dmin}, two for h>{Dmin}: (t,t,0) with t={tex(tp)} or {tex(tm)}.'
        w=[f'The squared distance is (t-{A}) squared +t squared +{B*B} = 2(t-{A//2}) squared +{Dmin}.',f'The square is nonnegative and zero only at t={A//2}; the unique closest point is {tex(foot)} and distance {tex(s.sqrt(Dmin))}.',f'For level h, the equation is (t-{A//2}) squared = (h-{Dmin})/2. Negative right side gives no solution, zero gives exactly the foot, positive gives exactly two real roots {tex(tp)} and {tex(tm)}.', 'Each gives the point (t,t,0); the squared equation is equivalent to the original distance condition, proving completeness.']
        facts=[mf(foot),str(Dmin),str(tp),str(tm)]
    elif path=='symmetric-parameter':
        D=2*v+5;P=a*k+v+3;poly=x*x-k*x+P;ks=s.solve(k*k-4*P-D*D,k);pairs=[[(j-D)/2,(j+D)/2] for j in ks]
        q=f'The real roots of {tex(poly)}=0 have absolute difference {D}. Determine every k, give both roots for each value, classify their signs and prove completeness.'
        ans='; '.join(f'k={tex(j)}: roots {tex(r[0])}, {tex(r[1])}, '+('opposite signs' if i==0 else 'both positive') for i,(j,r) in enumerate(zip(ks,pairs)))+'.'
        w=[f'The signed sum is k, product {tex(P)} and squared gap is {tex(k*k-4*P)}. Equate to {D*D}.',f'Solve the resulting quadratic to obtain {tex(ks[0])} and {tex(ks[1])}. Both yield positive discriminant {D*D}.',f'Using sum k and gap {D}, the roots are (k-{D})/2 and (k+{D})/2. Substitution gives {tex(pairs[0])} and {tex(pairs[1])}, respectively.',f'For the smaller k the product {tex(P.subs(k,ks[0]))} is negative; for the larger k the product {tex(P.subs(k,ks[1]))} and sum are positive. Thus the first pair has opposite signs, the second both positive. The quadratic condition is necessary and sufficient, so there are no other values.']
        facts=[str(j) for j in ks]+[[str(z) for z in pair] for pair in pairs]
    elif path=='system-consistency':
        A=v+1;B=v+3;Z=(h-A-B)/(k-1);point=s.Matrix([A-B+Z,B-Z,Z]);t=s.Symbol('t',real=True);line=s.Matrix([A-B+t,B-t,t]);M=s.Matrix([[1,1,0],[0,1,1],[1,2,k]])
        q=f'For every real pair (k,h), solve x+y={A}, y+z={B}, x+2y+kz=h. Classify the common intersection geometrically and give the full solution set in every case.'
        ans=f'k not equal to 1: unique point {tex(point)}; k=1 and h={A+B}: line {tex(line)}, t real; k=1 and h not equal to {A+B}: no common point.'
        w=[f'The first two equations give y={B}-z and x={A-B}+z. Substitute into the third: (k-1)z=h-{A+B}.',f'If k is not 1, divide to get z={tex(Z)}; back-substitution yields {tex(point)}. The determinant is {tex(M.det())}, so the intersection is a unique point.',f'If k=1, the scalar equation is 0=h-{A+B}; it is inconsistent unless h={A+B}.',f'When consistent, z is unrestricted; write z=t to obtain {tex(line)}, t real. The first two planes have independent normals and the third equation is redundant, giving exactly a common line. Otherwise no common point exists.']
        facts=[str(A+B),mf(point),mf(line)]
    else:raise ValueError('Missing BL demand')
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=w,facts=facts,
             progressive_hints=[CRITERIA[key][0][1],CRITERIA[key][1][1]],
             likely_mistake='Losing a parameter branch, exceptional case or necessary restriction; check every original constraint.',
             demand_rationale='FM-16BL: independent reconstruction or exhaustive parameter classification with exact verification; editorial difficulty only.')
    return p
