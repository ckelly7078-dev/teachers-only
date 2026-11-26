"""Independent structured checks using entry equations, nullspaces and linear spans."""
import sympy as s
M=s.Matrix
k,h,t,C=s.symbols('k h t C',real=True)
x,y,z=s.symbols('x y z',real=True)
def oracle(path,l,v):
 a=v+1;b=v+3;c=2*v+3
 if path=='zero-matrix':
  A=M([[a,-1],[b,c]]);O=s.zeros(2)
  if l==1:return [s.solve(a+x-a,x)[0]]
  if l==2:return [A.applyfunc(lambda e:e+0),A*O]
  if l==3:
   B=M([[1,b],[0,a]]);return [M(2,2,lambda i,j:A[i,j]+B[i,j])]
  if l==4:
   A=M([[a,1],[a*b,b]]);B=M([[1,2],[-a,-2*a]]);assert A.rank()==1 and B.rank()==1;return [A*B, A.det()]
  A=M([[a,1],[k,b]]);root=s.solve(A.det(),k)[0];N=A.subs(k,root).nullspace()[0];N=N/N[0];assert N==M([1,-a])
  if l==5:
   assert s.solve(list(A*M([c,-a*c])),k)=={k:root};return [root,N]
  assert A.subs(k,root).rank()==1 and A.subs(k,root)*N==s.zeros(2,1);return [A.det(),root,N]
 if path=='scalar-matrix':
  A=M([[a,-1],[b,c]])
  if l==1:return [a*(-b),a*c]
  if l==2:return [A+A]
  if l==3:return [A.applyfunc(lambda x:-b*x)]
  if l==4:
   p,q=s.symbols('p q');B=a*A-b*s.eye(2);sol=s.solve(list(p*A+q*s.eye(2)-B),(p,q));return [sol[p],sol[q]]
  if l==5:
   A=M([[a,1],[0,b]]);expr=(k*A).det();target=a*b*c*c;roots=s.solve(expr-target,k);assert all(expr.subs(k,r)>0 for r in roots);return sorted(roots)
  A=M([[k,a*k],[0,k]]);B=M([[h,a*h],[0,h*(h-b)]]);D=s.simplify((h/k*A-B)[1,1]);roots=s.solve(D,h);assert roots==[0,b+1];assert A.subs(k,0)==s.zeros(2);assert all((h/k*A-B).subs(h,r)==s.zeros(2) for r in roots);return [-D,roots[1]]
 if path=='vector-plane':
  P=M([1,2,3]);Q=M([1+a,2,4]);R=M([1,2+b,3]);U=Q-P;V=R-P
  if l==1:return [Q-P]
  if l==2:assert M.hstack(U,2*U).rank()==1;return [M([0,0,0])]
  if l==3:assert M.hstack(U,V).rank()==2;return [P,Q-P,R-P]
  if l==4:
   N=M.hstack(U,V).T.nullspace()[0];N=-N/N[0];W=P+2*U-V;sol=s.solve(list(P+t*U+k*V-W),(t,k));assert N.dot(W-P)==0;return [N,N.dot(P),sol[t],sol[k]]
  if l==5:
   W=M([1+a*c,2-b,k]);sol=s.solve(list(P+t*U+h*V-W),(t,h,k));return [sol[k],sol[t],sol[h]]
  E=M([a,0,0]);U=M([0,k,h]);V=M([0,b*b*h,k]);D=M.hstack(E,U,V).det()/a
  for sub,B in [({k:b*h},M([0,b,1])),({k:-b*h},M([0,-b,1]))]:
   assert M.hstack(E,B).rank()==2 and all(s.simplify(e)==0 for e in U.subs(sub).cross(B)) and all(s.simplify(e)==0 for e in V.subs(sub).cross(B))
  assert M.hstack(E,U,V).subs({k:0,h:0}).rank()==1
  return [D,M([0,b,1]),M([0,-b,1])]
 if path=='zero-cross':
  U=M([a,b,1]);V=2*U
  if l==1:return [s.solve(1*x-c,x)[0]]
  if l==2:return [s.zeros(3,1)]
  if l==3:
   V=-c*U;assert M.hstack(U,V).rank()==1;return [U.cross(V),V[2]/U[2]]
  if l==4:
   P=M([1,2,3]);Q=P+U;R=P-c*U;S=P+M([a,b,2]);assert M.hstack(Q-P,R-P).rank()==1 and M.hstack(Q-P,S-P).rank()==2;return [(Q-P).cross(R-P),(Q-P).cross(S-P)]
  if l==5:
   r=s.symbols('r',real=True);roots=s.solve((r*U).dot(r*U)-c*c*U.dot(U),r);return [j*U for j in roots]
  U=M([k,a,0]);V=M([h,k,0]);D=M([[U[0],V[0]],[U[1],V[1]]]).det();root=s.solve(D,h)[0];assert all(s.simplify(e)==0 for e in V.subs(h,root)-k/a*U);return [D,root]
 raise ValueError(path)
def equivalent(a,b):
 local={str(v):v for v in (k,h,t,C,x,y,z)}
 if isinstance(b,bool):return type(a) is bool and a==b
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  mat=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return mat.shape==b.shape and all(s.simplify(e)==0 for e in mat-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
