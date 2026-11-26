"""Independent structured-answer checks. These do not certify prose or difficulty."""
import sympy as s
from calibration_b_oracle import equivalent
M=s.Matrix
k,h,x,y,t,u,c=s.symbols('k h x y t u c',real=True)

def oracle(path,l,v):
 a=v+1;b=a+2
 if path=='det-three':
  A=M([[a,1,0],[1,b,1],[0,1,2]])
  if l==1:return [A[:2,:2].det()]
  if l==2:
   A.row_swap(0,2);return [A.det()]
  if l==3:return [A.det(method='berkowitz')]
  if l==4:
   B=M([[a,1,0],[1,b,1],[a,2,2]]);return [B.det(method='berkowitz'),B.rank()==3]
  if l==5:
   B=M([[a,1,0],[1,b,1],[0,1,k]]);r=s.solve(B.det(),k);return [r[0],B.subs(k,r[0]).rank()]
  B=M([[k,a,0],[a,k,a],[0,a,k]]);d=B.det(method='berkowitz');roots=sorted(s.solve(d,k),key=lambda r:float(r));ranks={B.subs(k,r).rank() for r in roots}
  if len(ranks)!=1 or B.extract([0,1],[1,2]).det()==0:raise ValueError('Rank proof check failed')
  return [d,*roots,ranks.pop(),B.subs(k,1).rank()]
 if path=='fixed-points':
  if l==1:return s.solve(a*y+b-b,y)
  if l==2:
   A=s.diag(a,1);return [A*M([1,0]),s.solve((a-1)*x,x)[0]]
  if l==3:return (M([[1,a],[0,b]])-s.eye(2)).nullspace()
  if l==4:
   A=M([[1+a,-a],[a,1-a]]);p=M([2,1]);q=A*p;return [q,*(A-s.eye(2)).nullspace(),q-p]
  if l==5:
   A=M([[k,a],[0,1]]);p=M([a,b]);j=s.solve(list(A*p-p),k)[0][0] if isinstance(s.solve(list(A*p-p),k),list) else s.solve(list(A*p-p),k)[k]
   B=A.subs(k,j);basis=(B-s.eye(2)).nullspace()[0];return [j,basis*(b/basis[1])]
  B=M([[k,a],[0,h]])-s.eye(2)
  # The nonzero off-diagonal entry excludes rank zero for every parameter.
  d=B.det();assert s.factor(d-(k-1)*(h-1))==0 and B[0,1]!=0
  basis=B.subs(k,1).nullspace()[0];direction=B.subs(h,1).nullspace()[0]
  # scale symbolic nullspace vector to requested convention
  return [basis,direction*(k-1),len(B.subs({k:2,h:2}).nullspace()),len(B.subs({k:1,h:1}).nullspace())]
 if path=='plane-plane-angle':
  angle=lambda n,m:s.acos(s.simplify(abs(n.dot(m))/(n.norm()*m.norm())))
  if l==1:return [s.acos(s.Rational(a,2*a))]
  if l==2:return [angle(M([-a,-a*s.sqrt(3),0]),M([1,0,0]))]
  if l==3:return [angle(M([a,a*s.sqrt(3),0]),M([0,1,0]))]
  if l==4:
   n=M([a,0,a]).cross(M([0,b,0]));n=n/n[2];return [n,angle(n,M([0,0,1]))]
  if l==5:
   n=M([k,a,0]);m=M([1,0,0]);return s.solve(4*n.dot(m)**2-n.dot(n)*m.dot(m),k)
  n=M([a,k,0]);m=M([a,-k,0]);numer=n.dot(m);den=n.dot(n)
  # Norms are identical and nonzero; count roots using squared cosine at endpoints and an interior value.
  counts=[len(s.solve(numer**2-value*value*den**2,k)) for value in (s.S.One,s.Rational(1,2),s.S.Zero)]
  # Recover each symbolic squared root independently from the signed equations.
  w=s.Symbol("w",real=True);num=numer.subs(k*k,w);de=den.subs(k*k,w)
  branches=[s.solve(num-sign*c*de,w)[0] for sign in (1,-1)]
  return [*counts,s.solve(numer,k)[-1],*branches]
 if path=='line-line-distance':
  if l==1:return [M([a,0,b]).norm()]
  if l==2:
   p=M([a,b,0]);d=M([1,0,0]);return [p.cross(d).norm()/d.norm()]
  if l==3:
   p=M([a,0,b]);n=M([1,0,0]).cross(M([0,1,0]));return [abs(p.dot(n))/n.norm()]
  if l==4:
   p=M([t,t,0]);q=M([a,u,b]);w=p-q;D=w.dot(w);j=s.solve([s.diff(D,t),s.diff(D,u)],(t,u));return [p.subs(j),q.subs(j),s.sqrt(D.subs(j))]
  if l==5:
   p=M([0,a,k]);d=M([1,0,0]);roots=s.solve(p.cross(d).dot(p.cross(d))-b*b,k);return [*roots,p]
  p=M([t,0,0]);q=M([a+u,b+k*u,h]);w=p-q;D=w.dot(w);j=s.solve([s.diff(D,t),s.diff(D,u)],(t,u));parallel=D.subs({k:0,t:a+u});return [s.sqrt(s.simplify(parallel)),s.sqrt(s.simplify(D.subs(j))),j[t],j[u]]
 raise ValueError(path)

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all((isinstance(a,str) and s.simplify(s.sympify(a,locals={'c':c})-b)==0) if isinstance(b,s.Expr) and c in b.free_symbols else equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
