"""Separate symbolic checks; structured facts are not a certification of prose or demand."""
import sympy as s
M=s.Matrix
k,h,t=s.symbols('k h t',real=True)

def oracle(path,l,v):
 a=v+1;b=v+2
 if path=='inverse-three':
  A=M([[1,a,0],[0,1,b],[0,0,1]]);N=A.inv()
  if l==1:return list(M([[1,a],[0,1]]).inv()*M([0,b]))
  if l==2:
   B=M([[1,-a,0],[0,1,-b],[0,0,1]]);return [(A*B)[0,2],N[0,2]]
  if l in (3,4):
   A=M([[1,a,0],[1,a+1,b],[0,1,1]]);N=A.inv();return [N] if l==3 else [N,A.LUsolve(M([b,a,1]))]
  if l==5:
   B=M([[1,a,0],[0,k,b],[0,0,1]]);rr=s.solve(B.inv()[0,2]-a,k);assert len(rr)==1 and rr[0]!=0;return [rr[0],B.subs(k,rr[0]).inv()]
  B=M([[1,a,0],[0,k,b],[0,0,h]])
  null1=B.subs(k,0).nullspace();assert null1==B.subs({k:0,h:0}).nullspace()
  null2=B.subs(h,0).nullspace();assert len(null1)==len(null2)==1
  return [B.det(),B.inv(),null1[0],null2[0]]
 if path=='composition-compute':
  A=M([[1,a],[0,1]]);B=M([[0,-1],[1,0]]);T=B*A
  if l==1:return [B*M([a,b])]
  if l==2:return [T*M([1,0]),A*B*M([1,0])]
  if l==3:return [T]
  if l==4:
   X=s.Symbol('X');curve=T*M([k,b*k+1]);Y=s.expand(curve[1].subs(k,s.solve(curve[0]-X,k)[0]));return [T,Y.coeff(X),Y.subs(X,0)]
  if l==5:
   C=M([[b,1],[2,1]]);U=C*A.inv();assert U*A==C;return [U,C*M([a,b])]
  A=M([[1,a*k],[0,1]]);B=M([[1,0],[b*h,1]]);BA=B*A;AB=A*B;assert BA.det()==AB.det()==1
  return [BA,AB,(BA-AB)[1,1]]
 if path=='plane-cartesian':
  n=M([a,1,2]);P=M([1,b,0]);Q=M([2,b-a,0]);R=M([1,b-2,1]);d=n.dot(P)
  if l==1:return [d]
  if l==2:return [(2*n).dot(P)]
  if l==3:return [n,d]
  if l==4:
   u=(Q-P).cross(R-P);u=u/u[1];assert u.dot(P)==u.dot(Q)==u.dot(R);return [u,u.dot(P)]
  if l==5:
   D=s.Symbol('D');z=s.Symbol('z');nn=M([k,1,2]);sol=s.solve([nn.dot(P)-D,nn.dot(Q)-D],(k,D));return [sol[k],sol[D],s.solve(2*z-sol[D],z)[0]]
  u=Q-P;ww=M([0,h,k]);cross=ww.cross(u);assert s.simplify(cross.dot(u))==s.simplify(cross.dot(ww))==0
  ns=M([list(u)]).nullspace();assert len(ns)==2
  return [cross,cross.dot(P),*ns]
 if path=='line-line-angle':
  d=M([1,a,0]);e=M([1,-b,0]);cos=lambda u,v:abs(u.dot(v))/(u.norm()*v.norm())
  if l==1:return [d.norm()]
  if l==2:return [cos(d,e)]
  if l==3:return [cos(d,e),s.acos(cos(d,e))]
  if l==4:
   P=M([1,2,0]);Q=M([2,a+2,1]);R=M([2,0,1]);S=M([3,0,1-b]);return [Q-P,S-R,cos(Q-P,S-R),s.acos(cos(Q-P,S-R))]
  if l==5:
   e=M([k,a,0]);eq=s.expand(4*e[0]**2-e.dot(e));return sorted(s.solveset(eq,k,domain=s.S.Reals),key=float)
  e=M([k,a,k-b]);eq=s.expand(e[0]**2-t*e.dot(e));disc=s.factor(s.discriminant(eq,k));rr=s.solve(disc,t);T=max(rr);linear=s.solve(eq.subs(t,s.Rational(1,2)),k)[0]
  sample=[0,s.Rational(1,4),s.Rational(1,2),(s.Rational(1,2)+T)/2,T,(T+1)/2]
  counts=[]
  for target in sample:
   roots=s.solveset(eq.subs(t,target),k,domain=s.S.Reals);counts.append(len(roots));assert all(s.simplify(e[0]**2/e.dot(e).subs(k,i)-target).subs(k,i).simplify()==0 for i in roots)
  return [eq,T,linear,*counts]
 raise ValueError(path)

def equivalent(a,b):
 local={str(z):z for z in (k,h,t)}
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(e)==0 for e in m-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
