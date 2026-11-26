"""Original six-stage learning pathways. Editorial demand, not empirical calibration.
Each stage changes the task structure; variants retain it. No CCEA question text.
"""
import sympy as s

PATHS={
 'root-squares':'ALG.roots-coefficients.sum-squares',
 'reciprocal':'ALG.related-quadratic.reciprocal',
 'complex-division':'CPX.arithmetic.divide',
 'locus-intersection':'CPX.loci.intersection',
 'det-area':'MAT.area-scale.area',
 'system-consistency':'MAT.zero-system.parameter',
 'point-line':'VEC.distance.point-line',
 'skew':'VEC.skew.classify',
}
LEVELS={1:('Prerequisite','Recall or use a prerequisite with a supplied representation; not direct mastery evidence.'),2:('Conceptual','Explain a relationship or diagnose an error; not merely execute a calculation.'),3:('Procedure','Carry out the standard method on fully specified data.'),4:('Linked','Connect two methods or representations in a multi-step task.'),5:('Exam-style','Select a method independently and satisfy explicit mathematical constraints; original proposed rubric.'),6:('Challenge','Reconstruct missing information, justify completeness, or prove a general claim with cases.')}
HINTS={
 'root-squares': [('Write the square as two factors.','Collect the two cross terms.'),('Expand the square of a sum.','Subtract twice the product.'),('Compare coefficients after dividing by the leading coefficient.','Use the square-of-sum identity.'),('First find the new root sum and product.','Apply the same identity to the shifted roots.'),('Write the root sum and product in terms of k.','After solving for k, test the discriminant.'),('Recover the square of the root sum from the given data.','Check both signs and reconstruct the monic equations.')],
 'reciprocal':[('Choose a common denominator.','Multiply each numerator by the other denominator.'),('Compare a sum of reciprocals with the reciprocal of a sum.','State why neither denominator can vanish.'),('Find the original sum and product.','Express both new coefficients using their reciprocals.'),('Compute the product after shifting.','Only then apply the reciprocal-root rule.'),('Use the given reciprocal sum to make an equation in k.','Use the reciprocal product to construct the new quadratic.'),('Use the original product to identify the transformed root.','A repeated root corresponds to a zero discriminant.')],
 'complex-division':[('Multiply the two brackets.','Use i squared equals minus one.'),('Identify the conjugate of the denominator.','Check that the conjugate product is real and nonzero.'),('Multiply by the conjugate.','Separate the real and imaginary parts after division.'),('First rationalise the quotient.','Compare its modulus with the ratio of the original moduli.'),('A real quotient has imaginary part zero.','Equate the imaginary numerator to zero.'),('A purely imaginary quotient has real part zero.','The denominator is positive; solve the real numerator condition and check uniqueness.')],
 'locus-intersection':[('Use horizontal and vertical coordinate differences.','Square and add those differences.'),('Interpret modulus as distance.','Compare the distance of the centre with the stated radius.'),('Use a Cartesian equation for the circle.','Substitute the fixed real coordinate and retain both signs.'),('Equal distances define a perpendicular bisector.','Find its intersection with the circle.'),('An argument specifies a ray rather than an entire straight line.','Use the radius as the positive parameter along the ray.'),('Fix the real coordinate in the circle equation.','Classify the sign of the remaining squared imaginary coordinate.')],
 'det-area':[('Use the two perpendicular side lengths.','Multiply them.'),('Write the reflection matrix.','Compare signed determinant and unsigned area.'),('Calculate the determinant.','Use its absolute value as a multiplier.'),('Apply the first matrix before the second.','Use the sign and magnitude of the determinant of the product.'),('Express the area scale as an absolute value.','Solve both signed equations and check orientation.'),('The determinant is quadratic in k.','Separate c=0, 0<c<a, c=a and c>a, noting when branches coincide.')],
 'system-consistency':[('Add the two equations.','Substitute into either equation.'),('Compare the left sides after scaling.','Ask whether the right sides agree.'),('Eliminate x before substituting k.','A zero coefficient may leave a free variable.'),('Subtract the first two equations from the third.','Compare the resulting equation for each k.'),('Eliminate the dependent rows.','Do not divide by k-1 until its zero case is handled.'),('Reduce the third equation to one involving z.','Partition the (k,h) plane by whether the coefficient and constant vanish.')],
 'point-line':[('Square each component.','Add the three squares.'),('Find the displacement from H to P.','Use its scalar product with the direction and Pythagoras.'),('Use the magnitude of the cross product.','Divide by the direction magnitude.'),('Parameterise an arbitrary point on the line.','Set the perpendicularity condition to zero.'),('The projection parameter does not depend on the vertical coordinate.','Use the squared distance equation and keep both signs.'),('Write squared distance as a polynomial in t.','Complete the square, then solve the larger distance equation.')],
 'skew':[('Compare the coordinates of both direction vectors.','Look for a single nonzero multiplier.'),('Check whether the directions are parallel.','Compare the constant z coordinates.'),('Equate corresponding coordinates.','Verify the proposed intersection in all three coordinates.'),('Solve the x and y equations together.','Check whether z is consistent and whether the directions are parallel.'),('The direction vectors do not depend on k.','Determine which k allows all three coordinate equations to hold.'),('Separate parallel and nonparallel directions first.','Within each case use the z-coordinate to decide whether a common point exists.')],
}
x,k,t=s.symbols('x k t',real=True)
I=s.I
M=s.Matrix

