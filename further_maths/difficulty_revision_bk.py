"""FM-16BK targeted demand and allocation successors; original candidates, teacher pending."""
from importlib import import_module
from copy import deepcopy
import sympy as s
from active_difficulty import require

# Predecessor, original marks, new marks. Allocation is justified by assessable stages,
# not by making marks monotonic. Explicit authorisations are checked by the resolver.
REGISTRY = {
 ('polar-geometry',3):('ay',2,4),
 ('argand-displacement',4):('ay',3,5),
 ('cartesian-sums',4):('aw',2,4),
 ('cross-product',4):('bf',3,5),
 ('det-area',4):('bd',2,4),
 ('fixed-invariant',4):('bc',3,5),
 ('invariant-lines',4):('bc',3,5),
 ('inverse-three',4):('bd',4,6),
 ('line-line-distance',4):('bh',3,5),
 ('plane-intersection-direction',4):('bh',3,5),
 ('point-line',4):('bh',2,4),
 ('symmetric-parameter',4):('au',3,5),
 ('system-consistency',4):('be',2,5),
 ('basis-images',5):('bc',3,5),
 ('exact-radians',5):('ay',3,5),
 ('line-line-distance',5):('bh',3,5),
 ('locus-intersection',5):('az',2,5),
 ('plane-cartesian',5):('bg',3,6),
 ('plane-intersection-direction',5):('bh',3,5),
 ('point-line',5):('bh',2,5),
 ('polar-quotients',5):('az',3,5),
 ('unit-vector',5):('bf',3,5),
 ('vector-components',5):('bf',3,5),
 ('vector-line-equation',5):('bg',3,5),
 ('verify-roots',5):('ax',3,5),
 ('argument-range',6):('ad',4,6),
 ('complex-division',6):('ad',5,7),
 ('conjugate-product',5):('aw',4,5),
 ('related-solids',6):('bh',4,7),
 ('solve-cubic',6):('ax',4,7),
 ('solve-quartic',6):('ax',4,8),
 ('vector-plane',6):('bg',5,7),
}
TARGETS={k:v[0] for k,v in REGISTRY.items()}
# The parallel closest-pair family and two-circle reconstruction already add genuine
# inverse reasoning. Retain their mathematical content and separate their credits.
NEW_DEMAND={('argand-displacement',4),('cartesian-sums',4),('invariant-lines',4),
 ('symmetric-parameter',4),('system-consistency',4),('exact-radians',5),
 ('locus-intersection',5),('plane-cartesian',5),('plane-intersection-direction',5),
 ('polar-quotients',5),('unit-vector',5),('vector-components',5),('vector-line-equation',5)}

