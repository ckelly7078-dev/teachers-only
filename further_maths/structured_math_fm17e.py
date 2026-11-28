"""Exact structured evidence for sixteen additional AS1 Tier 3 designs.

No parsing of learner expressions, grading, or change to canonical rubrics.
Null means unobserved/unrecognized, not an incorrect mathematical step.
"""
import re
from fractions import Fraction as F
from collections import Counter
from active_difficulty import require
from structured_math_fm17d import rational, pair, matrix, obs, flag
from engine_fm17d import reconcile_proposal

DESIGNS = frozenset(('root-squares','cube-sums','quadratic-from-roots','complex-discriminant',
    'cartesian-product','cartesian-sums','complex-division','argument-normalization',
    'det-two','inverse-two','composition-order','matrix-add-subtract',
    'scalar-product','cross-product','vector-combinations','zero-cross'))


def vector(v,n):
    require(isinstance(v,list) and len(v)==n,'Wrong vector length')
    return tuple(map(rational,v))


def matmul(a,b):
    return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]


def cross(a,b):
    return tuple(a[i]*b[j]-a[j]*b[i] for i,j in ((1,2),(2,0),(0,1)))


def det(a):
    return a[0][0]*a[1][1]-a[0][1]*a[1][0]


def cprod(a,b):
    x,y=a; u,v=b
    return (x*u-y*v,x*v+y*u)


def parse_blocks(q):
    return [[[rational(x.strip()) for x in r.split('&')] for r in block.split(r'\\')]
            for block in re.findall(r'\\begin\{matrix\}(.*?)\\end\{matrix\}',q)]


def ints(q,pattern):
    m=re.fullmatch(pattern,q); require(m is not None,'Unsupported prompt revision')
    return tuple(map(int,m.groups()))


def compare(actual,expected):
    """Compare bounded structured values only; lists preserve position."""
    if isinstance(expected,(int,F)):
        return rational(actual)==expected
    if isinstance(expected,str):
        require(isinstance(actual,str) and len(actual)<=100,'Invalid symbolic label')
        return actual==expected
    if isinstance(expected,(tuple,list)):
        require(isinstance(actual,list) and len(actual)==len(expected),'Invalid structured shape')
        return all([compare(a,b) for a,b in zip(actual,expected)])
    raise ValueError('Unsupported checker contract')


