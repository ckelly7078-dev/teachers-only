"""Independent structured checks via entry equations, nullspaces, and Gram determinants."""
import sympy as s
M=s.Matrix
k,h,t,C=s.symbols('k h t C',real=True)
x,y,z=s.symbols('x y z',real=True)

def gram(U,V):return s.expand(U.dot(U)*V.dot(V)-U.dot(V)**2)

def oracle(path,l,v):
 a=v+1;b=v+3;c=v+4
 if path=='identity-operations':
  A=M([[a,1],[b,c]]);I=s.eye(2)
  if l==1:return [s.solve(a*x-a,x)[0]]
  if l==2:return [A+I,A*I,A+I==A*I]
  if l==3:
   B=M([[1,b],[0,a]]);return [M(2,2,lambda i,j:2*A[i,j]-B[i,j])]
  if l==4:
   R=M([[1,a,0],[b,0,c]]) if v==1 else M([[1,a],[b,0],[0,c]]) if v==2 else M([[1,a,0,b],[b,0,c,1]]);m,n=R.shape;return [m,n,s.eye(m)*R*s.eye(n)]
  if l==5:
   A=M([[a,1],[0,1]]);B=A.inv();return [B[0,1],B]
  A=M([[k,a],[h,-k]]);P=A*A;root=s.solve(list(P-I),h,dict=True)[0][h];assert s.simplify(A.det().subs(h,root))==-1;assert P[0,0]==P[1,1] and P[0,1]==P[1,0]==0;return [P[0,0],root]
 if path=='figure-images':
  A=M([[1,a],[0,b]])
  if l==1:return [M([[a,0],[0,1]])*M([b,c])]
  if l==2:return [A*M([1,0]),A*M([0,1])]
  if l==3:return [M([c-a*a,-a*b])]
  if l==4:
   P=A*M([1,0]);Q=A*M([1,b]);R=A*M([c,0]);m,j=s.symbols('m j');sol=s.solve([P[1]-m*P[0]-j,Q[1]-m*Q[0]-j],(m,j));return [P,Q,R,sol[m],sol[j]]
  if l==5:
   R=A.LUsolve(M([c+a*b,b*b]));return [R,abs(M([[a,R[0]],[0,R[1]]]).det())/2]
  A=M([[1,a],[0,h]]);r=A*M([t,k*t+b]);p=r.subs(t,0);d=r.diff(t);root=s.solve(d[0],k)[0];assert d.subs({k:root,h:0})==M([0,0]);assert s.simplify(d[1].subs(k,root))==-h/a;assert s.simplify(r[1]-(p[1]+d[1]/d[0]*(r[0]-p[0])))==0;return [p,d,root]
 if path=='vector-line-equation':
  P=M([1,2,3]);Q=M([1+a,2+b,3+c]);D=Q-P
  if l==1:return [Q-P]
  if l==2:
   U=P+t*D;V=Q-2*k*D;return [U.subs(t,1-2*k)==V]
  if l==3:
   U=M([0,1,-1]);V=M([b,1-a,c-1]);return [U,V-U]
  if l==4:
   U=M([1,-b,c]);V=M([1+a,0,c-2]);D=V-U;r=U+t*D;root=s.solve(r[2],t)[0];return [U,D,root,r.subs(t,root)]
  if l==5:
   U=M([1,0,2]);W=M([1+2*a,2*b,2+2*c]);D=M([a,b,k]);sol=s.solve(list(U+t*D-W),(t,k),dict=True)[0];return [sol[k],D.subs(sol)]
  N=M([[a,b,0]]);D=M([k,h,0]);basis=N.nullspace();assert len(basis)==2 and basis[0]*(-a)==M([b,-a,0]) and basis[1]==M([0,0,1]);return [(N*D)[0],basis[0]*(-a),basis[1]]
 if path=='parallelogram-area':
  c=2*v+3
  if l==1:return [s.sqrt(gram(M([a,0]),M([0,b])))]
  if l==2:
   U=M([a,0,0]);V=M([0,b,0]);return [V.cross(U),s.sqrt(gram(U,V))]
  if l==3:return [s.sqrt(gram(M([a,1,0]),M([0,b,c])))]
  if l==4:
   P=M([1,2,3]);Q=M([1+a,2,3+b]);R=M([1,2+c,4]);S=2*((Q+R)/2)-P;return [S,s.sqrt(gram(Q-P,R-P))]
  if l==5:
   area2=gram(M([a,0,0]),M([k,b,k]));roots=s.solve(area2-a*a*(b*b+c*c),k);assert all(area2.subs(k,r)>0 for r in roots);return sorted(roots)
  expr=gram(M([a,0,0]),M([k,k-b,k+c]));mid=s.solve(s.diff(expr,k),k)[0];minimum=expr.subs(k,mid);coef=s.diff(expr,k,2)/2;assert coef>0;assert s.expand(expr-coef*(k-mid)**2-minimum)==0;return [expr,mid,minimum,(C*C-minimum)/coef]
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
