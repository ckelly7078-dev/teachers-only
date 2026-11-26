"""Independent structured checks via entry equations, determinants and linear solves."""
import sympy as s
M=s.Matrix
h,k,t,u,w,c,x,y,z=s.symbols('h k t u w c x y z',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 if path=='det-classification':
  A=M([[a,1],[b,d]])
  if l==1:return [a*d-b]
  if l==2:
   B=M([[a,b],[2*a,2*b]]);return [B.det(),B.rank()==2]
  if l==3:
   B=M([[a,1,b],[0,b,d],[a,1,b]]);C=M([[a,1,0],[1,b,1],[0,1,d]]);return [m.det(method='berkowitz') for m in (A,B,C)]
  if l==4:
   B=M([[1,b],[0,d]]);C=M([[a,1],[2*a,2]]);P=A*B;Q=A*C;return [P.det(),Q.det(),P.rank()==2,Q.rank()==2]
  if l==5:
   B=M([[k,a],[b,k]]);C=M([[k,a],[b,-k]]);return [*sorted(s.solve(B.det(),k)),C.det()]
  B=M([[a,1,0],[0,k,b],[0,h,k]]);C=M([[a,1,0],[0,k,b],[0,h,k-d]]);D=B.det(method='berkowitz');E=C.det(method='berkowitz');sol=s.solve([D,E],(k,h),dict=True);assert sol==[{h:0,k:0}];return [D,E,s.solve(D,h)[0],s.solve(E,h)[0],sol[0][k]]
 if path=='inverse-systems':
  A=M([[a,1],[1,b]])
  if l==1:return s.solve(a*x-d,x)
  if l==2:
   C=M([[1,a],[2,2*a]]);Y=M([b,2*b]);assert C.rank()==C.row_join(Y).rank()==1;return [C.det(),C.rank()==2]
  if l==3:
   B=M([a*d-a,d-a*b]);return [A.adjugate()/A.det(),A.gauss_jordan_solve(B)[0]]
  if l==4:
   C=M([[a,1,0],[1,b,1],[0,1,d]]);Z=M([0,1-a*b+b,-a+d*b]);return [C.gauss_jordan_solve(s.eye(3))[0],C.gauss_jordan_solve(Z)[0]]
  if l==5:
   sol=s.solve([a*x+y-d,x+b*y-k,x+y-a],(x,y,k),dict=True)[0];return [sol[k],M([sol[x],sol[y]])]
  C=M([[a,1],[k,b]]);Y=M([d,h]);sol=s.solve(list(C*M([x,y])-Y),(x,y),dict=True)[0];pole=s.solve(C.det(),k)[0];special=C.subs(k,pole);assert special.rank()==1;H=s.solve((Y[1]-b*Y[0]),h)[0];assert special.row_join(Y.subs(h,H)).rank()==1;param=s.solve(a*t+y-d,y)[0];return [M([sol[x],sol[y]]),pole,H,M([t,param])]
 if path=='plane-normal':
  U=M([a,1,0]);V=M([0,b,1]);C=M.vstack(U.T,V.T);N=C.nullspace()[0];N=N/N[0];P=M([1,2,3]);assert C*N==s.zeros(2,1)
  if l==1:return [(U.T*V)[0]]
  if l==2:return [(-2*N).norm()!=0 and C*(-2*N)==s.zeros(2,1),s.zeros(3,1).norm()!=0]
  if l==3:
   W=N+M([0,1,0]);return [*C*N,*C*W]
  if l==4:return [N,(P.T*N)[0]]
  if l==5:
   sol=s.solve(list(C*M([d,y,z])),(y,z),dict=True)[0];W=M([d,sol[y],sol[z]]);Q=P+U+V;return [W,(P.T*W)[0],(Q.T*W)[0]==(P.T*W)[0]]
  V=M([h,k,b*k]);C=M.vstack(U.T,V.T);sol=s.solve(list(C*M([1,y,z])),(y,z),dict=True)[0];assert C.subs({h:0,k:0}).rank()==1 and C.subs(k,0).subs(h,1).rank()==2;assert (C*M([1,-a,z])).subs(k,0)[1]==h;return [M([1,sol[y],sol[z]]),sol[y],M([1,sol[y],t]),s.solve(b*k,k)[0]]
 if path=='cross-order':
  U=M([a,0,0]);V=M([0,b,d]);cross=lambda A,B:M([M([[A[1],A[2]],[B[1],B[2]]]).det(),M([[A[2],A[0]],[B[2],B[0]]]).det(),M([[A[0],A[1]],[B[0],B[1]]]).det()])
  if l==1:return [(-a)*b]
  if l==2:return [cross(V,U)]
  if l==3:return [cross(U,V),cross(V,U)]
  if l==4:return [cross(U,V),cross(V-U,-U),cross(V,U)]
  if l==5:
   # Solve explicit cross product constraints in given order.
   Y=M([0,-a*a,a*b]);sol=s.solve(list(cross(M([d,y,z]),U)-Y),(y,z),dict=True)[0];W=M([d,sol[y],sol[z]]);return [W,cross(U,W)]
  U=M([a,b,0]);V=M([1,0,0]);sol=s.solve(list(cross(V,M([x,y,z]))-cross(U,V)),(y,z),dict=True)[0];W=M([x,sol[y],sol[z]]);norm2=W.dot(W);roots=s.solve(norm2-c*c,x);R=s.sqrt(c*c-b*b);assert set(roots)=={-R,R};return [W.subs(x,R),W.subs(x,-R),s.sqrt(norm2.subs(x,0))]
 raise ValueError(path)

def equivalent(actual,expected):
 local={str(v):v for v in (h,k,t,u,w,c,x,y,z)}
 if type(expected) is bool:return type(actual) is bool and actual==expected
 if isinstance(expected,s.MatrixBase):
  if not isinstance(actual,dict) or set(actual)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in actual['matrix']]);return m.shape==expected.shape and all(s.simplify(e)==0 for e in m-expected)
 return isinstance(actual,str) and s.simplify(s.sympify(actual,locals=local)-expected)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
