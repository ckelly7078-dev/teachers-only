"""Exact structured observations for transformed roots, complex, matrix and vector designs.

No raw-expression evaluation of learner input or grade release. Unsupported
representations are null/uncertain, not presumed incorrect.
"""
import re
from fractions import Fraction as F
from active_difficulty import require
from engine_fm17d import reconcile_proposal
from structured_math_fm17d import rational, pair, obs, flag
from structured_math_fm17e import compare, parse_blocks, ints, cross, cprod, det, vector

ROOTS = frozenset(('reciprocal-sums','reciprocal','shifted-products','shifted-roots','scaled-roots','squared-roots','root-ratios','combined-roots'))
COMPLEX = frozenset(('conjugate-deduction','conjugate-factor','conjugate-find','conjugate-product','identify-components'))
MATRICES = frozenset(('basis-images','det-three','det-area','det-classification','figure-images','zero-matrix'))
VECTORS = frozenset(('cross-order','cross-normal','cross-linearity','vector-plane','vector-line-equation'))
DESIGNS = ROOTS | COMPLEX | MATRICES | VECTORS


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def scale(k,a): return tuple(k*x for x in a)
def determinant(a):
    if len(a)==2: return det(a)
    require(len(a)==3 and all(len(r)==3 for r in a),'Unsupported determinant size')
    return dot(a[0],cross(a[1],a[2]))


def polynomial_fact(f, coefficients):
    import sympy as s
    x=s.Symbol('x')
    require(len(f)==1 and s.Poly(s.sympify(f[0]),x).all_coeffs()==list(coefficients),'Canonical polynomial mismatch')


def complex_fact(f, values):
    import sympy as s
    require(len(f)==len(values) and all(s.expand(s.sympify(t)-a-s.I*b)==0 for t,(a,b) in zip(f,values)),'Canonical complex mismatch')


def matrix_fact(f, value):
    require(len(f)==1 and compare(f[0]['matrix'],value),'Canonical matrix mismatch')


def scalar_fact(f,value): require(len(f)==1 and rational(f[0])==value,'Canonical scalar mismatch')


