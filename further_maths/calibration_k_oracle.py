"""Independent checks by coordinate solving, geometric projection, and determinant identities."""
import sympy as s
M=s.Matrix
k,h,t,x,y,z,C=s.symbols('k h t x y z C',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;c=2*v+3
 if path=='fixed-invariant':
  A=M([[1,0],[0,a]])
  if l==1:return [a*b==a*b]
  if l==2:return [A*M([0,b])]
  if l==3:
   P=A*M([c,0]);D=A*M([0,1]);return [P[0],bool(D[0]==0 and D[1]!=0),bool(D==M([0,1]) and P==M([c,0]))]
  if l==4:return [(A*M([0,0]))[1],(A*M([0,b]))[1],(A*M([c,0]))[0]]
  if l==5:
   A=M([[1,k],[0,a]]);u=M([b,a-1]);d=A*u;root=s.solve(M.hstack(u,d).det(),k)[0];assert A.subs(k,root)*u==a*u;assert s.solve(list((A.subs(k,root)-s.eye(2))*t*u),t)=={t:0};return [root,M([0,0])]
  A=M([[1,0],[0,k/v]]);m,d=s.symbols('m d',real=True);u=M([1,m]);p=M([0,d]);assert s.factor(M.hstack(u,A*u).det())==s.factor(m*(k-v)/v);assert s.factor(M.hstack(u,A*p-p).det())==s.factor(d*(k-v)/v);assert A.subs(k,v)==s.eye(2) and A.subs(k,0).rank()==1;return [A[1,1],s.solve(A.det(),k)[0],s.solve(A[1,1]-1,k)[0]]
 if path=='nonunique-set':
  if l==1:return [s.solve(x+a-b,x)[0]]
  if l==2:
   A=M([[1,1],[a,a]]);B=M([b,a*b]);assert A.rank()==A.row_join(B).rank()==1;return [M([b,0]),M([0,b])]
  if l==3:
   sol=next(iter(s.linsolve([x+y+t-b,y+a*t-c],(x,y))));return [M([*sol,t])]
  if l==4:
   A=M([[1,1,0],[0,1,1],[1,0,-1]]);B=M([b,c,b-c]);assert A.rank()==2;P=M([b-c,c,0]);D=A.nullspace()[0];assert A*P==B;return [P,D,P+a*D]
  if l==5:
   A=M([[1,1,0],[0,1,1],[1,0,-1]]);P=M([b,c,0]);D=A.nullspace()[0];assert A*P==M([b+c,c,b]);roots=s.solve((t*D).dot(t*D)-3*a*a,t);return [P+r*D for r in roots]
  sol=next(iter(s.linsolve([x+y+t-b,y+a*t-h],(x,y))));lo=s.solve(sol[0],t)[0];hi=s.solve(sol[1],t)[0];assert s.diff(sol[0],t)>0 and s.diff(sol[1],t)<0;endpoint=s.solve(lo-hi,h)[0];assert hi.subs(h,0)==0 and lo.subs(h,endpoint)==b;assert s.simplify(hi-lo)==(s.Rational(a*b, a*(a-1))-h/(a*(a-1)));return [0,endpoint,hi,lo]
 if path=='plane-common-point':
  if l==1:return [M([a,b,c]).dot(M([1,1,1]))]
  if l==2:
   P=M([a,b,0]);return [M([1,1,0]).dot(P),M([1,0,1]).dot(P)]
  A=M([[1,1,0],[1,a,1]]);B=M([b,c]);P=M(A[:,[0,2]].inv()*B);P=M([P[0],0,P[1]])
  if l==3:return [P]
  if l==4:
   D=A.nullspace()[0];D=D/D[1];assert A*P==B and A*D==s.zeros(2,1);return [P,P+D,D]
  if l==5:
   A=M([[1,1,0],[1,a+1,1],[1,0,-1]]);B=M([b,c,0]);assert A.det()!=0;return [A.inv()*B]
  A=M([[1,1,0],[1,k,1]]);B=M([b,h]);G=A*A.T;assert s.expand(G.det())==k*k-2*k+3;Q=s.simplify(A.T*G.inv()*B);assert all(s.simplify(e)==0 for e in A*Q-B);return [Q[1],Q,s.factor(Q.dot(Q))]
 if path=='related-solids':
  U=M([a,0,0]);V=M([1,b,0]);W=M([1,2,c]);det=abs(M.hstack(U,V,W).det());base=U.cross(V).norm()/2;height=abs(W.dot(U.cross(V)))/U.cross(V).norm()
  if l==1:return [2*base*height]
  if l==2:return [(3*det)/3]
  if l==3:return [base*height/3]
  if l==4:return [base*height/3,base*height,height]
  if l==5:
   r=s.Rational(v,v+2);expr=s.factor(M.hstack(t*U,t*V,W).det()/det);return [root for root in s.solve(expr-r*r,t) if 0<=root<=1]
  r=s.Rational(v,v+1);ratio=s.factor(M.hstack(t*U,(1-t)*V,r*W).det()/det);vertex=s.solve(s.diff(ratio,t),t)[0];assert vertex==s.Rational(1,2) and s.diff(ratio,t,2)<0;roots=s.solve(ratio-C,t);assert len(roots)==2;return [ratio.subs(t,vertex),s.simplify(roots[1]-roots[0])]
 raise ValueError(path)

from calibration_j_oracle import equivalent

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
