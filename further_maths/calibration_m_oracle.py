"""Independent structured checks via elimination, symbolic entry equations and nullspaces."""
import sympy as s
from calibration_l_oracle import equivalent
M=s.Matrix
k,h,t,x,y,z,c=s.symbols('k h t x y z c',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 if path=='two-variable-system':
  if l==1:return s.solve(a*x+b-(a*d+b),x)
  if l==2:
   A=M([[1,1],[b,b]]);B=M([a,a*b]);assert A.rank()==A.row_join(B).rank()==1;P=M(next(iter(s.linsolve((A,B),(x,t)))));return [P.subs(t,a),P.subs(t,0)]
  if l==3:
   A=M([[a,1],[1,b]]);B=M([a*b-d,b-b*d]);return [A.inv()*B]
  if l==4:
   A=M([[1,1],[d,a]]);B=M([a+b,d*a+a*b]);return [A.inv()*B]
  if l==5:
   sol=s.solve([x+y-a-b,a*x-b*y,k*x+a*y-d*b-a*a],(x,y,k),dict=True)[0];assert M([[1,1],[sol[k],a]]).det()!=0;return [sol[k],M([sol[x],sol[y]])]
  A=M([[1,1],[k,1]]);B=M([a,h]);P=A.inv()*B;assert all(s.simplify(e)==0 for e in A*P-B);sing=s.solve(A.det(),k)[0];S=A.subs(k,sing);assert S.rank()==1;condition=s.solve(S.T.nullspace()[0].dot(B),h)[0];assert condition==a;F=M(next(iter(s.linsolve((S,B.subs(h,condition)),(x,y))))).subs(y,a-t);return [(A*M([0,a]))[1],(A*M([a,0]))[1],P,F]
 if path=='inverse-identities':
  A=M([[a,1],[0,b]])
  if l==1:return s.solve(a*x-1,x)
  if l==2:
   B=s.eye(a);B[0,1]=b;return [B*B.inv(),B.inv()*B]
  if l==3:return [A.inv().inv(),A.inv()*A*A]
  if l==4:
   B=M([[1,d],[0,1]]);return [A.inv().inv()*B*B.inv()*A.inv()*B.inv()]
  if l==5:
   B=M([[1,b],[0,1]]);P=(B.inv()*A.inv()).inv();assert (P.inv()*A).inv()==B;return [P]
  A=M([[a,h],[0,k]]);assert s.solve(A.det(),k)==[0];E=A+A.inv()-c*s.eye(2);C=s.solve(E[0,0],c)[0];roots=s.solve(E[1,1].subs(c,C),k);free=[];zero=[]
  for r in roots:
   q=s.simplify(E[0,1].subs(k,r));assert r!=0
   if q==0:free.append(r)
   else:assert s.solve(q,h)==[0];zero.append(r)
  assert len(free)==len(zero)==1;return [C,free[0],zero[0]]
 if path=='normal-dot-plane':
  n=M([a,-1,b]);P=M([1,d,2]);D=n.dot(P)
  if l==1:return [n.dot(M([1,a,v]))]
  if l==2:return [D]
  if l==3:return [n.dot(M([a,b,-d]))]
  if l==4:return [D,bool(n.dot(P+M([1,a,0]))==D),bool(n.dot(P+M([0,0,1]))==D)]
  if l==5:
   N=M([k,-1,b]);root=s.solve(N.dot(M([1,a,0])),k)[0];return [root,N.subs(k,root).dot(P)]
  P=M([a,0,0]);Q=M([0,b,0]);N=M([x,y,h]);sol=s.solve([(Q-P).dot(N),N.dot(N)-1],(x,y));normals=[N.subs({x:u,y:w},simultaneous=True) for u,w in sol];normals.sort(key=lambda n: n[0].could_extract_minus_sign());assert len(normals)==2
  for n in normals:assert s.simplify(n.dot(n)-1)==0 and s.simplify(n.dot(Q-P))==0
  # Check the two normals can be proportional only at h=0 or h^2=1.
  cross=normals[0].cross(normals[1]);assert s.simplify(cross.subs(h,0))==s.zeros(3,1) and s.simplify(cross.subs(h,1))==s.zeros(3,1)
  return [*normals,s.simplify(normals[0].dot(P))]
 if path=='plane-intersection-line':
  if l==1:
   P=M([a,b,d]);return [bool(M([1,1,0]).dot(P)==a+b),bool(M([0,1,1]).dot(P)==b+d)]
  if l==2:return [M(next(iter(s.linsolve([x-a,y-b],(x,y,t)))))]
  if l==3:return [M(next(iter(s.linsolve([x+t-a,t+z-b],(x,t,z))))).subs(z,b-t)]
  if l==4:
   A=M([[1,a,0],[a,a*a,b]]);B=M([b,a*b+d]);return [M(next(iter(s.linsolve((A,B),(x,t,z)))))]
  if l==5:
   N=M([k,1,b]);K=s.solve(N.dot(M([1,-1,1])),k)[0];A=M([[1,1,0],[K,1,b]]);B=M([a,d]);F=M(next(iter(s.linsolve((A,B),(t,y,z)))));F=F.subs(z,t+s.Rational(d-a,b));assert all(s.simplify(e)==0 for e in A*F-B);return [K,F]
  A=M([[1,1,0],[k,1,h]]);B=M([a,b]);P=M(next(iter(s.linsolve((A,B),(x,y,z)))));P=s.simplify(P.subs(z,(b-a-(k-1)*t)/h));Q=M(next(iter(s.linsolve((A.subs(h,0),B),(x,y,t)))));assert all(s.simplify(e)==0 for e in A*P-B) and all(s.simplify(e)==0 for e in A.subs(h,0)*Q-B);Z=A.subs({k:1,h:0});assert Z.rank()<Z.row_join(B).rank();return [P,Q]
 raise ValueError(path)

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
