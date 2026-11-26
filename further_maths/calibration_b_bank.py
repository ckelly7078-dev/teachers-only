"""FM-16B original, editorial six-stage pathways. No empirical difficulty claims."""
import sympy as s
from calibration_bank import LEVELS,L,seq
M=s.Matrix
k,t,x,y,z,h=s.symbols('k t x y z h',real=True)
PATHS={
 'composition-order':'MAT.composition.order',
 'inverse-two':'MAT.inverse.two',
 'invariant-lines':'MAT.invariants.invariant-lines',
 'collapse':'MAT.zero-transformation.collapse',
 'line-plane-intersection':'VEC.intersections.line-plane',
 'point-plane':'VEC.distance.point-plane',
 'cross-product':'VEC.vector-product.calculate',
 'line-plane-angle':'VEC.scalar-product.line-plane',
}
MISTAKES={
 'composition-order':'Writing matrices in chronological order rather than applying the rightmost first.',
 'inverse-two':'Swapping diagonal entries without negating the off-diagonal entries or checking the determinant.',
 'invariant-lines':'Confusing a line mapped onto itself with every point on it being fixed.',
 'collapse':'Assuming every singular matrix maps the whole plane to the origin.',
 'line-plane-intersection':'Dividing by a zero direction-normal product without checking whether the whole line lies in the plane.',
 'point-plane':'Omitting the normal length or the absolute value of signed displacement.',
 'cross-product':'Reversing the order, missing the middle cofactor sign, or accepting a zero normal.',
 'line-plane-angle':'Reporting the angle with the normal rather than its complement, or using signed cosine for the smaller angle.'}

