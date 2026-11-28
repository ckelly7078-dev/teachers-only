"""Exact structured evidence for polynomial division, systems and geometry.

Only bounded rational strings, structured operands and fixed operation labels
are accepted from a caller. Unknown methods must remain null. No grade release.
"""
import re
from itertools import permutations
from fractions import Fraction as F
import sympy as s
from active_difficulty import require
from engine_fm17d import reconcile_proposal
from structured_math_fm17d import rational, matrix, obs, flag
from structured_math_fm17e import compare, parse_blocks, ints, cross, cprod, vector

POLYNOMIALS = frozenset(('solve-cubic','solve-quartic'))
SYSTEMS = frozenset(('inverse-three','inverse-systems','matrix-equation','two-variable-system','three-system','three-plane-unique'))
GEOMETRY = frozenset(('line-intersection','line-plane-intersection','line-line-distance','point-plane','point-line','plane-intersection-direction','triangle-area','parallelogram-area','triple-volume','related-solids','line-line-angle'))
DESIGNS = POLYNOMIALS | SYSTEMS | GEOMETRY | {'singular-condition','collapse-parameter','standard-cartesian'}


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(k,a): return tuple(k*x for x in a)
def norm2(a): return dot(a,a)
def identity(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def rows(m): return [[F(x) for x in r] for r in m.tolist()]
def matmul(a,b): return [[dot(r,c) for c in zip(*b)] for r in a]
def same_scalar_fact(f,v): require(len(f)==1 and s.simplify(s.sympify(f[0])-v)==0,'Canonical scalar mismatch')
def same_matrix_fact(f,v): require(matrix(f['matrix'],len(v),len(v[0]))==v,'Canonical matrix mismatch')
def col(v): return [[x] for x in v]
def rvec(m): return tuple(r[0] for r in m)
def proportional(a,b): return any(a) and any(b) and all(a[i]*b[j]==a[j]*b[i] for i in range(len(a)) for j in range(len(a)))


def polynomial(text):
    # Only called on trusted, fingerprint-bound original prompts.
    require(re.fullmatch(r'[0-9x +\-^{}]+',text) is not None,'Unexpected polynomial prompt')
    x=s.Symbol('x'); text=re.sub(r'x\^\{(\d+)\}',r'x**\1',text)
    text=re.sub(r'(\d+)\s*x',r'\1*x',text)
    return s.Poly(s.sympify(text),x)


def division_specs(path,q,f):
    polynomials=re.findall(r'\$([^$]+)\$',q)
    p=polynomial(polynomials[-1]); x=p.gens[0]
    d=s.Poly(x-int(re.search(r'Given that (-?\d+) is a root',q)[1]),x) if path=='solve-cubic' else polynomial(polynomials[0])
    quotient,rem=divmod(p,d); require(rem.is_zero and quotient.degree()==2 and d.LC()==1,'Unexpected division')
    a=list(map(F,p.all_coeffs())); b=list(map(F,d.all_coeffs())); target=list(map(F,quotient.all_coeffs())); n=len(a)
    result=[]; before=a[:]
    for i in range(3):
        term=before[i]/b[0]; after=before[:]
        for j,c in enumerate(b): after[i+j]-=term*c
        result.append(('M',f'reduction_{i+1}',[b,before,term,after])); before=after
    result.append(('A','quotient_and_remainder',[target,before]))
    if path=='solve-cubic':
        a_,b_,c_=target; result.append(('M','quadratic_method',[target,b_*b_-4*a_*c_,2*a_,'both_branches']))
    roots=[tuple(map(F,s.expand_complex(r).as_real_imag())) for r in s.solve(p.as_expr(),x)]
    require(len(roots)==p.degree() and {s.sympify(z) for z in f}=={r+s.I*i for r,i in roots},'Canonical roots mismatch')
    result.append(('A','roots',roots));return result


def combine(weights,aug): return [dot(weights,c) for c in zip(*aug)]


def system_specs(path,q,f):
    blocks=parse_blocks(q)
    if path in ('three-system','three-plane-unique'):
        if path=='three-system':
            b=ints(q,r'Solve x\+y\+z=(-?\d+), x\+2y=(-?\d+), y\+2z=(-?\d+) by elimination and verify all three equations\.')
            a=[[1,1,1],[1,2,0],[0,1,2]];w1=[-1,1,0];w2=[2,-2,-1]
        else:
            b=ints(q,r'Find the common point of x\+y=(-?\d+), x\+z=(-?\d+), y\+z=(-?\d+), and explain why it is unique\.')
            a=[[1,1,0],[1,0,1],[0,1,1]];w1=[1,1,-1]
        b=col(b)
    else:
        a=blocks[0];b=identity(3) if path=='inverse-three' else blocks[1]
    A=s.Matrix(a);B=s.Matrix(b); n=A.rows; inv=rows(A.inv()); solution=rows(A.inv()*B)
    same_matrix_fact(f[-1],solution); aug=[list(r)+list(t) for r,t in zip(a,b)]
    if path=='inverse-three':
        w=[-1,1,0];return [('M','initial_elimination',[w,combine(w,aug)]),('M','complete_elimination',[inv,matmul(inv,aug)]),('A','answer',inv),('R','verification',[a,inv,identity(3)])]
    if path in ('inverse-systems','matrix-equation'):
        if path=='inverse-systems': same_matrix_fact(f[0],inv)
        return [('M','inverse',[a,inv]),('A','answer',solution),('R','verification',[a,solution,b])]
    if path=='two-variable-system':
        w=[a[1][1],-a[0][1]]
        return [('M','equations',aug),('M','eliminate',[w,combine(w,aug)]),('A','answer_and_check',[solution,b])]
    result=[('M','initial_elimination',[w1,combine(w1,aug)])]
    if path=='three-system': result.append(('M','single_variable',[w2,combine(w2,aug)]))
    result.append(('A','answer',solution));result.append(('R','verification',[a,solution,b] if path=='three-system' else [a,solution,b,F(A.det())]));return result


def specifications(item):
    p=item['payload']; path=p['path']; q=p['question_latex'];f=p['facts']
    require(p['tier']==3 and path in DESIGNS,'Structured checker unavailable')
    if path in POLYNOMIALS: specs=division_specs(path,q,f)
    elif path in SYSTEMS: specs=system_specs(path,q,f)
    elif path=='singular-condition':
        a,b=ints(q,r'Find every real k for which \$\\left\[\\begin\{matrix\}k & (\d+)\\\\(\d+) & k\\end\{matrix\}\\right\]\$ is singular\.')
        n=a*b;require({s.sympify(z) for z in f}=={-s.sqrt(n),s.sqrt(n)},'Canonical singular roots mismatch')
        specs=[('M','determinant_equation',[1,0,-n]),('A','signed_root_squares',[[-1,n],[1,n]])]
    elif path=='collapse-parameter':
        a,b=ints(q,r'Find the real k for which \$\\left\[\\begin\{matrix\}k & (\d+)\\\\(\d+) & 1\\end\{matrix\}\\right\]\$ has zero determinant and hence maps every nondegenerate triangle to zero area\.')
        n=a*b;same_scalar_fact(f,n);specs=[('M','determinant_equation',[1,-n]),('A','parameter_and_area_multiplier',[n,0])]
    elif path=='standard-cartesian':
        a,b,c,d=ints(q,r'Write the quotient \(\$(\d+) - (\d+) i\$\)/\(\$(\d+) \+ (\d+) i\$\) in standard Cartesian form with exact real coefficients\.')
        z=(a,-b);w=(c,d);conj=(c,-d); num=cprod(z,conj);den=c*c+d*d;ans=tuple(F(v,den) for v in num)
        require(tuple(map(rational,f))==ans,'Canonical quotient mismatch');specs=[('M','rationalisation',[z,w,conj]),('A','expanded',[num,den]),('A','answer',ans)]
    else:
        blocks=parse_blocks(q); vs=[rvec(b) for b in blocks]
        if path=='line-intersection':
            a,d,b,e=vs; M=s.Matrix.hstack(s.Matrix(d),-s.Matrix(e)); t,u=map(F,M.gauss_jordan_solve(s.Matrix(sub(b,a)))[0]);point=add(a,scale(t,d))
            require(tuple(map(rational,f[:2]))==(t,u),'Canonical intersection parameters mismatch');same_matrix_fact(f[2],col(point))
            specs=[('M','coordinate_equations',[list(d),list(e),sub(b,a),t]),('A','parameters',[t,u]),('A','verified_point',[point,point])]
        elif path=='line-plane-intersection':
            a,b=ints(q,r'Find the intersection of line \$\((\d+)\+t,t,t\)\$ and plane \$x\+y\+z=(\d+)\$\.');t=F(b-a,3);point=(a+t,t,t);same_matrix_fact(f[0],col(point))
            specs=[('M','substitution',[a,3,b]),('A','point',point)]
        elif path=='line-line-distance':
            a,b=ints(q,r'Find the shortest distance between skew lines \$\(t,0,0\)\$ and \$\((\d+),u,(\d+)\)\$ using the scalar triple product\.');same_scalar_fact(f,b)
            specs=[('M','normal_work',[(1,0,0),(0,1,0),(0,0,1)]),('M','displacement',(a,0,b)),('A','distance',b)]
        elif path=='point-plane':
            a=vs[0];b=int(re.search(r'to \$x\+2y\+2z=(-?\d+)\$',q)[1]);n=(1,2,2);v=F(abs(dot(a,n)-b),3);same_scalar_fact(f,v)
            specs=[('M','residual',[a,n,b]),('A','distance',v)]
        elif path=='point-line':
            a=vs[0];d=(1,1,0);c=cross(a,d);v=F(norm2(c),norm2(d));same_scalar_fact(f,s.sqrt(v));specs=[('M','cross_work',[a,d,c]),('A','signed_distance_square',[1,v])]
        elif path=='plane-intersection-direction':
            a,_,b,_=ints(q,r'Find a nonzero direction vector of the common line of the planes \$x\+(\d+)y=(\d+)\$ and \$y\+(\d+)z=(\d+)\$\. Verify perpendicularity to both normals\.');n=(1,a,0);m=(0,1,b);c=cross(n,m);same_matrix_fact(f[0],col(c))
            specs=[('M','normals',[n,m]),('A','direction',c),('R','verification',[c,n,m,0,0])]
        elif path=='line-line-angle':
            a,b=vs;cos=s.Rational(abs(dot(a,b)))/s.sqrt(norm2(a)*norm2(b));angle=s.acos(cos);require(s.simplify(s.sympify(f[0])-cos)==0 and s.simplify(s.sympify(f[1])-angle)==0,'Canonical angle mismatch')
            tenth=F(round(float(s.N(angle*180/s.pi,30))*10),10);specs=[('M','directions',[a,b]),('A','degrees',tenth)]
        else:
            a,b,*rest=vs;c=cross(a,b)
            if path in ('triangle-area','parallelogram-area'):
                v=F(norm2(c),4 if path=='triangle-area' else 1);same_scalar_fact(f[-1:],s.sqrt(v));specs=[('M','cross_work',[a,b,c]),('A','signed_area_square',[1,v])]
            else:
                d=rest[0];v=F(abs(dot(c,d)),6 if path=='related-solids' else 1);same_scalar_fact(f,v);specs=[('M','triple_work',[a,b,c,d]),('A','volume',v)]
    require([(r['type'],r['marks']) for r in p['rubric']]==[(t,1) for t,_,_ in specs],'Unsupported rubric revision');return specs


def linear_observation(value,aug,*,single=False):
    require(isinstance(value,list) and len(value)==2,'Invalid elimination observation')
    w=vector(value[0],len(aug));r=vector(value[1],len(aug[0]));combined=combine(w,aug);n=len(aug)
    # Require an actual combination of equations, with at least one variable
    # cancelled that was present in a contributing equation.
    eliminated=sum(x==0 and any(k and a[j] for k,a in zip(w,aug)) for j,x in enumerate(combined[:n]))
    return sum(x!=0 for x in w)>=2 and tuple(combined)==r and eliminated>=1 and (not single or sum(x!=0 for x in r[:n])==1)


def check_work(engine,item_id,*,mode,item_fingerprint,work):
    context=engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    item=engine.bank.items[item_id];specs=specifications(item);path=item['payload']['path'];expected={k:v for _,k,v in specs}
    require(isinstance(work,dict) and set(work)==set(expected),'Unexpected observation fields'); decisions=[]
    for i,(_,field,e) in enumerate(specs,1):
        v=work[field];status='uncertain' if v is None else flag(compare(v,e))
        if v is not None:
            if field.startswith('reduction_'):
                j=i-1;b=vector(v[0],len(e[0]));before=vector(v[1],len(e[1]));term=rational(v[2]);after=vector(v[3],len(e[3]));prior=work.get(f'reduction_{j}')
                reference=e[1] if j==0 else vector(prior[3],len(before)) if prior is not None else None
                computed=list(before)
                for k,c in enumerate(b): computed[j+k]-=term*c
                good=b==tuple(e[0]) and all(x==0 for x in before[:j]) and term==before[j]/b[0]
                good=good and tuple(computed)==after
                status='uncertain' if good and reference is None else flag(good and before==tuple(reference)) if reference is not None else 'not_met'
            elif field=='quadratic_method':
                coeff=vector(v[0],3);a,b,c=coeff; prior=work['quotient_and_remainder'];ref=vector(prior[0],3) if prior is not None else tuple(e[0]);good=a!=0 and rational(v[1])==b*b-4*a*c and rational(v[2])==2*a and v[3]=='both_branches'
                status=flag(good and coeff==ref) if prior is not None or coeff==ref else 'uncertain' if good else 'not_met'
            elif field=='roots': status=flag(sorted(vector(z,2) for z in v)==sorted(e))
            elif field=='signed_root_squares': status=flag(sorted(vector(z,2) for z in v)==sorted(tuple(z) for z in e))
            elif field=='determinant_equation': status=flag(proportional(vector(v,len(e)),e))
            elif field in ('initial_elimination','single_variable','eliminate'):
                if path=='inverse-three':a=expected['verification'][0];b=identity(3)
                elif path=='two-variable-system':
                    aug=expected['equations'];a=[r[:2] for r in aug];b=[r[2:] for r in aug]
                else:a,b=expected['verification'][0],expected['verification'][2]
                status=flag(linear_observation(v,[list(r)+list(t) for r,t in zip(a,b)],single=field in ('single_variable','eliminate')))
            elif field=='complete_elimination':
                a=expected['verification'][0];T=matrix(v[0],3,3);result=matrix(v[1],3,6);aug=[list(r)+t for r,t in zip(a,identity(3))]
                status=flag(matmul(T,aug)==result and [r[:3] for r in result]==identity(3))
            elif field=='verification' and path=='inverse-three':
                a,b,c=(matrix(z,3,3) for z in v);A=expected['verification'][0];I=identity(3);inv=expected['answer'];status=flag(((a==A and b==inv) or (b==A and a==inv)) and matmul(a,b)==c==I)
                if status=='met' and work['answer'] is not None and not compare(work['answer'],inv):status='uncertain'
            elif field=='verification' and path in SYSTEMS:
                if status=='met' and work['answer'] is not None and not compare(work['answer'],expected['answer']):status='uncertain'
            elif field=='direction':status=flag(proportional(vector(v,3),e))
            elif field=='verification' and path=='plane-intersection-direction':
                d,n,m=(vector(z,3) for z in v[:3]);status=flag(any(d) and proportional(n,e[1]) and proportional(m,e[2]) and dot(d,n)==rational(v[3])==0 and dot(d,m)==rational(v[4])==0)
                if status=='met' and work['direction'] is not None and d!=vector(work['direction'],3):status='uncertain'
            elif field=='normals' or field=='directions':status=flag(all(proportional(vector(z,3),r) for z,r in zip(v,e)))
            elif field in ('cross_work','normal_work'):
                a,b,c=(vector(z,3) for z in v);status=flag(((a,b)==(tuple(e[0]),tuple(e[1])) or (b,a)==(tuple(e[0]),tuple(e[1]))) and c==cross(a,b))
            elif field=='triple_work':
                a,b,c,d=(vector(z,3) for z in v);status=flag((a,b,d) in set(permutations((tuple(e[0]),tuple(e[1]),tuple(e[3])))) and c==cross(a,b))
            elif field=='displacement':status=flag(vector(v,3) in (tuple(e),scale(-1,e)))
        decisions.append(obs(i,status,'Unrecognized or unavailable evidence; interpretation required.' if status=='uncertain' else 'Exact check on the supplied structured observation.'))
    require([r['type'] for r in context['criteria']]==[t for t,_,_ in specs] and all(r['marks']==1 for r in context['criteria']),'Context rubric mismatch')
    result=reconcile_proposal(context,decisions);result['basis']='exact_checks_on_supplied_structured_observations';return result
