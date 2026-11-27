"""FM-16BN5: version-bound matrix presentation repairs; one explicit allocation repair; no scope changes."""
from importlib import import_module
import re
from active_difficulty import require

TARGETS = {('composition-order', 2): 'bc', ('composition-order', 3): 'bc', ('composition-order', 4): 'bc', ('composition-order', 5): 'bc', ('composition-compute', 4): 'bc', ('composition-compute', 5): 'bc', ('orientation', 4): 'bd', ('fixed-points', 2): 'bc', ('fixed-invariant', 4): 'bk', ('fixed-invariant', 5): 'bc', ('invariant-lines', 2): 'bc', ('invariant-lines', 4): 'bk', ('det-two', 2): 'bb', ('det-three', 2): 'bd', ('det-three', 6): 'bd', ('det-area', 2): 'bd', ('det-area', 4): 'bk', ('det-area', 6): 'bd', ('det-classification', 2): 'bd', ('singular-condition', 2): 'bd', ('singular-condition', 4): 'bd', ('collapse', 1): 'bd', ('collapse', 2): 'bd', ('inverse-two', 1): 'bd', ('inverse-two', 3): 'bd', ('inverse-two', 6): 'aj', ('inverse-product', 2): 'bd', ('inverse-three', 3): 'bd', ('inverse-three', 5): 'bl', ('inverse-three', 6): 'bd', ('inverse-identities', 2): 'bd', ('inverse-identities', 3): 'bd', ('matrix-equation', 1): 'bd', ('matrix-equation', 2): 'bd', ('system-consistency', 2): 'be', ('system-classification', 1): 'be', ('system-classification', 2): 'be', ('nonunique-set', 5): 'be', ('three-plane-unique', 2): 'be', ('three-plane-unique', 3): 'be', ('two-variable-system', 2): 'be', ('inverse-systems', 2): 'be', ('inverse-systems', 4): 'be', ('inverse-systems', 6): 'aj', ('three-system', 2): 'be', ('inconsistent-geometry', 1): 'be', ('inconsistent-geometry', 4): 'be', ('nonunique-geometry', 2): 'be', ('nonunique-geometry', 4): 'be', ('nonunique-geometry', 6): 'be', ('basis-images', 2): 'bc', ('basis-images', 5): 'bk', ('describe-transform', 2): 'bc', ('describe-transform', 5): 'bc', ('describe-transform', 6): 'bc', ('figure-images', 2): 'bc', ('figure-images', 4): 'bc', ('figure-images', 5): 'bc', ('figure-images', 6): 'bc', ('identity-operations', 1): 'bb', ('identity-operations', 4): 'bb', ('identity-operations', 5): 'bb', ('matrix-add-subtract', 2): 'bb', ('matrix-add-subtract', 6): 'bb', ('matrix-conformability', 2): 'bb', ('matrix-products', 2): 'bb', ('matrix-products', 3): 'bb', ('scalar-matrix', 2): 'bb', ('scalar-matrix', 5): 'bb', ('scalar-matrix', 6): 'bb', ('zero-matrix', 2): 'bb'}

# Specific previously verified reasoning steps complete the corresponding short answers.
ADD_STEPS = {
    ('composition-order',2):(2,), ('invariant-lines',2):(1,),
    ('det-two',2):(2,), ('det-three',2):(0,), ('det-area',2):(0,1), ('det-area',6):(1,),
    ('det-classification',2):(0,1), ('singular-condition',2):(0,),
    ('inverse-two',1):(1,), ('inverse-product',2):(2,), ('inverse-identities',2):(0,),
    ('inverse-identities',3):(0,1), ('matrix-equation',2):(0,),
    ('system-consistency',2):(0,1), ('system-classification',1):(0,),
    ('system-classification',2):(0,1,2), ('three-plane-unique',2):(1,),
    ('three-plane-unique',3):(2,), ('two-variable-system',2):(0,),
    ('three-system',2):(0,1), ('inconsistent-geometry',1):(1,),
    ('inconsistent-geometry',4):(3,), ('nonunique-geometry',2):(0,), ('nonunique-geometry',4):(2,),
    ('basis-images',2):(2,), ('basis-images',5):(2,), ('describe-transform',2):(0,1),
    ('figure-images',2):(0,), ('figure-images',5):(0,), ('identity-operations',1):(1,),
    ('identity-operations',4):(1,), ('identity-operations',5):(1,2),
    ('matrix-add-subtract',2):(0,1), ('matrix-conformability',2):(0,1),
    ('matrix-products',2):(0,), ('scalar-matrix',2):(0,), ('zero-matrix',2):(1,),
}

