"""Independent structured checks for FM-16H using equation solving, ranks and exact geometry."""
import sympy as s
M=s.Matrix
k,h,x,y,z=s.symbols('k h x y z',real=True)

def oracle(path,l,v):
 a=v+1;b=v+2;c=v+3
 if path=='matrix-equation':
  A=M([[a,1],[0,1]]);B=M([[b,c],[a,b]])
  if l==1:return s.solve(a*x-a*b,x)
  if l==2:
   C=M([[1,0],[b,1]]);left=A.inv()*C;right=C*A.inv();return [left,right,A*right==C]
  if l==3:return [A.LUsolve(B)]
  if l==4:
   C=M([[a,1],[b,2]]);X=C.T.LUsolve(B.T).T;Y=C.LUsolve(B);return [X,Y,X==Y]
  if l==5:
   p,q,r=s.symbols('p q r',real=True);X=M([[p,q],[q,r]]);sol=s.solve(list(A*X-M([[b,h],[c,b]])),(p,q,r,h));return [sol[h],X.subs(sol)]
  A=M([[a,1],[0,k]]);B=M([[b,h],[0,b]]);p,q,r,t=s.symbols('p q r t');X=M([[p,q],[r,t]]);sol=s.solve(list(A*X-B),(p,q,r,t));XX=X.subs(sol);comm=(A*B-B*A)[0,1];assert s.solve(comm,k)==[a];assert A.subs(k,0).rank()==1 and B.det()!=0;assert all(s.simplify(e)==0 for e in (XX*A-B).subs(h,0));assert all(s.simplify(e)==0 for e in (XX*A-B).subs(k,a));return [XX,comm,a,0]
 if path=='system-classification':
  if l==1:return [bool(s.linsolve([x-a,2*x-2*a-1],x))]
  if l==2:return [bool(s.linsolve([x+a*y-b,2*x+2*a*y-2*b],(x,y))),bool(s.linsolve([x+a*y-b,2*x+2*a*y-2*b-1],(x,y)))]
  if l==3:
   eq=x+a*y-b;sol=next(iter(s.linsolve([eq,3*eq],(x,y))));return [M(sol),bool(s.linsolve([eq,3*eq-2],(x,y)))]
  e1=x+z-b;e2=y+a*z-c
  if l==4:
   e3=x+y+(a+1)*z-b-c;return [M(next(iter(s.linsolve([e1,e2,e3],(x,y,z))))),bool(s.linsolve([e1,e2,e3-1],(x,y,z)))]
  if l==5:
   e3=x+2*y+(1+2*a)*z-h;sol=s.solve([e1,e2,e3],(x,y,h));return [sol[h],M([sol[x],sol[y],z])]
  A=M([[1,0,1],[0,1,a],[1,1,a+1+k]]);B=M([b,c,h]);assert A.det()==k;sol=A.LUsolve(B);zero=A.subs(k,0);good=B.subs(h,b+c);assert zero.rank()==zero.row_join(good).rank()==2;assert zero.row_join(B.subs(h,b+c+1)).rank()==3;return [b+c,sol,M(next(iter(s.linsolve((zero,good),(x,y,z)))))]
 if path=='scalar-product':
  U=M([a,b,c]);V=M([2,-1,3]);
  if l==1:return [sum([a,-2*b,3*c])]
  if l==2:
   A=M([a,b,0]);B=M([b,-a,0]);return [A.dot(B),A.is_zero_matrix or B.is_zero_matrix]
  if l==3:return [(U.T*V)[0]]
  if l==4:
   P=M([1,2,3]);Q=M([a+2,b+2,c+2]);R=M([2,0,1]);S=M([3,-2,4]);d=Q-P;e=S-R;return [d,e,d.dot(e)]
  if l==5:
   A=M([[1,a],[b,1]]);B=M([a+2*a*b,b*a+2*b]);sol=A.LUsolve(B);return [M([*sol,c])]
  expr=(M([k,k-a,b]).T*M([k-a,k,1]))[0].expand();mid=s.solve(s.diff(expr,k),k)[0];minimum=expr.subs(k,mid);assert s.diff(expr,k,2)>0;return [expr,minimum,mid,*[len(s.solveset(expr-t,k,domain=s.S.Reals)) for t in (minimum-1,minimum,minimum+1)]]
 if path=='plane-intersection-direction':
  N=M([1,a,0]);P=M([0,1,b]);
  if l==1:return [(N.T*M([a,-1,0]))[0]]
  if l==2:return [N.dot(P),N.dot(N)==0]
  if l==3:
   # independent solve of normal constraints; scale to specified x component
   A=M([[1,a,0],[0,1,b]]);d=A.nullspace()[0];return [d* (a*b/d[0])]
  if l==4:
   E=M([0,0,1]);F=M([a+1,-1,0]);G=M([1,0,0]);H=M([0,b+1,-1]);N=E.cross(F);P=G.cross(H);d=M.vstack(N.T,P.T).nullspace()[0];D=N.cross(P);assert d.cross(D)==M([0,0,0]);return [N,P,D]
  if l==5:
   D=M([a*b,-b,1-a*c]);P=M([k,1,b]);root=s.solve(P.dot(D),k)[0];assert N.dot(D)==0;return [root,N.cross(P.subs(k,root))]
  P=M([k,a*k+h,0]);d=s.symbols('d',real=True);A=M.vstack(N.T,P.T);rhs=M([c,d]);assert A[:,0:2].det()==h;assert A.subs({h:0,k:2}).rank()==1;assert A.subs({h:0,k:2}).row_join(rhs.subs(d,2*c)).rank()==1;assert A.subs({h:0,k:2}).row_join(rhs.subs(d,2*c+1)).rank()==2;return [N.cross(P),s.solve(d-k*c,d)[0],0,3-A.subs(h,1).rank(),3-A.subs({h:0,k:2}).rank()]
 raise ValueError(path)

def equivalent(a,b):
 local={str(v):v for v in (k,h,x,y,z)}
 if isinstance(b,bool):return type(a) is bool and a==b
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  mat=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return mat.shape==b.shape and all(s.simplify(e)==0 for e in mat-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
