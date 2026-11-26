"""FM-16AD additive revisions; original FM-16AB generators remain historical."""
import sympy as s
from calibration_bank import L
from calibration_bank import make as base_make
from calibration_z_bank import make as z_make

TARGETS={('complex-division',6),('cartesian-product',4),('argument-range',6),('angle-units',6)}
ENRICHMENT={'complex-regions','conjugate-product','cross-linearity','cube-sums','describe-transform','exact-radians','matrix-add-subtract','matrix-products','polar-quotients','standard-cartesian','vector-combinations','angle-units'}
SYSTEM_FAMILY={'system-consistency','system-classification','three-system','three-plane-unique'}

def design_metadata(path,tier):
    return {'scope':'enrichment_only' if tier==6 and path in ENRICHMENT else 'scope_review_pending',
            'family':'parameter-system-reduction' if tier==6 and path in SYSTEM_FAMILY else None,
            'teacher_approved':False}

def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not an FM-16AD revision')
    a=s.Integer(v+1); b=a+2; h,k,t=s.symbols('h k t',real=True)
    p=(base_make if path=='complex-division' else z_make)(path,tier,v)
    if path=='angle-units':
        p['demand_rationale']='Enrichment only: compare mixed-unit congruences under a half-angle restriction and prove completeness.'
        return p
    if path=='complex-division':
        D=a*a-k*k; X=-k*h/D; Y=a*h/D
        q=f'For real h,k, find all real x,y such that ({2*a}x+hi)/(x+yi) = {a}+ki. The denominator must be nonzero. Classify every parameter pair and prove completeness.'
        ans=f'For k not equal to plus or minus {a} and h nonzero: x={L(X)}, y={L(Y)}. For k={a} and h=0: y=-x, x nonzero. For k={-a} and h=0: y=x, x nonzero. Otherwise no solution.'
        steps=[f'Multiply by x+yi, requiring (x,y) not equal to (0,0). Equating components gives {a}x+ky=0 and kx+{a}y=h.',f'The determinant is {L(D)}. When it is nonzero, elimination gives x={L(X)}, y={L(Y)}. The pair is nonzero exactly when h is nonzero.',f'When k={a}, the equations require x+y=0 and {a}(x+y)=h. Thus h=0 is necessary and sufficient, with y=-x and x nonzero.',f'When k={-a}, the first equation requires x=y and the second forces h=0. All x=y nonzero work. These cases exhaust the parameters; multiplying back verifies the original quotient.']
        facts=[X,Y,a,-a,True,False]; hints=['Cross-multiply only after recording the denominator restriction.','Compare the determinant-zero cases separately.']; mistake='Accepting the zero denominator or dividing by a vanishing determinant.'
        rationale='Classify a complex quotient with unknown denominator components and two parameters; separate singular consistency from domain restrictions.'
        criteria=[('M',1,'Cross-multiply and equate both components, retaining the nonzero denominator.'),('A',1,'Obtain both regular-case component formulas.'),('R',1,'Justify exactly when the regular pair is admissible.'),('R',2,'Classify both singular cases with their nonzero families and prove completeness.')]
    elif path=='cartesian-product':
        T=(a-b)/(a+b); Z=s.expand((a+b*s.I)*(1+T*s.I)); C=s.re(Z)
        q=f'Let z={L(a+b*s.I)}. Find the real t for which multiplying z by 1+ti gives a point on the ray with principal argument pi/4. Give the exact Cartesian product and justify that the ray condition, not merely its supporting line, is satisfied.'
        ans=f't={L(T)}; product {L(Z)}.'
        steps=[f'Expand to obtain real part {L(a-b*t)} and imaginary part {L(b+a*t)}.',f'Equal components require {a}-{b}t={b}+{a}t; since {a+b} is nonzero, t={L(T)} is unique.',f'Substitution gives both components equal to {L(C)}, which is positive, so the product is on the required ray, not its opposite. Thus {ans}']
        facts=[T,Z,True]; hints=['Expand before applying the geometric condition.','Equal components alone permit the opposite ray; check their signs.']; mistake='Using equality of components without checking the direction of the ray.'
        rationale='Link Cartesian multiplication to an exact argument condition and verify the ray direction.'
        criteria=[('M',1,'Obtain the two product components and impose equality.'),('A',1,'Find the unique t and exact product.'),('R',1,'Verify positivity and distinguish the ray from the opposite ray.')]
    else:
        # Both coordinates vary, and the imaginary component is quadratic.
        A=s.atan(h-b); H=b-1
        q=f'Let z=(h-{a})+i(h-{a})(h-{b}), where h is real. Determine its principal argument in (-pi,pi] for every h, including axis and origin cases. Hence solve arg(z)=-pi/4 and arg(z)=3pi/4 separately, proving completeness.'
        ans=f'h<{a}: {L(A+s.pi)} (quadrant II); h={a}: undefined; {a}<h<{b}: {L(A)} (quadrant IV); h={b}: 0; h>{b}: {L(A)} (quadrant I). Argument -pi/4 occurs at h={H}; argument 3pi/4 has no solution.'
        steps=[f'The real component changes sign at h={a}; the imaginary component is zero at h={a} or h={b}. At h={a} both components vanish.',f'For h<{a}, the real part is negative and imaginary part positive. The tangent ratio is h-{b}, negative; adding pi to arctan(h-{b}) gives the principal argument in quadrant II.',f'For h>{a}, the real part is positive, so arctan(h-{b}) is already principal. It is negative below {b}, zero at {b}, and positive above {b}.',f'Both requested angles have tangent -1, forcing h={H}. Since {H}>{a} and {H}<{b}, the point is in quadrant IV. Only -pi/4 is attained; 3pi/4 is not. The origin was excluded, so no extra solutions exist.']
        facts=[a,b,A+s.pi,A,H,False]; hints=['Find the zeros and signs of both components before cancelling.','Use the tangent ratio only away from the origin, then choose the correct quadrant.']; mistake='Cancelling h-a without excluding the origin, or accepting an angle from the wrong quadrant.'
        rationale='Determine moving-point quadrant boundaries and piecewise principal arguments; use inverse conditions to reject an apparent solution.'
        criteria=[('M',1,'Identify both component zeros and the origin exception.'),('R',1,'Justify the quadrant-II branch.'),('A',1,'Give the correct principal argument on all positive-real branches.'),('R',1,'Solve both angle constraints and reject the wrong quadrant.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[x if type(x) is bool else str(x) for x in facts],rubric=[{'type':c,'marks':m,'criterion':r} for c,m,r in criteria])
    return p
