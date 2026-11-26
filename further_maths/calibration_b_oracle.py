"""Independent exact checks of locally authored structured facts, not prose certification."""
import sympy as s
M=s.Matrix
k,t,x,y,z,h=s.symbols('k t x y z h',real=True)
R=s.Rational

def oracle(path,l,v):
 a=v+1;b=v+3
 if path=='composition-order':
  A=M([[1,a],[0,1]]);B=s.diag(b,1);u=M([1,1]);C=B*A
  if l==1:return [C[0,0]+C[0,1]]
  if l==2:return [B*(A*u),A*(B*u)]
  if l==3:return [M.hstack(B*(A*M([1,0])),B*(A*M([0,1])))]
  if l==4:
   j=C*u;return [C,j[1]/j[0]]
  if l==5:
   S=M([[1,k],[0,1]]);sol=s.solve((B*S*u)[0]-b*(a+1),k)[0];return [sol,S.subs(k,sol)*B*M([0,1])]
  D=s.diag(h,b);S=M([[1,k],[0,1]]);return [s.solve((D*S-S*D)[0,1],h)[0]]
 if path=='inverse-two':
  A=M([[a,1],[1,b]]);d=A.det();u=M([1,2]);w=A*u
  if l==1:return [s.solve(a*x-2*a,x)[0]]
  if l==2:return [(A*M([[b,1],[1,a]])/d)[0,1]]
  if l==3:return [A.inv()]
  if l==4:return [A.inv(),A.LUsolve(w)]
  if l==5:
   C=M([[k,1],[1,b]]);j=s.solve(C.inv()[0,0]-R(1,a),k)[0];return [j,C.subs(k,j).inv()]
  C=M([[k,a],[0,k]]);return [C.inv(),bool(s.solve(list(C*C-s.eye(2)),k))]
 if path=='invariant-lines':
  A=s.diag(a,b)
  if l==1:return [M([1,s.diff(a*x,x)])]
  if l==2:
   u=M([1,0]);return [bool(M.hstack(u,A*u).rank()==1 and A.det()!=0),bool(A*u==u)]
  if l==3:return [j[2][0] for j in A.eigenvects()]
  if l==4:
   p=A*M([0,1]);d=A*M([1,a]);return [d[1]/d[0],p[1]]
  if l==5:
   C=M([[1,a],[0,b]]);basis=[j[2][0] for j in C.eigenvects()];return [basis[0],basis[1]*(b-1)/basis[1][1]]
  C=s.diag(1,b);u=M([0,1]);return [C.eigenvals() and C[1,1],bool(C*M([1,0])==M([1,0])),bool(C*u==u)]
 if path=='collapse':
  A=M([[1,a],[b,a*b]])
  if l==1:return [A[0,1]/A[0,0]]
  if l in (2,3):return A.columnspace()
  if l==4:return [*A.nullspace(),*A.columnspace()]
  if l==5:
   C=M([[1,a],[b,k]]);j=s.solve(C.det(),k)[0];C=C.subs(k,j);return [j,*C.columnspace(),*C.nullspace()]
  return [(k*A).subs(k,0).rank(),A.rank(),s.solve((k*A*M([x,y]))[0]-1,x)[0]+a*y]
 if path=='line-plane-intersection':
  P=M([a,0,0]);D=M([1,1,1]);N=D;c=a+3*b;H=P+D*s.solve(N.dot(P+t*D)-c,t)[0]
  if l==1:return [s.solve(N.dot(P+t*D)-c,t)[0]]
  if l==2:return [bool(s.solve(N.dot(M([t,-t,a]))-a-1,t))]
  if l==3:return [H]
  if l==4:return [N.dot(M([0,0,c])),H]
  D=M([1,-1,k]);j=s.solve(N.dot(P+t*D)-(c if l==5 else h),t)[0]
  if l==5:return [P+j*D]
  return [N.dot(P),P+j*D]
 if path=='point-plane':
  n=M([1,2,2]);P=M([a,b,0]);c=a+2*b-9
  j=s.solve(n.dot(P-t*n)-c,t)[0];H=P-j*n;dist=(H-P).norm()
  if l==1:return [(a*n).norm()]
  if l==2:return [abs(n.dot(P)-c),abs((a*n).dot(P)-a*c),dist]
  if l==3:return [dist]
  if l==4:return [H,dist]
  if l==5:return s.solve((n.dot(P)-h)**2-a*a*n.dot(n),h)
  return [H,s.sqrt(25-dist**2)]
 if path=='cross-product':
  U=M([1,a,0]);V=M([0,1,b]);W=U.cross(V)
  if l==1:return [M([[a,0],[1,b]]).det()]
  if l==2:return [V.cross(U)[0]]
  if l==3:return [W]
  if l==4:return [W,s.sqrt(U.dot(U)*V.dot(V)-U.dot(V)**2)/2]
  if l==5:
   C=U.cross(M([0,1,k]));roots=s.solve(C.dot(C)-W.dot(W),k);return [*roots,*[C.subs(k,j) for j in roots]]
  # Solve the three linear equations; normalise free parameter to first coordinate.
  sol=next(iter(s.linsolve(list(U.cross(M([x,y,z]))-W),(y,z,x))));family=M([sol[2],sol[0],sol[1]]);return [family.subs(x,0),family.diff(x)]
 if path=='line-plane-angle':
  D=M([a,0,a*s.sqrt(3)]);n=M([0,0,1]);ang=s.asin(abs(D.dot(n))/D.norm())
  if l==1:return [s.acos(s.sqrt(1-R(1,4)))]
  if l in (2,3):return [ang]
  if l==4:return [n.dot(M([0,0,b])),ang]
  if l==5:return s.solve(4*k*k-M([a,0,k]).dot(M([a,0,k])),k)
  # Squared ratio at 0, 30, 90 degrees; coefficient in tan relation.
  return [len(s.solve(k*k-q*(a*a+k*k),k)) for q in (0,R(1,4),1)]+[a]
 raise ValueError(path)

def equivalent(a,b):
 if isinstance(b,bool):return type(a) is bool and a==b
 local=dict(k=k,t=t,x=x,y=y,z=z,h=h)
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(e)==0 for e in m-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
