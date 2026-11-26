"""Original algebra difficulty revisions, additive to earlier overlays."""
import sympy as s
from calibration_bank import L,make as base
from calibration_s_bank import make as scaled
TARGETS={('scaled-roots',4),('root-squares',6),('reciprocal',6)}
def revise(path,tier,v):
    if (path,tier) not in TARGETS or v not in (1,2,3): raise ValueError('Not an FM-16AF revision')
    a=s.Integer(v+1); b=a+2; x,h,k,d,c=s.symbols('x h k d c',real=True)
    p=(scaled if path=='scaled-roots' else base)(path,tier,v)
    if path=='scaled-roots':
        S=a+b; P=a*b; m=-b; F=x*x-S*x+P; G=x*x-m*S*x+m*m*P; H=G+1
        first,second=(G,H) if v%2 else (H,G)
        label='first' if v%2 else 'second'; wrong='second' if v%2 else 'first'
        q=f'The roots of ${s.latex(2*F.expand())}=0$ are multiplied by the same real number m. Exactly one of the monic equations ${s.latex(first)}=0$ and ${s.latex(second)}=0$ can result. Identify it, find m, and explain why matching the root sum alone is insufficient.'
        ans=f'The {label} equation; m={m}. The {wrong} has the same sum but the wrong product.'
        steps=[f'Dividing the original equation by 2 gives sum {S} and product {P}. Both proposed equations have sum {m*S}.',f'Scaling changes the sum to {S}m, so the sum uniquely forces m={m}.',f'The product must then be {P} times m squared, equal to {m*m*P}. Only the {label} equation has that constant. The other constant is {m*m*P+1}.', f'The sum and product fix a monic quadratic, so the {label} is sufficient and the {wrong} is impossible.']
        facts=[m,G,v%2==1,v%2==0]; hints=['Normalize the original leading coefficient.','Use the sum to force a scale, then check the product independently.']; mistake='Matching one coefficient while ignoring how the other scales.'
        rationale='Compare two candidate target equations using both coefficient invariants of a common scale, not two successive routine scalings.'
        rub=[('M',1,'Normalize the polynomial and recover its signed root sum and product.'),('A',1,'Determine the unique scale from the candidate sum.'),('R',2,'Check both constants and justify necessity and sufficiency.')]
    elif path=='root-squares':
        C=a*a+b*b; low=-C/2; high=C/2; S=s.sqrt(C+2*h); G=x*x-S*x+h; H=x*x+S*x+h
        q=f'For every real h find every monic real quadratic with two real roots (counting multiplicity) whose squares sum to {C} and whose product is h. Count the distinct equations and classify the signs of the roots, including zero and repeated roots. Prove completeness.'
        ans=f'None outside [{L(low)}, {L(high)}]. At h={L(low)} one equation {L(x*x+low)}=0. For {L(low)}<h<={L(high)} two equations {L(G)}=0 and {L(H)}=0. Negative product: opposite signs; zero product: one zero root; positive product: both signs equal, determined by the sum. Repeated roots only at h={L(high)}.'
        steps=[f'Let S be the original root sum. The sum-of-squares identity gives $S^2={C}+2h$, so $h\\geq {s.latex(low)}$.',f'Real roots require discriminant $S^2-4h={C}-2h\\geq0$, hence $h\\leq {s.latex(high)}$.',f'At the lower endpoint S=0, so there is one equation. Elsewhere in the admissible interval S has two nonzero opposite values, giving {L(G)} and {L(H)} set equal to zero.',f'If h is negative the two real roots have opposite signs. At h=0 one is zero and the other is the nonzero sum. If h is positive the roots have the same sign as S. At the upper endpoint the discriminant alone is zero, giving a repeated root in each equation.', 'Conversely each constructed equation has the stated product, nonnegative discriminant and square sum by the identity. All possible sums were exhausted.']
        facts=[low,high,G,H,1,2,high]; hints=['Write the square of the sum using the given sum of squares.','The root sum must be real, and so must the roots: use both inequalities.']; mistake='Checking only that the root sum is real, not that the discriminant is nonnegative.'
        rationale='Intersect two independent inequalities, reconstruct all original equations and classify root signs and multiplicity.'
        rub=[('M',1,'Derive the squared sum identity.'),('R',2,'Derive and intersect the two necessary inequalities.'),('A',2,'Construct all equations with correct endpoint counts.'),('R',2,'Classify signs and repeated roots and prove sufficiency.')]
    else:
        P=a*b; r=s.Symbol('r'); K=2*s.sqrt(P)
        q=f'The roots of $x^2-kx+{P}=0$ (k real, roots may be complex) are each transformed by $r\\mapsto c/(r-d)$, where c,d are real. Find all ordered pairs (c,d) that preserve the original root multiset, for every real k. Exclude undefined transformations and distinguish repeated roots. Prove completeness.'
        ans=f'For k not equal to plus or minus {L(K)}: (c,d)=({P},0) or ({-P},k). At k=plus or minus {L(K)}, write r=k/2: c=r(r-d) with d real and d not equal to r.'
        steps=[f'Let the roots be u,v; their sum is k and product is {P}, so neither is zero. A preserving transformation has nonzero denominators and nonzero c.',f'If u and v are distinct, the transformation must either fix each or interchange them. In the fixed case c=u(u-d)=v(v-d), so $(u-v)(u+v-d)=0$ gives d=k and c=-{P}. Then u-d=-v and v-d=-u, both nonzero.',f'In the interchange case c=v(u-d)=u(v-d); subtracting gives d(u-v)=0, so d=0 and c={P}. These denominators are also nonzero.',f'The repeated-root case is precisely $k^2=4({P})$. With r=k/2, preservation is equivalent to c=r(r-d) and d not equal to r. Here r is nonzero, so c is nonzero automatically.', 'The distinct-root permutations and repeated-root case exhaust all multisets, including non-real conjugates. Every listed pair satisfies the original map.']
        facts=[P,0,-P,k,-K,K,(k/2)*(k/2-d),k/2]; hints=['A map preserving two distinct roots either fixes both or interchanges them.','For repeated roots only one equation remains; retain the original denominator restriction.']; mistake='Assuming a multiset-preserving map must interchange distinct roots or treating a repeated root as two independent constraints.'
        rationale='Enrichment only: determine every reciprocal transformation preserving a root multiset by distinguishing permutations and repeated-root freedom.'
        rub=[('M',1,'Identify both permutations and the nonzero conditions.'),('R',2,'Derive the unique fixed-root pair and verify denominators.'),('R',2,'Derive the unique interchange pair and verify denominators.'),('A',1,'Find repeated-root parameter values.'),('R',2,'Give the full repeated-root family and establish completeness.')]
    p.update(question_latex=q,final_answer_latex=ans,worked_solution_latex=steps,progressive_hints=hints,likely_mistake=mistake,demand_rationale=rationale,facts=[z if type(z) is bool else str(z) for z in facts],rubric=[{'type':t,'marks':m,'criterion':r} for t,m,r in rub])
    return p
