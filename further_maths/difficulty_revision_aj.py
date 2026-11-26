"""FM-16AJ: inverse reconstruction and comparison of two systems."""
import sympy as s
from calibration_bank import L
from calibration_b_bank import make as bmake
from calibration_o_bank import make as omake
TARGETS={('inverse-two',6),('inverse-systems',6)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not FM-16AJ')
    a=s.Integer(v+1); b=a+2; k,h,r=s.symbols('k h r',real=True)
    if path=='inverse-two':
        p=bmake(path,tier,v); Q=s.sqrt(a/r-a*b); C=s.Matrix([[Q,a],[b,-Q]]); J=s.Matrix([[r*Q/a,r],[b*r/a,-r*Q/a]])
        q=f'A real matrix C has rows (k,{a}) and ({b},l). Its inverse exists, has diagonal entries summing to zero and upper-right entry r. For each real r find every possible C and its inverse. Count the distinct matrices and prove completeness.'
        ans=f'No matrix unless 0<r<={L(1/b)}. In the admissible interval, k=+/-{L(Q)}, l=-k; the inverse has rows (rk/{a},r) and ({b}r/{a},-rk/{a}). One matrix at r={L(1/b)}, two otherwise.'
        steps=[f'Write D=kl-{a*b}. Since D is nonzero, the inverse has diagonal sum (k+l)/D, forcing l=-k.',f'Then D=-k squared-{a*b}, strictly negative. The inverse upper-right entry is {a}/(k squared+{a*b}), so r must be positive and at most {L(1/b)}.',f'Rearranging gives k squared={L(a/r-a*b)}, producing both signs of {L(Q)} except at the upper endpoint, where k=0.',f'Substituting l=-k and D=-{a}/r into the inverse formula gives the stated entries. Each candidate is invertible and satisfies both constraints, so the counts are exhaustive.']
        facts=[1/b,Q,*C,*J,0,1,2]; hints=['Use the diagonal sum of the inverse before solving for r.','The sign of the determinant follows once l=-k.']; mistake='Allowing r=0 or counting both signs at the zero radicand.'; rationale='Reconstruct an inverse family from two entry constraints and classify exact parameter bounds.'
        rub=[('M',1,'Use the inverse formula and diagonal constraint.'),('R',2,'Derive the sharp range of r.'),('A',2,'Recover both matrices and their inverses.'),('R',1,'Verify invertibility, boundary count and completeness.')]
    else:
        p=omake(path,tier,v); C=s.Matrix([[a,1],[k,b]]); D=a*b-k; B=s.Matrix([1,h]); E=s.Matrix([2,2*h+1]); X=s.Matrix([b-h,a*h-k])/D; Y=s.Matrix([2*b-2*h-1,a*(2*h+1)-2*k])/D
        q=f'Let C have rows ({a},1) and (k,{b}). Compare CX=(1,h)^T and CY=(2,2h+1)^T for every real k,h. Find both solutions using an inverse when possible and prove whether the two solution vectors are independent. In the singular case classify compatibility of each system and give every solution of any compatible system.'
        ans=f'If k differs from {a*b}, X={L(X)}, Y={L(Y)}; their determinant is {L(1/D)}, so independent. If k={a*b}, only the first is compatible at h={b}; only the second at h={L(b-s.Rational(1,2))}; otherwise neither. Compatible families: (t,1-{a}t) or (t,2-{a}t) respectively.'
        steps=[f'The determinant is {L(D)}. For nonzero D use the inverse on each right-hand side, giving {L(X)} and {L(Y)}.',f'The two right-hand sides form a matrix with determinant 1. Multiplying it by the inverse gives determinant 1/D, nonzero, so the solutions are independent.',f'At k={a*b}, row two is {b} times row one. Compatibility of the first requires h={b}; compatibility of the second requires 2h+1={2*b}, or h={L(b-s.Rational(1,2))}. These are distinct, so never both compatible.',f'For the first compatible system choose x=t and y=1-{a}t; for the second choose x=t and y=2-{a}t. In each case t is arbitrary real. For every other h neither is compatible. The determinant and row dependence cases exhaust all k,h.']
        facts=[a*b,*X,*Y,1/D,b,b-s.Rational(1,2)]; hints=['Use the same inverse for both RHS columns.','When the matrix is singular, compare RHS proportionality separately.']; mistake='Assuming the two systems have the same compatibility condition because their coefficient matrix is identical.'; rationale='Compare two right-hand sides under one inverse, prove independence by determinant and classify distinct singular compatibility conditions.'
        rub=[('M',1,'Find determinant and inverse condition.'),('A',2,'Find both regular solution vectors.'),('R',1,'Prove independence using the RHS determinant.'),('R',2,'Derive distinct singular compatibility conditions.'),('A',1,'Give all compatible solutions and exclude remaining cases.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[str(f) for f in facts],rubric=[{'type':t,'marks':m,'criterion':c} for t,m,c in rub]);return p