def L(z):return '$'+s.latex(z)+'$'
def seq(*v):return '; '.join(L(z) for z in v)
def make(path,level,variant):
 if path not in PATHS or level not in LEVELS or variant not in (1,2,3):raise ValueError('Unknown path, level or variant')
 a=variant+1; b=a+2; S=a+b; P=a*b; R=s.Rational
 if path=='root-squares':
  if level==1:
   q=f'Expand $(x+{a})^2$. Identify the middle term.'; ans=L(s.expand((x+a)**2))+f'; middle term ${2*a}x$'; steps=[f'Multiply $(x+{a})(x+{a})$.',f'The two cross terms sum to ${2*a}x$; the result is {ans}.']; facts=[s.expand((x+a)**2)]
  elif level==2:
   q=f'A learner says $u^2+v^2=(u+v)^2$. Using $u={a},v={b}$, explain the mistake and derive the corrected identity.'; facts=[S*S-2*P]; ans=f'$u^2+v^2=(u+v)^2-2uv$; here {L(facts[0])}.'; steps=[f'The claimed right side is ${S*S}$, but the left side is ${a*a+b*b}$.','Expanding the square gives an additional $2uv$. Subtract this term.']
  elif level==3:
   q=f'The roots of {L(2*x*x-2*S*x+2*P)} $=0$ are $u,v$. Without solving the equation, calculate $u^2+v^2$.'; facts=[S*S-2*P]; ans=L(facts[0]); steps=[f'Comparing coefficients gives $u+v={S}$ and $uv={P}$.',f'Use $(u+v)^2-2uv={S}^2-2({P})={facts[0]}$.']
  elif level==4:
   q=f'The roots $u,v$ of {L(x*x-S*x+P)} $=0$ are shifted to $u+{a}$ and $v+{a}$. Find the sum of squares of the shifted roots without finding $u,v$.'; facts=[(a+a)**2+(b+a)**2]; ans=L(facts[0]); steps=[f'The shifted sum is ${S+2*a}$ and shifted product is ${P+a*S+a*a}$.',f'Square the shifted sum and subtract twice the shifted product: {ans}.']
  elif level==5:
   q=f'A monic quadratic $x^2-{S}x+k=0$ has roots $u,v$. Their squares sum to ${a*a+b*b}$. Find $k$ and verify that the roots are real.'; facts=[P,4]; ans=f'$k={P}$; discriminant $4>0$.'; steps=[f'$u+v={S},uv=k$, so ${S*S}-2k={a*a+b*b}$.',f'Solve to get $k={P}$. The discriminant is ${S*S}-4({P})=4$, so the roots are real and distinct.']
  else:
   q=f'A monic real quadratic has roots $u,v$ (not assumed real), with $uv={P}$ and $u^2+v^2={a*a+b*b}$. Determine every possible quadratic and prove the list is complete.'; facts=[x*x-S*x+P,x*x+S*x+P]; ans=seq(*facts)+' (each set equal to zero).'; steps=[f'$(u+v)^2=u^2+v^2+2uv={S*S}$.',f'The real sum is therefore ${S}$ or $-{S}$. The product is fixed at ${P}$.',f'These two monic quadratics are {ans} Both have discriminant 4, and their roots satisfy the required identities; no other sum is possible.']
 elif path=='reciprocal':
  if level==1:
   q=f'Add the fractions $1/{a}+1/{b}$ using a common denominator.'; facts=[R(S,P)];ans=L(facts[0]);steps=[f'Use denominator ${P}$ and numerator ${b}+{a}$.',f'Reduce to {ans}.']
  elif level==2:
   q=f'A learner claims that the reciprocal-root sum for roots ${a},{b}$ is $1/({a}+{b})$. Explain the error and state the general identity, with its restriction.'; facts=[R(S,P)];ans=f'$1/u+1/v=(u+v)/(uv)$, provided $uv\\ne0$; {L(facts[0])} here.';steps=['Combine fractions over the product of the denominators; one cannot invert a sum term by term.',f'For these roots the sum is {L(facts[0])}, not {L(R(1,S))}. The identity requires both roots nonzero.']
  elif level==3:
   q=f'Find the monic equation for the reciprocal roots of {L(x*x-S*x+P)} $=0$, without solving for the original roots.'; facts=[x*x-R(S,P)*x+R(1,P)];ans=L(facts[0])+' = 0';steps=[f'The original sum and product are ${S},{P}$.',f'The reciprocal sum and product are {L(R(S,P))} and {L(R(1,P))}. Substitute in the monic quadratic to get {ans}.']
  elif level==4:
   q=f'The roots of {L(x*x-S*x+P)} $=0$ are increased by 1, then reciprocated. Form the resulting monic quadratic without finding the original roots.'; p=(a+1)*(b+1);u=S+2;facts=[x*x-R(u,p)*x+R(1,p)];ans=L(facts[0])+' = 0';steps=[f'The shifted sum is ${u}$, and product ${P}+{S}+1={p}$.',f'Both shifted roots are nonzero. The reciprocal sum is {L(R(u,p))} and product {L(R(1,p))}; hence {ans}.']
  elif level==5:
   q=f'The roots of $x^2-{S}x+k=0$ are nonzero and their reciprocal sum is {L(R(S,P))}. Determine $k$ and the monic reciprocal-root equation.';facts=[P,x*x-R(S,P)*x+R(1,P)];ans=f'$k={P}$; '+L(facts[1])+' = 0';steps=[f'$k\\ne0$ and the reciprocal sum is ${S}/k$. Equate this to {L(R(S,P))} to obtain $k={P}$.',f'The reciprocal product is $1/{P}$. The required equation is {L(facts[1])} $=0$.']
  else:
   q=f'For real $k$, the roots of $x^2-kx+{P}=0$ are each replaced by ${P}/x$. Prove that the root multiset is unchanged for every $k$, and find all $k$ for which the two roots coincide. Roots may be complex.';facts=[-2*s.sqrt(P),2*s.sqrt(P)];ans=f'The map interchanges the two roots (with multiplicity); repeated roots at {seq(*facts)}.';steps=[f'Let the roots be $u,v$. Their product is ${P}\\ne0$, so ${P}/u=v$ and ${P}/v=u$.',f'A repeated root requires discriminant $k^2-4({P})=0$. Both real solutions {seq(*facts)} satisfy this.', 'The interchange argument also holds at repeated roots, so no additional exceptional case occurs.']
 elif path=='complex-division':
  z=a+(b+1)*I;w=1+a*I;quot=s.expand_complex(z/w)
  if level==1:
   q=f'Simplify $(1+{a}i)(1-{a}i)$ using $i^2=-1$.';facts=[1+a*a];ans=L(facts[0]);steps=['The mixed terms cancel.',f'The remaining terms are $1-{a*a}i^2={facts[0]}$.']
  elif level==2:
   q=f'Explain why multiplying numerator and denominator of $1/(1+{a}i)$ by $1-{a}i$ produces a real denominator. Give the result.';facts=[s.expand_complex(1/w)];ans=L(facts[0]);steps=[f'$1-{a}i$ is the conjugate of the nonzero denominator. The product is $1+{a*a}$.',f'Multiplying by this quotient of equal nonzero factors preserves the value: {ans}.']
  elif level==3:
   q=f'Write {L(z)} divided by {L(w)} in Cartesian form.';facts=[quot];ans=L(quot);steps=[f'Multiply above and below by {L(s.conjugate(w))}.',f'The numerator becomes {L(s.expand(z*s.conjugate(w)))} and the denominator is ${1+a*a}$, giving {ans}.']
  elif level==4:
   q=f'Let $z={s.latex(z)}$ and $w={s.latex(w)}$. Calculate $z/w$ in Cartesian form, then determine its modulus exactly by two methods.';facts=[quot,s.Abs(quot).simplify()];ans=seq(*facts);steps=[f'Rationalising gives {L(quot)}.',f'Taking the modulus of this Cartesian result gives {L(facts[1])}.',f'Independently $|z|/|w|=\\sqrt{{{a*a+(b+1)**2}}}/\\sqrt{{{1+a*a}}}$, the same value.']
  elif level==5:
   q=f'Find every real $k$ for which $( {a}+ki)/(1+{b}i)$ is real, and state the real quotient.';facts=[a*b,a];ans=f'$k={a*b}$; quotient ${a}$.';steps=[f'Rationalise: the imaginary numerator is $k-{a*b}$.',f'This vanishes only at $k={a*b}$. The quotient is then ${a}$, checked by multiplying the denominator by ${a}$.']
  else:
   q=f'Let $w=1+{a}i$ and $k$ be real. Determine all $k$ such that $(k+{b}i)/w$ is purely imaginary (real part zero). Find the quotient and prove uniqueness; could the quotient be zero?';facts=[-a*b,b];ans=f'$k=-{a*b}$; quotient ${b}i$; it is nonzero.';steps=[f'After multiplying by the conjugate, the real numerator is $k+{a*b}$; the denominator ${1+a*a}$ is positive.',f'Exactly one real $k=-{a*b}$ makes the real part zero.',f'The numerator then equals ${b}i(1+{a}i)$, so the quotient is ${b}i\\ne0$.']
 elif path=='locus-intersection':
  r=a+2;c=a
  if level==1:
   q=f'For Cartesian points $(0,0)$ and $({a},{b})$, find the squared distance.';facts=[a*a+b*b];ans=L(facts[0]);steps=['Use Pythagoras on the horizontal and vertical displacements.',f'The squared distance is ${a}^2+{b}^2={facts[0]}$.']
  elif level==2:
   q=f'Explain the centre and radius of $|z-{c}|={r}$. Does the centre satisfy the equation?';facts=[c,r,False];ans=f'Centre $({c},0)$; radius ${r}$; centre excluded.';steps=['The modulus measures distance from the point represented by the subtracted complex number.',f'The equation specifies distance ${r}>0$. The centre has distance zero, so it is not on the circle.']
  elif level==3:
   q=f'Find all intersections of $|z-{c}|={r}$ and $\\Re z={c}$. Give Cartesian form.';facts=[c-r*I,c+r*I];ans=seq(*facts);steps=[f'The vertical line passes through the centre. Put $x={c}$ in $(x-{c})^2+y^2={r*r}$.',f'Then $y=\\pm{r}$, giving {ans}.']
  elif level==4:
   q=f'Find the points satisfying $|z-{c}|={r}$ and $|z-{c}|=|z-{c+2}|$. Explain why there are two.';h=s.sqrt(r*r-1);facts=[c+1-h*I,c+1+h*I];ans=seq(*facts);steps=[f'Equal distances give the perpendicular bisector $x={c+1}$.',f'Substituting into the circle gives $y^2={r*r-1}>0$. Both signs give the two points {ans}.']
  elif level==5:
   q=f'Find all $z$ with $|z-{c}|={r}$, $\\arg(z-{c})=\\pi/3$ and $\\Im z>0$. Justify whether any other point on the circle can satisfy these conditions.';facts=[c+R(r,2)+R(r,2)*s.sqrt(3)*I];ans=L(facts[0]);steps=[f'The argument condition selects the ray from ${c}$ with direction $\\cos(\\pi/3)+i\\sin(\\pi/3)$.',f'On the circle the ray parameter must be the positive radius ${r}$. Hence {ans}, with positive imaginary part. The opposite ray has a different argument.']
  else:
   q=f'For real $k$, classify the number of intersections of $|z-{c}|={r}$ and $\\Re z=k$. Give their Cartesian form in each nonempty case, including the tangencies.';facts=[c-r,c+r,r*r-(k-c)**2,0,1,2];ans=f'None outside $[{c-r},{c+r}]$; one at either endpoint; two inside, $z=k\\pm i\\sqrt{{{r*r}-(k-{c})^2}}$.';steps=[f'Write $z=x+iy$. Setting $x=k$ gives $y^2={r*r}-(k-{c})^2$.',f'The right side is positive exactly when ${c-r}<k<{c+r}$, zero at either endpoint, and negative elsewhere.', 'A positive value has two real square roots; zero has one; a negative value has none. This proves all cases.']
 elif path=='det-area':
  A=M([[a,1],[0,b]])
  if level==1:
   q=f'A rectangle has sides ${a}$ and ${b}$. Find its area.';facts=[P];ans=L(P);steps=['Multiply its perpendicular side lengths.',f'Area is ${a}\\times {b}={P}$.']
  elif level==2:
   q=f'A rectangle of area ${P}$ is reflected in the x-axis. Explain why the determinant is $-1$ but the new area is still ${P}$.';facts=[-1,P];ans=f'Determinant $-1$; unsigned area ${P}$.';steps=['Reflection has matrix $\\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}$; its determinant is negative because orientation reverses.', 'Distances and unsigned areas are unchanged. The multiplier is the absolute determinant, not its sign.']
  elif level==3:
   q=f'A triangle has area 3 and is transformed by {L(A)}. Find the image area.';facts=[3*P];ans=L(facts[0]);steps=[f'The determinant is ${a}\\times{b}-0={P}$.',f'Multiply the original area by its absolute value: ${3*P}$.']
  elif level==4:
   B=M([[1,0],[0,-2]]);q=f'A region of area 3 undergoes {L(A)} followed by {L(B)}. Find the composition matrix, image area and whether orientation is reversed.';facts=[B*A,6*P];ans=seq(*facts)+'; reversed.';steps=[f'The composition is $BA$, namely {L(B*A)}.',f'Its determinant is $-{2*P}$, so the image area is ${6*P}$ and orientation reverses.']
  elif level==5:
   B=M([[k,a],[1,b]]);q=f'A triangle of area 3 is mapped by {L(B)} to a triangle of area ${3*a}$. Find all real $k$, identifying the orientation in each case.';facts=[s.Integer(0),R(2*a,b)];ans=f'$k=0$ (reversed); $k={s.latex(facts[1])}$ (preserved).';steps=[f'The determinant is ${b}k-{a}$, so $|{b}k-{a}|={a}$.',f'Solve both signed equations: $k=0$ or $k={s.latex(facts[1])}$.',f'The determinants at these values are $-{a}$ and ${a}$ respectively.']
  else:
   q=f'Under the matrix $\\begin{{pmatrix}} k&{a}\\\\1&k\\end{{pmatrix}}$, a triangle of positive area $A$ is mapped to area $cA$. For real $k$ and $c\\ge0$, classify the number of admissible values of $k$ for each possible $c$. Explain the degenerate case.';facts=[a,2,4,3,2];ans=f'$c=0$: 2; $0<c<{a}$: 4; $c={a}$: 3; $c>{a}$: 2.';steps=[f'The determinant is $k^2-{a}$. Therefore $|k^2-{a}|=c$, giving $k^2={a}+c$ or $k^2={a}-c$.',f'At $c=0$ the branches coincide, producing two roots; the matrix has rank one and collapses area to zero.',f'For $0<c<{a}$ both squared values are distinct and positive. At $c={a}$ the second is zero; beyond it only the first is nonnegative.', 'These are all possibilities because a real square cannot be negative.']
 elif path=='system-consistency':
  if level==1:
   q=f'Solve $x+y={a+b}$ and $x-y={a-b}$ by elimination.';facts=[a,b];ans=seq(*facts);steps=[f'Adding the equations gives $2x={2*a}$.',f'Substituting $x={a}$ gives $y={b}$.']
  elif level==2:
   q=f'Explain why $x+y={a}$ and $2x+2y={2*a+1}$ cannot have a common solution. Contrast with replacing the second constant by ${2*a}$.';facts=[0,1];ans='First system inconsistent; second has infinitely many solutions (one free parameter).';steps=[f'Double the first equation to obtain $2x+2y={2*a}$; this contradicts ${2*a+1}$.',f'With constant ${2*a}$ the second equation is redundant and every point on the first line is a solution.']
  elif level==3:
   q=f'Classify the system $x+y={a}$, $2x+ky={2*a}$ at $k=2$ and at $k={b+1}$. Give its solution set in both cases.';facts=[a,0];ans=f'$k=2$: $(x,y)=({a}-t,t)$ for real $t$; $k={b+1}$: $({a},0)$.';steps=['Subtract twice the first equation from the second: $(k-2)y=0$.',f'At $k=2$ this is redundant; otherwise $y=0,x={a}$.']
  elif level==4:
   q=f'Three planes obey $x+y={a}$, $y+z={b}$ and $x+2y+kz={a+b+1}$. Classify their common intersection at $k=1$ and $k=2$.';facts=[a-b+1,b-1,1];ans=f'$k=1$: no common point; $k=2$: {L(M(facts))}.';steps=['Subtract the first two equations from the third: $(k-1)z=1$.',f'At $k=1$ contradiction; at $k=2$ $z=1$, $y={b-1}$, $x={a-b+1}$.']
  elif level==5:
   q=f'For real $k$, solve $x+y={a}$, $y+z={b}$, $x+2y+kz={a+b}$. Give the full common intersection for every $k$.';facts=[a-b,b,0];ans=f'$k\\ne1$: {L(M(facts))}; $k=1$: {L(M([a-b+t,b-t,t]))}, $t\\in\\mathbb R$.';steps=['Eliminate to obtain $(k-1)z=0$.',f'For $k\\ne1$, $z=0$ and the other coordinates are forced: {L(M(facts))}.',f'For $k=1$ the third equation is redundant; set $z=t$, then back-substitute to obtain the line in the answer.']
  else:
   q=f'For real $k,h$, classify the common intersection of $x+y={a}$, $y+z={b}$, $x+2y+kz=h$. Give the solution or parametric family whenever it exists, and justify completeness.';facts=[a+b,M([a-b+t,b-t,t])];ans=f'$k\\ne1$: $z=(h-{a+b})/(k-1), y={b}-z, x={a}-y$; $k=1,h={a+b}$: line $({a-b}+t,{b}-t,t)$; otherwise none.';steps=[f'Eliminate: $(k-1)z=h-{a+b}$.',f'When $k\\ne1$ this fixes $z$, followed uniquely by $y$ and $x$.',f'When $k=1$ the equation becomes $0=h-{a+b}$. If true, $z$ is free; otherwise there is a contradiction.', 'The cases partition the entire real parameter plane, so no other intersection type can occur.']
 elif path=='point-line':
  p=M([2*a,0,b]);d=M([1,1,0]);foot=M([a,a,0]);dist=s.sqrt(2*a*a+b*b)
  if level==1:
   q=f'Find the squared length of the vector $({a},-{a},{b})$.';facts=[2*a*a+b*b];ans=L(facts[0]);steps=['Square each Cartesian component and add.',f'The result is ${a*a}+{a*a}+{b*b}={facts[0]}$.']
  elif level==2:
   q=f'For $P=({2*a},0,{b})$ and $H=({a},{a},0)$, show that $PH$ is perpendicular to direction $(1,1,0)$. Explain why that is relevant to shortest distance.';facts=[0];ans='Scalar product zero; the perpendicular segment is shortest.';steps=[f'$P-H=({a},-{a},{b})$. Its scalar product with $(1,1,0)$ is ${a}-{a}=0$.','Any other point on the line differs from H by a parallel displacement. Pythagoras adds a positive squared length.']
  elif level==3:
   q=f'Find the perpendicular distance from {L(p)} to the line $\\mathbf r=t(1,1,0)$.';facts=[dist];ans=L(dist);steps=[f'The cross product of $P$ with direction $(1,1,0)$ is {L(p.cross(d))}.',f'Divide its magnitude by $\\sqrt2$ to get {ans}.']
  elif level==4:
   q=f'For $P={s.latex(p)}$ and $L: \\mathbf r=t(1,1,0)$, find the foot of the perpendicular and the distance, using the scalar product to determine $t$.';facts=[foot,dist];ans=seq(*facts);steps=[f'Let $H=(t,t,0)$. Perpendicularity gives $(P-H)\\cdot(1,1,0)={2*a}-2t=0$.',f'So $t={a}$ and $H={s.latex(foot)}$. The displacement has squared norm ${dist**2}$; distance {L(dist)}.']
  elif level==5:
   q=f'Point $P=({2*a},0,k)$ is at distance {L(dist)} from $L: \\mathbf r=t(1,1,0)$. Find all real $k$ and the foot of the perpendicular.';facts=[-b,b,foot];ans=f'$k=\\pm{b}$; $H=({a},{a},0)$.';steps=[f'Projection gives $t={a}$ independently of $k$. Thus the squared distance is ${2*a*a}+k^2$.',f'Equate to ${dist**2}$ and solve $k^2={b*b}$. Both signs give the stated distance.']
  else:
   q=f'For $P=({2*a},0,{b})$ and line $L: \\mathbf r=t(1,1,0)$, prove using a squared-distance argument that there is a unique closest point. Then find every point on L at squared distance ${dist**2+8}$ from P.';facts=[foot,dist,a-2,a+2];ans=f'Closest point $({a},{a},0)$ at distance {L(dist)}; other points $({a-2},{a-2},0)$ and $({a+2},{a+2},0)$.';steps=[f'$D^2=(t-{2*a})^2+t^2+{b*b}=2(t-{a})^2+{dist**2}$.',f'The square is nonnegative and zero only at $t={a}$, proving a unique minimum.',f'The specified larger distance gives $2(t-{a})^2=8$, so $t={a}\\pm2$. These exhaust the solutions.']
 elif path=='skew':
  if level==1:
   q=f'Are $(1,{a},0)$ and $(2,{2*a},0)$ parallel? Explain using a scalar multiple.';facts=[True];ans='Yes; the second is twice the first.';steps=['Compare all three components, including the zero component.','The common nonzero multiplier is 2.']
  elif level==2:
   q=f'Two lines have directions $(1,0,0)$ and $(0,1,0)$. One passes through the origin and the other through $(0,0,{a})$. Explain why non-parallel directions do not guarantee an intersection.';facts=[False];ans='Skew: the first line has z=0 and the second has z='+str(a)+'.';steps=['The direction vectors are not scalar multiples.',f'The constant z-coordinates differ ($0$ and ${a}$), so no point can lie on both.']
  elif level==3:
   q=f'Classify the lines $(s,0,0)$ and $({a},t,0)$ for real $s,t$, and give their common point if any.';facts=[M([a,0,0])];ans=f'Intersect at $({a},0,0)$.';steps=['The directions are nonparallel.',f'Equate coordinates: $s={a}$ and $t=0$, with z equal automatically.']
  elif level==4:
   q=f'Classify the lines $L:(s,{a}s,0)$ and $M:({b},t,{a})$ for real $s,t$. Solve the x and y coordinate equations first, then check z.';facts=[b,a*b];ans=f'$s={b}$, $t={a*b}$ from x,y, but z contradicts; skew.';steps=[f'Equating x and y forces $s={b},t={a*b}$.',f'The z coordinates would require $0={a}$, impossible. The directions are nonparallel, hence the lines are skew.']
  elif level==5:
   q=f'For real $k$, classify $L:(s,{a}s,0)$ and $M:({b},t,k)$ for all $k$. Give the intersection if one exists.';facts=[M([b,a*b,0])];ans=f'$k=0$: intersect at $({b},{a*b},0)$; otherwise skew.';steps=['The directions are independent for every k.',f'x and y force $s={b},t={a*b}$; z equality requires $k=0$.',f'At $k=0$ the common point is $({b},{a*b},0)$. All other k yield skew lines.']
  else:
   q=f'For real $k,h$, classify every pair of lines $L:(s,0,0)$ and $M:({a}+t,kt,h)$, including coincident and parallel cases. Prove that the list is exhaustive.';facts=[M([a,0,0]),True,False,True,False];ans=f'$k=0,h=0$: coincident; $k=0,h\\ne0$: distinct parallel; $k\\ne0,h=0$: intersect at $({a},0,0)$; $k\\ne0,h\\ne0$: skew.';steps=['Directions $(1,0,0)$ and $(1,k,0)$ are parallel exactly when $k=0$.', 'For $k=0$, the second line lies at constant z=h and y=0; it is the same line only when h=0.',f'For $k\\ne0$, equality of y forces $t=0$; equality of z forces $h=0$, then $s={a}$.', 'The four cases partition all real k,h, and neither direction is ever zero.']
 else:raise AssertionError(path)
 # Rubric steps award one proposed mark per individually written criterion; pending teacher review.
 def encode(v):
  if isinstance(v,bool):return v
  if isinstance(v,s.MatrixBase):return {'matrix':[[str(x) for x in row] for row in v.tolist()]}
  return str(v)
 return dict(path=path,focus_skill=PATHS[path],tier=level,variant=variant,assessment_role='prerequisite_bridge' if level==1 else 'concept_diagnostic' if level==2 else 'direct_focus_task',question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=list(HINTS[path][level-1]),rubric=[{'marks':1,'criterion':step} for step in steps],facts=[encode(v) for v in facts],likely_mistake={'root-squares':'Omitting the cross term or discarding the negative root-sum case.','reciprocal':'Inverting a sum or failing to check nonzero denominators.','complex-division':'Changing the denominator without changing the numerator.','locus-intersection':'Discarding a valid sign, or counting the tangency twice.','det-area':'Using a signed determinant as an unsigned area multiplier.','system-consistency':'Dividing by a parameter before checking its zero case.','point-line':'Using a distance to an arbitrary point instead of the perpendicular foot.','skew':'Assuming nonparallel lines must intersect in three dimensions.'}[path],origin='original',examination_source=None,difficulty_status='editorial_design_teacher_pending',demand_rationale=LEVELS[level][1])
