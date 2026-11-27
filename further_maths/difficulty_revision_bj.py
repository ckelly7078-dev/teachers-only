"""FM-16BJ original difficulty and allocation successors."""
from importlib import import_module
from copy import deepcopy
import sympy as s
from active_difficulty import require

TARGETS = {
    ('angle-units',5): 'ay', ('argument-range',5): 'ay',
    ('cartesian-to-polar',5): 'az', ('complex-division',5): 'aw',
    ('conjugate-product',4): 'aw', ('inverse-systems',5): 'be',
    ('related-solids',5): 'bh', ('solve-cubic',5): 'ax',
    ('solve-quartic',5): 'ax', ('vector-plane',5): 'bg',
}

def tex(a):
    return '$'+s.latex(a)+'$'

def rubric(*rows):
    return [{'type':t,'marks':1,'criterion':c} for t,c in rows]

def revise(path,tier,v,resolver=None):
    require((path,tier) in TARGETS and type(tier) is int and type(v) is int and 1<=v<=3,'Unknown BJ candidate')
    r=resolver
    if r is None:
        old={"payload":import_module("difficulty_revision_"+TARGETS[path,tier]).revise(path,tier,v)}
    else:
        old=r._resolve_version(path,tier,v,TARGETS[path,tier])
    p=deepcopy(old['payload'])
    q,a,w,f=p['question_latex'],p['final_answer_latex'],p['worked_solution_latex'],p['facts']
    if path=='angle-units':
        p['rubric']=rubric(('M','Convert both interval bounds consistently.'),('M','Derive the integer inequality with its correct inclusive and exclusive bounds.'),('A','List every admissible integer and no others.'))
    elif path=='solve-cubic':
        p['rubric']=rubric(('M','Substitute the supplied complex root into the known polynomial terms.'),('A','Obtain the correct constant.'),('R','Explain why its coefficient one fixes the constant uniquely.'),('M','Construct the real quadratic factor using the conjugate root.'),('M','Determine the remaining linear factor by exact division or coefficient comparison.'),('A','Give the complete exact root set.'))
    elif path=='solve-quartic':
        p['rubric']=rubric(('M','Substitute the supplied complex root into the known polynomial terms.'),('A','Obtain the correct constant.'),('M','Deduce the conjugate and construct the real monic quadratic factor.'),('M','Use valid polynomial division or equivalent coefficient comparison.'),('A','Obtain the exact remaining quadratic factor.'),('M','Solve the remaining quadratic over the complex numbers, retaining both branches.'),('A','Give the complete exact root set.'))
    elif path=='argument-range':
        z=s.sympify(f[0]); theta=-[s.pi*5/6,s.pi*3/4,s.pi*2/3][v-1]; opposite=theta+s.pi
        q += ' A second number has the opposite real part and the same tangent of its principal argument. Find it and its exact principal argument; explain why it is not on the original ray.'
        a += '; second number '+tex(-z)+', argument '+tex(opposite)+'.'
        w += ['The tangent fixes the slope; reversing the real component therefore reverses the imaginary component. The second number is '+tex(-z)+'.', 'The new principal argument is '+tex(opposite)+', differing by pi from the first. A supporting line contains both rays, but the original argument specifies just one.']
        f += [str(-z),str(opposite)]
        p['rubric']=rubric(('M','Use the tangent relation with the given real component.'),('A','Give the exact first complex number.'),('R','Check the original ray and exclude the opposite direction.'),('M','Use the same slope and opposite real component to recover the second point.'),('A','Give the second point and its exact principal argument, distinguishing the two rays.'))
    elif path=='cartesian-to-polar':
        y,theta=map(s.sympify,f); modulus=2*(v+1); real=s.simplify(modulus*s.cos(theta))
        q=f'A complex number has modulus {modulus} and real part {tex(real)}. Determine all possible imaginary components and exact principal arguments in (-pi,pi]. Identify the one with strictly negative imaginary part and justify completeness.'
        a=f'Imaginary components {tex(y)} and {tex(-y)}, with corresponding arguments {tex(theta)} and {tex(-theta)}; the first is the unique negative branch.'
        w=[f'The squared modulus gives y squared = {modulus**2} - {tex(real**2)} = {tex(y**2)}.',f'The two distinct real roots are {tex(y)} and {tex(-y)}. Both satisfy the modulus equation.',f'The real part is negative; the lower and upper half-plane branches have principal arguments {tex(theta)} and {tex(-theta)} respectively. Only the first imaginary component is strictly negative.']
        f=[str(y),str(theta),str(-y),str(-theta)]
        p['rubric']=rubric(('M','Form and simplify the squared-modulus equation.'),('A','Recover both distinct imaginary components.'),('M','Determine the exact angles with correct quadrant adjustments.'),('A','Give both corresponding principal arguments.'),('R','Justify completeness and identify the unique negative branch.'))
        p['progressive_hints']=['Square the modulus.','Keep both square-root branches before selecting the required sign.']
        p['likely_mistake']='Using only one square root before applying the final sign constraint.'
    elif path=='complex-division':
        a0=v+1; b=v+3; kr=a0*b; ki=-s.Rational(a0,b); qi=-s.Rational(a0,b)*s.I
        q=f'Find every real k for which $({a0}+ki)/(1+{b}i)$ is real, and every real k for which it is purely imaginary. State the quotient in each case and justify that these are the only possibilities.'
        a=f'Real: k={kr}, quotient {a0}. Purely imaginary: k={tex(ki)}, quotient {tex(qi)}.'
        w=[f'Rationalising gives real numerator {a0}+{b}k and imaginary numerator k-{kr}, with denominator {1+b*b}.',f'The imaginary numerator vanishes only at k={kr}; the quotient is {a0}.',f'The real numerator vanishes only at k={tex(ki)}; the quotient is {tex(qi)}.', 'Both equations have nonzero coefficients, and the numerator cannot be zero because its real part is nonzero. These are the only values.']
        f=[str(kr),str(a0),str(ki),str(qi)]
        p['rubric']=rubric(('M','Rationalise or use equivalent component comparison.'),('M','Form and solve the imaginary-component condition for a real quotient.'),('A','Give the correct real-case k and quotient.'),('M','Form and solve the real-component condition for a purely imaginary quotient.'),('A','Give the correct imaginary-case k and quotient.'),('R','Justify both unique values and the nonzero denominator.'))
        p['progressive_hints']=['Write the real and imaginary numerators separately.','Set the appropriate component to zero in each case.']
    elif path=='conjugate-product':
        x=v+1; yy=2*v+5; z=x+yy*s.I; zbar=s.conjugate(z); rat=s.simplify(s.expand_complex(z/zbar)); rat2=s.conjugate(rat)
        q+= ' For each possible y, also express z/conjugate(z) in exact Cartesian form and explain why the two quotients are conjugates.'
        a+=f' For y={yy}, quotient {tex(rat)}; for y={-yy}, quotient {tex(rat2)}.'
        w+=[f'For y={yy}, multiply numerator and denominator by z: the quotient is z squared over {x*x+yy*yy}, namely {tex(rat)}.',f'For y={-yy}, the quotient is {tex(rat2)}. Changing the sign of y conjugates both numerator and denominator, so conjugates the quotient. The denominator is nonzero.']
        f += [str(rat),str(rat2)]
        p['rubric']=rubric(('M','Form the conjugate-product equation.'),('A','Find both signed y values.'),('M','Rationalise each quotient or use the squared numerator divided by the norm-square.'),('A','Give the two exact Cartesian quotients paired with their signs.'),('R','Explain why the quotients are conjugates and the two branches are exhaustive.'))
    elif path=='inverse-systems':
        A=s.Matrix([[v+1,1,0],[1,v+3,1],[0,1,2*v+5]]); X=s.Matrix([v+2,1-v,v+4]); b=A*X; k=s.Symbol('k'); B=s.Matrix([b[0],b[1],k]); inv=A.inv(); Y=inv*B; total=sum(X)
        q=f'Let A={tex(A)} and AX={tex(B)}. The three components of X sum to {total}. Use matrix inversion to determine k and X, verify the original equation and justify uniqueness.'
        a=f'k={b[2]}, X={tex(X)}.'
        w=[f'The determinant is {A.det()}, so A has inverse {tex(inv)}.', f'Multiply the inverse by the symbolic right-hand side to obtain X={tex(Y)}.',f'The component sum is {tex(s.expand(sum(Y)))}; equating to {total} gives k={b[2]}. The coefficient of k is nonzero, so the value is unique.',f'Substitution gives X={tex(X)}. Multiplying by A returns {tex(b)} and the components sum to {total}.']
        f=[str(b[2]),{'matrix':[[str(x)] for x in X]}]
        p['rubric']=rubric(('M','Establish that the coefficient matrix is invertible.'),('M','Obtain its inverse by a valid method.'),('M','Express the solution vector in terms of k.'),('M','Form and solve the component-sum equation.'),('A','Give the correct k and solution vector.'),('R','Verify the equation and sum and justify uniqueness from the nonzero linear coefficient.'))
        p['progressive_hints']=['Keep k symbolic when multiplying by the inverse.','Use the sum of all three solution components.']
    elif path=='related-solids':
        t=s.Rational(1,v+3); rho=t*(1-t)
        q=f'In a nondegenerate tetrahedron OABC, P lies on OA and Q lies on OB with OP/OA=t and OQ/OB=1-t, where 0<=t<=1. The volume of OPQC is {tex(rho)} times that of OABC. Find every admissible t. Determine the maximum possible volume ratio and justify both conclusions without calculus.'
        a=f't={tex(t)} or {tex(1-t)}; maximum ratio {tex(s.Rational(1,4))} at t={tex(s.Rational(1,2))}.'
        w=[f'By multilinearity of the scalar triple product, the volume ratio is t(1-t) throughout the interval.',f'Solve t(1-t)={tex(rho)} to obtain t={tex(t)} or {tex(1-t)}. Both are distinct and lie in [0,1]. A quadratic has no further roots.',f'Complete the square: t(1-t)=1/4-(t-1/2) squared. Its maximum is 1/4, uniquely at t=1/2, including both endpoints in the comparison.']
        f=[str(t),str(1-t),'1/4','1/2']
        p['rubric']=rubric(('M','Use multilinearity to derive the product of the two scale factors.'),('M','Solve the resulting quadratic equation.'),('A','Give both admissible solutions.'),('R','Prove completeness using the interval and degree.'),('M','Complete the square or use equivalent algebraic reasoning to bound the ratio.'),('A','Give the maximum and its unique attaining value.'))
        p['progressive_hints']=['Each changed edge contributes its own scale factor.','Complete the square for the maximum.']
        p['likely_mistake']='Squaring one scale factor although the two edges have different factors.'
    elif path=='vector-plane':
        P=s.Matrix([1,2,3]); u=s.Matrix([v+1,1,1]); h=s.Matrix([1,v+3,-1]); ss=v+2; tt=-v; W=P+ss*u+tt*h; k=s.Symbol('k'); point=s.Matrix([W[0],W[1],k]); n=u.cross(h); C=n.dot(P); det=(v+1)*(v+3)-1
        q=f'The point W={tex(point)} lies on r={tex(P)}+s{tex(u)}+t{tex(h)}. Determine k and both parameters, derive a Cartesian equation of the plane, verify W using it and justify uniqueness.'
        a=f'k={W[2]}, s={ss}, t={tt}; plane {tex(n.dot(s.Matrix(s.symbols("x y z"))))}={C}.'
        w=[f'The first two coordinates give {(v+1)}s+t={W[0]-1} and s+{v+3}t={W[1]-2}. Their determinant is {det}, so the unique solution is s={ss}, t={tt}.',f'The third coordinate then gives k=3+s-t={W[2]}.',f'The cross product of the two directions is {tex(n)}. Its dot product with the base point is {C}, giving the Cartesian equation {tex(n.dot(s.Matrix(s.symbols("x y z"))))}={C}.',f'The dot product with W is {n.dot(W)}, so the recovered point satisfies the Cartesian equation.']
        f=[str(W[2]),str(ss),str(tt),{'matrix':[[str(x)] for x in n]},str(C)]
        p['rubric']=rubric(('M','Set up the coupled first two coordinate equations.'),('M','Solve the two equations using a valid method.'),('A','Give both parameters and the missing coordinate.'),('M','Find a nonzero normal from the independent plane directions.'),('A','Give a valid equivalent Cartesian plane equation.'),('R','Verify membership and show why the parameter system has a unique solution.'))
        p['progressive_hints']=['Use the two coordinates not involving k as simultaneous equations.','Use the same directions to find a normal and verify the point.']
    if path in ('solve-cubic','solve-quartic'):
        x=s.Symbol('x'); c=s.sympify(f[0]); roots=list(map(s.sympify,f[1:])); P=s.Poly(s.prod(x-root for root in roots).expand(),x)
        root=next(root for root in roots if s.im(root)>0)
        terms=[s.expand(coef*root**(P.degree()-i)) for i,coef in enumerate(P.all_coeffs()[:-1])]
        factor=s.expand((x-root)*(x-s.conjugate(root))); quotient,rem=s.div(P.as_expr(),factor,x)
        require(rem==0 and P.TC()==c,'Unexpected polynomial predecessor')
        w=[f'At the supplied root {tex(root)}, the known polynomial terms are '+ ' + '.join(tex(term) for term in terms)+f', summing to {tex(-c)}. Thus k={tex(c)} because the constant enters with coefficient one.',
           f'Real coefficients force the distinct conjugate {tex(s.conjugate(root))}; their monic factor is {tex(factor)}.',
           f'Exact polynomial division (or matching coefficients) gives {tex(quotient)}. Multiplying the two factors gives {tex(P.as_expr())}, with zero remainder.',
           'The complete exact root set is '+', '.join(tex(root) for root in roots)+'. The factors have these roots and their total degree equals the polynomial degree.']
        if path=='solve-quartic':
            centre=-s.Poly(quotient,x).nth(1)/2; constant=s.simplify(quotient-(x-centre)**2)
            w.insert(3,f'Complete the square in the quotient: {tex((x-centre)**2)} = {tex(-constant)}. Both square-root branches give the remaining two non-real roots.')
        else:
            w.insert(3,f'Set the remaining linear factor {tex(quotient)} equal to zero to obtain {tex(roots[0])}.')
    p['question_latex'],p['final_answer_latex'],p['worked_solution_latex'],p['facts']=q,a,w,f
    p['demand_rationale']={
        'angle-units':'Integer-turn enumeration in a mixed-unit half-open interval; distinguish endpoint inclusion from signed conversion.',
        'argument-range':'Recover a ray point then reconstruct the opposite direction; distinguish angle from supporting-line slope.',
        'cartesian-to-polar':'Invert the modulus constraint, retain both branches, and associate each with its exact argument.',
        'complex-division':'Recover parameters for two different axial constraints on a quotient; prove both are exhaustive.',
        'conjugate-product':'Reverse the norm constraint and rationalise both signed solutions; establish conjugation symmetry.',
        'inverse-systems':'Invert a three-variable matrix with a symbolic right-hand side and an extra scalar constraint; verify uniqueness.',
        'related-solids':'Derive a volume ratio from unequal edge scaling; solve both branches and prove its maximum algebraically.',
        'solve-cubic':'Recover an unknown polynomial coefficient from a supplied non-real root, then construct the complete root set.',
        'solve-quartic':'Recover an unknown coefficient, deduce conjugation, divide by the forced quadratic and solve the quotient.',
        'vector-plane':'Recover coupled vector parameters and a missing coordinate, then derive and verify an independent Cartesian equation.',
    }[path] + ' Editorial demand only, not empirical calibration.' 
    return p
