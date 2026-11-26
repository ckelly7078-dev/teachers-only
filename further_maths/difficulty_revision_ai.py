"""FM-16AI: original matrix challenge revisions."""
import sympy as s
from calibration_bank import L
from calibration_b_bank import make as trans
from calibration_d_bank import make as det
TARGETS={('collapse',6),('invariant-lines',6),('det-two',6)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not an FM-16AI revision')
    a=s.Integer(v+1); b=a+2; h,k,d=s.symbols('h k d',real=True)
    if path=='collapse':
        p=trans(path,tier,v); U=s.Matrix([1,b]); W=s.Matrix([[a,1]]); C=U*W; X=s.Matrix([0,h]); V=s.Matrix([1,-a])
        q=f'A linear transformation maps the whole plane onto the line y={b}x, maps ({1},{-a}) to the origin and maps (0,1) to (1,{b}). Reconstruct its matrix. For every real h,k determine all preimages of (h,k), and prove both uniqueness of the matrix and completeness of the preimages.'
        ans=f'Matrix {L(C)}. If k={b}h, all preimages are {L(X)}+t{L(V)} for real t; otherwise none.'
        steps=[f'The second column is {L(U)}. Since (1,{-a}) maps to zero, the first column must be {a} times the second. Thus the unique matrix is {L(C)}.',f'The image of (x,y) is ( {a}x+y ) times {L(U)}. Every real scalar occurs, so the image is exactly the required line.',f'A target (h,k) must lie on this image, hence k={b}h. Under that condition {a}x+y=h, giving (x,y)=(0,h)+t(1,{-a}) for arbitrary real t.', 'If the condition fails the target is outside the image; otherwise every point in the displayed line maps to the target. This proves necessity and sufficiency.']
        facts=[*C,*X,*V,b]; hints=['Use the image of (0,1) to find a column.','Use the given zero image to constrain the other column and then solve for a general target.']; mistake='Assuming a singular transformation has a unique inverse image, or failing to check target membership.'
        rationale='Reconstruct a rank-one map from its kernel and a basis image, then classify all target preimages.'
        rub=[('M',1,'Use the zero image to relate the two columns.'),('A',1,'Obtain the unique matrix.'),('R',1,'Prove the image is exactly the specified line.'),('A',2,'Find the target condition and entire preimage line.'),('R',1,'Verify necessity and sufficiency.')]
    elif path=='invariant-lines':
        p=trans(path,tier,v); C=s.Matrix([[1,a],[0,1]]); m=h/a
        q=f'Let T have matrix {L(C)}. Classify all affine lines mapped onto themselves by T, and identify those fixed pointwise. For each real h find all affine lines on which every point is moved by exactly the displacement (h,0). Prove completeness, distinguishing setwise invariance from pointwise motion.'
        ans=f'All horizontal lines y=c are invariant; only y=0 is fixed pointwise. The unique line with displacement (h,0) at every point is y={L(m)}.'
        steps=[f'T sends (x,y) to (x+{a}y,y). On y=c it translates the x-coordinate by {a}c, which is a bijection of that line.',f'A vertical line has direction (0,1), whose image is ({a},1), not parallel to the original. A nonhorizontal nonvertical line has direction (1,m), m nonzero, whose image is (1+{a}m,m). Parallelism would force the multiplier to be 1 from the second component, then {a}m=0, a contradiction.',f'Thus precisely the horizontal lines are invariant. The displacement is ({a}y,0), zero exactly on y=0.',f'The displacement equals (h,0) precisely when y={L(h/a)}, so that horizontal line is the unique full line with the required property. These cases exhaust every affine line.']
        facts=[*C,0,m]; hints=['Apply the map to a direction vector as well as a point.','Subtract each point from its image to determine the displacement.']; mistake='Confusing a line mapping onto itself with each of its points being unchanged.'
        rationale='Classify all invariant directions of a shear and invert a prescribed pointwise displacement, distinct from diagonal scaling.'
        rub=[('M',1,'Obtain the image of a general point.'),('R',2,'Prove that horizontal lines and only those are invariant, including vertical directions.'),('A',1,'Find the fixed-pointwise line.'),('A',1,'Find the unique line for a prescribed displacement.'),('R',1,'Justify the setwise and pointwise distinctions.')]
    else:
        p=det(path,tier,v); P=d+a*b; S=h-d-1; D=S*S-4*P; X=(S-s.sqrt(D))/2; Y=(S+s.sqrt(D))/2
        q=f'Let A have rows (k,{a}) and ({b},l), with k,l real. Given det A=d and det(A+I)=h, where I is the two-by-two identity, find every ordered pair (k,l) for each real pair (d,h). Classify the number of solutions and state when each of A and A+I is invertible. Prove completeness.'
        ans=f'Put S={L(S)} and P={L(P)}. If S squared-4P is negative, none; if zero, one pair (S/2,S/2); if positive, two ordered pairs ({L(X)},{L(Y)}) and the reverse. For every admissible pair A is invertible exactly when d is nonzero and A+I exactly when h is nonzero.'
        steps=[f'det A=kl-{a*b}, hence kl={L(P)}. Also det(A+I)=(k+1)(l+1)-{a*b}=d+k+l+1.',f'Therefore k+l={L(S)}. The two unknown entries are roots of the monic quadratic with sum S and product P.',f'Its discriminant is {L(D)}. Negative gives no real pairs; zero gives one equal-entry pair; positive gives the two orders of its distinct roots {L(X)} and {L(Y)}.', 'Conversely each root pair has the specified sum and product and hence both prescribed determinants. Invertibility follows from the nonzero determinant criterion, including when either target determinant vanishes.']
        facts=[S,P,D,X,Y,0,1,2]; hints=['Expand the determinant of A+I and subtract det A.','Use the sum and product of the diagonal entries to construct a quadratic.']; mistake='Using only one determinant or counting both orders when the diagonal entries coincide.'
        rationale='Use two determinant constraints to recover symmetric data, classify parameter regions and distinguish invertibility of two related matrices.'
        rub=[('M',2,'Derive both determinant relations and the sum and product.'),('A',1,'Construct the quadratic and its discriminant.'),('A',2,'Find every ordered pair and count the boundary case.'),('R',1,'Prove sufficiency and classify invertibility.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(f) for f in facts],rubric=[{'type':t,'marks':m,'criterion':r} for t,m,r in rub]);return p