def specifications(item):
    """Derive expected observations from trusted current prompt, not learner data."""
    p=item['payload']; path=p['path']; q=p['question_latex']; f=p['facts']
    require(p['tier']==3 and path in DESIGNS,'Structured checker unavailable')
    # Each criterion: type, field name, expected structured observation.
    if path in ('root-squares','cube-sums','complex-discriminant'):
        if path=='root-squares':
            a,b,c=ints(q,r'The roots of \$(\d+) x\^\{2\} - (\d+) x \+ (\d+)\$ \$=0\$ are \$u,v\$\. Without solving the equation, calculate \$u\^2\+v\^2\$\.')
            S,P=F(b,a),F(c,a); result=S*S-2*P
            specs=[('M','identity_work',[[[b,a],[c,a]],'S_squared_minus_2P']),('A','answer',result)]
        elif path=='cube-sums':
            b,c=ints(q,r'Find the sum of cubes of the roots of \$x\^\{2\} - (\d+) x \+ (\d+)\$=0 without solving it\.')
            S,P=F(b),F(c); result=S**3-3*S*P
            specs=[('M','coefficient_ratios',[[[b,1],[c,1]],[S,P]]),('M','identity_work',['S_cubed_minus_3SP',S,P]),('A','answer',result)]
        else:
            a,b,c=ints(q,r'Classify the roots of \$(\d+) x\^\{2\} \+ (\d+) x \+ (\d+)\$=0 by calculating its discriminant, without solving it\.')
            result=b*b-4*a*c
            require(result<0,'Unexpected root classification')
            specs=[('M','discriminant_work',['b_squared_minus_4ac',a,b,c]),('A','answer',[result,'two_distinct_nonreal_conjugates'])]
        require(len(f)==1 and rational(f[0])==result,'Canonical scalar mismatch')
    elif path=='quadratic-from-roots':
        S,P=ints(q,r'Construct the monic quadratic equation whose roots have sum (-?\d+) and product (-?\d+), without finding either root\.')
        result=[1,-S,P]
        import sympy as s
        x=s.Symbol('x'); require(len(f)==1 and s.Poly(s.sympify(f[0]),x).all_coeffs()==result,'Canonical polynomial mismatch')
        specs=[('M','identity_work',['x_squared_minus_Sx_plus_P',S,P]),('A','coefficients',result)]
    elif path in ('cartesian-product','cartesian-sums','complex-division'):
        patterns={'cartesian-product':r'Expand \$\((\d+) \+ (\d+) i\)\((\d+) - (\d+) i\)\$ and write the result in Cartesian form\.',
            'cartesian-sums':r'Calculate both \$(\d+) \+ (\d+) i\$ plus \$(\d+) - (\d+) i\$ and \$\1 \+ \2 i\$ minus \$\3 - \4 i\$ in Cartesian form\.',
            'complex-division':r'Write \$(\d+) \+ (\d+) i\$ divided by \$(\d+) \+ (\d+) i\$ in Cartesian form\.'}
        a,b,c,d=ints(q,patterns[path]); z=(a,b); w=(c,d if path=='complex-division' else -d)
        if path=='cartesian-product':
            values=[cprod(z,w)]; specs=[('M','expansion',[z,w,'i_squared_minus_one']),('A','answer',values[0])]
        elif path=='cartesian-sums':
            values=[(a+c,b-d),(a-c,b+d)]; specs=[('A','sum',values[0]),('A','difference',values[1])]
        else:
            conj=(c,-d); norm=c*c+d*d; require(norm!=0,'Zero divisor')
            values=[tuple(F(v,norm) for v in cprod(z,conj))]
            specs=[('M','rationalisation',[z,w,conj]),('A','answer',values[0])]
        import sympy as s
        require(len(f)==len(values) and all(s.expand(s.sympify(v)-(a+s.I*b))==0 for v,(a,b) in zip(f,values)),'Canonical complex mismatch')
    elif path=='argument-normalization':
        n,d=ints(q,r'Normalize the angle \$\\frac\{(\d+) \\pi\}\{(\d+)\}\$ to the principal range \$\(-\\pi ,\\pi \]\$\.')
        angle=F(n,d); k=(1-angle)//2; ans=angle+2*k
        if ans<=-1: ans+=2; k+=1
        import sympy as s
        require(-1<ans<=1 and len(f)==1 and s.simplify(s.sympify(f[0])-ans*s.pi)==0,'Canonical angle mismatch')
        specs=[('M','full_turn_work',[angle,k]),('A','answer_pi_multiple',ans)]
    else:
        blocks=parse_blocks(q)
        if path in ('det-two','inverse-two','composition-order','matrix-add-subtract'):
            require(len(blocks)==(1 if path in ('det-two','inverse-two') else 2) and all(len(a)==2 and all(len(r)==2 for r in a) for a in blocks),'Wrong matrix dimensions')
            a=blocks[0]
            if path=='det-two':
                result=det(a); require(q.startswith('Calculate the signed determinant') and f==[str(result)],'Canonical determinant mismatch')
                specs=[('M','diagonal_products',[[a[0][0],a[1][1]],[a[0][1],a[1][0]]]),('A','answer',result)]
            elif path=='inverse-two':
                d=det(a); require(d!=0 and q.endswith('and verify it by multiplication.'),'Unsupported inverse')
                adj=[[a[1][1],-a[0][1]],[-a[1][0],a[0][0]]]; result=[[v/d for v in row] for row in adj]
                specs=[('M','inverse_work',[[[a[0][0],a[1][1]],[a[0][1],a[1][0]]],adj,d,d]),('A','answer',result),('R','verification',[a,result,[[1,0],[0,1]]])]
            else:
                b=blocks[1]
                if path=='composition-order':
                    require(' followed by ' in q,'Composition order unavailable'); result=matmul(b,a); work=[b,a]; field='ordered_factors'
                else:
                    require(q.startswith('Calculate A-2B '),'Unsupported matrix operation'); result=[[x-2*y for x,y in zip(r,t)] for r,t in zip(a,b)]; work=[a,b,-2]; field='signed_operation'
                specs=[('M',field,work),('A','answer',result)]
            if path!='det-two': require(len(f)==1 and matrix(f[0]['matrix'],2,2)==result,'Canonical matrix mismatch')
        else:
            require(len(blocks)==2 and all(len(a)==3 and all(len(r)==1 for r in a) for a in blocks),'Wrong vector dimensions')
            a,b=(tuple(r[0] for r in block) for block in blocks)
            if path=='scalar-product':
                result=sum(x*y for x,y in zip(a,b)); require(f==[str(result)],'Canonical scalar product mismatch')
                specs=[('M','component_products',list(zip(a,b))),('A','answer',result)]
            else:
                result=tuple(2*x-3*y for x,y in zip(a,b)) if path=='vector-combinations' else cross(a,b)
                require(vector([r[0] for r in f[0]['matrix']],3)==result,'Canonical vector mismatch')
                if path=='vector-combinations':
                    require(q.startswith('Calculate 2u-3v'),'Unsupported vector operation'); specs=[('M','scaled_vectors',[2,a,-3,b]),('A','answer',result)]
                elif path=='cross-product': specs=[('A',f'component_{i+1}',v) for i,v in enumerate(result)]
                else:
                    k=b[next(i for i,v in enumerate(a) if v)]/next(v for v in a if v)
                    require(result==(0,0,0) and tuple(k*v for v in a)==b and k!=0 and rational(f[1])==k,'Canonical parallelism mismatch')
                    specs=[('A','cross_product',result),('R','parallel_work',['parallel',k,a,b])]
    require([(r['type'],r['marks']) for r in p['rubric']]==[(t,1) for t,_,_ in specs],'Unsupported rubric revision')
    return specs


