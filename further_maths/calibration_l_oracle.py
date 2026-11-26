"""Independent structured checks using rank, elimination, determinants and nullspaces."""
import sympy as s
M=s.Matrix
k,h,t,x,y,z,p,C=s.symbols('k h t x y z p C',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;c=2*v+5
 if path=='three-plane-unique':
  if l==1:
   value=M([1,1,1]).dot(M([a,b,c]));return [value,bool(value==a+b+c)]
  if l==2:
   A=M([[1,0,0],[0,1,0],[1,1,0]]);B=M([a,b,a+b]);assert A.rank()==A.row_join(B).rank()==2;return [M(next(iter(s.linsolve((A,B),(x,y,t)))))]
  if l==3:
   A=M([[1,1,0],[1,0,1],[0,1,1]]);B=M([a+b,a+c,b+c]);return [A.inv()*B]
  if l==4:
   A=M([[1,1,0],[1,0,1],[2,1,2]]);B=M([a-b,a+c,2*a-b+2*c]);return [A.det(),M(next(iter(s.linsolve((A,B),(x,y,z)))))]
  A=M([[1,1,0],[1,0,1],[k,1,1]])
  if l==5:
   B=M([a+b,a+c,b+c+3*a]);sol=s.solve(list(A*M([a,y,z])-B),(k,y,z));assert A.subs(k,sol[k]).det()!=0;return [sol[k],M([a,sol[y],sol[z]])]
  B=M([a,b,h]);sing=s.solve(A.det(),k)[0];assert A.subs(k,sing).rank()==2;left=A.subs(k,sing).T.nullspace()[0];H=s.solve(left.dot(B),h)[0];P=A.inv()*B;assert all(s.simplify(e)==0 for e in A*P-B);family=M([t,a-t,b-t]);assert A.subs(k,sing)*family==B.subs(h,H);return [sing,H,P,family]
 if path=='collapse-parameter':
  if l==1:return [M([[a,b],[1,c]]).det()]
  if l==2:
   A=M([[a,b],[0,0]]);assert A.rank()==1;return [A[:,0]]
  if l==3:return s.solve(M([[k,a],[b,1]]).det(),k)
  if l==4:
   A=M([[k,a],[b,k]]);roots=s.solve(A.det(),k);cols=[]
   for r in roots:
    B=A.subs(k,r);assert B.rank()==1;cols.append(B[:,1]);assert M.hstack(*B.columnspace(),cols[-1]).rank()==1
   return [*roots,*cols]
  if l==5:b=c
  A=M([[k,a],[h,k-b]]);d=A.det();D=s.discriminant(d,k);H=s.solve(D,h)[0]
  if l==5:
   roots=s.solve(d.subs(h,H),k);assert len(roots)==1;K=roots[0];B=A.subs({h:H,k:K});assert B.rank()==1;return [H,K,B[:,1]]
  roots=s.solve(d,k);B=A.subs(h,s.solve(d,h)[0]);ker=B.nullspace()[0];ker=s.simplify(ker*a/ker[0]);assert B.rank()==1 and B*ker==s.zeros(2,1);return [H,*roots,B[:,1],ker]
 if path=='zero-direction':
  P=M([a,b,c]);D=M([0,a,-b]);
  if l==1:return [(P+t*D)[0]]
  if l==2:return [(P+t*D)[0],D[1:3,0]]
  if l==3:
   Q=M([-a,b,c]);E=M([b,0,a]);return [(Q+t*E)[1],Q+2*E]
  if l==4:
   Q=M([a,b+2*a,c-2*b]);R=M([a+1,b+3*a,c-3*b]);assert M.hstack(Q-P,R-P).rank()==2;return [Q-P,False]
  if l==5:
   E=M([0,k,-b]);root=s.solve(E.cross(D)[0],k)[0];param=s.solve((P+t*E)[2]-(c-2*b),t)[0];return [root,(P+t*E).subs({k:root,t:param})[1]]
  E=M([0,k,h]);Q=P+t*E;param=s.solve(Q[2]-c-p,t)[0];assert Q[0]==a and s.simplify(Q[2].subs(t,param)-c-p)==0;assert Q.subs({k:0,h:0})==P;return [Q.subs(t,param),P,Q.subs(h,0)]
 if path=='cross-normal':
  U=M([1,a,0]);V=M([0,b,1]);N=U.cross(V)
  if l==1:
   val=M([a,-1,0]).dot(U);return [val,bool(val==0)]
  if l==2:return [U.cross(b*U)]
  if l==3:
   mat=M.vstack(U.T,V.T);normal=mat.nullspace()[0];normal=normal*b;assert normal==N;return [normal,normal.dot(U),normal.dot(V)]
  if l==4:
   P=M([a,b,c]);Q=P+U;R=P+V;mat=M.vstack((Q-P).T,(R-P).T);normal=mat.nullspace()[0]*b;assert normal.dot(Q)==normal.dot(P)==normal.dot(R);return [normal,normal.dot(P)]
  if l==5:
   U=M([1,k,0]);n=M([a,-1,b]);root=s.solve(n.dot(U),k)[0];assert n.dot(V)==0;return [root,U.subs(k,root).cross(V)]
  U=M([1,k,a*k]);V=M([h,b,a*b]);N=U.cross(V);factor=s.factor(N[2]);unit=s.simplify(N/factor);assert unit.dot(U)==unit.dot(V)==0 and U.subs(k,b/h)*h==V;return [factor,unit/unit.norm(),-unit/unit.norm()]
 raise ValueError(path)

def equivalent(actual,expected):
 local={str(q):q for q in (k,h,t,x,y,z,p,C)}
 if isinstance(expected,bool):return type(actual) is bool and actual==expected
 if isinstance(expected,s.MatrixBase):
  if not isinstance(actual,dict) or set(actual)!={'matrix'}:return False
  mat=M([[s.sympify(e,locals=local) for e in row] for row in actual['matrix']]);return mat.shape==expected.shape and all(s.simplify(e)==0 for e in mat-expected)
 return isinstance(actual,str) and s.simplify(s.sympify(actual,locals=local)-expected)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
