"""Independent exact checks of structured facts; prose proofs require editorial review.
No evaluation of arbitrary learner-supplied expressions. Inputs are local fixtures only.
"""
import sympy as s
from calibration_bank import PATHS
M=s.Matrix;I=s.I
x,k,t,h,y,z=s.symbols('x k t h y z',real=True)

def encoded(v):
 if isinstance(v,bool):return v
 if isinstance(v,s.MatrixBase):return {'matrix':[[str(e) for e in row] for row in v.tolist()]}
 return str(v)

def equivalent(a,b):
 if isinstance(b,bool):return type(a) is bool and a==b
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  try:
   m=M([[s.sympify(e,locals={'x':x,'k':k,'t':t}) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(v)==0 for v in m-b)
  except (ValueError,TypeError,s.SympifyError):return False
 if not isinstance(a,str):return False
 try:return s.simplify(s.sympify(a,locals={'x':x,'k':k,'t':t})-b)==0
 except (ValueError,TypeError,s.SympifyError):return False

def oracle(path,l,v):
 a=v+1;b=v+3;poly=s.Poly((x-a)*(x-b),x);p=poly.TC();u=-poly.nth(1);roots=poly.all_roots();R=s.Rational
 if path=='root-squares':
  m=sum(r*r for r in roots)
  if l==1:return [s.Poly.from_list([1,2*a,a*a],x).as_expr()]
  if l in (2,3):return [m]
  if l==4:return [sum((r+a)**2 for r in roots)]
  if l==5:
   sol=s.solve(u*u-2*k-m,k);return [sol[0],s.discriminant(x*x-u*x+sol[0],x)]
  sums=s.solve(k*k-(m+2*p),k);return [x*x-j*x+p for j in reversed(sums)]
 if path=='reciprocal':
  r=sum(1/r for r in roots);rev=s.Poly.from_list(list(reversed(poly.all_coeffs())),x).monic().as_expr()
  if l in (1,2):return [r]
  if l==3:return [rev]
  if l==4:return [s.expand(s.prod(x-1/(j+1) for j in roots))]
  if l==5:return [s.solve(u/k-r,k)[0],rev]
  # Reversal of a quadratic under x -> p/x; compare polynomial identity.
  f=x*x-k*x+p;assert s.expand(x*x*f.subs(x,p/x)/p-f)==0
  return s.solve(s.discriminant(f,x),k)
 if path=='complex-division':
  w=1+a*I;Z=a+(b+1)*I
  if l==1:return [s.expand(w*s.conjugate(w))]
  if l==2:return [s.expand_complex(1/w)]
  # Solve the real 2x2 linear system representing multiplication by w.
  c,d=s.symbols('c d',real=True); sol=s.solve([c-a*d-a,a*c+d-(b+1)],(c,d));Q=sol[c]+I*sol[d]
  if l==3:return [Q]
  if l==4:return [Q,s.sqrt((a*a+(b+1)**2)/(s.Integer(1)+a*a))]
  if l==5:
   sol=s.solve([c-a,b*c-k],(c,k));return [sol[k],sol[c]]
  sol=s.solve([-a*d-k,d-b],(d,k));return [sol[k],sol[d]]
 if path=='locus-intersection':
  c=a;r=b
  if l==1:return [M([a,b]).dot(M([a,b]))]
  if l==2:return [c,r,False]
  f=(x-c)**2+y*y-r*r
  if l==3:return [c+I*j for j in s.solve(f.subs(x,c),y)]
  if l==4:
   bx=s.solve((x-c)**2-(x-c-2)**2,x)[0];return [bx+I*j for j in s.solve(f.subs(x,bx),y)]
  if l==5:
   vals=s.solve([f,y-s.sqrt(3)*(x-c)],(x,y));return [u+I*v for u,v in vals if v>0]
  expr=s.solve(f.subs({x:k,y*y:t}),t)[0];ends=s.solve(expr,k)
  # Test outside, tangent, centre. Exact solutions over reals.
  counts=[len(s.solve(f.subs(x,j),y)) for j in (ends[0]-1,ends[0],c)]
  return [*ends,expr,*counts]
 if path=='det-area':
  A=M([[a,1],[0,b]]);E=M([[1,0],[0,-2]])
  if l==1:return [M([a,0,0]).cross(M([0,b,0])).norm()]
  if l==2:return [M.diag(1,-1).det(),p]
  if l==3:return [abs(s.det(M.hstack(A*M([3,0]),A*M([0,2]))))/2]
  if l==4:
   B=E*A;return [B,abs(s.det(M.hstack(B*M([3,0]),B*M([0,2]))))/2]
  if l==5:
   B=M([[k,a],[1,b]]);return s.solve(B.det()**2-a*a,k)
  # Solve real roots at representative scale values on either side of boundary.
  B=M([[k,a],[1,k]]);return [a,*[len(s.solve(B.det()**2-c*c,k)) for c in (0,R(a,2),a,a+1)]]
 if path=='system-consistency':
  if l==1:return list(M([[1,1],[1,-1]]).inv()*M([a+b,a-b]))
  B=M([[1,1],[2,2]])
  if l==2:return [int(B.row_join(M([a,2*a+1])).rank()==B.rank()),int(B.row_join(M([a,2*a])).rank()==B.rank())]
  if l==3:
   C=M([[1,1],[2,b+1]]);assert B.rank()==B.row_join(M([a,2*a])).rank()==1;return list(C.inv()*M([a,2*a]))
  A=M([[1,1,0],[0,1,1],[1,2,k]])
  if l==4:
   rhs=M([a,b,a+b+1]);assert A.subs(k,1).rank()<A.subs(k,1).row_join(rhs).rank();return list(A.subs(k,2).inv()*rhs)
  if l==5:
   rhs=M([a,b,a+b]);assert A.subs(k,1).rank()==A.subs(k,1).row_join(rhs).rank()==2;return list((A.inv()*rhs).applyfunc(s.simplify))
  # Solve row dependence using nullspace of transpose, then parameterise at singular value.
  C=A.subs(k,1);n=C.T.nullspace()[0];threshold=s.solve(n.dot(M([a,b,h])),h)[0];sol=s.linsolve((C,M([a,b,threshold])),(x,y,t));return [threshold,M(next(iter(sol)))]
 if path=='point-line':
  P=M([2*a,0,b]);d=M([1,1,0]);norm=(P-t*d).dot(P-t*d).expand();m=s.solve(s.diff(norm,t),t)[0];H=m*d;D=s.sqrt(norm.subs(t,m))
  if l==1:return [norm.subs(t,m)]
  if l==2:return [(P-H).dot(d)]
  if l==3:return [D]
  if l==4:return [H,D]
  if l==5:
   expr=(M([2*a,0,k])-H).dot(M([2*a,0,k])-H);return [*s.solve(expr-D**2,k),H]
  assert s.diff(norm,t,2)>0;return [H,D,*s.solve(norm-(D**2+8),t)]
 if path=='skew':
  if l==1:return [M([1,a,0]).cross(M([2,2*a,0]))==s.zeros(3,1)]
  if l==2:return [bool(s.linsolve([x, y, s.Integer(a)],(x,y)))]
  if l==3:return [M([a,0,0])]
  if l==4:
   sol=s.solve([x-b,a*x-y],(x,y));return [sol[x],sol[y]]
  if l==5:
   sol=s.solve([x-b,a*x-y,k],(x,y,k));return [M([sol[x],sol[y],0])]
  # Independently classify by rank of the direction matrix vs augmented displacement.
  def meets(K,H):
   B=M([[1,-1],[0,-K],[0,0]]);return B.rank()==B.row_join(M([a,0,H])).rank()
  return [M([a,0,0]),*[meets(K,H) for K,H in ((0,0),(0,1),(1,0),(1,1))]]
 raise ValueError('Unknown path')

def check(body):
 expected=oracle(body['path'],body['tier'],body['variant']);given=body['facts']
 return len(given)==len(expected) and all(equivalent(a,b) for a,b in zip(given,expected))