def specifications(item):
    p=item['payload']; path=p['path']; q=p['question_latex']; f=p['facts']
    require(p['tier']==3 and path in DESIGNS,'Structured checker unavailable')
    if path in ROOTS:
        m=re.findall(r'x\^\{2\} - (\d+) x \+ (\d+)',q);require(len(m)==1,'Unsupported root prompt revision')
        S,P=map(F,m[0]); h=0
        if path in ('shifted-products','shifted-roots','combined-roots'):
            h=F(ints(q,r'.*alpha-(\d+).*beta-\1.*')[0])
        elif path=='scaled-roots': h=F(ints(q,r'Construct the monic equation with roots (-\d+) times .*')[0])
        recover=('M','recover',[[S,1],[P,1],[S,P]])
        shifted=[S-2*h,P-h*S+h*h]
        if path=='reciprocal-sums':
            require(P!=0,'Zero root'); value=S/P; scalar_fact(f,value)
            specs=[recover,('M','transform',['reciprocal_sum',S,P]),('A','answer',value)]
        elif path=='shifted-products':
            value=shifted[1]; scalar_fact(f,value)
            specs=[recover,('M','transform',['shift_product',S,P,h]),('A','answer',value)]
        else:
            if path=='shifted-roots':
                new=shifted; specs=[('M','transform',['shift_both',S,P,h])]
            elif path=='reciprocal':
                require(P!=0,'Zero root'); new=[S/P,1/P]; specs=[('M','transform',['reciprocal_both',S,P])]
            elif path=='scaled-roots':
                new=[h*S,h*h*P]; specs=[recover,('M','transform',['scale_both',S,P,h])]
            elif path=='squared-roots':
                new=[S*S-2*P,P*P]; specs=[recover,('M','transform',['square_both',S,P])]
            elif path=='root-ratios':
                require(P!=0,'Zero root'); new=[S*S/P-2,1]; specs=[('M','transform',['ratio_sum',S,P]),('M','product_reason',['reciprocal_pair',P,1])]
            else:
                require(shifted[1]!=0,'Zero translated root'); new=[shifted[0]/shifted[1],1/shifted[1]]
                specs=[('M','translate',[S,P,h,shifted]),('M','transform',['reciprocal_both',*shifted])]
            coefficients=[1,-new[0],new[1]]; polynomial_fact(f,coefficients); specs.append(('A','coefficients',coefficients))
    elif path in COMPLEX:
        if path=='conjugate-deduction':
            a,b,r=ints(q,r'A real cubic has distinct roots \$(\d+) \+ (\d+) i\$ and (-\d+)\. List all its roots without expanding or solving a polynomial\.')
            values=[(a,-b),(a,b),(r,0)]; complex_fact(f,values)
            specs=[('M','theorem',['real_coefficients_conjugate_pair',(a,b),(a,-b)]),('A','roots',values)]
        elif path=='conjugate-factor':
            a,b=ints(q,r'Construct the monic real quadratic factor corresponding to the known non-real root \$(\d+) \+ (\d+) i\$\.')
            value=[1,-2*a,a*a+b*b]; polynomial_fact(f,value)
            specs=[('M','factors',[(a,b),(a,-b)]),('A','coefficients',value)]
        elif path=='conjugate-find':
            a,b,c=ints(q,r'Expand \((\d+)\+i\)\((\d+)-(\d+)i\) and then find its conjugate in standard form\.')
            re_,im=cprod((a,1),(b,-c)); value=(re_,-im); complex_fact(f,[value])
            specs=[('M','expansion',[(a,1),(b,-c),'i_squared_minus_one']),('A','answer',value)]
        elif path=='conjugate-product':
            a,b,c=ints(q,r'Use the conjugate product to express \((\d+)\+i\)/\((\d+)\+(\d+)i\) in standard form\.')
            numerator=cprod((a,1),(b,-c)); den=b*b+c*c; value=tuple(F(v,den) for v in numerator); complex_fact(f,[value])
            specs=[('M','rationalise',[(a,1),(b,c),(b,-c)]),('A','expanded',[numerator,den]),('A','answer',value)]
        else:
            a,b,c,d,e=ints(q,r'Find the real and imaginary parts of \(\$(\d+) - (\d+) i\$\)-\(\$(\d+) \+ (\d+) i\$\)\+(\d+)i\.')
            value=[a-c,-b-d+e]; require(list(map(rational,f))==value,'Canonical components mismatch')
            specs=[('A','real',value[0]),('A','imaginary',value[1])]
    else:
        blocks=parse_blocks(q)
        if path=='basis-images':
            require(len(blocks)==2 and all(len(m)==2 and all(len(r)==1 for r in m) for m in blocks),'Wrong basis images')
            value=[[a[0],b[0]] for a,b in zip(*blocks)];matrix_fact(f,value);specs=[('A','answer',value)]
        elif path in ('det-three','det-classification','det-area','figure-images','zero-matrix'):
            a=blocks[0]
            if path=='det-three':
                require(len(blocks)==1 and len(a)==3 and all(len(r)==3 for r in a),'Wrong matrix dimensions')
                value=determinant(a);scalar_fact(f,value)
                specs=[('M','cofactors',[[a[0][j],(-1)**j,[[a[i][k] for k in range(3) if k!=j] for i in (1,2)]] for j in range(3) if a[0][j]!=0]),('A','answer',value)]
            elif path=='det-classification':
                require(len(blocks)==3,'Three matrices required');values=[determinant(m) for m in blocks];require(list(map(rational,f))==values,'Canonical determinants mismatch')
                specs=[('A',f'matrix_{i+1}',[v,'singular' if v==0 else 'nonsingular']) for i,v in enumerate(values)]
            elif path=='det-area':
                area=ints(q,r'A triangle has area (\d+) and is transformed by .*')[0];d=det(a);value=area*abs(d);scalar_fact(f,value)
                specs=[('M','area_method',[a,area,'absolute_determinant']),('A','answer',value)]
            elif path=='figure-images':
                point=ints(q,r'Calculate the image of P=\((-?\d+), (-?\d+)\) under .*');value=[dot(row,point) for row in a];matrix_fact(f,[[v] for v in value])
                specs=[('M','ordered_product',[a,point]),('A','answer',value)]
            else:
                b=blocks[1];value=[add(x,y) for x,y in zip(a,b)];matrix_fact(f,value)
                specs=[('M','isolation',['X_equals_A_plus_B',a,b]),('A','answer',value)]
        else:
            require(all(len(m)==3 and all(len(r)==1 for r in m) for m in blocks),'Wrong vector dimensions')
            a,b,*rest=[tuple(r[0] for r in m) for m in blocks];c=cross(a,b)
            if path=='cross-order':
                require(len(f)==2 and compare(f[0]['matrix'],[[v] for v in c]) and compare(f[1]['matrix'],[[v] for v in scale(-1,c)]),'Canonical cross mismatch')
                specs=[('A','forward',c),('A','reverse',['negate_forward',c,scale(-1,c)])]
            elif path=='cross-normal':
                require(any(c) and len(f)==3 and compare(f[0]['matrix'],[[v] for v in c]) and f[1:]==['0','0'],'Canonical normal mismatch')
                specs=[('A','normal',c),('R','verification',[c,a,b,0,0])]
            elif path=='cross-linearity':
                k,l=ints(q,r'.*Use distributivity to expand A cross \((\d+)B-(\d+)C\) and calculate the result\.')
                d=rest[0];value=cross(a,sub(scale(k,b),scale(l,d)));matrix_fact(f,[[v] for v in value])
                specs=[('M','distributive_work',[a,b,d,k,-l,c,cross(a,d)]),('A','answer',value)]
            elif path=='vector-line-equation':
                d=sub(b,a);require(any(d) and len(f)==2 and all(compare(t['matrix'],[[v] for v in z]) for t,z in zip(f,(a,d))),'Canonical line mismatch')
                specs=[('M','direction_work',[b,a]),('A','line',[a,d,'real_parameter'])]
            else:
                d,e=sub(b,a),sub(rest[0],a);n=cross(d,e);require(any(n) and len(f)==3 and all(compare(t['matrix'],[[v] for v in z]) for t,z in zip(f,(a,d,e))),'Canonical plane mismatch')
                specs=[('M','directions',[b,a,rest[0],a]),('R','independence',[d,e,n]),('A','plane',[a,d,e,'real_parameters'])]
    require([(r['type'],r['marks']) for r in p['rubric']]==[(t,1) for t,_,_ in specs],'Unsupported rubric revision')
    return specs