# Each string is an independently creditable stage. These are original provisional
# rubrics, not board schemes. M/A/R retain their usual editorial meanings.
CRITERIA={
 ('polar-geometry',3):[('M','Apply the modulus and exact trigonometric values to obtain Cartesian components.'),('A','Give both exact Cartesian complex numbers.'),('A','Give the correct smaller angular separation.'),('R','Identify and justify reflection in the real axis.')],
 ('argand-displacement',4):[('M','Use equal directed sides to construct the fourth vertex.'),('A','Give the fourth vertex and origin-to-vertex diagonal.'),('A','Give the other directed diagonal with its correct sign.'),('M','Calculate the midpoint of each diagonal from its endpoints.'),('R','Show the midpoints agree, explaining the bisection property.')],
 ('cartesian-sums',4):[('M','Expand the nested difference and isolate the unknown.'),('A','Give the exact first complex number.'),('A','Give the exact complementary complex number.'),('R','Verify both the specified sum and directed difference, and justify uniqueness.')],
 ('cross-product',4):[('M','Use the ordered cross-product component formula or determinant.'),('A','Give the correct ordered cross product.'),('R','Verify its dot products with both original vectors vanish.'),('M','Use half the magnitude for the triangle area.'),('A','Give the exact area.')],
 ('det-area',4):[('M','Compose in the specified order.'),('A','Give the correct composition matrix.'),('A','Give the image area using the absolute determinant.'),('R','Use the signed determinant to justify the orientation conclusion.')],
 ('fixed-invariant',4):[('M','Relate original and image coordinates under the given matrix.'),('A','Give all three image equations.'),('R','Justify the pointwise fixed horizontal axis.'),('R','Justify noninvariance of the other horizontal line.'),('R','Show the vertical line maps onto itself but is not pointwise fixed.')],
 ('invariant-lines',4):[('M','Relate original and image coordinates under the matrix.'),('A','Give the image of the specified affine line.'),('M','Derive the conditions on a general nonvertical line to be invariant.'),('R','Analyse vertical lines separately and exclude other intercepts or slopes.'),('A','Give the complete invariant affine-line set.')],
 ('inverse-three',4):[('M','Begin a valid inverse method.'),('M','Complete elimination or an equivalent adjugate calculation.'),('A','Give the exact complete inverse.'),('M','Apply the inverse to the supplied right-hand side.'),('A','Give the solution vector.'),('R','Verify the solution in the original system.')],
 ('line-line-distance',4):[('M','Write the squared separation in the two independent line parameters.'),('R','Use nonnegative squares or equivalent orthogonality to establish the global minimum.'),('A','Give both unique parameter values.'),('A','Give both closest points.'),('A','Give the exact minimum distance.')],
 ('plane-intersection-direction',4):[('M','Use cross products or equivalent orthogonality equations to find normals.'),('A','Give a valid nonzero normal for each plane.'),('M','Find a vector perpendicular to both normals.'),('A','Give a valid nonzero intersection direction.'),('R','Justify that the nonparallel normals give a line through the common origin.')],
 ('point-line',4):[('M','Set up the required scalar-product perpendicularity equation.'),('A','Give the foot of the perpendicular.'),('M','Calculate the magnitude of the displacement from the point to the foot.'),('A','Give the correct exact distance.')],
 ('symmetric-parameter',4):[('M','Use sum and product of roots to express the reciprocal sum, retaining the nonzero product restriction.'),('M','Factor the resulting parameter condition into its two branches.'),('A','Give both exact admissible parameter values.'),('M','Use the discriminant for each branch.'),('R','Classify the roots for each value and justify completeness.')],
 ('system-consistency',4):[('M','Eliminate using the first two equations to obtain the scalar constraint.'),('R','Identify the inconsistent case at the singular parameter.'),('A','Give the unique common point in the regular case.'),('A','Give the corrected right-hand side for a common line at the singular parameter.'),('R','Give the full one-parameter solution family and justify that it is complete.')],
 ('basis-images',5):[('R','Establish that the two input vectors are independent.'),('M','Set up and solve the matrix equation relating the input and image columns.'),('A','Give the correct transformation matrix.'),('M','Apply the recovered matrix to the additional input.'),('A','Give the exact predicted image.')],
 ('exact-radians',5):[('M','Use the exact reference angle for the given sine value.'),('R','Select the appropriate quadrant using the strict cosine inequality.'),('M','Enumerate the compatible doubled angles across the full doubled interval.'),('A','Give both exact angles in the original interval.'),('R','Prove completeness using the periodicity and interval endpoints.')],
 ('line-line-distance',5):[('M','Write the squared separation of the parallel lines.'),('R','Prove the minimum occurs precisely when their free coordinates agree.'),('M','Form the equation in the unknown offset.'),('A','Give both exact offset values.'),('R','Describe the entire family of closest pairs for each offset.')],
 ('locus-intersection',5):[('M','Parametrise the ray from its specified base point with strictly positive parameter.'),('M','Substitute into the circle to form the quadratic.'),('A','Give the two exact parameter roots.'),('R','Verify both parameters are positive and distinct, excluding other intersections.'),('A','Give the two Cartesian complex numbers.')],
 ('plane-cartesian',5):[('M','Use both point equations and eliminate to determine the fixed coefficients.'),('A','Give the correct k and D.'),('M','Use the distance formula to derive the equation for the remaining normal component.'),('A','Give both admissible h values.'),('A','Give both Cartesian equations and their z-axis intersections.'),('R','Justify completeness and that the planes are distinct.')],
 ('plane-intersection-direction',5):[('M','Use the direction to form an orthogonality equation for the second normal.'),('M','Use the supplied additional point to form the other equation.'),('A','Give both recovered coefficients.'),('A','Give the cross product or a nonzero proportional direction.'),('R','Verify the direction belongs to both planes and the normals are independent, establishing uniqueness.')],
 ('point-line',5):[('M','Determine the perpendicular foot independently of the unknown coordinate.'),('A','Give the foot.'),('M','Form the equation using the squared distance.'),('A','Give both real values of the unknown coordinate.'),('R','Justify that both satisfy the original distance and no others do.')],
 ('polar-quotients',5):[('M','Use multiplication and division of the known nonzero polar quotients to reconstruct the two unknown numbers.'),('A','Give the first reconstructed number in principal polar form.'),('A','Give the second reconstructed number in principal polar form.'),('A','Give their quotient in principal polar form.'),('R','Verify the constraints and justify uniqueness by invertibility.')],
 ('unit-vector',5):[('M','Express a parallel vector as a real scalar multiple of the unit direction.'),('M','Use the absolute component constraint to obtain both scalar values.'),('A','Give both original vectors.'),('A','Give their common magnitude.'),('R','Explain why the nonzero given component excludes other solutions.')],
 ('vector-components',5):[('M','Use the given component difference to eliminate one unknown.'),('M','Use the squared magnitude to form a quadratic in the other component.'),('A','Give both exact pairs of unknown components.'),('A','Give the two vectors.'),('R','Verify both constraints and show the quadratic exhausts the possibilities.')],
 ('vector-line-equation',5):[('M','Use the known direction component and the given point to determine the line parameter.'),('M','Use the other two coordinates to recover both missing direction components.'),('A','Give the complete line equation.'),('A','Give its specified plane intersection.'),('R','Verify the given point and justify uniqueness of both the recovered direction and intersection.')],
 ('verify-roots',5):[('M','Substitute the supplied root into the quartic.'),('A','Give the exact constant.'),('M','Recover the complete factorisation.'),('A','Give the corrected root list with multiplicities.'),('R','Justify the multiplicities from the distinct, disjoint factors.')],
 ('argument-range',6):[('M','Identify component zeros and the excluded origin.'),('R','Justify the negative-real quadrant branch.'),('A','Give the principal arguments on the positive-real branches, including the axis.'),('M','Use the common tangent to obtain the candidate parameter.'),('A','Give the solution of the first angle equation.'),('R','Reject the opposite quadrant and prove there is no second-angle solution.')],
 ('complex-division',6):[('M','Cross-multiply and equate components, retaining the nonzero denominator.'),('M','Use the determinant to separate regular and singular parameters.'),('A','Give both regular-case formulas.'),('R','Give the exact regular admissibility condition.'),('R','Classify the positive singular parameter and its nonzero solution family.'),('R','Classify the negative singular parameter and its nonzero solution family.'),('R','Exclude inconsistent and zero-denominator cases and prove completeness.')],
 ('conjugate-product',5):[('M','Translate both norm-square constraints into real component equations.'),('M','Eliminate the common squared terms to recover the real component.'),('A','Give both possible imaginary components.'),('A','Give the two exact complex solutions.'),('R','Verify both original constraints and prove completeness.')],
 ('related-solids',6):[('M','Use multilinearity to derive the product of the three scale factors.'),('M','Complete the square or otherwise establish the upper bound.'),('A','Give the maximum and the unique attaining value.'),('M','Derive the general quadratic roots in terms of the prescribed ratio.'),('R','Classify when two distinct admissible interior roots exist.'),('R','Distinguish the zero-volume endpoints and the repeated maximum case.'),('R','Exclude ratios outside the attainable interval and prove completeness.')],
 ('solve-cubic',6):[('M','Remove the given linear factor by exact division.'),('M','Solve the parameter-dependent quadratic retaining both branches.'),('A','Give the exact root branches.'),('R','Classify the negative and zero parameter cases with multiplicity.'),('M','Derive the collision condition with the known root.'),('A','Give the exceptional value and corresponding roots and multiplicities.'),('R','Classify the remaining positive case and prove completeness.')],
 ('solve-quartic',6):[('M','Divide by the given factor.'),('A','Give the remaining parameter-dependent quadratic.'),('M','Solve both quadratic factors over the complex numbers.'),('A','Give both fixed roots and both variable root branches.'),('R','Classify the zero parameter case and double real root.'),('M','Use substitution into the other factor to derive the common-root condition.'),('R','Classify the common-root case and both double roots.'),('R','Exclude other repeated roots and classify the remaining positive and negative cases.')],
 ('vector-plane',6):[('R','Establish that each possible plane passes through the origin and contains the given line direction.'),('M','Form the determinant of the two remaining components.'),('R','Explain why a nonzero determinant precludes a common plane.'),('A','Give the full family when both points are zero.'),('M','Solve the determinant-zero condition outside the origin.'),('A','Give the unique plane equations on both nonzero branches.'),('R','Prove the rank cases exhaust all real parameters.')],
}


