"""FM-16BN9: version-bound vector written-answer and derivation repairs."""
from importlib import import_module
import re
from active_difficulty import require

TARGETS = {('vector-components', 2): 'bf', ('vector-components', 4): 'bf', ('vector-components', 6): 'bf', ('vector-combinations', 2): 'bf', ('vector-combinations', 5): 'bf', ('vector-combinations', 6): 'bf', ('unit-vector', 2): 'bf', ('unit-vector', 4): 'bf', ('unit-vector', 5): 'bk', ('scalar-product', 6): 'ao', ('perpendicular-test', 3): 'bf', ('perpendicular-test', 4): 'bf', ('perpendicular-test', 6): 'bf', ('perpendicular-parameter', 2): 'bf', ('perpendicular-parameter', 5): 'bf', ('perpendicular-parameter', 6): 'ao', ('cross-product', 4): 'bk', ('cross-product', 5): 'bf', ('cross-order', 2): 'bf', ('cross-order', 4): 'bf', ('cross-order', 6): 'bf', ('cross-linearity', 2): 'bf', ('cross-linearity', 3): 'bf', ('cross-linearity', 5): 'bf', ('cross-linearity', 6): 'bf', ('zero-cross', 3): 'bf', ('zero-cross', 4): 'bf', ('vector-line-equation', 2): 'bg', ('vector-line-equation', 4): 'bg', ('vector-line-equation', 6): 'bg', ('cartesian-line', 2): 'bg', ('cartesian-line', 4): 'bg', ('zero-direction', 2): 'bg', ('zero-direction', 4): 'bg', ('zero-direction', 6): 'bg', ('vector-plane', 3): 'bg', ('vector-plane', 4): 'bg', ('vector-plane', 6): 'bk', ('plane-cartesian', 2): 'bg', ('plane-cartesian', 4): 'bg', ('plane-cartesian', 5): 'bk', ('plane-cartesian', 6): 'bl', ('plane-normal', 2): 'bg', ('plane-normal', 3): 'bg', ('plane-normal', 4): 'bg', ('cross-normal', 3): 'bg', ('cross-normal', 4): 'bg', ('cross-normal', 6): 'bg', ('normal-dot-plane', 2): 'bg', ('normal-dot-plane', 3): 'bg', ('normal-dot-plane', 4): 'bg', ('normal-dot-plane', 5): 'bg', ('normal-dot-plane', 6): 'bg', ('line-line-angle', 5): 'bg', ('line-line-angle', 6): 'bg', ('plane-plane-angle', 2): 'bg', ('plane-plane-angle', 3): 'bg', ('plane-plane-angle', 6): 'bg', ('line-plane-angle', 2): 'bg', ('line-plane-angle', 4): 'bg', ('line-plane-angle', 5): 'bg', ('line-plane-angle', 6): 'ao', ('line-intersection', 2): 'bh', ('line-intersection', 4): 'bh', ('line-plane-intersection', 6): 'ak', ('point-line', 2): 'bh', ('point-line', 3): 'bh', ('point-line', 5): 'bk', ('point-line', 6): 'bl', ('skew', 4): 'bh', ('skew', 6): 'al', ('point-plane', 2): 'bh', ('point-plane', 4): 'bh', ('point-plane', 5): 'bh', ('point-plane', 6): 'bh', ('line-line-distance', 2): 'bh', ('line-line-distance', 6): 'ap', ('triangle-area', 5): 'bh', ('triangle-area', 6): 'ao', ('triple-volume', 6): 'bh', ('plane-intersection-direction', 3): 'bh', ('plane-intersection-direction', 5): 'bk', ('plane-intersection-direction', 6): 'aq', ('parallelogram-area', 3): 'bh', ('parallelogram-area', 4): 'bh', ('parallelogram-area', 5): 'bh', ('parallelogram-area', 6): 'bh', ('plane-common-point', 2): 'bh', ('plane-common-point', 4): 'bh', ('plane-common-point', 5): 'bh', ('plane-common-point', 6): 'bh', ('related-solids', 2): 'bh', ('related-solids', 5): 'bj', ('related-solids', 6): 'bk', ('plane-intersection-line', 1): 'bh', ('plane-intersection-line', 2): 'bh', ('plane-intersection-line', 3): 'bh', ('plane-intersection-line', 4): 'bh', ('plane-intersection-line', 5): 'bh', ('plane-intersection-line', 6): 'bh', ('justify-skew', 1): 'bh', ('justify-skew', 4): 'bh', ('justify-skew', 6): 'ap'}
ADD_STEPS = {('vector-components', 2): (0,), ('vector-combinations', 2): (0,), ('unit-vector', 2): (0, 1), ('perpendicular-test', 3): (0,), ('perpendicular-test', 4): (0, 1, 2), ('perpendicular-parameter', 2): (1, 2), ('perpendicular-parameter', 5): (2,), ('cross-product', 4): (1,), ('cross-order', 2): (0,), ('cross-linearity', 2): (1,), ('cross-linearity', 3): (1,), ('zero-cross', 4): (1,), ('cartesian-line', 2): (0,), ('zero-direction', 2): (0,), ('vector-plane', 3): (1,), ('plane-cartesian', 2): (0, 1), ('plane-cartesian', 4): (2,), ('plane-normal', 2): (0, 1), ('plane-normal', 3): (0, 1), ('plane-normal', 4): (2,), ('cross-normal', 3): (1,), ('normal-dot-plane', 2): (0,), ('normal-dot-plane', 4): (1, 2), ('plane-plane-angle', 2): (0, 1), ('line-plane-angle', 2): (0, 1), ('line-plane-angle', 4): (2,), ('line-plane-angle', 5): (0, 2), ('line-intersection', 2): (0, 1), ('skew', 4): (1,), ('point-plane', 2): (1,), ('line-line-distance', 2): (0, 1, 2), ('triangle-area', 5): (2,), ('plane-intersection-direction', 3): (2,), ('parallelogram-area', 5): (2,), ('plane-common-point', 2): (0, 1), ('plane-common-point', 4): (0,), ('related-solids', 2): (0, 1), ('plane-intersection-line', 1): (0,), ('justify-skew', 1): (0, 1)}

