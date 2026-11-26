"""FM-16C: original six-stage editorial pathways with explicit case analysis."""
import sympy as s
from calibration_bank import LEVELS,L,seq
M=s.Matrix
k,h,x,y,t,u,c=s.symbols('k h x y t u c',real=True)
PATHS={
 'det-three':'MAT.determinant.three',
 'fixed-points':'MAT.invariants.fixed-points',
 'plane-plane-angle':'VEC.scalar-product.plane-plane',
 'line-line-distance':'VEC.distance.line-line',
}
MISTAKES={
 'det-three':'Omitting the alternating cofactor signs, or dividing by a parameter before checking whether it is zero.',
 'fixed-points':'Confusing a fixed point with a point on a setwise invariant line; neglecting a zero coefficient case.',
 'plane-plane-angle':'Using a signed dot product for the smaller angle between unoriented planes, or treating the angle between planes as the complement of the angle between normals.',
 'line-line-distance':'Using distance between arbitrary points, or dividing by the cross-product magnitude when the directions are parallel.',
}
RATIONALES={
 'det-three':['Calculate a minor needed in later expansion.','Diagnose the row-exchange sign rule.','Expand a fully specified determinant with cofactors.','Connect a row operation with determinant evaluation and singularity.','Reverse a determinant calculation to recover a parameter.','Factor a symbolic determinant, identify all roots, and prove ranks in every case.'],
 'fixed-points':['Solve a linear equation before using matrix notation.','Distinguish setwise invariance from pointwise fixing with a counterexample.','Solve the two fixed-point equations.','Connect an image calculation with the fixed-point locus and verify both.','Reconstruct a matrix parameter from a prescribed fixed point and describe all fixed points.','Classify the full fixed-point set over two real parameters, including overlapping cases.'],
 'plane-plane-angle':['Recover an exact acute angle from a ratio.','Explain why reversing a normal must preserve the smaller plane angle.','Calculate the acute angle from specified normals.','Construct a plane from three points before comparing normals.','Recover all parameter values satisfying a prescribed angle.','Solve a two-branch inverse-angle problem and prove the endpoint counts.'],
 'line-line-distance':['Calculate a displacement length.','Diagnose the difference between arbitrary point separation and shortest distance.','Apply the skew-line distance formula to specified lines.','Find the actual closest points by solving orthogonality constraints.','Reconstruct the missing offset for a prescribed parallel-line distance.','Classify parallel, intersecting and skew lines and prove distance and minimiser multiplicity.'],
}

