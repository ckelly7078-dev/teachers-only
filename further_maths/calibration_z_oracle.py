"""Independent exact calculations for FM-16Z facts."""
import sympy as s
x,h,k=s.symbols('x h k',real=True); I=s.I; pi=s.pi

def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5)); z=a+b*I; w=d-a*I
 if path=='cartesian-product':
  if l==1:return [s.exp(I*pi*(4*d+v)/2).expand(complex=True)]
  if l==2:return [s.re((a*I)*(b*I))]
  if l==3:return [s.expand_complex(z*w)]
  if l==4:return [s.expand_complex(z*w),s.expand_complex(z*w*(1+I))]
  X,Y=s.symbols('X Y',real=True); P=s.expand_complex(z*(X+I*Y))
  if l==5:
   R=s.solve([s.re(P-z*w),s.im(P-z*w)],(X,Y));return [R[X],R[Y]]
  R=s.solve([s.re(P)-h,s.im(P)],(X,Y));return [s.diff(R[X],h),s.diff(R[Y],h),s.simplify(R[Y]/R[X])]
 if path=='argument-range':
  t=[1/s.sqrt(3),s.Integer(1),s.sqrt(3)][v-1];Z=1+I*t
  if l==1:return [s.arg(d)]
  if l==2:return [s.arg(-a*Z)]
  if l==3:return [s.arg(-a*s.conjugate(Z))]
  if l==4:
   A=d+b*I;B=A+a*s.conjugate(Z);return [s.arg(B-A)+2*pi]
  if l==5:
   A=s.arg(-Z);Y=s.solve(s.sin(A)*(-d)-s.cos(A)*x,x)[0];return [-d+I*Y]
  return [s.arg(Z),s.arg(-Z),s.arg(s.conjugate(Z)),s.arg(-s.conjugate(Z))]
 if path=='angle-units':
  D=30*a
  if l==1:return [s.rad(D)]
  if l==2:return [s.deg(pi/(2*a))]
  if l==3:return [s.deg(-b*pi/a)]
  if l==4:
   A=s.rad(45*b)-pi/a;return [s.deg(A),A]
  if l==5:return [n for n in range(-20,21) if 2*b*pi<=s.rad(D+360*n)<2*(b+2)*pi]
  allT=[T for T in range(-180,901) if (T-D)%360==0];return allT+[T for T in allT if (T-D)%720==0]
 if path=='verify-roots':
  F=s.expand((x-z)*(x-s.conjugate(z)));G=s.Poly((x+d)*F,x);R=s.Poly((x+d)**2*F,x)
  if l==1:return [G.eval(-d)]
  if l==2:
   roots=s.roots(G);return [bool(s.expand((x+d)**2*(x-z)-G.as_expr())==0),roots[-d]]
  if l==3:return G.all_roots()
  if l==4:
   roots=s.roots(R);return [n for r in sorted(roots,key=lambda t:(float(s.re(t)),float(s.im(t)))) for n in (r,roots[r])]
  if l==5:
   P=R.as_expr()-R.eval(0)+k;K=s.solve(P.subs(x,z),k)[0];Q=s.Poly(P.subs(k,K),x);return [K,bool(s.expand((x+d)*(x-z)**2*(x-s.conjugate(z))-Q.as_expr())==0),s.roots(Q)[-d]]
  P=s.Poly(F*(x*x+h*x+k),x);out=[]
  for Q in (s.Poly((x-z)*(x-s.conjugate(z))*(x+d)**2,x),s.Poly((x-z)**2*(x-s.conjugate(z))**2,x)):
   sol=s.solve((P-Q).all_coeffs(),(h,k),dict=True)[0];out.extend([sol[h],sol[k]])
  return out
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);return len(f)==len(g) and all((type(A) is bool and A==B) if type(B) is bool else (type(A) is not bool and s.simplify(s.sympify(A,locals={'x':x,'h':h,'k':k})-B)==0) for A,B in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