def once(text, old, new):
    require(text.count(old)==1, 'Unexpected repair site: '+old)
    return text.replace(old,new,1)


def append_steps(a,w,indices):
    return a.rstrip('.')+'. '+' '.join(w[i] for i in indices)


def revise(path,tier,variant):
    key=path,tier
    require(key in TARGETS and type(variant) is int and variant in (1,2,3),'Invalid BN5 target')
    p=import_module('difficulty_revision_'+TARGETS[key]).revise(path,tier,variant)
    q,a,w=p['question_latex'],p['final_answer_latex'],p['worked_solution_latex']
    v=variant; n=v+1; b=v+3
    if key in ADD_STEPS:
        a=append_steps(a,w,ADD_STEPS[key])
    elif key in (('composition-order',3),('composition-order',4),('composition-compute',4),('orientation',4),('det-area',4)):
        # Define names in the question, including when they appear in the final answer.
        mats=list(re.finditer(r'\$\\left\[\\begin\{matrix\}.*?\\end\{matrix\}\\right\]\$',q))
        require(len(mats)==2,'Expected two matrices')
        for m,label in reversed(list(zip(mats,('A','B')))):
            q=q[:m.start()]+'$'+label+'='+m[0][1:]+q[m.end():]
        if key==('composition-compute',4):
            a=once(a,'+(- ','-'); a=once(a,')$','$')
            w[2]=once(w[2],'+(- ','-'); w[2]=once(w[2],')$','$')
    elif key==('composition-order',5):
        w[2]=once(w[2],'under B','under the displayed second matrix')
    elif key==('composition-compute',5):
        w[0]='Let A be the displayed first transformation. '+w[0]
    elif key==('fixed-points',2):
        w[1]=once(w[1],'ax=x with the displayed a greater than 1',f'${n}x=x$ with ${n}>1$')
    elif key==('fixed-invariant',4):
        a=once(a,'y=0 fixed pointwise','y=0 fixed pointwise (image $Y=0$)')
        c=2*v+3
        a=once(a,f'x={c} invariant but not fixed pointwise.',f'x={c} invariant but not fixed pointwise (image $X={c}$).')
    elif key==('fixed-invariant',5):
        m=re.search(r'line y=\$(.*?)\$x',q); require(m is not None,'Expected slope')
        w[0]='Let $m='+m[1]+'$ be the displayed slope. '+w[0]
    elif key==('invariant-lines',4):
        a=once(a,'$y=','$Y=');a=once(a,'x+','X+')
    elif key==('det-three',6):
        q=once(q,'classify the rank of $','classify the rank of $B=')
    elif key==('singular-condition',4):
        w[2]=once(w[2],f'Since {n}< ',f'Since ${n}< '); w[2]=once(w[2],f' <{b-1} (by squaring)',f' <{b-1}$ (by squaring)')
    elif key==('collapse',1):
        a='Yes; multiplier '+a.rstrip('.')+'.'
    elif key==('collapse',2):
        w[0]=once(w[0],'nonzero..','nonzero.')
    elif key==('inverse-two',3):
        q=once(q,'inverse of $','inverse of $A=')
    elif key==('inverse-two',6):
        a=once(a,'0<r<=$',r'$0<r\le '); a=once(a,'k=+/-$',r'$k=\pm ')
    elif key==('inverse-three',3):
        w[2]=once(w[2],'coefficients of u, v, w','coefficients of $U,V,W$')
    elif key==('inverse-three',5):
        q=once(q,'The matrix $','The matrix $A='); w[1]=once(w[1],'since a is nonzero','since the specified inverse entry is nonzero')
    elif key==('inverse-three',6):
        w[0]=once(w[0],'allow back-substitution:', 'allow back-substitution for an arbitrary right-hand side $(U,V,W)^T$:')
    elif key==('matrix-equation',1):
        a+=' Division by the given nonzero coefficient is allowed.'
    elif key==('nonunique-set',5):
        w[1]=once(w[1],'3t^2.',r'$3t^2$.');w[1]=once(w[1],f't=±{n}.',rf'$t=\pm {n}$.')
    elif key==('inverse-systems',2):
        q=once(q,'X=C^(-1)Y',r'$X=C^{-1}Y$'); a=append_steps(a,w,(0,1))
    elif key==('inverse-systems',4):
        w[2]=once(w[2],'(x,y,z)^T',r'$(x,y,z)^T$')
    elif key==('inverse-systems',6):
        w[0]=once(w[0],'The determinant is $','The coefficient determinant is $D=')
    elif key==('nonunique-geometry',6):
        a=once(a,f'k not equal to {n}: ',f'k not equal to {n}: line '); a=once(a,f'k={n}: ',f'k={n}: plane ');a=append_steps(a,w,(3,))
    elif key==('describe-transform',5):
        w[0]=once(w[0],'The fixed direction is','Let the fixed direction $D$ be'); w[0]=once(w[0],'a perpendicular direction is','the perpendicular direction $N$ be');w[1]='Let A be the reflection matrix. '+w[1]
    elif key==('describe-transform',6):
        for i,s in enumerate([a]+w):
            s=s.replace('rho=sqrt(p^2+h^2)',r'$\rho=\sqrt{p^2+h^2}$').replace('p^2+h^2=1',r'$p^2+h^2=1$').replace('squared length p^2+h^2.',r'squared length $p^2+h^2$.').replace('rho^2=p^2+h^2',r'$\rho^2=p^2+h^2$').replace('$>0', '>0$')
            if i==0:a=s
            else:w[i-1]=s
    elif key==('figure-images',4):
        # Join the complete line equation; no separate text-mode signs or variable.
        m=re.search(r'Y=\$(.*?)\$X \+ \(\$-\s*(.*?)\$\)\.',a);require(m is not None,'Expected image equation')
        a=once(a,m[0],f'$Y={m[1]}X-{m[2]}$.')
        m=re.search(r'Y=\$(.*?)\$\(X-1\)',w[2]);require(m is not None,'Expected point-slope equation')
        w[2]=once(w[2],m[0],f'$Y={m[1]}(X-1)$'); w[0]=once(w[0],'by A','by the displayed matrix')
    elif key==('figure-images',6):
        # The existing fraction is kept exactly, but the image equation is one math span.
        for i,s in ((-1,a),(3,w[3])):
            m=re.search(r'Y=\$(.*?)\$ \+ \$(.*?)\$\(X-(\d+)\)',s);require(m is not None,'Expected line equation')
            s=once(s,m[0],f'$Y={m[1]}+{m[2]}(X-{m[3]})$')
            if i==-1:a=s
            else:w[i]=s
    elif key==('matrix-add-subtract',6):
        q=once(q,'K^T=-K',r'$K^T=-K$')
        w[0]=once(w[0],'A^T=S-K',r'$A^T=S-K$'); w[0]=once(w[0],'S=(A+A^T)/2 and K=(A-A^T)/2',r'$S=(A+A^T)/2$ and $K=(A-A^T)/2$')
        w[2]=once(w[2],f'(h+k)^2={4*n*b}',f'$(h+k)^2={4*n*b}$')
    elif key==('matrix-products',3):
        a+=' (order $2\\times 2$).'
    elif key==('scalar-matrix',5):
        a=once(a,f'k=+/-{2*v+3}',rf'$k=\pm {2*v+3}$')
    elif key==('scalar-matrix',6):
        w[0]=once(w[0],'If k=0, A=O. Equality is possible exactly when B=O', 'If k=0, A is the zero matrix. Equality is possible exactly when B is the zero matrix')
    else:
        raise ValueError('Unimplemented repair '+str(key))
    if key==('inverse-three',6):
        criteria=[
            ('M','Use triangularity or an equivalent determinant method.'),
            ('A','State the exact necessary and sufficient invertibility condition kh nonzero.'),
            ('M','Derive the inverse by back-substitution or equivalent valid matrix operations.'),
            ('A','Give all nine entries of the exact inverse for nonzero k and h.'),
            ('M','For k=0, derive the homogeneous restrictions z=0 and x=-a*y, with a the displayed entry in row one, column two.'),
            ('A','Give the complete homogeneous solution line for k=0, including h=0.'),
            ('A','Give the complete homogeneous solution line for k nonzero and h=0.'),
            ('R','Justify necessity, sufficiency and completeness of both disjoint singular cases, including the unrestricted coordinate in each.')]
        p['rubric']=[{'type':t,'marks':1,'criterion':c+(' Accept equivalent valid reasoning; allow a correct subsequent method after a consistent earlier error without re-awarding lost accuracy.' if t=='M' else ' Require the specified correct result.' if t=='A' else ' Accept equivalent valid reasoning supported by the constraints.')} for t,c in criteria]
    p.update(question_latex=q,final_answer_latex=a,worked_solution_latex=w)
    return p