def check_work(engine,item_id,*,mode,item_fingerprint,work):
    """Accept exact field observations or null (unrecognized/unavailable)."""
    context=engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    item=engine.bank.items[item_id]; specs=specifications(item)
    require(isinstance(work,dict) and set(work)=={k for _,k,_ in specs},'Unexpected observation fields')
    decisions=[]
    for i,(_,field,expected) in enumerate(specs,1):
        value=work[field]
        status='uncertain' if value is None else flag(compare(value,expected))
        path=item['payload']['path']
        if value is not None:
            if field=='diagonal_products':
                status=flag([sorted(pair(v)) for v in value]==[sorted(v) for v in expected])
            elif field=='component_products':
                status=flag(Counter(tuple(sorted(pair(v))) for v in value)==Counter(tuple(sorted(v)) for v in expected))
            elif path=='cartesian-product' and field=='expansion':
                status=flag(value[2]==expected[2] and Counter(pair(v) for v in value[:2])==Counter(expected[:2]))
            elif path=='root-squares' and field=='identity_work':
                ratios=tuple(pair(v) for v in value[0]); raw=tuple(tuple(v) for v in expected[0])
                monic=tuple((F(n,d),1) for n,d in raw)
                status=flag(value[1]==expected[1] and ratios in (raw,monic))
        if value is not None and path=='cube-sums':
            if field=='coefficient_ratios':
                # A valid ratio setup may precede an arithmetic slip.
                status=flag(compare(value[0],expected[0]))
            elif field=='identity_work' and value[0]=='S_cubed_minus_3SP':
                previous=work['coefficient_ratios']
                if previous is not None:
                    status=flag(pair(value[1:])==pair(previous[1]))
                elif status=='not_met':
                    status='uncertain'
        if value is not None and path=='inverse-two':
            if field=='inverse_work':
                # A mistaken determinant can retain method credit if the
                # correct adjugate is divided by that same nonzero value.
                status=flag(compare(value[:2],expected[:2]) and rational(value[2])!=0
                            and rational(value[2])==rational(value[3]))
            elif field=='verification':
                a,b,c=(matrix(m,2,2) for m in value)
                source=expected[0]; inv=expected[1]; identity=[[1,0],[0,1]]
                status=flag(((a==source and b==inv) or (a==inv and b==source)) and matmul(a,b)==c==identity)
                if status=='met' and work['answer'] is not None and not compare(work['answer'],inv):
                    status='uncertain'  # Verification refers to a different inverse than the reported answer.
        decisions.append(obs(i,status,'Unrecognized or unavailable evidence; interpretation required.' if status=='uncertain' else 'Exact comparison with the supported structured observation.'))
    require([r['type'] for r in context['criteria']]==[t for t,_,_ in specs] and all(r['marks']==1 for r in context['criteria']),'Context rubric mismatch')
    result=reconcile_proposal(context,decisions)
    result['basis']='exact_checks_on_supplied_structured_observations'
    return result