def tex(x):return '$'+s.latex(x)+'$'
def mf(m):return {'matrix':[[str(m[i,j]) for j in range(m.cols)] for i in range(m.rows)]}
def cis(r,a):return f'{tex(r)} (cos({tex(a)}) + i sin({tex(a)}))'
def norm_angle(a):return s.simplify(a-2*s.pi*s.ceiling((a-s.pi)/(2*s.pi)))

def revise(path,tier,v):
    key=path,tier
    require(type(tier) is int and type(v) is int and v in (1,2,3) and key in TARGETS,'Unknown BK target')
    predecessor=import_module('difficulty_revision_'+TARGETS[key])
    p=deepcopy(predecessor.revise(path,tier,v))
    require(sum(x['marks'] for x in p['rubric'])==REGISTRY[key][1],'Predecessor marks mismatch')
    require(len(CRITERIA[key])==REGISTRY[key][2],'BK allocation mismatch')
    p['rubric']=[{'type':t,'marks':1,'criterion':c + (
        ' Accept equivalent valid methods respecting explicit restrictions; retain independently demonstrated method credit after arithmetic slips.' if t=='M' else
        ' Require the specified correct result.' if t=='A' else ' Accept equivalent valid reasoning supported by the stated constraints.')}
        for t,c in CRITERIA[key]]
    q,a,w,f=p['question_latex'],p['final_answer_latex'],p['worked_solution_latex'],p['facts']
    if key==('argand-displacement',4):
        mid=s.sympify(f[0])/2
        q+=' Calculate the midpoint of each diagonal and show that the two diagonals bisect one another.'
        a+=' Both midpoints are '+tex(mid)+'.'
        w+=['The midpoint of OC is (0+C)/2, and that of AB is (A+B)/2. Since C=A+B, both equal '+tex(mid)+'.']
        f += [str(mid)]
    elif key==('cartesian-sums',4):
        u=s.sympify(f[0]); W=3*v+5-(v+1)*s.I; b=W-u
        q+=' Let b=w-u, where w is the supplied constant inside the bracket. Give b, verify that u+b=w and that u-b equals the supplied right-hand side, and justify uniqueness.'
        a+='; b='+tex(b)+'.'
        w+=['The complementary number is '+tex(W)+'-u='+tex(b)+'. Their sum is '+tex(W)+' and their directed difference is '+tex(u-b)+'. The equation 2u=W+(u-b) fixes u uniquely, so b is unique.']
        f += [str(b)]
    elif key==('invariant-lines',4):
        m=v+1;n=v+3
        q+=f' Classify every affine line mapped onto itself by this matrix, including vertical lines. Prove completeness.'
        a+=' The only invariant affine lines are x=0 and y=0.'
        w += [f'For a nonvertical line y=ax+b, the image is Y=({n}/{m})aX+{n}b. Equality of lines requires a=({n}/{m})a and b={n}b, so a=b=0.',f'A vertical line x=c becomes X={m}c, invariant only if c=0. Both axes map onto themselves because both scale factors are nonzero.']
        f+=['x=0','y=0']
    elif key==('symmetric-parameter',4):
        A=v+1;B=2*v+5;k=s.Symbol('k'); vals=[-s.Integer(A),s.Rational(1,B)]; disc=[s.expand((k+A)**2-4*B*k).subs(k,x) for x in vals]
        q=f'The roots alpha and beta of x^2-(k+{A})x+{B}k=0 are both nonzero, and their sum equals the sum of their reciprocals. Determine every real k and classify the roots for each value. Prove completeness without finding the roots.'
        labels=['two distinct real roots' if x>0 else 'a repeated real root' if x==0 else 'a non-real conjugate pair' for x in disc]
        a='; '.join(f'k={tex(x)}: {l}' for x,l in zip(vals,labels))+'.'
        w=[f'Vieta gives S=k+{A}, P={B}k. Since both roots are nonzero, k cannot be zero. The reciprocal sum is S/P.',f'Equality S=S/P implies (k+{A})({B}k-1)=0, so k={tex(vals[0])} or {tex(vals[1])}. Both are nonzero.',f'The respective discriminants are {tex(disc[0])} and {tex(disc[1])}; they give {labels[0]} and {labels[1]}. The factorisation is equivalent under k nonzero, proving completeness.']
        f=[*[str(x) for x in vals],*[str(x) for x in disc]]
    elif key==('system-consistency',4):
        A=v+1;B=v+3
        q+=f' For k=1, replace the right-hand side of the third equation by c. Find the unique c for which a common line exists, and give the complete line.'
        a+=f' For k=1, c={A+B}; common line (x,y,z)=({A}-t,t,{B}-t), for every real t.'
        w += [f'With the third right-hand side c, elimination gives (k-1)z=c-{A+B}. At k=1 consistency requires c={A+B}, and then the third equation is the sum of the first two. Set y=t to obtain x={A}-t and z={B}-t; all real t satisfy all three equations.']
        f += [str(A+B),[str(A),str(B)]]
    elif key==('exact-radians',5):
        alpha=[s.pi/6,s.pi/4,s.pi/3][v-1]; b=s.pi-alpha; roots=[b/2,b/2+s.pi]
        q=f'Find every theta in [0,2pi) satisfying sin(2theta)={tex(s.sin(alpha))} and cos(2theta)<0. Give exact radians and prove completeness.'
        a='theta='+', '.join(tex(x) for x in roots)+'.'
        w=[f'The exact reference angle is {tex(alpha)}. In each full revolution the positive sine and negative cosine select quadrant II, angle {tex(b)}.',f'As theta ranges over [0,2pi), 2theta ranges over [0,4pi). The only doubled angles are {tex(b)} and {tex(b+2*s.pi)}.',f'Dividing by two gives {tex(roots[0])} and {tex(roots[1])}. Both lie in the requested interval, and the two quadrant-II positions exhaust the doubled interval.']
        f=[str(x) for x in roots]
    elif key==('locus-intersection',5):
        C=v+1;R=v+3;B=C-R-1;D=s.sqrt(4*R**2-(R+1)**2);rr=[s.simplify((s.sqrt(3)*(R+1)+sign*D)/2) for sign in (-1,1)];zz=[s.expand(B+t*(s.sqrt(3)+s.I)/2) for t in rr]
        q=f'Find every complex number z satisfying |z-{C}|={R} and arg(z-({B}))=pi/6. Give the answers in exact Cartesian form and prove completeness, including the ray restriction.'
        a='; '.join(tex(z) for z in zz)+'.'
        w=[f'The argument specifies z={B}+t(cos(pi/6)+i sin(pi/6)), with t>0. Substituting in the circle gives t^2-{tex(s.sqrt(3)*(R+1))}t+{2*R+1}=0.',f'The discriminant is {4*R**2-(R+1)**2}>0, so the two distinct real parameter roots are {tex(rr[0])} and {tex(rr[1])}. Their sum and product are positive, so both are positive.',f'Substitute each parameter into the ray: the resulting points are {tex(zz[0])} and {tex(zz[1])}. A quadratic has no other roots; both positive parameters satisfy the original argument condition.']
        f=[*[str(t) for t in rr],*[str(z) for z in zz]]
    elif key==('plane-cartesian',5):
        K=v+1;D=2*v+3;H=v+2;dist=s.Rational(D,1)/s.sqrt(K*K+1+H*H)
        q=f'A plane has equation kx+y+hz=D, contains (1,{v+2},0) and (2,1,0), and has perpendicular distance {tex(dist)} from the origin. Find all real k,h,D, give each plane equation and its z-axis intersection, and prove completeness.'
        a=f'k={K}, D={D}, h=+/-{H}; planes {K}x+y+{H}z={D} and {K}x+y-{H}z={D}; z-axis intersections (0,0,{tex(s.Rational(D,H))}) and (0,0,{tex(-s.Rational(D,H))}).'
        w=[f'The two point equations are k+{v+2}=D and 2k+1=D, hence k={K}, D={D}.',f'Distance from the origin is {D}/sqrt({K*K+1}+h^2). Equate to {tex(dist)} and square positive quantities to obtain h^2={H*H}.',f'The two distinct planes use h={H} and h=-{H}; both have the required distance. On the z-axis hz={D}, yielding the two intersections {tex(s.Rational(D,H))} and {tex(-s.Rational(D,H))}. No other h satisfies the squared equation.']
        f=[str(K),str(D),str(-H),str(H),str(-s.Rational(D,H)),str(s.Rational(D,H))]
    elif key==('plane-intersection-direction',5):
        K=v+3;H=v+2;A=v+1;d=s.Matrix([A*H,-H,1-A*K]);P=s.Matrix([0,-H,1]);
        q=f'The planes x+{A}y=0 and kx+y+hz=0 have intersection direction {tex(d)}. The second plane also contains the point {tex(P)}. Recover k and h and verify the stated direction and uniqueness.'
        a=f'k={K}, h={H}; intersection direction {tex(d)}.'
        w=[f'Substitution of the additional point gives -{H}+h=0, hence h={H}.',f'Orthogonality of the specified direction to the second normal gives {A*H}k-{H}+{1-A*K}h=0, so k={K}.',f'The cross product of (1,{A},0) and ({K},1,{H}) is {tex(d)}, nonzero. The direction is perpendicular to both normals. The two recovery equations fix h and then k uniquely.']
        f=[str(K),str(H),mf(d)]
    elif key==('polar-quotients',5):
        R=v+1;T=v+3;U=v+2;A=-3*s.pi/4;B=s.pi/3;C=-s.pi/2
        zR=R*T;zA=norm_angle(A+B);uR=s.Rational(R,U);uA=norm_angle(A-C);qR=s.Rational(zR,uR);qA=norm_angle(zA-uA)
        q=f'Given w={cis(R,A)}, nonzero numbers z and u satisfy |z/w|={T}, arg(z/w)=pi/3, |w/u|={U}, arg(w/u)=-pi/2. Recover z, u and z/u in polar form with principal arguments. Verify the conditions and prove uniqueness.'
        a=f'z={cis(zR,zA)}; u={cis(uR,uA)}; z/u={cis(qR,qA)}.'
        w=[f'Multiply w by the specified quotient z/w to obtain z, modulus {zR} and principal argument {tex(zA)}.',f'Divide w by the specified quotient w/u to obtain u, modulus {tex(uR)} and principal argument {tex(uA)}.',f'The quotient z/u=(z/w)(w/u) has modulus {tex(qR)} and principal argument {tex(qA)}. Subtracting arguments and dividing moduli in the reconstructed numbers recovers both given quotients. Nonzero w and both nonzero quotients fix z and u uniquely.']
        f=[str(zR),str(zA),str(uR),str(uA),str(qR),str(qA)]
    elif key==('unit-vector',5):
        V=s.Matrix([v+1,v+2,v+3]);N=s.sqrt(V.dot(V));D=2*(v+3);W=2*V
        q=f'A nonzero vector is parallel to the unit vector {tex(V/N)} and its third component has absolute value {D}. Recover every possible vector and its magnitude, proving completeness. Parallel here includes the opposite direction.'
        a=f'Vectors {tex(W)} and {tex(-W)}; common magnitude {tex(2*N)}.'
        w=[f'Every vector parallel to the unit direction is a real multiple lambda of it. The magnitude of its third component is |lambda|({v+3})/{tex(N)}.',f'The constraint forces |lambda|={tex(2*N)}, so the two vectors are {tex(W)} and {tex(-W)}.',f'Both have third-component absolute value {D} and common magnitude {tex(2*N)}. Since the direction has nonzero third component, there are no other scalar values.']
        f=[mf(W),mf(-W),str(2*N)]
    elif key==('vector-components',5):
        X=v+1;J=v+3;K=2*v+5;D=K-J;N=X*X+J*J+K*K;V=s.Matrix([X,J,K]);W=s.Matrix([X,-K,-J])
        q=f'A vector has i-component {X}, squared magnitude {N}, and its k-component exceeds its j-component by {D}. Recover all possible vectors and prove completeness.'
        a=tex(V)+' or '+tex(W)+'.'
        w=[f'Let the j-component be y, so the k-component is y+{D}. The squared magnitude condition is {X*X}+y^2+(y+{D})^2={N}.',f'The quadratic factors as 2(y-{J})(y+{K})=0. Thus y={J} or y=-{K}, with corresponding k-components {K} and -{J}.',f'The vectors are {tex(V)} and {tex(W)}. Both satisfy the magnitude and component-difference constraints; the quadratic exhausts the real solutions.']
        f=[mf(V),mf(W)]
    elif key==('vector-line-equation',5):
        P=s.Matrix([1,0,2]);D=s.Matrix([v+1,v+3,v+4]);W=P+2*D;I=P+3*D;C=sum(I)
        q=f'A line r={tex(P)}+t(k,h,{D[2]}) passes through {tex(W)}. Recover k and h, give the full line equation and its intersection with x+y+z={C}. Prove the recovery and intersection are unique.'
        a=f'k={D[0]}, h={D[1]}; r={tex(P)}+t{tex(D)}; intersection {tex(I)}.'
        w=[f'The third coordinate fixes t=({W[2]}-2)/{D[2]}=2. The other coordinates give k=({W[0]}-1)/2={D[0]} and h={W[1]}/2={D[1]}.',f'The recovered line passes through the given point at t=2. Its coordinate sum is 3+{sum(D)}t. Set equal to {C}; t=3 and the intersection is {tex(I)}.',f'The third direction component and the sum of direction components are both nonzero, so both recovery and intersection are unique.']
        f=[str(D[0]),str(D[1]),mf(D),mf(I)]
    elif key==('point-line',5):
        h=v+1
        w += [f'The foot is H=({h},{h},0) for both signs of k. Both signs have the required squared distance, and the equation in k^2 admits no other real values.']
    p['question_latex'],p['final_answer_latex'],p['worked_solution_latex'],p['facts']=q,a,w,f
    if key in NEW_DEMAND:
        p['demand_rationale']='BK successor: '+ ' '.join(c for _,c in CRITERIA[key] if _ in ('M','R'))
        p['progressive_hints']=[CRITERIA[key][0][1],next(c for t,c in CRITERIA[key][1:] if t in ('M','R'))]
        p['likely_mistake']='Stopping after a partial reconstruction or failing to check the requested constraints and all admissible branches.'
    return p
