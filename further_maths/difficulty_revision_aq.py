"""FM-16AQ: reconstruct a plane from two prescribed intersection directions."""
import sympy as s
from calibration_bank import L
from calibration_h_bank import make
TARGETS={('plane-intersection-direction',6)}

def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not FM-16AQ')
    a=s.Integer(v+1); b=a+2; h,k,m=s.symbols('h k m',real=True)
    p=make(path,tier,v); N=s.Matrix([h*k,-k,-h]); C=a*h*k-b*k-h
    q=f'Find every plane P through ({a},{b},1) whose intersections with z=0 and y=0 are lines with directions (1,h,0) and (1,0,k), respectively. For every real h,k classify the number of such planes, give all equations and prove the intersections really are lines.'
    ans=f'If hk is nonzero: the unique plane has normal {L(N)} and constant {L(C)}. If exactly one of h,k is zero: none. If both are zero: infinitely many planes y+m z={b}+m, for every nonzero real m.'
    steps=[f'Write a normal (A,B,C). The two required directions impose A+hB=0 and A+kC=0. The plane must not be parallel to either coordinate plane, so (A,B) and (A,C) must both be nonzero pairs.',f'If hk is nonzero the directions are independent and the normal is proportional to {L(N)}. Both required nonparallel conditions hold, so the plane through the given point is unique, with constant {L(C)}.', 'If h=0 and k is nonzero, A=C=0, forcing a normal parallel to the y-axis. If k=0 and h is nonzero, A=B=0, forcing a normal parallel to the z-axis. Neither can have both required line intersections.',f'If h=k=0, A=0 and both B and C must be nonzero. Normalise B=1 and set C=m, giving y+m z={b}+m for any nonzero real m. Each plane meets both coordinate planes in a line parallel to the x-axis, and distinct m give distinct planes.', 'In each admissible case the required direction is perpendicular to both normals of the intersection, which are independent. Two nonparallel planes always intersect in a line. The normal equations and the point determine all possibilities.']
    facts=[*N,C,b+m,1,0]; hints=['Use orthogonality of the unknown normal to both given directions.','Check that the unknown plane is not parallel to either coordinate plane before counting.']; mistake='Accepting a normal that makes one intersection empty or a whole plane.'; rationale='Reconstruct a plane from two prescribed intersection directions; classify dependent constraints and reject parallel-plane degeneracy.'
    rub=[('M',1,'Derive both normal constraints and nonparallel requirements.'),('A',2,'Find the unique generic normal and plane equation; one mark each.'),('R',1,'Exclude both exactly-one-zero branches.'),('A',1,'Give the entire two-zero plane family, excluding zero slope.'),('R',2,'Verify actual line intersections and prove the classification exhaustive; one mark each.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(s.simplify(f)) for f in facts],rubric=[{'type':t,'marks':n,'criterion':c} for t,n,c in rub]);return p
