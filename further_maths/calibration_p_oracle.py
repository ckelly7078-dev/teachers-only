"""Independent structured checks: solve equations and verify geometric invariants."""
import sympy as s
M=s.Matrix
k,h,r,t,u,w,x,y,z=s.symbols('k h r t u w x y z',real=True)

def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 if path=='three-system':
  if l==1:
   sol=s.linsolve([z-d-1,y+z-(d+1-b),x+y-(a+1-b)],(x,y,z));return [M(next(iter(sol)))]
  if l==2:return [s.linsolve([x+y+z-d,2*x+2*y+2*z-2*d-1,x-z-a],(x,y,z))!=s.EmptySet]
  if l==3:
   sol=s.linsolve([x+y+z-(a-b+d),x+2*y-(a-2*b),y+2*z-(-b+2*d)],(x,y,z));return [M(next(iter(sol)))]
  if l==4:
   sol=s.linsolve([x+y+z-(d+a+b),x-y-(d-a),y-2*z-(a-2*b)],(x,y,z));return [M(next(iter(sol)))]
  if l==5:
   sol=next(iter(s.linsolve([x+y+z-(b+d-a),x+2*y-(b+2*d),y+2*z-k,x-z-(a+b)],(k,x,y,z))));return [sol[0],M(sol[1:])]
  eq=[x+y+z-d,y-b,x+y+(1+k-a)*z-(d+h-b)];sol=M(next(iter(s.linsolve(eq,(x,y,z)))));pole=s.solve(M([[1,1,1],[0,1,0],[1,1,1+k-a]]).det(),k)[0];boundary=s.solve(eq[2].subs({k:pole,x:d-y-z}),h)[0];special=next(iter(s.linsolve([e.subs({k:pole,h:boundary}) for e in eq],(x,y,z))));assert s.linsolve([e.subs({k:pole,h:boundary+1}) for e in eq],(x,y,z))==s.EmptySet;return [sol,pole,boundary,M(special).subs(z,t)]
 if path=='describe-transform':
  if l==1:
   A=M([[0,-a],[a,0]]);return [A*M([1,0]),A*M([0,1])]
  if l==2:
   A=M([[0,1],[1,0]]);assert A*M([1,1])==M([1,1]) and A*M([1,-1])==M([-1,1]);return [A*M([a,b]),A.det()]
  if l==3:
   angle=[90,180,270][v-1];p=s.pi*angle/180;A=M([[s.cos(p),-s.sin(p)],[s.sin(p),s.cos(p)]]);return [A*M([1,0]),A*M([0,1]),angle]
  if l==4:
   # Action on basis by three geometric operations, without multiplying matrices.
   A=M.hstack(M([0,a]),M([a,0]));D=M([1,1]);assert A*D==a*D and A*M([1,-1])==-a*M([1,-1]);return [A,A.det(),D]
  if l==5:
   D=M([1,a]);N=M([-a,1]);B=M.hstack(D,N);A=M.hstack(D,-N)*B.inv();assert A.T*A==s.eye(2) and A.det()==-1;return [A,D,N]
  p=k-a;A=M([[p,h],[h,-p]]);rho=s.sqrt((A.T*A)[0,0]);assert (A.T*A-rho**2*s.eye(2)).applyfunc(s.simplify)==s.zeros(2);D=M([rho+p,h]);N=M([h,rho-p]);assert (A*D-rho*D).applyfunc(s.simplify)==s.zeros(2,1) and (A*N-rho*N).applyfunc(s.simplify)==s.zeros(2,1);assert s.simplify(D.dot(D)+N.dot(N)-4*rho**2)==0;return [rho,A.det(),D,N]
 if path=='vector-components':
  if l==1:return [M([a,-b,d])]
  if l==2:return [M([b-a,a+b,-2*d])]
  if l==3:return [M([a+d,0,d-a])]
  if l==4:return [M([s.Rational(a+a*b,a+1),s.Rational(-b+a*a,a+1),s.Rational(d-a*d,a+1)])]
  if l==5:
   roots=s.solve(a*a+y*y+d*d-(a*a+b*b+d*d),y);return [M([a,roots[1],d]),M([a,roots[0],d])]
  E=(x-a)**2+y*y+b*b-r*r;F=(x+a)**2+y*y+b*b-h*h;X=s.solve(F-E,x)[0];Y=s.solve(E.subs(x,X),y**2)[0];assert s.simplify(F.subs(x,X).subs(y*y,Y))==0;return [X,Y,M([X,s.sqrt(Y),b]),M([X,-s.sqrt(Y),b])]
 if path=='justify-skew':
  if l==1:
   D=M([1,a,0]);return [D.cross(M([2,2*a,0]))==s.zeros(3,1),D.cross(M([1,a,1]))==s.zeros(3,1)]
  if l==2:return [s.linsolve(list(t*M([1,a,0])-u*M([0,1,b])),(t,u))==s.EmptySet]
  if l in (3,4):
   U=M([1,a,0]);V=M([0,1,b]);offset=d+(l==4);P=M([0,0,0]) if l==3 else M([1,2,3]);Q=P+M([offset,0,1]);diff=Q+u*V-P-t*U;sol=s.solve(list(diff)[:2],(t,u),dict=True)[0];assert U.cross(V)!=s.zeros(3,1) and s.linsolve(list(diff),(t,u))==s.EmptySet;f=[sol[t],sol[u],diff[2].subs(sol)];return [U,V,*f] if l==4 else f
  if l==5:
   sol=s.solve(list(M([d,u,k+b*u])-M([t,a*t,0])),(t,u,k),dict=True)[0];return [sol[k],M([sol[t],a*sol[t],0])]
  D=M([1,k,1]);assert D.cross(M([1,0,0]))!=s.zeros(3,1);diff=M([d+u,b+k*u,h+u])-M([t,0,0]);sol=s.solve([diff[0],diff[2]],(t,u),dict=True)[0];return [sol[t],sol[u],diff[1].subs(sol),M([sol[t],0,0])]
 raise ValueError(path)

def equivalent(actual,expected):
 local={str(v):v for v in (k,h,r,t,u,w,x,y,z)}
 if type(expected) is bool:return type(actual) is bool and actual==expected
 if isinstance(expected,s.MatrixBase):
  if not isinstance(actual,dict) or set(actual)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in actual['matrix']]);return m.shape==expected.shape and all(s.simplify(e)==0 for e in m-expected)
 return isinstance(actual,str) and s.simplify(s.sympify(actual,locals=local)-expected)==0

def check(p):
 try:
  e=oracle(p['path'],p['tier'],p['variant']);return len(e)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],e))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