def check_work(engine,item_id,*,mode,item_fingerprint,work):
    context=engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    item=engine.bank.items[item_id];specs=specifications(item);path=item['payload']['path']
    require(isinstance(work,dict) and set(work)=={k for _,k,_ in specs},'Unexpected observation fields')
    decisions=[]
    for i,(_,field,expected) in enumerate(specs,1):
        v=work[field];status='uncertain' if v is None else flag(compare(v,expected))
        if v is not None:
            if field in ('recover','translate'):
                status=flag(compare(v[:-1],expected[:-1]))
            elif field=='transform' and v[0]==expected[0]:
                prior=work.get('recover') or work.get('translate')
                if prior is not None:
                    S,P=pair(prior[-1]);status=flag(pair(v[1:3])==(S,P) and compare(v[3:],expected[3:]) and (v[0] not in ('reciprocal_sum','reciprocal_both') or P!=0))
                elif ('recover' in work or 'translate' in work) and status=='not_met': status='uncertain'
            elif field=='roots': status=flag(sorted(pair(x) for x in v)==sorted(expected))
            elif field=='factors': status=flag(sorted(pair(x) for x in v)==sorted(expected))
            elif field=='verification':
                n,a,b=(vector(x,3) for x in v[:3]);status=flag(any(n) and a==expected[1] and b==expected[2] and dot(n,a)==rational(v[3])==0 and dot(n,b)==rational(v[4])==0)
                if status=='met' and work['normal'] is not None and n!=vector(work['normal'],3): status='uncertain'
            elif field=='independence':
                a,b,n=(vector(x,3) for x in v);normal=expected[2]
                status=flag(any(n) and cross(a,b)==n and dot(a,normal)==dot(b,normal)==0)
                if status=='met' and work['plane'] is not None:
                    plane=work['plane'];require(isinstance(plane,list) and len(plane)==4,'Invalid plane observation')
                    u,w=(vector(x,3) for x in plane[1:3])
                    if (a,b) not in ((u,w),(w,u)): status='uncertain'
            elif field=='plane':
                a,b,c=(vector(x,3) for x in v[:3]);base,u,w=expected[:3];normal=cross(u,w)
                status=flag(v[3]=='real_parameters' and any(cross(b,c)) and dot(sub(a,base),normal)==dot(b,normal)==dot(c,normal)==0)
        decisions.append(obs(i,status,'Unrecognized or unavailable evidence; interpretation required.' if status=='uncertain' else 'Exact check on the supplied structured observation.'))
    require([r['type'] for r in context['criteria']]==[t for t,_,_ in specs] and all(r['marks']==1 for r in context['criteria']),'Context rubric mismatch')
    result=reconcile_proposal(context,decisions);result['basis']='exact_checks_on_supplied_structured_observations';return result