def once(s,old,new):
    require(s.count(old)==1,'Unexpected repair site: '+old)
    return s.replace(old,new,1)

def append(a,s):
    return a.rstrip('.')+'. '+s

def revise(path,tier,variant):
    key=path,tier
    require(key in TARGETS and type(variant) is int and variant in (1,2,3),'Invalid BN9 target')
    p=import_module('difficulty_revision_'+TARGETS[key]).revise(path,tier,variant)
    q,a,w=p['question_latex'],p['final_answer_latex'],p['worked_solution_latex']
    v=variant; n=v+1; d=v+3
    if key in ADD_STEPS:
        a=append(a,' '.join(w[i] for i in ADD_STEPS[key]))
    elif key==('vector-components',6):
        a=append(a,r'Writing $D$ for the displayed right-hand side of $y^2$, the feasible values are $y=0$ when $D=0$ and $y=\pm\sqrt{D}$ when $D>0$.')
    elif key==('vector-combinations',5):
        w[2]=once(w[2],'λ','t');a=append(a,w[2].split('Since ')[1].join(['Since ','']))
    elif key==('vector-combinations',6):
        a=append(a,'The boundary consists of the cases with at least one zero coefficient.')
        a=a.replace('h≥0, k≥0',r'$h\geq0$, $k\geq0$').replace('$≤1',r'\leq1$')
    elif key==('unit-vector',4):
        w[0]=once(w[0],'normalize to obtain $',r'normalize to obtain $\mathbf u=')
    elif key==('perpendicular-test',6):
        a=append(a,f'The excluded pairs also forbid $h=0$ and $h={d}$.')
    elif key==('cross-order',4):
        w[0]=r'Let $u=Q-P$ and $v=R-P$. '+w[0];a=append(a,'The first two vertex orders agree; the third reverses the orientation.')
    elif key==('cross-order',6):
        a=rf'$C<{d}$: no solutions; $C={d}$: one, $w=(0,-{d},0)$; $C>{d}$: two, $w=(\pm\sqrt{{C^2-{d*d}}},-{d},0)$.'
    elif key==('cross-linearity',5):
        w[0]='Let V be the supplied particular vector. '+w[0]
    elif key==('cross-linearity',6):
        w[0]='Let $S=X+Y$ denote the given sum. '+w[0]
    elif key==('zero-cross',3):
        w[0]='Let u and v denote the first and second vectors respectively. '+w[0]
    elif key==('vector-line-equation',4):
        w[0]=append(w[0],a.split(';')[0]+', t real.')
    elif key==('vector-line-equation',6):
        a=append(a,'In the coincident case there are infinitely many distinct lines. All line parameters t are real.')
    elif key==('cartesian-line',4):
        mats=re.findall(r'\$\\left\[\\begin\{matrix\}.*?\\end\{matrix\}\\right\]\$',a)
        require(len(mats)==3,'Expected point, direction and intersection')
        eq='The line is $r='+mats[0][1:-1]+'+t'+mats[1][1:-1]+'$, with t real.'
        a=append(a,eq);w[0]=append(w[0],eq)
    elif key==('zero-direction',6):
        a=append(a,'S is a line whenever at least one of h and k is nonzero; when both vanish, all three coordinates are fixed at the displayed point.')
    elif key==('plane-cartesian',6):
        w[0]='Let P be the displayed base point of the line. '+w[0]
    elif key==('normal-dot-plane',5):
        a=append(a,rf'Equivalently, $(r-P)\cdot({n},-1,{d})=0$.')
    elif key==('line-plane-intersection',6):
        # The signed constant varies; normalize only an actual double minus.
        found=re.search(r'h--(\d+)',w[3]);require(found is not None,'Expected double minus')
        w[3]=once(w[3],found[0],'h+'+found[1]);
        a=a.replace('k not equal to +/-1',r'$k\ne\pm1$')
    elif key==('line-line-distance',6):
        w[2]=once(w[2],'(t,-t,-t)',r'$(-t,t,t)$')
        a=once(a,'Substitute the parameters in the stated lines for both point pairs.',rf'For each signed offset $D\in\{{{d},-{d}\}}$, the closest points on L and the corresponding M are $((h-D)/3,(h-D)/3,0)$ and $((2h-2D)/3,0,(D-h)/3)$ respectively.')
    elif key==('triangle-area',6):
        import sympy as s
        from sympy import latex
        # Preserve existing ranges; explicitly group the boundary and the two signs.
        a=a.replace(f'|h|>{d}',f'$|h|>{d}$').replace(f'|h|={d}',f'$|h|={d}$').replace(f'|h|<{d}',f'$|h|<{d}$').replace('+/-$',r'$\pm ')
        a=a.replace('|h|>$',r'$|h|>').replace('|h|<$',r'$|h|<')
        a=append(a,rf'At $|h|={d}$ the sole point gives area ${latex(s.Rational(n,2)*s.sqrt(2*d*d+n*n))}$, both the minimum and the maximum.')
    elif key==('plane-intersection-direction',6):
        a=append(a,rf'For $hk\ne0$ the full equation is $hkx-ky-hz={n}hk-h-{d}k$.')
    elif key==('plane-intersection-line',3):
        a=append(a,rf'For every real $t$, $x+y=({n}-t)+t={n}$ and $y+z=t+({d}-t)={d}$.')
    elif key==('plane-intersection-line',4):
        b=v+3;c=v+5;znum=2*v+5;rhs=n*b+znum
        a=append(a,rf'For every real $t$, $x+{n}y=({b}-{n}t)+{n}t={b}$ and ${n}x+{n*n}y+{d}z={n}({b}-{n}t)+{n*n}t+{znum}={rhs}$.')
    elif key==('plane-intersection-line',5):
        a=append(a,rf'For every real $t$, $x+y=t+({n}-t)={n}$ and $-{d-1}x+y+{d}z=-{d-1}t+{n}-t+{d}t+{d+1}={n+d+1}$.')
    elif key==('vector-components',4):
        def fix(s):
            m=re.search(r'\(\$(.*?)\$\)i\+\(\$(.*?)\$\)j\+\(\$(.*?)\$\)k',s)
            require(m is not None,'Expected component representation')
            return once(s,m[0],r'$('+m[1]+r')\mathbf{i}+('+m[2]+r')\mathbf{j}+('+m[3]+r')\mathbf{k}$').replace('..','.')
        a=fix(a);w[1]=fix(w[1])
    elif key==('unit-vector',5):
        m=re.search(r'\|lambda\|\((\d+)\)/\$(.*?)\$',w[0]);require(m is not None,'Expected magnitude')
        w[0]=once(w[0],m[0],r'$\frac{'+m[1]+r'|\lambda|}{'+m[2]+'}$')
        w[0]=w[0].replace('multiple lambda',r'multiple $\lambda$');w[1]=w[1].replace('|lambda|=$',r'$|\lambda|=')
    elif key==('scalar-product',6):
        q=q.replace('pi/3',r'$\pi/3$').replace('pi/2',r'$\pi/2$')
        a=a.replace('h >= $',r'$h\geq ').replace('with -$',r'with $-').replace('$ <= k <= -3h/4',r'\leq k\leq -3h/4$')
        w[0]=once(w[0],f'h/sqrt(h squared+k squared+{n*n}) >= 1/2',rf'$\frac{{h}}{{\sqrt{{h^2+k^2+{n*n}}}}}\geq\frac12$').replace('h must be positive',r'$h>0$ is required')
        w[1]=w[1].replace(f'k squared <= 3h squared-{n*n}',rf'$k^2\leq3h^2-{n*n}$').replace('3h+4k <= 0',r'$3h+4k\leq0$')
        w[2]=w[2].replace('between -$',r'between $-').replace('and -3h/4',r'and $-3h/4$').replace(f'sqrt(3h squared-{n*n}) >= 3h/4',rf'$\sqrt{{3h^2-{n*n}}}\geq3h/4$').replace(f'39h squared >= {16*n*n}',rf'$39h^2\geq{16*n*n}$')
    elif key==('perpendicular-parameter',6):
        a=rf'$h=0$: none. For $h\ne0$, $k=-{n}$ at A and $k={n}$ at B. At C, additionally $k=\pm\sqrt{{{n*n}-h^2}}$ when $0<|h|\leq{n}$, counting zero once. Counts: four for $0<|h|<{n}$, three for $|h|={n}$, two for $|h|>{n}$.'
        w[2]=rf'At C the product CA dot CB is $k^2+h^2-{n*n}$. Thus $k=\pm\sqrt{{{n*n}-h^2}}$ when $|h|\leq{n}$.'
        w[3]=w[3].replace(f'|k|<{n}',f'$|k|<{n}$')
    elif key==('cross-product',5):
        vals=a.split('; ');require(len(vals)==4,'Expected two roots and two vectors')
        a='For $k='+vals[0][1:-1]+'$, the cross product is '+vals[2]+'. For $k='+vals[1][1:-1]+'$, the cross product is '+vals[3]+'.'
    elif key==('vector-line-equation',2):
        w[0]='Let P and d denote the first base point and direction, and Q the second base point. '+w[0];a=append(a,w[0]+' '+w[1])
    elif key==('zero-direction',4):
        w[0]='Let P and Q be the first two points and R the point to test. '+w[0];a=append(a,w[2])
    elif key==('vector-plane',4):
        w[0]='Let P be the base point and u,v the displayed directions, in order. '+once(w[0],'get normal $','get normal $n=');w[3]=once(w[3],'Its scalar product','The scalar product of W');a=append(a,w[3])
    elif key==('vector-plane',6):
        a=append(a,r'In every displayed equation $s,t\in\mathbb R$; in the infinite family $(u,w)\ne(0,0)$, with proportional directions identified.')
    elif key==('plane-cartesian',5):
        c=2*n+1;w[1]=w[1].replace(f'{c}/sqrt({n*n+1}+h^2)',rf'$\frac{{{c}}}{{\sqrt{{{n*n+1}+h^2}}}}$').replace(f'h^2={(n+1)**2}',rf'$h^2={(n+1)**2}$');a=a.replace(f'h=+/-{n+1}',rf'$h=\pm{n+1}$')
    elif key==('cross-normal',4):
        w[0]='Let P,Q,R denote the three displayed points in order. '+once(w[0],'their cross product is $','their cross product is $n=')
    elif key==('cross-normal',6):
        a=once(a,'Cross product $','Cross product $(');a=once(a,'$ times $',r')$ times $')
        for op in ('<','>','='):
            a=a.replace(f'kh{op}{d}',f'$kh{op}{d}$');w=[s.replace(f'kh{op}{d}',f'$kh{op}{d}$') for s in w]
    elif key==('normal-dot-plane',3):
        w[0]='Let Q be the displayed point and n the displayed normal. '+w[0];w[1]=once(w[1],'.;',';')
    elif key==('normal-dot-plane',6):
        val=re.search(r'put u=\$(.*?)\$',a);require(val is not None,'Expected magnitude')
        a=rf'For $|h|\leq1$ put $u={val[1]}\geq0$. Equations $\pm u({d}x+{n}y)+hz=\pm{n*d}u$ with consistent signs. No planes if $|h|>1$; one if $h=0$ or $|h|=1$; two if $0<|h|<1$.'
        w[1]=rf'Unit length requires $({n*n+d*d})\lambda^2+h^2=1$, giving $\lambda=\pm u$ where $u={val[1]}$ if $|h|\leq1$ and none otherwise.'
        w[2]=rf'Using P, the equation is $\lambda({d}x+{n}y)+hz={n*d}\lambda$.'
    elif key==('line-line-angle',5):
        m=re.search(r'\$k=\\pm (.*?)\$',a);require(m is not None,'Expected roots')
        a=rf'$k=\pm {m[1]}$. The two lines are $\mathbf r=(0,{v+2},1)+u({m[1]},{n},0)$ and $\mathbf r=(0,{v+2},1)+u(-{m[1]},{n},0)$, where $u\in\mathbb R$.'
    elif key==('line-line-angle',6):
        from sympy import Rational,latex
        b=v+2;C=n*n+b*b;D=2*n*n+b*b;T=latex(Rational(C,D));K=latex(Rational(C,2*b))
        a=rf'$t=0$: $k=0$; $0<t<1/2$: two; $t=1/2$: $k={K}$; $1/2<t<{T}$: two; $t={T}$: one; ${T}<t\leq1$: none. For $t\ne1/2$, roots are $k=\frac{{-{b}t\pm\sqrt{{t({C}-{D}t)}}}}{{1-2t}}$ when real.'
        w[0]=rf'The squared cosine is $\frac{{k^2}}{{k^2+{n*n}+(k-{b})^2}}$. The denominator is positive for all k, so equating it to t is equivalent to $(1-2t)k^2+{2*b}tk-{C}t=0$.'
        w[1]=w[1].replace('between 1/2 and 1','between $1/2$ and $1$');w[2]=w[2].replace('At t=0','At $t=0$').replace('k=0',' $k=0$').replace('On (0,1/2) and (1/2,T)','On $(0,1/2)$ and $(1/2,T)$')
    elif key==('plane-plane-angle',3):
        q=q.replace(r'\sqrt3',r'\sqrt{3}');w=[s.replace(r'\sqrt3',r'\sqrt{3}') for s in w]
    elif key==('plane-plane-angle',6):
        a=a.replace(r'\sqrt{(1-c)/(1+c)}',r'\sqrt{\frac{1-c}{1+c}}').replace(r'\sqrt{(1+c)/(1-c)}',r'\sqrt{\frac{1+c}{1-c}}');a=append(a,r'The counts are one at $\theta=0$, four for $0<\theta<\pi/2$, and two at $\theta=\pi/2$.')
    elif key==('line-plane-angle',6):
        a=a.replace('p squared+q squared >= 1',r'$p^2+q^2\geq1$').replace('x=+/-$',r'$x=\pm ').replace('z=+/-$',r'$z=\pm ')
        w[0]=w[0].replace('|x|=pN and |z|=qN',r'$|x|=pN$ and $|z|=qN$')
        w[1]=rf'Substitution into $N^2=x^2+{n*n}+z^2$ gives $N^2(1-p^2-q^2)={n*n}$. Since N is positive, the factor must be strictly positive.'
        w[2]=w[2].replace('N=$','$N=')
    elif key==('line-intersection',4):
        w[0]='Let L be its first displayed point plus t times its direction, with t real. '+w[0];a=append(a,'The directions are nonproportional, so the disjoint lines are skew.')
    elif key==('point-line',2):
        w[0]=r'The directed displacement from H to P is '+w[0]+r' The opposite displacement $H-P$ also has zero scalar product.'
    elif key==('point-line',3):
        w[0]='Let P be the displayed point; the line passes through the origin. '+w[0]
    elif key==('point-line',5):
        w[2]=re.sub(r'H=\(([^)]+)\)',r'$H=(\1)$',w[2]).replace('signs of k','signs of $k$').replace('in k^2','in $k^2$')
    elif key==('point-line',6):
        b=v+3;D=2*n*n+b*b
        w[0]=rf'The squared distance is $(t-{2*n})^2+t^2+{b*b}=2(t-{n})^2+{D}$.'
        w[2]=w[2].replace(f'(t-{n}) squared = (h-{D})/2',rf'$(t-{n})^2=(h-{D})/2$');w[3]=w[3].replace('(t,t,0)','$(t,t,0)$')
        for op in ('<','=','>'):a=a.replace(f'h{op}{D}',f'$h{op}{D}$')
        a=a.replace('(t,t,0) with t=$','$(t,t,0)$ with $t=')
    elif key==('skew',6):
        a=a.replace(f'{n}x-y+(k-{n})z=0',f'${n}x-y+(k-{n})z=0$').replace(f'{n}x-y+(k-{n})z=$',f'${n}x-y+(k-{n})z=').replace('h=$','$h=')
        w[1]=w[1].replace(f'{n}x-y+(k-{n})z=0',f'${n}x-y+(k-{n})z=0$');w[2]=w[2].replace('$=0','=0$');w[3]=w[3].replace('h=$','$h=')
    elif key==('point-plane',4):
        w[0]='Let P be the displayed point, treated as a position vector. '+w[0]
    elif key==('point-plane',5):
        w[0]='Let P be the displayed point. A positive signed residual means the side in the direction of the displayed normal. '+w[0]
        a=append(a,rf'The signed residual is $n\cdot P-h={3*v+7}-h$ for the displayed normal n.')
    elif key==('point-plane',6):
        w[0]='Let P be the displayed point. '+once(w[0],'gives foot $','gives perpendicular foot $H=');a=once(a,'Foot $','Foot $H=');a=append(a,'Here Q denotes an arbitrary point in the given plane.')
    elif key==('triple-volume',6):
        b=v+2
        a=a.replace('c=0:','$c=0$:').replace('0<c<B:','$0<c<B$:').replace('c=B:','$c=B$:').replace('c>B:','$c>B$:').replace(f'k=({b}\\pm',rf'k=\frac{{{b}\pm').replace('})/2$',r'}}{2}$')
        a=append(a,rf'At $c=0$ the two branches coincide; at $c=B$ the negative signed branch has a repeated root $k={b}/2$.')
    elif key==('plane-intersection-direction',5):
        w[0]=re.sub(r'(-\d+\+h=0)',r'$\1$',w[0]);w[1]=re.sub(r'(\d+k-\d+)\+-([0-9]+)h=0',r'$\1-\2h=0$',w[1])
    elif key==('parallelogram-area',3):
        w[0]='Let u and v denote the two displayed adjacent vectors, in order. '+w[0]
    elif key==('parallelogram-area',4):
        w[0]='Let $u=Q-P$ and $v=R-P$. '+w[0]
    elif key==('parallelogram-area',6):
        from sympy import Rational,latex
        b=latex(Rational(v,2));m=re.search(r'roots k=\$(.*?)\$ \+/- sqrt\(\$(.*?)\$\)',a);require(m is not None,'Expected root formula')
        a=once(a,m[0],rf'roots $k={m[1]}\pm\sqrt{{{m[2]}}}$')
        w[2]=re.sub(r'\(k-\$(.*?)\$\) squared = \$(.*?)\$',lambda m:rf'$(k+{b})^2={m[2]}$',w[2])
    elif key==('plane-common-point',5):
        w[1]=re.sub(r'(\d+)y=(-?\d+)',lambda m:'$'+('' if m[1]=='1' else m[1])+'y='+m[2]+'$',w[1])
    elif key==('plane-common-point',6):
        w[0]=once(w[0],'Set y=t.','Set y=t. Denote the base point by P and the direction vector by D, in the order displayed.');
    elif key==('related-solids',5):
        q=q.replace('0<=t<=1',r'$0\leq t\leq1$');w[0]=w[0].replace('t(1-t)','$t(1-t)$');w[1]=w[1].replace('t(1-t)=$','$t(1-t)=');w[2]=r'Complete the square: $t(1-t)=\frac14-(t-\frac12)^2$. Its maximum is $1/4$, uniquely at $t=1/2$, including both endpoints in the comparison.'
    elif key==('related-solids',6):
        a=a.replace('t=1/2','$t=1/2$').replace('C<0 or C>$',r'$C<0$ or $C>').replace('C=0 and for 0<C>$',r'$C=0$ and for $0<C>').replace('C=0 and for 0<C<$',r'$C=0$ and for $0<C<')
        def roots(s):return re.sub(r't=\(1±\$(.*?)\$\)/2',lambda m:r'$t=\frac{1\pm'+m[1]+r'}{2}$',s)
        a=roots(a);w[2]=roots(w[2]).replace('0≤C≤$',r'$0\leq C\leq ')
        w[1]=re.sub(r'C=\$(.*?)\$-\$(.*?)\$\(t-1/2\)\^2',lambda m:r'$C='+m[1]+'-'+m[2]+r'(t-1/2)^2$',w[1]).replace('t=1/2','$t=1/2$')
    elif key==('plane-intersection-line',2):
        a=append(a,w[0]);w[1]=once(w[1],'t real. satisfies','t real, satisfies')
    elif key==('plane-intersection-line',6):
        a=a.replace('h≠0:',r'$h\ne0$:').replace('h=0,k≠1:',r'$h=0,k\ne1$:').replace('h=0,k=1:',r'$h=0,k=1$:').replace('iff k=1','iff $k=1$');a=append(a,r'In both line families $t\in\mathbb R$.')
    elif key==('justify-skew',4):
        w[0]='Let P and R denote the first points of L and K, respectively, and U,V their respective directions. '+w[0]
    elif key==('justify-skew',6):
        a=a.replace('k=1','$k=1$').replace('t=u=$','$t=u=').replace('u=$','$u=').replace('t=$','$t=').replace('k differs from 1',r'$k\ne1$').replace(f'h(k-1) differs from {n}',rf'$h(k-1)\ne{n}$').replace(f'iff h(k-1)={n}',f'iff $h(k-1)={n}$')
    else:raise ValueError('Missing repair '+str(key))
    p.update(question_latex=q,final_answer_latex=a,worked_solution_latex=w)
    return p
