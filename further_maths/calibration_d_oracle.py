"""Independent SymPy fact checks, not certification of prose or difficulty."""
import sympy as s
M=s.Matrix
k,h,d,C=s.symbols('k h d C',real=True)

def oracle(path,l,v):
 a=v+1;b=a+1
 if path=='det-two':
  A=M([[a,1],[2,b]])
  if l==1:return [A.det()]
  if l==2:
   B=A.copy();B.row_swap(0,1);return [A.det(),B.det()]
  if l==3:return [M([[a,-2],[3,b]]).det()]
  if l==4:
   B=M([[2,1],[0,a]]);P=A*B;return [P.det(),(P*B.inv()).det()]
  if l==5:
   B=M([[k,a],[b,k]]);E=s.diag(a,1);roots=s.solve((B*E).det()+a*a,k);return [*roots,all(B.subs(k,r).det()!=0 for r in roots)]
  p=M([[k,a],[a,k]]).det();vertex=s.solve(s.diff(p,k),k)[0];bound=p.subs(k,vertex)
  counts=[len(s.solveset(p-target,k,domain=s.S.Reals)) for target in (bound-1,bound,bound+1)]
  roots=s.solve(p-d,k);assert all(s.simplify(p.subs(k,r)-d)==0 for r in roots)
  return [p,bound,*counts]
 if path=='inverse-product':
  A=M([[1,a],[0,1]]);B=s.diag(b,1);P=A*B;u=M([1,2]);w=P*u
  if l==1:return s.solve(a*b*k-2*a*b,k)
  if l==2:return [P.inv(),A.inv()*B.inv()]
  if l==3:return [P.inv()]
  if l==4:return [A.LUsolve(w),P.LUsolve(w)]
  if l==5:return [P.inv().inv()*B.inv()]
  U=M([[1,k],[0,1]]);D=s.diag(h,b);left=(U*D).inv();right=U.inv()*D.inv();diff=s.factor((left-right)[0,1]*b*h)
  # The difference numerator may have the opposite sign; choose the BA-AB convention.
  comm=D*U-U*D
  assert s.simplify(diff-comm[0,1])==0 or s.simplify(diff+comm[0,1])==0
  assert U.det()==1 and D.det()==b*h
  assert s.solve(comm[0,1],h)==[b] and comm.subs(k,0)==s.zeros(2)
  return [comm[0,1],s.solve(comm[0,1],h)[0]]
 if path=='perpendicular-parameter':
  if l==1:return s.solve(2*k+a*b-1,k)
  if l==2:
   u=M([k-a,0,0]).subs(k,a);w=M([1,b,0]);return [u.dot(w),bool(u.norm()*w.norm()!=0)]
  if l==3:return s.solve(M([k,a,1]).dot(M([2,b,-1])),k)
  if l==4:return s.solve((M([k,2,0])-M([a,0,1])).dot(M([1,b,1])),k)
  if l==5:
   u=M([1,a,0]);w=M([0,1,b]);n=u.cross(w);n=n/n[2];return [n[0],n[1]]
  p=M([k,a,1]).dot(M([k,-a,h]));bound=s.solve(p.subs(k,0),h)[0]
  counts=[len(s.solveset(p.subs(h,target),k,domain=s.S.Reals)) for target in (bound+1,bound,bound-1)]
  assert all(s.simplify(p.subs(k,r))==0 for r in s.solve(p,k))
  return [p,bound,*counts]
 if path=='triangle-area':
  # Gram determinant gives the unsigned area independently of the cross-product norm.
  area=lambda u,w:s.sqrt(s.expand(u.dot(u)*w.dot(w)-u.dot(w)**2))/2
  if l==1:return [area(M([a,0,0]),M([0,b,0]))]
  if l==2:
   u=M([a,0,0]);w=M([0,b,0]);return [u.cross(w),w.cross(u),area(u,w)]
  if l==3:
   u=M([a,0,0]);w=M([0,b,1]);return [u.cross(w),area(u,w)]
  if l==4:
   p=M([1,2,3]);q=M([a+1,3,3]);r=M([1,b+2,4]);u=q-p;w=r-p;return [u,w,u.cross(w),area(u,w)]
  if l==5:
   ar=area(M([a,0,0]),M([k,b,k]));target=a*s.sqrt(a*a+b*b)/2;roots=s.solve(ar**2-target**2,k);assert all(s.simplify(ar.subs(k,r)-target)==0 for r in roots);return roots
  ar=area(M([a,0,0]),M([k,k-b,k]));sq=s.expand(ar**2);vertex=s.solve(s.diff(sq,k),k)[0];mn=ar.subs(k,vertex)
  poly=s.Poly(sq-C*C,k);coeff=poly.all_coeffs();disc=s.factor(s.discriminant(poly.as_expr(),k)/coeff[0]**2)
  counts=[len(s.solveset(sq-target**2,k,domain=s.S.Reals)) for target in (s.S.Zero,mn,mn+1)]
  roots=s.solve(sq-C*C,k);assert all(s.simplify(sq.subs(k,r)-C*C)==0 for r in roots)
  return [mn,vertex,disc,*counts]
 raise ValueError(path)

def equivalent(a,b):
 if isinstance(b,bool):return type(a) is bool and a==b
 local={'k':k,'h':h,'d':d,'C':C}
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(e)==0 for e in m-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
