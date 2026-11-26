"""Independent structured facts: solve entry/component equations, inspect ranks and dot products."""
import sympy as s
M=s.Matrix
h,k,t,z,u,w,x,y,p,q=s.symbols('h k t z u w x y p q',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 if path=='matrix-add-subtract':
  A=M([[a,-b],[d,1]]);B=M([[1,d],[-a,b]])
  if l==1:return [sum([-a,-b])]
  if l==2:
   C=M([[a,b,d],[1,0,a]]);return [A.shape==C.shape,C.shape==C.shape,C-C]
  if l==3:return [M(2,2,lambda i,j:A[i,j]-B[i,j]-B[i,j])]
  if l==4:
   # Solve four independent systems of entry equations rather than using matrix formulas.
   S=A+B;D=A-B;out=[[],[]]
   for i in range(4):
    pair=s.solve([x+y-S[i],x-y-D[i]],(x,y));out[0].append(pair[x]);out[1].append(pair[y])
   return [M(2,2,row) for row in out]
  if l==5:
   C=M([[h,a],[b,k]]);D=M([[d,k],[h,1]]);E=C+D
   target=3*b-2*a+2*d+1
   sol=s.solve([E[0,1]-E[1,0],s.trace(E)-target],(h,k));return [sol[h],sol[k],E.subs(sol)]
  C=M([[a,h],[k,b]]);S=M([[x,y],[y,z]]);K=M([[0,p],[-p,0]]);sol=s.solve(list(S+K-C),(x,y,z,p));S=S.subs(sol);K=K.subs(sol);assert S==S.T and K==-K.T and S+K==C
  roots=s.solve(S.det().subs(k,q-h),q);return [S,K,*sorted(roots,reverse=True)]
 if path=='matrix-products':
  A=M([[a,1,-b],[1,d,2]]);B=M([[1,a],[b,-1],[d,2]])
  if l==1:return [(M([[1,b]])*M([a,d]))[0]]
  if l==2:return [(M([[a,1],[0,b]])*M([[1,0],[d,1]]))[0,0]]
  if l==3:return [M(2,2,lambda i,j:sum(A[i,r]*B[r,j] for r in range(3)))]
  if l==4:
   C=M([[a,1],[1,b]]);Q=M([[a*d-a,d-a*b]]);return [C.T.inv().multiply(Q.T).T]
  C=M([[1,0,a],[0,1,b]]);F=M([[x,y],[p,q],[d,1]]) if l==5 else M([[x,y],[p,q],[u,w]])
  sol=s.solve(list(C*F-s.eye(2)),(x,y,p,q));F=F.subs(sol);assert C*F==s.eye(2)
  if l==5:return [F,F*C]
  n=C.nullspace()[0];assert n!=s.zeros(3,1) and F*C*n==s.zeros(3,1) and s.simplify((F*C)**2-F*C)==s.zeros(3,3);return [F,n,F*C]
 if path=='vector-combinations':
  A=M([a,-b,d]);B=M([1,d,-a]);P=M([1,2,3])
  if l==1:return [sum([-a,b,b])]
  if l==2:return [M([sum([e]*a) for e in A])]
  if l==3:return [M([sum([j,j,-i,-i,-i]) for j,i in zip(A,B)])]
  if l==4:
   Q=P+A;R=P+B;assert A.cross(B)!=s.zeros(3,1);mid=(Q+R)/2;S=2*mid-P;assert S-Q==R-P and S-R==Q-P;return [S,mid]
  if l==5:
   Q=P+A;first=1+s.Rational(a,b);param=s.solve((P+t*(Q-P))[0]-first,t)[0];return [param,P+param*(Q-P),s.simplify(param/(1-param))]
  U=M([a,0,1]);V=M([0,b,1]);target=M([h,k,z]);sol=s.solve(list(p*U+q*V-target),(p,q,z));assert U.cross(V)!=s.zeros(3,1);assert s.simplify(p*U+q*V-target).subs(sol,simultaneous=True).applyfunc(s.simplify)==s.zeros(3,1);return [sol[p],sol[q],sol[z],1-sol[p]-sol[q]]
 if path=='perpendicular-test':
  A=M([a,b,0]);B=M([b,-a,d]);P=M([1,2,3])
  if l==1:return [(M([[1,-a,b]])*M([d,b,2]))[0]]
  if l==2:
   Z=s.zeros(3,1);return [Z.dot(A),bool(Z.norm()!=0 and A.norm()!=0)]
  if l==3:return [(A.T*B)[0],(A.T*(B+M([1,0,0])))[0]]
  if l==4:
   Q=P+A;R=P+B;return [(j-i).dot(k-i) for i,j,k in ((P,Q,R),(Q,P,R),(R,P,Q))]
  if l==5:
   C=M([a,1,0]);D=M([0,b,1]);N=C.cross(D);W=d*N/N[2];assert W.dot(C)==W.dot(D)==0 and W.norm()!=0;return [W]
  C=M([h,k,0]);D=M([k-a,h-b,0]);E=C.dot(D);K=s.solve(E,k)[0];pole=s.solve(s.diff(E,k),h)[0];assert E.subs(h,pole)!=0 and s.simplify(E.subs(k,K))==0
  zero1=s.solve(list(C),(h,k));zero2=s.solve(list(D),(h,k));return [K,pole,M([zero1[h],zero1[k]]),M([zero2[h],zero2[k]])]
 raise ValueError(path)

def equivalent(actual,expected):
 local={str(v):v for v in (h,k,t,z,u,w,x,y,p,q)}
 if type(expected) is bool:return type(actual) is bool and actual==expected
 if isinstance(expected,s.MatrixBase):
  if not isinstance(actual,dict) or set(actual)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in actual['matrix']]);return m.shape==expected.shape and all(s.simplify(e)==0 for e in m-expected)
 return isinstance(actual,str) and s.simplify(s.sympify(actual,locals=local)-expected)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