def make(path,l,v):
 if path not in PATHS or l not in LEVELS or v not in (1,2,3):raise ValueError('Unknown pathway cell')
 a=v+1;b=a+2
 if path=='det-three':
  A=M([[a,1,0],[1,b,1],[0,1,2]]);d=2*a*b-a-2
  if l==1:
   q=f'Calculate the determinant of {L(M([[a,1],[1,b]]))}.';f=[a*b-1];ans=L(f[0]);steps=[f'Multiply the main diagonal and subtract the other: ${a}\\cdot {b}-1={a*b-1}$.'];hints=['Use ad-bc.','The off-diagonal product is 1.']
  elif l==2:
   q=f'A 3 by 3 matrix has determinant {d}. Its first and third rows are exchanged. A learner says its determinant stays {d}. Correct the claim and explain.';f=[-d];ans=L(-d);steps=['A determinant is alternating in its rows. Exchanging two rows reverses its sign.',f'Therefore the determinant is ${-d}$.'];hints=['Recall the effect of a single row swap.','Do not take an absolute value.']
  elif l==3:
   q=f'Using cofactor expansion along the first row, calculate the determinant of {L(A)}.';f=[d];ans=L(d);steps=[f'The signed terms are ${a}(2\\cdot {b}-1)-1(2\\cdot1-0)+0$.',f'This is ${a}\\cdot {2*b-1}-2={d}$.'];hints=['The first-row signs are +, -, +.','The final term is zero.']
  elif l==4:
   B=M([[a,1,0],[1,b,1],[a,2,2]])
   q=f'For {L(B)}, use a determinant-preserving row operation to recover a row with first entry zero. Evaluate the determinant and decide whether the matrix is invertible.';f=[d,True];ans=f'{L(d)}; invertible.';steps=['Subtract row 1 from row 3. Adding a multiple of another row preserves determinant.',f'The resulting matrix is {L(A)}.',f'Expanding gives ${a}(2\\cdot {b}-1)-2={d}$.', 'The determinant is nonzero, so the matrix is invertible.'];hints=['Try row 3 minus row 1.','Then expand the simplified matrix.']
  elif l==5:
   B=M([[a,1,0],[1,b,1],[0,1,k]]);root=s.Rational(a,a*b-1)
   q=f'Find every real value of $k$ for which {L(B)} has determinant zero. Verify that its rank is exactly two.';f=[root,2];ans=f'$k={s.latex(root)}$; rank 2.';steps=[f'First-row expansion gives $k({a*b-1})-{a}$.',f'The coefficient is nonzero, so the only root is $k={s.latex(root)}$.',f'The leading 2 by 2 minor is ${a*b-1}\\ne0$, so rank is at least two.', 'Zero determinant forces rank below three; hence rank two.'];hints=['Keep k symbolic in the minor.','Use a nonzero 2 by 2 minor to bound rank.']
  else:
   B=M([[k,a,0],[a,k,a],[0,a,k]]);roots=[-a*s.sqrt(2),s.S.Zero,a*s.sqrt(2)]
   q=f'For every real $k$, classify the rank of {L(B)}. Derive and factor its determinant; prove that no singular case has rank below two.';f=[k*(k*k-2*a*a),*roots,2,3];ans=f'$\\det B=k(k^2-{2*a*a})$; rank 2 at {seq(*roots)}; rank 3 otherwise.';steps=[f'First-row expansion gives $k(k^2-{a*a})-{a*a}k=k(k^2-{2*a*a})$.',f'The determinant vanishes only at $k=0$ or $k=\\pm {a}\\sqrt2$.',f'The minor using rows 1,2 and columns 2,3 is $\\begin{{vmatrix}}{a}&0\\\\k&{a}\\end{{vmatrix}}={a*a}$ for all k.', 'That minor is never zero, so the rank is at least two. At a determinant root the rank is two; outside these roots it is three.'];hints=['Expand the sparse first row and factor k.','Look at rows 1,2 and columns 2,3 for a parameter-independent minor.']
 elif path=='fixed-points':
  A=M([[1,a],[0,b]])
  if l==1:
   q=f'Solve ${a}y+{b}={b}$ for y.';f=[0];ans='$y=0$.';steps=[f'Subtract {b} to obtain ${a}y=0$. Since {a} is nonzero, y=0.'];hints=['Subtract the constant.','Divide by the nonzero coefficient.']
  elif l==2:
   A=s.diag(a,1);P=M([1,0]);Q=A*P
   q=f'Under {L(A)}, the x-axis maps onto itself. A learner concludes every point on it is fixed. Refute the conclusion using (1,0) and identify the fixed points on this axis.';f=[Q,0];ans=f'Image of (1,0): {L(Q)}; only the origin is fixed on the x-axis.';steps=[f'The image of (1,0) is $({a},0)$, different from (1,0).','On the x-axis fixed points satisfy ax=x with the displayed a greater than 1, so x=0.'];hints=['Apply the matrix to (1,0).','Solve the equality of original and image coordinates.']
  elif l==3:
   q=f'Find the complete fixed-point set of {L(A)}.';f=[M([1,0])];ans='All $(x,0)$ for real x.';steps=[f'Equating the first coordinates gives ${a}y=0$.',f'The second gives $({b}-1)y=0$, consistent with y=0.', 'No condition remains on x, so the whole x-axis, and only that axis, is fixed pointwise.'];hints=['Solve (A-I)r=0.','Keep any free variable.']
  elif l==4:
   B=M([[1+a,-a],[a,1-a]]);P=M([2,1]);Q=M([2+a,1+a]);
   q=f'Under {L(B)}, find the image of (2,1), derive the fixed-point locus, and verify that the displacement from (2,1) to its image is parallel to that locus.';f=[Q,M([1,1]),M([a,a])];ans=f'Image {L(Q)}; fixed line $y=x$; displacement {L(M([a,a]))}.';steps=[f'Matrix multiplication gives {L(Q)}.',f'The fixed-point equations both reduce to ${a}(x-y)=0$, hence x=y.',f'The displacement is {L(M([a,a]))}, a multiple of (1,1), the direction of the fixed line.'];hints=['Multiply first, then solve (B-I)r=0.','Subtract the original point from its image.']
  elif l==5:
   B=M([[k,a],[0,1]]);j=1-b
   q=f'Choose real $k$ so that point $({a},{b})$ is fixed by {L(B)}. Then determine and justify the complete fixed-point set for that k.';f=[j,M([a,b])];ans=f'$k={j}$; all multiples of $({a},{b})$.';steps=[f'The first-coordinate equality is ${a}k+{a*b}={a}$, so $k={j}$.','The second coordinate is unchanged automatically.',f'For arbitrary (x,y) the remaining equation is $-{b}x+{a}y=0$.',f'This describes exactly the line spanned by $({a},{b})$.'];hints=['Use the prescribed point to recover k.','Now solve the fixed-point equation for arbitrary coordinates.']
  else:
   B=M([[k,a],[0,h]]);f=[M([1,0]),M([-a,k-1]),0,1]
   q=f'For all real pairs $(k,h)$ classify the complete fixed-point set of {L(B)}. Give a direction when it is a line; prove the plane is never fixed pointwise.';ans=f'$h\\ne1,k\\ne1$: origin only; $h\\ne1,k=1$: x-axis; $h=1,k=1$: x-axis; $h=1,k\\ne1$: span of $(-{a},k-1)$. Never the entire plane.';steps=[f'The fixed equations are $(k-1)x+{a}y=0$ and $(h-1)y=0$.','If h is not 1, y=0; x is free exactly when k=1, and otherwise x=0.',f'If h=1 and k=1, ${a}y=0$ again gives the x-axis.',f'If h=1 and k is not 1, the first equation gives exactly the line spanned by $(-{a},k-1)$.',f'The first equation always has nonzero y coefficient {a}, so it cannot hold for every (x,y). These cases exhaust the real parameter plane.'];hints=['Solve the second fixed-point equation first.','Separate k=1 from k not equal to 1 and retain all free parameters.']
 elif path=='plane-plane-angle':
  if l==1:
   q=f'An acute angle has adjacent side {a} and hypotenuse {2*a}. Find the angle in radians.';f=[s.pi/3];ans=L(f[0]);steps=['The cosine ratio is 1/2.', 'The acute angle is $\\pi/3$.'];hints=['Use adjacent over hypotenuse.','Recall the exact angle with cosine 1/2.']
  elif l==2:
   N=M([a,a*s.sqrt(3),0]);U=M([1,0,0]);theta=s.pi/3
   q=f'Two planes have normals {L(N)} and {L(U)}. A learner reverses the first normal and reports a different smaller angle. Explain why that is wrong and give the smaller angle.';f=[theta];ans=L(theta);steps=['Reversing the normal does not change the plane; the normals are unoriented.',f'The absolute cosine ratio is ${a}/({2*a})=1/2$ for both signs.', 'The smaller angle is $\\pi/3$, not $2\\pi/3$.'];hints=['Changing the sign of the entire plane equation does not change its points.','Use the absolute scalar product.']
  elif l==3:
   q=f'Find the smaller angle between the planes ${a}x+{a}\\sqrt3 y={b}$ and $y={a}$.';f=[s.pi/6];ans=L(f[0]);steps=[f'Take normals $({a},{a}\\sqrt3,0)$ and $(0,1,0)$.','The absolute cosine ratio is $\\sqrt3/2$, so the smaller angle is $\\pi/6$.'];hints=['Read the normal coefficients, not the constant.','Use cosine, not sine.']
  elif l==4:
   q=f'A plane passes through the origin, $({a},0,{a})$ and $(0,{b},0)$. Find its Cartesian equation and the smaller angle it makes with $z={b}$. Verify that all three points lie in the plane.';f=[M([-1,0,1]),s.pi/4];ans='Plane $-x+z=0$; smaller angle $\\pi/4$.';steps=[f'The two directions are $({a},0,{a})$ and $(0,{b},0)$.',f'Their cross product is $(-{a*b},0,{a*b})$, so a normal is (-1,0,1).','The plane through the origin has equation -x+z=0; each supplied point satisfies it.','The normal of z=constant is (0,0,1). The absolute cosine ratio is $1/\\sqrt2$, giving $\\pi/4$.'];hints=['Take the cross product of two independent directions.','Use the normal and the origin to construct the plane.']
  elif l==5:
   j=a/s.sqrt(3)
   q=f'Find every real k such that the smaller angle between planes $kx+{a}y=1$ and $x={b}$ is $\\pi/3$. Check each sign in the original angle equation.';f=[-j,j];ans=seq(*f);steps=[f'The cosine ratio is $|k|/\\sqrt{{k^2+{a*a}}}=1/2$.',f'Squaring gives $3k^2={a*a}$, so $k=\\pm {s.latex(j)}$.','The denominator is positive and the original ratio is nonnegative. Both signs satisfy it exactly.'];hints=['Use normals (k,a,0) and (1,0,0).','Retain both signs and check the original equation.']
  else:
   f=[1,4,2,a,a*a*(1-c)/(1+c),a*a*(1+c)/(1-c)]
   q=f'Let the planes be ${a}x+ky=1$ and ${a}x-ky=2$. For every desired smaller angle $\\theta\\in[0,\\pi/2]$, classify the number of finite real k that produce it, express them in terms of $\\cos\\theta$, and justify all endpoints.';ans=f'With $c=\\cos\\theta$: at $\\theta=0$, k=0 only; for $0<\\theta<\\pi/2$, $k=\\pm {a}\\sqrt{{(1-c)/(1+c)}}$ or $k=\\pm {a}\\sqrt{{(1+c)/(1-c)}}$; at $\\theta=\\pi/2$, $k=\\pm {a}$.';steps=[f'The absolute cosine ratio is $|{a*a}-k^2|/({a*a}+k^2)$. The denominator is always positive.',f'For $0<c<1$, the two signed equations give $k^2={a*a}(1-c)/(1+c)$ and $k^2={a*a}(1+c)/(1-c)$.', 'These are distinct positive values, each with two square roots. All four satisfy the original absolute ratio.',f'At c=1, the first branch gives k=0 and the second signed equation has no solution because {a*a}>0.',f'At c=0, the branches coincide at $k^2={a*a}$, giving two solutions. The cases exhaust the required angular interval.'];hints=['Write the absolute cosine ratio using the normals.','Solve the two signed branches, but do not divide by 1-c at c=1.']
 elif path=='line-line-distance':
  if l==1:
   q=f'Find the distance between points (0,0,0) and $({a},0,{b})$.';f=[s.sqrt(a*a+b*b)];ans=L(f[0]);steps=[f'The displacement is $({a},0,{b})$.',f'Its norm is $\\sqrt{{{a*a}+{b*b}}}={s.latex(f[0])}$.'];hints=['Subtract the position vectors.','Take the Euclidean norm.']
  elif l==2:
   q=f'Lines L and K have equations $(t,0,0)$ and $({a}+u,{b},0)$. A learner uses the two base points to claim the line distance is $\\sqrt{{{a*a}+{b*b}}}$. Explain the error and find the true distance.';f=[b];ans=L(b);steps=['The lines are parallel to the x-axis. Base points need not be nearest points.',f'Choose points with equal x coordinates, for example (0,0,0) and $(0,{b},0)$.',f'Every displacement has y component {b}; its length is at least {b}, achieved by those points.'];hints=['The arbitrary x offset can be removed by moving along a line.','Prove the lower bound using squared length.']
  elif l==3:
   q=f'Find the shortest distance between skew lines $(t,0,0)$ and $({a},u,{b})$ using the scalar triple product.';f=[b];ans=L(b);steps=['The directions are (1,0,0) and (0,1,0), with cross product (0,0,1).',f'The displacement between base points is $({a},0,{b})$.',f'The absolute triple product divided by the cross-product norm is ${b}/1={b}$.'];hints=['Find a vector perpendicular to both directions.','Project the base-point displacement onto that direction.']
  elif l==4:
   P=M([a,a,0]);Q=M([a,a,b]);
   q=f'Find the unique closest pair of points on lines $(t,t,0)$ and $({a},u,{b})$, and their distance. Prove that your pair attains the minimum.';f=[P,Q,b];ans=f'{L(P)} and {L(Q)}; distance {b}.';steps=[f'The squared separation is $(t-{a})^2+(t-u)^2+{b*b}$.',f'The first two terms are nonnegative and vanish simultaneously only at $t=u={a}$.',f'The resulting points are {L(P)} and {L(Q)}, with distance {b}. This proves uniqueness and minimality.'];hints=['Parameterise a point on each line independently.','Minimise the squared distance, not just the dot product with one direction.']
  elif l==5:
   j=s.sqrt(b*b-a*a)
   q=f'Parallel lines $(t,0,0)$ and $(u,{a},k)$ have distance {b}. Determine every real k and describe all closest pairs for each solution.';f=[-j,j,M([0,a,k])];ans=f'$k=\\pm {s.latex(j)}$; closest pairs $(t,0,0)$ and $(t,{a},k)$ for all real t.';steps=[f'The squared separation is $(t-u)^2+{a*a}+k^2$, minimised exactly when t=u.',f'The target requires $k^2={b*b}-{a*a}={b*b-a*a}>0$.',f'Both signs $k=\\pm {s.latex(j)}$ produce distance {b}. There are infinitely many nearest pairs, one for each t.'];hints=['Remove the displacement parallel to the common direction.','Solve for both signs and preserve the free parameter.']
  else:
   f=[s.sqrt(b*b+h*h),s.Abs(h),a-b/k,-b/k]
   q=f'For all real k,h consider lines $L:(t,0,0)$ and $K:({a}+u,{b}+ku,h)$. Classify them as parallel distinct, intersecting or skew; find their exact distance and all closest parameter pairs, and prove completeness.';ans=f'$k=0$: parallel distinct, distance $\\sqrt{{{b*b}+h^2}}$, all pairs $t={a}+u$. $k\\ne0$: distance $|h|$, unique pair $u=-{b}/k$, $t={a}-{b}/k$; intersecting when h=0, otherwise skew.';steps=[f'The squared separation is $(t-{a}-u)^2+({b}+ku)^2+h^2$.',f'If k=0, the second term is the fixed positive number {b*b}; minimisation requires only $t={a}+u$. The lines are parallel and distinct.',f'If k is nonzero, both variable squares vanish exactly for $u=-{b}/k$ and $t={a}-{b}/k$. The remaining squared distance is $h^2$.','The directions (1,0,0) and (1,k,0) are nonparallel in this case. They intersect exactly if h=0; otherwise they are skew.', 'The two cases cover all real k; the square decomposition proves minimality and specifies every minimising pair.'];hints=['Write the squared separation with two free parameters.','Handle k=0 before solving b+ku=0.']
 else:raise AssertionError(path)
 def encode(w):
  if isinstance(w,bool):return w
  if isinstance(w,s.MatrixBase):return {'matrix':[[str(e) for e in row] for row in w.tolist()]}
  return str(w)
 return dict(path=path,focus_skill=PATHS[path],tier=l,variant=v,assessment_role='prerequisite_bridge' if l==1 else 'concept_diagnostic' if l==2 else 'direct_focus_task',question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,rubric=[dict(marks=1,criterion=p) for p in steps],facts=[encode(e) for e in f],likely_mistake=MISTAKES[path],origin='original',examination_source=None,difficulty_status='editorial_design_teacher_pending',demand_rationale=RATIONALES[path][l-1])