def make(path,l,v):
 if path not in PATHS or l not in LEVELS or v not in (1,2,3):raise ValueError('Unknown pathway cell')
 a=v+1;b=a+2;R=s.Rational
 if path=='composition-order':
  A=M([[1,a],[0,1]]); B=M([[b,0],[0,1]]); u=M([1,1]); C=B*A
  if l==1:
   q=f'First add {a} to 1, then multiply the result by {b}. Find the result.';f=[b*(1+a)];ans=L(f[0]);steps=[f'Addition first gives ${1+a}$.',f'Multiplication next gives {ans}.'];h=['Follow the stated order.','Multiply only after adding.']
  elif l==2:
   q=f'Let $A={s.latex(A)}$, $B={s.latex(B)}$. A learner writes $AB$ for A followed by B. Test both orders on {L(u)} and explain the error.';f=[C*u,A*B*u];ans='A then B gives '+L(f[0])+'; B then A gives '+L(f[1])+'.';steps=[f'Applying A first gives {L(A*u)}; B next gives {L(f[0])}.',f'Applying B first gives {L(B*u)}; A next gives {L(f[1])}.', 'The rightmost matrix acts first on column vectors.'];h=['Apply each transformation separately.','Compare the resulting first coordinates.']
  elif l==3:
   q=f'Find the matrix for {L(A)} followed by {L(B)}.';f=[C];ans=L(C);steps=['The second matrix multiplies the first on the left.',f'Multiply rows by columns to get $BA={s.latex(C)}$.'];h=['Write BA, not AB.','Use the row-column rule.']
  elif l==4:
   q=f'Find the image of $y=x$ under {L(A)} followed by {L(B)}, and verify it using the composition matrix.';f=[C,R(1,b*(1+a))];ans=f'$BA={s.latex(C)}$; $y={s.latex(f[1])}x$.';steps=[f'The direction $(1,1)$ maps first to $({1+a},1)$ and then to $({b*(1+a)},1)$.',f'The product is {L(C)} and maps $(1,1)$ to the same direction.',f'The origin is fixed, so the image is $y={s.latex(f[1])}x$.'];h=['A line through the origin is determined by its direction.','Check by applying the product.']
  elif l==5:
   q=f'A shear $S=\\begin{{pmatrix}}1&k\\\\0&1\\end{{pmatrix}}$ followed by {L(B)} sends $(1,1)$ to $({b*(1+a)},1)$. Find k and state the image of $(0,1)$ if the order is reversed.';f=[a,M([a,1])];ans=f'$k={a}$; reversed image {L(f[1])}.';steps=[f'First $(1,1)$ becomes $(1+k,1)$, then $({b}(1+k),1)$.',f'Equate first coordinates to obtain $k={a}$.',f'Reversed order fixes $(0,1)$ under B, then S gives {L(f[1])}.'];h=['Track the test point in the stated order.','Repeat with the basis vector in reverse order.']
  else:
   q=f'For $S=\\begin{{pmatrix}}1&k\\\\0&1\\end{{pmatrix}}$ and $D=\\begin{{pmatrix}}h&0\\\\0&{b}\\end{{pmatrix}}$, with real k and nonzero real h, determine all pairs (k,h) for which the two orders give the same map. Prove completeness.';f=[b];ans=f'$k=0$ or $h={b}$, with $h\\ne0$.';steps=[f'$DS=\\begin{{pmatrix}}h&hk\\\\0&{b}\\end{{pmatrix}}$ and $SD=\\begin{{pmatrix}}h&{b}k\\\\0&{b}\\end{{pmatrix}}$.',f'Equality is equivalent to $k(h-{b})=0$.','The zero-product rule gives both branches, and each makes all matrix entries equal.'];h=['Compare the two matrix products.','Only the upper-right entries can differ.']
 elif path=='inverse-two':
  A=M([[a,1],[1,b]]);d=a*b-1;inv=M([[b,-1],[-1,a]])/d;u=M([1,2]);w=A*u
  if l==1:
   q=f'Solve ${a}x={2*a}$ and explain why division by {a} reverses multiplication.';f=[2];ans='$x=2$.';steps=[f'{a} is nonzero, so divide both sides by it.','Multiplication by the reciprocal reverses the operation.'];h=['Is the coefficient zero?','Divide both sides by the same nonzero value.']
  elif l==2:
   q=f'A learner proposes {L(M([[b,1],[1,a]])/d)} as the inverse of {L(A)}. Compute the upper-right entry of the product and explain why it cannot be an inverse.';f=[R(2*a,d)];ans=L(f[0])+'; nonzero, so the product is not the identity.';steps=[f'The upper-right entry is $({a}+{a})/{d}={s.latex(f[0])}$.','An inverse must give the identity with zero off-diagonal entries; the off-diagonal signs must be negated.'];h=['Multiply row one by column two.','Compare with the identity matrix.']
  elif l==3:
   q=f'Find the inverse of {L(A)} and verify it by multiplication.';f=[inv];ans=L(inv);steps=[f'Determinant ${a}\\cdot{b}-1={d}\\ne0$.',f'Swap the diagonal entries, negate off-diagonal entries, and divide by {d}: {ans}.',f'The product with A is {L(s.eye(2))}.'];h=['Find the determinant first.','Multiply to verify the proposed inverse.']
  elif l==4:
   q=f'Find the inverse of {L(A)} and use it to recover the original point mapped to {L(w)}.';f=[inv,u];ans=seq(*f);steps=[f'Determinant {d} is nonzero, giving inverse {L(inv)}.',f'Multiply the image by this inverse to obtain {L(u)}.',f'Forward multiplication recovers {L(w)}.'];h=['The inverse reverses the given map.','Check by applying the original map.']
  elif l==5:
   q=f'Let $C=\\begin{{pmatrix}}k&1\\\\1&{b}\\end{{pmatrix}}$. Its inverse has upper-left entry $1/{a}$. Determine all real k for which this is possible and find the inverse.';j=R(1,b)+a;J=M([[j,1],[1,b]]);f=[j,J.inv()];ans=seq(*f);steps=[f'The determinant is ${b}k-1$, which must be nonzero.',f'Equate ${b}/({b}k-1)=1/{a}$ to get $k={s.latex(j)}$.',f'The determinant is ${a*b}\\ne0$; the inverse is {L(f[1])}.'];h=['Use the inverse formula for the specified entry.','Check the determinant at the candidate.']
  else:
   q=f'For $C=\\begin{{pmatrix}}k&{a}\\\\0&k\\end{{pmatrix}}$ classify every real k for which C is invertible, and whether its inverse equals C. Prove the answer, including the singular case.';f=[M([[1/k,-a/k**2],[0,1/k]]),False];ans=f'$k\\ne0$: inverse {L(f[0])}; no real k gives $C^{{-1}}=C$.';steps=['The determinant is $k^2$, so k=0 is singular.',f'For nonzero k the inverse is {L(f[0])}.',f'If the inverse equals C, then $C^2=I$ requires $k^2=1$ and $2k\\cdot{a}=0$. These are incompatible.', 'The singular case has no inverse; this exhausts all real k.'];h=['Separate k=0 before dividing.','Square C and compare every entry with the identity.']
 elif path=='invariant-lines':
  A=M([[a,0],[0,b]])
  if l==1:
   q=f'Find a nonzero direction vector for the line $y={a}x$.';f=[M([1,a])];ans=L(f[0]);steps=[f'Choose a unit change in x, giving a change of {a} in y.','Any nonzero multiple is also a direction.'];h=['Use rise over run.','The run can be 1.']
  elif l==2:
   q=f'Under {L(A)}, is the x-axis fixed pointwise, mapped onto itself, both or neither? Explain using $(1,0)$.';f=[True,False];ans='Setwise invariant, not pointwise fixed.';steps=[f'Every $(t,0)$ maps to $({a}t,0)$, and all real first coordinates occur.',f'But $(1,0)$ maps to $({a},0)$, so not every point is fixed.'];h=['Compare membership in the axis with equality of points.','Check that the image is the whole axis.']
  elif l==3:
   q=f'Find all invariant lines through the origin under {L(A)}.';f=[M([1,0]),M([0,1])];ans='$x=0$ and $y=0$.';steps=[f'A direction $(u,v)$ must map to a nonzero multiple of itself: $({a}u,{b}v)=\\lambda(u,v)$.',f'If both components are nonzero, the multiplier must be both {a} and {b}, impossible.', 'Both coordinate axes map onto themselves.'];h=['A line through O is determined by its direction.','Treat zero components separately.']
  elif l==4:
   q=f'Find the image of $y={a}x+1$ under {L(A)} and decide if the original line is invariant.';f=[b,b];ans=f'$y={b}x+{b}$; not invariant.';steps=[f'Write image coordinates $X={a}x,Y={b}y$.',f'Substitute the original equation to get $Y={b}({a}x+1)={b}X+{b}$.','The slope and intercept differ from the original, so the lines are distinct.'];h=['Use image coordinates X,Y.','Eliminate the original x and y.']
  elif l==5:
   q=f'Under $C=\\begin{{pmatrix}}1&{a}\\\\0&{b}\\end{{pmatrix}}$, find all invariant lines through O, including the vertical case.';f=[M([1,0]),M([a,b-1])];ans=f'$y=0$ and $y={s.latex(R(b-1,a))}x$.';steps=[f'For finite slope m, direction $(1,m)$ maps to $(1+{a}m,{b}m)$.',f'Collinearity gives $m(1+{a}m-{b})=0$, hence $m=0$ or $m={s.latex(R(b-1,a))}$.',f'The vertical direction maps to $({a},{b})$, which is not vertical. The matrix is invertible so both retained lines map onto themselves.'];h=['Use a determinant of two directions.','Test the vertical direction independently.']
  else:
   q=f'Classify every invariant affine line (not just lines through O) under $C=\\begin{{pmatrix}}1&0\\\\0&{b}\\end{{pmatrix}}$. Which are fixed pointwise? Prove completeness.';f=[b,True,False];ans='All vertical lines $x=c$ for real c, and the x-axis $y=0$. Only the x-axis is fixed pointwise.';steps=[f'A vertical line $x=c$ maps onto itself because $y\\mapsto {b}y$ is bijective.',f'A nonvertical line $y=mx+c$ maps to $y={b}mx+{b}c$.',f'Equality of both coefficients requires $m=c=0$, since ${b}\\ne1$.','The x-axis is fixed pointwise. Each vertical line has points with nonzero y which move. All affine lines are vertical or nonvertical.'];h=['Separate vertical from nonvertical lines.','For nonvertical lines compare both gradient and intercept.']
 elif path=='collapse':
  A=M([[1,a],[b,a*b]]);u=M([-a,1]);w=M([1,b]);B=M([[1,a],[b,k]])
  if l==1:
   q=f'Are $(1,{b})$ and $({a},{a*b})$ parallel? State the multiplier.';f=[a];ans=L(a);steps=[f'Multiply both components of the first vector by {a}.','The second vector is that multiple.'];h=['Compare both coordinates.','Use the first coordinate to find the multiplier.']
  elif l==2:
   q=f'The matrix {L(A)} has zero determinant. A learner says all points map to the origin. Use the image of $(1,0)$ to refute this.';f=[w];ans=L(w)+' is nonzero.';steps=[f'The first column is the image of $(1,0)$: {ans}.','A zero determinant implies loss of dimension, not necessarily a zero map.'];h=['Use the first column.','Distinguish zero determinant from zero matrix.']
  elif l==3:
   q=f'Find the line which is the image of the whole plane under {L(A)}.';f=[w];ans=f'$y={b}x$.';steps=[f'An input $(x,y)$ maps to $(x+{a}y,{b}(x+{a}y))$.',f'Every first coordinate is possible (take y=0); the image is exactly $y={b}x$.'];h=['Compute the general image.','Show every point on the proposed line is attained.']
  elif l==4:
   q=f'Under {L(A)}, determine all points mapping to the origin and the image of the line $y=1$.';f=[u,w];ans=f'Kernel $x=-{a}y$; image of $y=1$ is $y={b}x$ in image coordinates.';steps=[f'The output vanishes iff $x+{a}y=0$, a line of direction {L(u)}.',f'On the input line $y=1$, output is $(x+{a},{b}(x+{a}))$.', 'As x ranges over the reals, the first output coordinate ranges over all reals.'];h=['Set both output coordinates to zero.','Parameterise the input line and examine the range.']
  elif l==5:
   q=f'For which real k does {L(B)} map the whole plane onto a line? Give that image line and all preimages of the origin.';f=[a*b,w,u];ans=f'$k={a*b}$; image $y={b}x$; kernel $x=-{a}y$.';steps=[f'Determinant $k-{a*b}$ vanishes exactly at $k={a*b}$.','The first column is nonzero, so the rank is one, not zero.',f'At this value the general output is $(x+{a}y,{b}(x+{a}y))$, proving the image and kernel.'];h=['Find when the determinant vanishes.','Check rank and the general output at that value.']
  else:
   q=f'For real k, classify the image dimension of $C=k\\begin{{pmatrix}}1&{a}\\\\{b}&{a*b}\\end{{pmatrix}}$. Prove that for nonzero k the image line is independent of k and determine all preimages of $(1,{b})$.';f=[0,1,1/k];ans=f'$k=0$: image origin, no preimage of $(1,{b})$; $k\\ne0$: image $y={b}x$, preimages $x+{a}y=1/k$.';steps=['When k=0 all outputs are zero.',f'Otherwise output is $k(x+{a}y)(1,{b})$. The scalar ranges over all reals, so rank is one with the same image line.',f'The target $(1,{b})$ requires $k(x+{a}y)=1$. This is equivalent to $x+{a}y=1/k$ and sufficient as well.'];h=['Separate zero from nonzero k.','Factor the general output as a scalar times a direction.']
 elif path=='line-plane-intersection':
  P=M([a,0,0]);D=M([1,1,1]);N=M([1,1,1]); c=a+3*b;H=P+b*D
  if l==1:
   q=f'Solve ${a}+3t={c}$ for t.';f=[b];ans=L(b);steps=[f'Subtract {a} from both sides.',f'Divide by 3 to get {ans}.'];h=['Isolate the t term.','Divide by its coefficient.']
  elif l==2:
   q=f'Line $(t,-t,{a})$ has direction perpendicular to normal $(1,1,1)$. Explain whether it intersects the plane $x+y+z={a+1}$.';f=[False];ans='No intersection; line parallel to and outside plane.';steps=[f'Substitution gives $t-t+{a}={a}$ for every t.',f'That constant differs from {a+1}, so no point satisfies the plane equation.'];h=['Substitute a general point.','A zero parameter coefficient does not imply intersection.']
  elif l==3:
   q=f'Find the intersection of line $({a}+t,t,t)$ and plane $x+y+z={c}$.';f=[H];ans=L(H);steps=[f'Substitute to obtain ${a}+3t={c}$, so $t={b}$.',f'The point is {ans}; its coordinates sum to {c}.'];h=['Substitute line coordinates into plane.','Recover the point from the parameter.']
  elif l==4:
   q=f'Find the intersection of $({a}+t,t,t)$ with the plane through $(0,0,{c})$ having normal $(1,1,1)$. Give the Cartesian plane equation and verify the point.';f=[c,H];ans=f'$x+y+z={c}$; {L(H)}.';steps=[f'The normal dotted with a known plane point gives constant {c}.',f'Substitute the line: ${a}+3t={c}$, hence $t={b}$.',f'The point {L(H)} satisfies both representations.'];h=['Use normal dot position equals constant.','Then solve the parameter equation.']
  elif l==5:
   q=f'For real k, classify intersection of line $({a}+t,-t,kt)$ with $x+y+z={c}$. Give the point when it exists.';f=[M([a+3*b/k,-3*b/k,3*b])];ans=f'$k=0$: none; otherwise {L(f[0])}.';steps=[f'Substitution gives $kt={c-a}$.','If k=0 the positive right side is impossible.',f'Otherwise $t={3*b}/k$ and the stated point is unique.'];h=['Collect the t terms.','Do not divide until k=0 is handled.']
  else:
   q=f'For real k,h classify all intersections of $({a}+t,-t,kt)$ with $x+y+z=h$, giving the point or entire line when applicable. Prove completeness.';f=[a,M([a+(s.Symbol('h',real=True)-a)/k,-(s.Symbol('h',real=True)-a)/k,s.Symbol('h',real=True)-a])];ans=f'$k\\ne0$: point $({a}+(h-{a})/k,-(h-{a})/k,h-{a})$; $k=0,h={a}$: entire line; $k=0,h\\ne {a}$: none.';steps=[f'The plane equation reduces to $kt=h-{a}$.','For nonzero k it fixes exactly one parameter.',f'For k=0 the equation is true for every t exactly when $h={a}$; otherwise it is false for every t.','The direction is never zero, and these cases exhaust real k,h.'];h=['Reduce to one scalar equation.','Separate zero coefficient from nonzero coefficient.']
 elif path=='point-plane':
  n=M([1,2,2]);P=M([a,b,0]);c=a+2*b-9;H=P-n;dist=3
  if l==1:
   q=f'Find the length of vector $({a},{2*a},{2*a})$.';f=[3*a];ans=L(f[0]);steps=[f'Squared length is ${a*a}+{4*a*a}+{4*a*a}={9*a*a}$.',f'The nonnegative square root is {ans}.'];h=['Use all three components.','Take the nonnegative square root.']
  elif l==2:
   q=f'The same plane is written $x+2y+2z={c}$ or ${a}x+{2*a}y+{2*a}z={a*c}$. Explain why the point-plane distance formula cannot use only its numerator, using point {L(P)}.';f=[9,9*a,3];ans=f'Numerators 9 and {9*a}; both distances 3.';steps=[f'The absolute residual is 9 in the first form and {9*a} in the scaled form.',f'The normal lengths are 3 and {3*a}; dividing by them cancels the scaling.', 'Distance is geometric and cannot depend on the chosen scalar multiple of the equation.'];h=['Compare the residuals.','Compare normal lengths too.']
  elif l==3:
   q=f'Find the perpendicular distance from {L(P)} to $x+2y+2z={c}$.';f=[3];ans='$3$.';steps=[f'The signed residual is ${a}+2\\cdot{b}-({c})=9$.','Divide its absolute value by normal length 3 to get 3.'];h=['Compute the residual.','Divide by the magnitude of the normal.']
  elif l==4:
   q=f'Find the foot of the perpendicular from {L(P)} to $x+2y+2z={c}$ and its distance.';f=[H,3];ans=seq(*f);steps=[f'Write the foot as $P-tn$ with $n=(1,2,2)$.',f'Plane membership gives $9-9t=0$, so t=1 and the foot is {L(H)}.','The displacement has length 3.'];h=['The perpendicular is parallel to the normal.','Impose plane membership to find t.']
  elif l==5:
   q=f'Find all real h for which plane $x+2y+2z=h$ is distance {a} from {L(P)}. Identify on which side of each plane P lies using the displayed normal.';j=a+2*b;f=[j-3*a,j+3*a];ans=f'$h={f[0]}$ (positive residual) or $h={f[1]}$ (negative residual).';steps=[f'Distance equation is $|{j}-h|/3={a}$.',f'Solve both signed equations, giving h={f[0]} or h={f[1]}.','The first has positive residual and the second negative.'];h=['Both sides of a plane have positive unsigned distance.','Solve both signs, then test the residual.']
  else:
   q=f'For point {L(P)} and plane $x+2y+2z={c}$, prove the foot is unique. Find the exact set of plane points at distance 5 from P and describe it geometrically.';f=[H,4];ans=f'Foot {L(H)}; circle in the given plane centred at H, radius 4: $|Q-H|=4$.';steps=[f'The normal projection gives foot {L(H)}, at distance 3.', 'For any plane point Q, Q-H is perpendicular to P-H, so $|P-Q|^2=9+|Q-H|^2$.','The second term is nonnegative and zero only at H, proving uniqueness.','Setting the squared distance to 25 gives $|Q-H|^2=16$, the circle of radius 4 in the plane.'];h=['Use the normal projection.','Apply Pythagoras within the plane and its normal.']
 elif path=='cross-product':
  U=M([1,a,0]);V=M([0,1,b]);W=M([a*b,-b,1]);
  if l==1:
   q=f'Calculate the determinant of {L(M([[a,0],[1,b]]))}.';f=[a*b];ans=L(f[0]);steps=['Use diagonal product minus other diagonal product.',f'The result is ${a}\\cdot{b}-0={a*b}$.'];h=['Multiply along each diagonal.','Subtract the off-diagonal product.']
  elif l==2:
   q=f'Given $u={s.latex(U)}$, $v={s.latex(V)}$, a learner claims $v\\times u=u\\times v={s.latex(W)}$. Refute this by calculating the first component of $v\\times u$.';f=[-a*b];ans=L(f[0])+'; order reverses the sign.';steps=[f'The first component is $1\\cdot0-{b}\\cdot{a}=-{a*b}$.','Swapping the vectors reverses the determinant orientation, so the whole vector changes sign.'];h=['Use the y and z coordinates in the stated order.','Compare with the positive first component given.']
  elif l==3:
   q=f'Calculate {L(U)} cross {L(V)}.';f=[W];ans=L(W);steps=[f'First component: ${a}\\cdot{b}-0={a*b}$.',f'Second: $0-{b}=-{b}$; third: $1-0=1$.',f'Therefore the vector is {ans}.'];h=['Use the component formula.','Check the sign of the middle component.']
  elif l==4:
   q=f'Find the cross product of {L(U)} and {L(V)}, verify orthogonality to both, and find the area of their spanned triangle.';f=[W,W.norm()/2];ans=seq(*f);steps=[f'The cross product is {L(W)}.',f'The dot products are ${a*b}-{a*b}=0$ and $-{b}+{b}=0$.',f'Half the magnitude is the triangle area {L(f[1])}.'];h=['Calculate the vector first.','Check both dot products; halve the magnitude.']
  elif l==5:
   q=f'Let $u=(1,{a},0)$, $v=(0,1,k)$ for real k. Their cross product has magnitude {L(W.norm())}. Find every k and give each cross product.';f=[-b,b,M([-a*b,b,1]),W];ans=seq(*f);steps=[f'The cross product is $({a}k,-k,1)$.',f'Equate squared lengths: $({a*a+1})k^2+1={W.dot(W)}$.',f'Thus $k=\\pm {b}$. Substitution gives the two vectors {L(f[2])}, {L(W)}.'];h=['Compute the cross product in terms of k.','Square magnitudes and keep both signs.']
  else:
   q=f'For $u=(1,{a},0)$ and $v=(0,1,{b})$, determine every vector w satisfying $u\\times w=u\\times v$. Prove the family is complete.';f=[V,U];ans=f'$w=v+tu$, $t\\in\\mathbb R$, i.e. {L(V)} plus t times {L(U)}.';steps=['By distributivity, the equation is equivalent to $u\\times(w-v)=0$.','Since u is nonzero, the cross product vanishes exactly when w-v is a scalar multiple of u (including zero).','Every vector of the stated family satisfies the equation, because $u\\times u=0$.'];h=['Subtract the two cross products.','Use the zero-cross-product condition for a nonzero vector.']
 elif path=='line-plane-angle':
  n=M([0,0,1]);D=M([a,0,a*s.sqrt(3)]);theta=s.pi/3
  if l==1:
   q=f'In a right triangle the hypotenuse is {2*a} and opposite side is {a}. Find the acute angle in radians.';f=[s.pi/6];ans=L(f[0]);steps=['Sine is opposite over hypotenuse, here $1/2$.',f'The acute angle is {ans}.'];h=['Use the sine ratio.','Give the exact angle in radians.']
  elif l==2:
   q=f'A direction {L(D)} makes angle $\\pi/6$ with the positive z-axis. Explain why its angle with the plane $z={a}$ is not $\\pi/6$.';f=[theta];ans=L(theta);steps=['The z-axis is normal to the plane, not in the plane.',f'The smaller angle to the plane is the complement, $\\pi/2-\\pi/6={s.latex(theta)}$.'];h=['The normal is perpendicular to the plane.','Take the complementary angle.']
  elif l==3:
   q=f'Find the smaller angle in radians between direction {L(D)} and plane $z={a}$.';f=[theta];ans=L(theta);steps=[f'Use normal $(0,0,1)$ and direction length {2*a}.',f'The sine of the line-plane angle is $|d\\cdot n|/(|d||n|)=\\sqrt3/2$, giving {ans}.'];h=['Use the normal and direction.','The line-plane angle uses sine of the smaller angle.']
  elif l==4:
   q=f'Find the smaller angle between the line through $(0,0,0)$ and $({a},0,{a}\\sqrt3)$ and the plane through $(0,0,{b})$ parallel to the xy-plane. Give the plane equation and justify the angle convention.';f=[b,theta];ans=f'$z={b}$; {L(theta)}.';steps=[f'The plane has normal $(0,0,1)$ and equation $z={b}$.',f'The line direction is {L(D)}; its vertical component is ${a}\\sqrt3$ and length ${2*a}$.', 'The angle with the plane is the complement of the smaller normal angle, so it is $\\pi/3$.'];h=['Construct the line direction and plane normal.','Use the vertical-to-total length ratio.']
  elif l==5:
   q=f'Find all real k for which direction $({a},0,k)$ makes angle $\\pi/6$ with the plane $z={b}$. Explain why both signs are allowed.';j=a/s.sqrt(3);f=[-j,j];ans=seq(*f);steps=[f'The sine condition is $|k|/\\sqrt{{{a*a}+k^2}}=1/2$.',f'Squaring gives $3k^2={a*a}$, hence $k=\\pm {s.latex(j)}$.','Both signs satisfy the original unsigned ratio; the line is unoriented.'];h=['Set the sine ratio equal to one half.','Check both signs in the unsquared equation.']
  else:
   q=f'For real k and fixed {a}>0, let a line have direction $({a},0,k)$. For each desired smaller angle $\\theta\\in[0,\\pi/2]$ with the plane $z=0$, classify the number of real k and express them in terms of theta. Justify endpoints.';f=[1,2,0,a];ans=f'$\\theta=0$: $k=0$; $0<\\theta<\\pi/2$: $k=\\pm {a}\\tan\\theta$; $\\theta=\\pi/2$: no finite k.';steps=[f'The sine ratio is $|k|/\\sqrt{{{a*a}+k^2}}$, and the horizontal component {a} is nonzero.',f'Equivalently for angles below $\\pi/2$, $\\tan\\theta=|k|/{a}$.','At zero there is one k. At each strictly intermediate angle there are two opposite nonzero values.','At $\\pi/2$ a vertical direction is necessary, impossible with the fixed nonzero horizontal component.'];h=['Relate vertical and horizontal components.','Check zero and right-angle cases separately.']
 else:raise AssertionError(path)
 def encode(w):
  if isinstance(w,bool):return w
  if isinstance(w,s.MatrixBase):return {'matrix':[[str(e) for e in row] for row in w.tolist()]}
  return str(w)
 return dict(path=path,focus_skill=PATHS[path],tier=l,variant=v,assessment_role='prerequisite_bridge' if l==1 else 'concept_diagnostic' if l==2 else 'direct_focus_task',question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=h,rubric=[dict(marks=1,criterion=p) for p in steps],facts=[encode(e) for e in f],likely_mistake=MISTAKES[path],origin='original',examination_source=None,difficulty_status='editorial_design_teacher_pending',demand_rationale=LEVELS[l][1])
