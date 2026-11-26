"""FM-16Y original complex loci and polynomial solving pathways."""
import sympy as s
from calibration_bank import LEVELS,L
x,y,h,k=s.symbols('x y h k',real=True); I=s.I
PATHS={'distance-circle':'CPX.loci.circle','equidistant-locus':'CPX.loci.bisector','solve-cubic':'CPX.cubic-quartic.cubic','solve-quartic':'CPX.cubic-quartic.quartic'}
RATIONALES={
'distance-circle':['Calculate distance from a point.','Distinguish radius from radius squared.','Translate modulus into Cartesian circle.','Recover centre and radius by completing squares.','Intersect a translated circle and a line.','Classify two circles with parameter-dependent radius, including zero-radius exclusion and both tangent cases.'],
'equidistant-locus':['Find the midpoint of a segment.','Explain why the entire perpendicular bisector is needed.','Construct a non-axis-aligned perpendicular bisector.','Intersect two independent equidistant loci.','Use a bisector to solve a simultaneous circle condition.','Classify a moving equidistant locus, including identical sites and coincident or parallel lines.'],
'solve-cubic':['Factor a cubic using a given real factor.','Correct the assumption that a cubic must have three real roots.','Solve using one supplied real root and division.','Use a supplied non-real root to obtain the real factor.','Recover a missing parameter from a given root and solve.','Classify all roots and multiplicities of a parameter-dependent cubic with a known root.'],
'solve-quartic':['Solve a quadratic in x squared with positive values.','Diagnose missing signs and imaginary roots.','Solve using a supplied real quadratic factor.','Use a supplied non-real root and divide to solve a quartic.','Recover a missing coefficient from a supplied conjugate pair and solve.','Classify every root and multiplicity of a quartic with a fixed irreducible factor and variable quadratic.']}
def division_steps(dividend,divisor):
 dividend=s.expand(dividend); divisor=s.expand(divisor); out=[]
 while dividend!=0 and s.degree(dividend,x)>=s.degree(divisor,x):
  term=s.LC(s.Poly(dividend,x))/s.LC(s.Poly(divisor,x))*x**(s.degree(dividend,x)-s.degree(divisor,x))
  product=s.expand(term*divisor); dividend=s.expand(dividend-product)
  out.append(f'Quotient term {L(term)}: subtract {L(product)}, leaving {L(dividend)}.')
 assert dividend==0
 return out

