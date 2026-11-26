"""Independent exact checks using linear solvers and determinant expansions."""
import sympy as s
from calibration_p_oracle import equivalent as old_equivalent
M=s.Matrix
k,h,t,u,x,y,z,p,q=s.symbols('k h t u x y z p q',real=True)
def solve3(eq,free=None):
 sol=next(iter(s.linsolve(eq,(x,y,z))))
 return M(sol).subs(free or {})
def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 if path=='inconsistent-geometry':
  if l==1:return [s.linsolve([x-a,x-b],(x,y,z))!=s.EmptySet]
  if l==2:
   eq=[x-a,y-b,x+y-a-b-1];assert all(s.linsolve([eq[i],eq[j]],(x,y,z))!=s.EmptySet for i,j in ((0,1),(0,2),(1,2)));return [s.linsolve(eq,(x,y,z))!=s.EmptySet,solve3(eq[:2],{z:t})]
  if l==3:
   A=M([[1,a,0],[0,1,1],[1,a+1,1]]);B=M([b,d,b+2*d]);return [A.rank()==A.row_join(B).rank(),(M([[-1,-1,1]])*B)[0]]
  if l==4:
   e=[x-a,y-b,x+y-a-b-d];return [solve3([e[i],e[j]],{z:t}) for i,j in ((0,1),(0,2),(1,2))]
  if l==5:
   A=M([[1,a,0],[0,1,1],[1,a+2,2]]);B=M([b,d,k]);null=A.T.nullspace()[0];K=s.solve(null.dot(B),k)[0];assert all(A[[i,j],:].rank()==2 for i,j in ((0,1),(0,2),(1,2)));return [K,solve3([x+a*y-b,y+z-d],{z:t})]
  e=[x-a,y-b,(k-a)*(x-a)+y-h];condition=s.solve(e[2].subs({x:a,y:b}),h)[0];pole=s.solve(s.diff(e[2],x),k)[0];assert s.linsolve([e[1],e[2].subs({k:pole,h:condition+1})],(x,y,z))==s.EmptySet;return [pole,condition,*[solve3([e[i],e[j]],{z:t}) for i,j in ((0,1),(0,2),(1,2))]]
 if path=='nonunique-geometry':
  if l==1:return [solve3([x-a,y-b],{z:t})]
  if l==2:return [solve3([x-a,2*x-2*a,b*x-a*b],{y:t,z:u})]
  if l==3:return [solve3([x+a*y+z-d,y+z-b,x+(a+1)*y+2*z-d-b],{z:t})]
  if l==4:return [solve3([x+a*y+b*z-d,-2*x-2*a*y-2*b*z+2*d,3*x+3*a*y+3*b*z-3*d],{y:t,z:u})]
  if l==5:
   V=solve3([y-2*x-b+2*a,z+x-d-a],{z:d-t});expr=s.Poly(V.dot(M([1,k,h]))-a-b,t);sol=s.solve(expr.all_coeffs(),(k,h),dict=True)[0];return [sol[k],sol[h],V]
  e=[x-a,x+(k-a)*(y-b)-a,x+(k-a)*(y-b)-a-h+d];K=s.solve(s.diff(e[1],y),k)[0];H=s.solve(e[2]-e[1],h)[0];assert s.linsolve([e0.subs(h,H+1) for e0 in e],(x,y,z))==s.EmptySet;return [K,b,H,solve3([e0.subs(h,H) for e0 in e],{z:t}),solve3([e0.subs({h:H,k:K}) for e0 in e],{y:t,z:u})]
 A=M([1,a,0]);B=M([0,1,b]);C=M([d,0,1]);
 def cross(V,W):return M([M([[V[(i+1)%3],V[(i+2)%3]],[W[(i+1)%3],W[(i+2)%3]]]).det() for i in range(3)])
 if l==1:return [M([0,a,a*b])]
 if l==2:return [cross(a*A,B),cross(a*A,a*B)]
 if l==3:return [cross(A,a*B-b*C)]
 if l==4:
  target=cross(A,b*B-d*C);sol=next(iter(s.linsolve(list(cross(A,p*B+q*C)-target),(p,q))));return list(sol)
 if l==5:
  V=b*B+d*C;W=cross(A,V);sol=next(iter(s.linsolve(list(cross(A,M([x,y,z]))-W),(x,y,z))));X=M(sol);return [X.subs(y,a*t+V[1])]
 S=M([a,0,0]);X=M([t,y,z]);Y=S-X;eq=cross(X,Y);sol=s.solve(list(eq-M([0,k,h])),(y,z),dict=True)[0];X=X.subs(sol);Y=S-X;T=s.solve(X.dot(X)-Y.dot(Y),t)[0];return [X,Y,T,s.linsolve(list(eq-M([1,k,h])),(y,z))!=s.EmptySet]
def check(p):
 try:
  e=oracle(p['path'],p['tier'],p['variant']);return len(e)==len(p['facts']) and all(old_equivalent(a,b) for a,b in zip(p['facts'],e))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
