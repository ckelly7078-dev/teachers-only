"""Independent exact checks for FM-16AA structured answers."""
import sympy as s
I=s.I

def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5)); A=s.Matrix([a,b]); B=s.Matrix([d,-a]); z=a+b*I;w=d-a*I;t,h=s.symbols('t h',real=True)
 def complex_of(M):return M[0]+I*M[1]
 def quadrant(M):
  x,y=M
  return {(1,1):1,(-1,1):2,(-1,-1):3,(1,-1):4}[(s.sign(x),s.sign(y))]
 if path=='argand-coordinates':
  if l==1:return list(s.Matrix([a,-b]))
  if l==2:return [*A,s.im(z)]
  if l==3:
   M=s.Matrix([s.re(-s.conjugate(z)),s.im(-s.conjugate(z))]);return [*M,quadrant(M)]
  if l==4:
   R=s.diag(1,-1);S=s.diag(-1,1);return [*(R*B),*(S*B),*(S*R*B)]
  if l==5:
   M=s.Matrix([(a-d)/2,0]);Q=2*M-A;return [*Q,quadrant(Q)]
  X=s.Matrix([t-a,t-b]);bounds=sorted([s.solve(e,t)[0] for e in X]);samples=[bounds[0]-1,sum(bounds)/2,bounds[1]+1];return [*bounds,*[quadrant(X.subs(t,T)) for T in samples],bool(s.solve(list(X),t))]
 if path=='argand-displacement':
  if l==1:return [complex_of(s.Matrix([a,-b]))]
  if l==2:return [complex_of(B-A)]
  if l==3:return [complex_of(A+B),complex_of(A-B)]
  if l==4:
   C=B+A;return [complex_of(C),complex_of(C),complex_of(B-A)]
  if l==5:
   S=A+B;D=A-B;M=s.Matrix([[1,1],[1,-1]]).inv()*s.Matrix.vstack(S.T,D.T);return [complex_of(M.row(0)),complex_of(M.row(1))]
  P=s.Matrix([t,a]);return [s.solve(s.Matrix.hstack(A,P).det(),t)[0],s.solve(A.dot(P),t)[0],s.expand((A+P)[0]).coeff(t,0),(A+P)[1]]
 if path=='cartesian-sums':
  if l==1:return [sum([a,b]),sum([-d,a])]
  if l==2:return [complex_of(A-B)]
  if l==3:return [complex_of(A+B),complex_of(A-B)]
  u,vv=s.symbols('u vv')
  if l==4:return [s.solve(u-(w-u)-(2*z-w),u)[0]]
  if l==5:
   r=s.solve([u+2*vv-(z+2*w),2*u-vv-(2*z-w)],(u,vv));return [r[u],r[vv]]
  M=s.Matrix([[1,a],[1,t]]);T=s.solve(M.det(),t)[0];rhs=s.Matrix([z,z+h]);bad=s.solve((rhs[1]-rhs[0]).subs(t,T),h)[0];return [s.re(rhs[0]),s.im(rhs[0]),T,bad]
 if path=='zero-exception':
  if l==1:return [s.Abs(s.expand(a-a+I*(b-b)))]
  if l==2:return [bool(s.arg(0)!=s.nan),s.Abs(0)]
  if l==3:return [s.solve((t-a)**2*(1+b*b),t)[0],bool(s.arg(0)!=s.nan)]
  if l==4:return [s.solve(t-a,t)[0],s.solve(t-b,t)[0],bool(s.arg(0)!=s.nan)]
  if l==5:
   y=s.symbols('y',real=True);counts=[len(s.solveset(y*y+a*a-R*R,y,domain=s.S.Reals)) for R in [a-1,a,a+1]];return [a,*counts,bool(s.solve([a,y],y))]
  N=(t-a)*(t-b)+I*h*(t-b);D=t-b;Z=s.cancel(N/D);r=s.solve([s.re(Z),s.im(Z)],(t,h));return [s.solve(D,t)[0],r[t],r[h]]
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);return len(f)==len(g) and all((type(A) is bool and A==B) if type(B) is bool else (type(A) is not bool and s.simplify(s.sympify(A)-B)==0) for A,B in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