def make(path,l,v):
 if path not in PATHS or l not in LEVELS or v not in (1,2,3):raise ValueError('Unknown cell')
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5));F=(x-a)**2+b*b; z=a+b*I
 if path=='distance-circle':
  if l==1:
   f=[s.sqrt(a*a+b*b)];q=f'Find the distance between the points 0 and {L(a+b*I)} on an Argand diagram.';ans=L(f[0]);steps=[f'Use Pythagoras: the distance is {L(s.sqrt(a*a+b*b))}.'];hint=['Square both coordinate differences.'];mist='Adding coordinate differences instead of using Pythagoras.'
  elif l==2:
   f=[b,b*b];q=f'A student says the locus |z-{a}|={b} has radius {b*b}. Correct the radius and give the squared Cartesian equation.';ans=f'Radius {b}; (x-{a}) squared + y squared = {b*b}.';steps=[f'Modulus is distance, so radius is {b}.',f'Squaring both sides gives (x-{a}) squared + y squared = {b*b}.'];hint=['Distance is not distance squared.'];mist='Confusing radius and radius squared.'
  elif l==3:
   f=[a,b,d*d];q=f'Express the locus |z-({a}+{b}i)|={d} as a Cartesian circle equation and state its centre and radius.';ans=f'(x-{a}) squared + (y-{b}) squared = {d*d}; centre ({a},{b}), radius {d}.';steps=[f'Write z=x+iy; the displacement is (x-{a})+i(y-{b}).',f'Its squared modulus gives {ans}'];hint=['Subtract the centre before calculating distance.'];mist='Reversing the signs of the centre.'
  elif l==4:
   G=s.expand((x-a)**2+(y+b)**2-d*d);f=[a,-b,d];q=f'The locus is {L(G)}=0. Complete both squares to determine the centre and radius.';ans=f'Centre ({a},{-b}), radius {d}.';steps=[f'Complete squares in x and y, adding {a*a} and {b*b} respectively.',f'The equation becomes (x-{a}) squared + (y+{b}) squared = {d*d}.',ans];hint=['Group the x and y terms separately.'];mist='Reading the linear coefficients directly as the centre.'
  elif l==5:
   f=[a-s.sqrt(d*d-b*b),a+s.sqrt(d*d-b*b)];q=f'Find all real complex numbers on the circle |z-({a}+{b}i)|={d}. Give exact values and justify completeness.';ans=', '.join(map(L,f));steps=['A real complex number has y=0.',f'The circle then requires (x-{a}) squared = {d*d-b*b}.',f'Both square-root signs give the two solutions {ans}, and each satisfies the distance equation.'];hint=['Intersect with the real axis.'];mist='Discarding the negative square-root branch.'
  else:
   lo=d-b;hi=d+b;f=[lo,hi,(d*d+b*b-h*h)/(2*d),b*b-((d*d+b*b-h*h)/(2*d))**2];q=f'For every real h classify the number of distinct solutions of |z|={b} and |z-{d}|=h. Find every solution in exact Cartesian form, including both tangencies and negative h.';ans=f'None for h<{lo} or h>{hi}; one at h={lo} or {hi}; two for {lo}<h<{hi}. x={L(f[2])}, y={L(s.sqrt(f[3]))} or {L(-s.sqrt(f[3]))} for admissible h.';steps=[f'The second radius requires h>=0. For nonnegative h, square the two equations and subtract: {2*d}x={d*d+b*b}-h squared.',f'Thus x={L(f[2])} and y squared={L(f[3])}.',f'A real y exists precisely when |x|<={b}; since d is positive, this is equivalent to {lo}<=h<={hi} after using h>=0.',f'At either boundary y=0, giving one tangent point; strictly between them both signs give distinct points. Outside there are no solutions. Substitution restores both original nonnegative distances.'];hint=['Subtract squared distances to eliminate y squared.'];mist='Counting negative radii or counting a tangent point twice.'
 elif path=='equidistant-locus':
  if l==1:
   f=[a,b];q=f'Find the midpoint of the points (0,0) and ({2*a},{2*b}).';ans=f'({a},{b})';steps=[f'Average each coordinate: midpoint {ans}.'];hint=['Average separately.'];mist='Using half the distance as a coordinate.'
  elif l==2:
   f=[a,True];q=f'A student claims z={a} is the only point equidistant from 0 and {2*a}. State the full locus and decide whether {a}+{b}i lies on it.';ans=f'x={a}; yes.';steps=[f'Squared distances are x squared + y squared and (x-{2*a}) squared + y squared.',f'Equating gives x={a} without restricting y, so the stated non-real point is also on the locus.'];hint=['Cancel the common y squared terms.'];mist='Confusing the midpoint with the entire perpendicular bisector.'
  elif l==3:
   f=[a,b,a*a+b*b];q=f'Find the Cartesian equation of the locus |z|=|z-({2*a}+{2*b}i)|.';ans=f'{a}x+{b}y={a*a+b*b}.';steps=['Square both nonnegative distances.',f'Expand and cancel x squared and y squared to obtain {ans}','This is a line through the midpoint with normal parallel to the segment between the sites.'];hint=['Cancel the quadratic terms.'];mist='Treating the equality as a circle.'
  elif l==4:
   f=[a,b];q=f'Find the point equidistant from 0, {2*a} and {2*b}i. Justify uniqueness.';ans=L(z);steps=[f'Equality of the first two squared distances forces x={a}.',f'Equality of the first and third forces y={b}.',f'The two independent lines intersect only at {ans}, which satisfies both equalities.'];hint=['Use two perpendicular bisectors.'];mist='Equating only two of the three distances.'
  elif l==5:
   f=[a-s.I*s.sqrt(d*d-a*a),a+s.I*s.sqrt(d*d-a*a)];q=f'Find every complex number equidistant from 0 and {2*a} that also satisfies |z|={d}. Give exact values.';ans=', '.join(map(L,f));steps=[f'The equal distances force x={a}.',f'The circle gives y squared={d*d-a*a}.',f'The two signs yield {ans}; both satisfy the original equations.'];hint=['Intersect the perpendicular bisector with the circle.'];mist='Keeping only the upper semicircle.'
  else:
   f=[a,b,2*a,0];q=f'For each real k classify the simultaneous loci |z|=|z-{2*a}| and |z|=|z-(k+{2*b}ki)|. Find all solutions. Then replace the moving site k+{2*b}ki by the real number k and repeat, including coincident and identical-site cases.';ans=f'First family: k=0 gives all x={a}; otherwise z={a}+i((1+{4*b*b})k-2({a}))/{4*b}. Second family: k=0 or {2*a} gives all x={a}; otherwise none.';f=[a,((1+4*b*b)*k-2*a)/(4*b),2*a];steps=[f'The fixed bisector is x={a}.',f'For the moving site k+{2*b}ki the squared-distance equality is 2kx+{4*b}ky=(1+{4*b*b})k squared.',f'At k=0 the sites coincide and the equality holds everywhere, leaving the fixed line. Otherwise divide by k and substitute x={a}, giving y={L(f[1])}; there is one point.',f'For a real moving site the second equation is 2kx=k squared. At k=0 it imposes no constraint, and otherwise x=k/2. This agrees with the fixed line only at k={2*a}; all other nonzero k give distinct parallel lines and no solutions.'];hint=['Separate k=0 before division.'];mist='Cancelling k and losing the identical-site case.'
 elif path=='solve-cubic':
  r=-d;G=s.expand((x-r)*F)
  if l==1:
   f=[a,b];q=f'Given x+{d} is a factor of {L(s.expand((x+d)*(x-a)*(x-b)))}, find the other two real roots by division.';ans=f'{a}, {b}';steps=[f'Divide by x+{d} to obtain {L(s.expand((x-a)*(x-b)))}.',f'Factor as (x-{a})(x-{b}), giving {ans}.'];hint=['Use the supplied factor.'];mist='Reporting the known root instead of the remaining two.'
  elif l==2:
   f=[r,a-b*I,a+b*I];q=f'A student claims (x+{d})((x-{a}) squared + {b*b})=0 has three real roots. Give all complex roots and correct the claim.';ans=', '.join(map(L,f));steps=[f'The linear factor gives {-d}.',f'The quadratic factor requires (x-{a}) squared = {-b*b}, giving the conjugate pair {L(a-b*I)}, {L(z)}.'];hint=['A negative real square has imaginary square roots.'];mist='Assuming real coefficients force all roots to be real.'
  elif l==3:
   f=[r,a-b*I,z];q=f'Given that {-d} is a root, solve {L(G)}=0 over the complex numbers using polynomial division.';ans=', '.join(map(L,f));steps=[f'Divide the cubic by x+{d}: the quotient is {L(s.expand(F))}, with remainder zero.',f'Complete the square: (x-{a}) squared = {-b*b}.',f'Combine the two conjugate solutions with the given root: {ans}.'];hint=['Divide before using the quadratic formula.'];mist='Omitting the supplied root in the final set.'
  elif l==4:
   f=[r,a-b*I,z];q=f'Given that {L(z)} is a root of {L(G)}=0, find all roots without guessing the real root.';ans=', '.join(map(L,f));steps=[f'Real coefficients force {L(a-b*I)} as a root.',f'Their product factor is {L(s.expand(F))}. Divide the cubic by it to obtain x+{d}, remainder zero.',f'The remaining real root is {-d}; all roots are {ans}.'];hint=['Use the conjugate-pair factor.'];mist='Dividing by only one complex factor.'
  elif l==5:
   H=G-G.subs(x,0)+k;f=[G.subs(x,0),r,a-b*I,z];q=f'The real cubic {L(H)} has root {L(z)}. Find k and all roots, explaining why k is unique.';ans=f'k={L(f[0])}; roots '+', '.join(map(L,f[1:]));steps=[f'Substituting {L(z)} in the known terms gives {L(s.expand((G-G.subs(x,0)).subs(x,z)))}. Adding k must give zero, so k={L(f[0])}; its coefficient is one, so unique.',f'The conjugate pair forces {L(s.expand(F))}. Divide to obtain x+{d}.',f'Thus the roots are '+', '.join(map(L,f[1:]))+'.'];hint=['Only the constant term is unknown.'];mist='Treating the complex substitution as two independent unknowns.'
  else:
   b=b+v-1;G=(x-a)*((x-b)**2-h);B=(b-a)**2;f=[0,B,b-s.sqrt(h),b+s.sqrt(h),a];q=f'For every real h solve {L(s.expand(G))}=0, given that {a} is a root. Classify distinct roots and multiplicities, including collisions with the known root.';ans=f'Roots {a} and {L(b-s.sqrt(h))}, {L(b+s.sqrt(h))}; h<0 gives conjugate pair plus real root; h=0 gives double root {b}; h={B} gives double root {a}; all other positive h give three distinct real roots.';steps=[f'Divide by x-{a}; quotient is (x-{b}) squared - h.',f'The remaining roots are {L(b-s.sqrt(h))}, {L(b+s.sqrt(h))}, interpreted over complex numbers.',f'At h<0 the pair is distinct non-real; at h=0 it coalesces at {b}, different from {a}.',f'The known root is also a root of the quotient exactly when h={B}; it then has multiplicity two and the other root is {2*b-a}. All other positive h give three distinct real roots.'];hint=['Check whether the quotient also vanishes at the known root.'];mist='Only checking whether the quadratic discriminant is zero.'
 else:
  H=(x+d)**2+1;G=s.expand(F*H)
  if l==1:
   f=[-b,-a,a,b];q=f'Solve (x squared - {a*a})(x squared - {b*b})=0 over the reals.';ans=', '.join(map(L,f));steps=[f'Each factor gives x squared equal to {a*a} or {b*b}.',f'Take both signs for each square root: {ans}.'];hint=['Use both square-root signs.'];mist='Reporting only positive roots.'
  elif l==2:
   f=[-a,a,-b*I,b*I];q=f'A student claims (x squared - {a*a})(x squared + {b*b})=0 has only two solutions. Give all four complex roots.';ans=', '.join(map(L,f));steps=[f'The first factor gives +/-{a}.',f'The second gives +/-{b}i because i squared = -1.',f'All four distinct roots are {ans}.'];hint=['The domain is complex numbers.'];mist='Discarding negative squared values.'
  elif l==3:
   f=[a-b*I,z,-d-I,-d+I];q=f'Given the factor {L(s.expand(F))}, solve {L(G)}=0 over the complex numbers by division.';ans=', '.join(map(L,f));steps=[f'Division by the supplied quadratic gives {L(s.expand(H))} with remainder zero.',f'Completing each square gives the four roots {ans}.'];hint=['Solve both quadratic factors.'];mist='Solving only the quotient.'
  elif l==4:
   J=(x+d)*(x-b);P=s.expand(F*J);f=[a-b*I,z,-d,b];q=f'Given that {L(z)} is a root of {L(P)}=0, find every root, using conjugation and polynomial division.';ans=', '.join(map(L,f));steps=[f'The given root forces {L(a-b*I)} and factor {L(s.expand(F))}.',f'Division gives {L(s.expand(J))}; factor as (x+{d})(x-{b}).',f'The four roots are {ans}.'];hint=['Construct the real factor before division.'];mist='Assuming the remaining roots are also non-real.'
  elif l==5:
   P=G-G.subs(x,0)+k;f=[G.subs(x,0),a-b*I,z,-d-I,-d+I];q=f'The real quartic {L(P)} has root {L(z)}. Find its unknown constant k and solve completely.';ans=f'k={L(f[0])}; roots '+', '.join(map(L,f[1:]));steps=[f'Substituting {L(z)} in the known terms gives {L(s.expand((G-G.subs(x,0)).subs(x,z)))}. Adding k must give zero, so k={L(f[0])}.',f'Its conjugate supplies the real factor {L(s.expand(F))}. Divide to obtain {L(s.expand(H))}.',f'Complete the square in each factor and obtain '+', '.join(map(L,f[1:]))+'.'];hint=['Substitution determines the missing constant.'];mist='Finding k without solving the remaining factor.'
  else:
   G=s.expand(F*((x-a)**2-h));f=[0,-b*b,a-b*I,z,a-s.sqrt(h),a+s.sqrt(h)];q=f'For every real h solve {L(G)}=0 given the factor {L(s.expand(F))}. Classify every distinct root and its multiplicity, including cases when the factors share roots.';ans=f'Fixed pair {L(a-b*I)}, {L(z)}; other roots {L(a-s.sqrt(h))}, {L(a+s.sqrt(h))}. h={-b*b}: two double non-real roots; h=0: one double real root and two simple non-real roots; otherwise four simple roots.';steps=[f'Division by the given factor gives (x-{a}) squared - h.',f'The first factor gives {L(a-b*I)}, {L(z)}; the second gives {L(a-s.sqrt(h))}, {L(a+s.sqrt(h))}.',f'At h=0 the second factor has the double real root {a}. At h={-b*b} the factors are identical, giving two double non-real roots.',f'For all other h the second factor has two distinct roots and no root in common with the first: substitute either fixed root to obtain {-b*b}-h, nonzero. Positive h gives two real and two non-real roots; negative h other than {-b*b} gives four distinct non-real roots.'];hint=['Check both internal repetition and overlap between factors.'];mist='Counting repeated roots as distinct or missing identical factors.'
 # Include explicit numerical polynomial division in the routine and linked tiers.
 if path=='solve-cubic' and l in (3,4):
  steps[1 if l==3 else 2:1 if l==3 else 2]=division_steps(G,x+d if l==3 else F)
 if path=='solve-quartic' and l in (3,4):
  steps[1 if l==3 else 2:1 if l==3 else 2]=division_steps(G if l==3 else P,F)
 return dict(path=path,focus_skill=PATHS[path],tier=l,variant=v,assessment_role='prerequisite_bridge' if l==1 else 'concept_diagnostic' if l==2 else 'direct_focus_task',question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hint,rubric=[dict(marks=1,criterion=e) for e in steps],facts=[e if type(e) is bool else str(e) for e in f],likely_mistake=mist,origin='original',examination_source=None,difficulty_status='editorial_design_teacher_pending',demand_rationale=RATIONALES[path][l-1])
