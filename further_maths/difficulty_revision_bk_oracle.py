"""Independent exact checks of BK new mathematical facts; retained facts use predecessor oracles."""
from importlib import import_module
import sympy as s
from difficulty_revision_bk import TARGETS, NEW_DEMAND, REGISTRY

def mat(x):return s.Matrix([[s.sympify(y) for y in row] for row in x['matrix']])
def check(p):
    path,t,v=p['path'],p['tier'],p['variant'];key=path,t
    if key not in TARGETS or type(v) is not int or v not in (1,2,3):return False
    if sum(r['marks'] for r in p['rubric'])!=REGISTRY[key][2]:return False
    if key not in NEW_DEMAND:
        return import_module('difficulty_revision_'+TARGETS[key]+'_oracle').check(p)
    f=p['facts']
    if path=='argand-displacement':
        A=v+1+(v+3)*s.I; B=3*v+5-(v+1)*s.I; C,oc,ab,mid=map(s.sympify,f)
        return C-A==B and C-B==A and oc==C and ab==B-A and 2*mid==C==A+B
    if path=='cartesian-sums':
        u,b=map(s.sympify,f); W=3*v+5-(v+1)*s.I; q=2*(v+1+(v+3)*s.I)-W
        return u+b==W and u-b==q and 2*u==W+q
    if path=='invariant-lines':
        a,b=s.symbols('a b');m=v+1;n=v+3; slope,intercept=map(s.sympify,f[:2]);
        sol=s.linsolve([(n-m)*a,(n-1)*b],(a,b))
        return slope==n and intercept==n and sol=={(0,0)} and m!=1 and f[2:]==['x=0','y=0']
    if path=='symmetric-parameter':
        k=s.Symbol('k'); A=v+1;B=2*v+5;k1,k2,d1,d2=map(s.sympify,f)
        eq=(k+A)-(k+A)/(B*k)
        return {k1,k2}==set(s.solve(eq,k)) and k1!=0 and k2!=0 and [d1,d2]==[(i+A)**2-4*B*i for i in (k1,k2)]
    if path=='system-consistency':
        x,y,z,t0=s.symbols('x y z t'); A=v+1;B=v+3; xx,yy,zz,c=map(s.sympify,f[:4]);family=s.Matrix([A-t0,t0,B-t0]); M=s.Matrix([[1,1,0],[0,1,1],[1,2,1]]);M2=s.Matrix([[1,1,0],[0,1,1],[1,2,2]])
        return M.rank()==2 and M.row_join(s.Matrix([A,B,A+B+1])).rank()==3 and M2.det()!=0 and M2*s.Matrix([xx,yy,zz])==s.Matrix([A,B,A+B+1]) and M*family==s.Matrix([A,B,c]) and f[4]==[str(A),str(B)]
    if path=='exact-radians':
        x=s.Symbol('x',real=True);q=[s.Rational(1,2),s.sqrt(2)/2,s.sqrt(3)/2][v-1];roots=list(map(s.sympify,f));allroots=s.solveset(s.sin(2*x)-q,x,domain=s.Interval.Ropen(0,2*s.pi));expected={r for r in allroots if s.cos(2*r)<0}
        return len(roots)==2 and set(roots)==expected
    if path=='locus-intersection':
        C=v+1;R=v+3;B=C-R-1;t0=s.Symbol('t',real=True);t1,t2,z1,z2=map(s.sympify,f);a=s.sqrt(3)/2;b=s.Rational(1,2)
        eq=(B+a*t0-C)**2+(b*t0)**2-R**2
        expected=s.solve(eq,t0)
        return t1>0 and t2>t1 and len(expected)==2 and all(any(s.simplify(t-x)==0 for x in expected) for t in (t1,t2)) and all(s.simplify(s.re(z)-B-a*t)==0 and s.simplify(s.im(z)-b*t)==0 and s.simplify((s.re(z)-C)**2+s.im(z)**2-R**2)==0 for t,z in ((t1,z1),(t2,z2)))
    if path=='plane-cartesian':
        k,D,h1,h2,z1,z2=map(s.sympify,f);h=s.Symbol('h',real=True);target=s.Rational(2*v+3,1)/s.sqrt((v+1)**2+1+(v+2)**2)
        return k+v+2==D==2*k+1 and {h1,h2}==set(s.solve(D**2-target**2*(k*k+1+h*h),h)) and h1<0<h2 and h1*z1==D==h2*z2
    if path=='plane-intersection-direction':
        k,h=map(s.sympify,f[:2]);d=mat(f[2]);A=v+1;H=v+2;K=v+3;given=s.Matrix([A*H,-H,1-A*K]);n1=s.Matrix([1,A,0]);n2=s.Matrix([k,1,h]);x,y=s.symbols('x y');sol=s.linsolve([given.dot(s.Matrix([x,1,y])),s.Matrix([0,-H,1]).dot(s.Matrix([x,1,y]))],(x,y))
        return sol=={(k,h)} and d==given and d!=s.zeros(3,1) and n1.cross(n2)==d
    if path=='polar-quotients':
        zr,za,ur,ua,qr,qa=map(s.sympify,f);w=(v+1)*s.exp(-3*s.pi*s.I/4);z=zr*s.exp(s.I*za);u=ur*s.exp(s.I*ua);q=qr*s.exp(s.I*qa)
        return all(x>0 for x in (zr,ur,qr)) and all(-s.pi<a<=s.pi for a in (za,ua,qa)) and s.simplify(s.expand_complex(z/w-(v+3)*s.exp(s.I*s.pi/3)))==0 and s.simplify(s.expand_complex(w/u+(v+2)*s.I))==0 and s.simplify(s.expand_complex(z/u-q))==0
    if path=='unit-vector':
        A,B=map(mat,f[:2]);n=s.sympify(f[2]);d=s.Matrix([v+1,v+2,v+3]);lam=s.Symbol('lam',real=True)
        return A==-B and A.cross(d)==s.zeros(3,1) and A[2]>0 and {A[2]/d[2],B[2]/d[2]}==set(s.solve((lam*d[2])**2-4*d[2]**2,lam)) and A.dot(A)==n*n and n>0
    if path=='vector-components':
        A,B=map(mat,f);X=v+1;J=v+3;K=2*v+5;d=K-J;N=X*X+J*J+K*K;y=s.Symbol('y',real=True)
        return {A[1],B[1]}==set(s.solve(X*X+y*y+(y+d)**2-N,y)) and all(m[0]==X and m[2]-m[1]==d and m.dot(m)==N for m in (A,B))
    if path=='vector-line-equation':
        k,h=map(s.sympify,f[:2]);D,I=map(mat,f[2:]);P=s.Matrix([1,0,2]);W=P+2*s.Matrix([v+1,v+3,v+4]);C=3+3*(3*v+8);t0=s.Symbol('t')
        return D==s.Matrix([k,h,v+4]) and D[2]!=0 and P+((W[2]-P[2])/D[2])*D==W and sum(D)!=0 and I==P+((C-sum(P))/sum(D))*D and sum(I)==C
    return False
