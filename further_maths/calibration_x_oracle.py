"""Independent discriminant, polynomial root and coefficient calculations."""
import sympy as s
x,h,k,u=s.symbols('x h k u',real=True); I=s.I

def ordered_roots(G):
 return sorted(s.Poly(G,x).all_roots(),key=lambda r:float(s.im(r)))
def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5));z=a+b*I; F=s.expand((x-z)*(x-s.conjugate(z)))
 if path=='complex-discriminant':
  if l==1:return [s.discriminant(F,x)]
  if l==2:return [s.discriminant((x-a)**2,x),s.discriminant(F,x)]
  if l==3:return [s.discriminant(a*x*x+2*b*x+d*d,x)]
  if l==4:return sorted(s.solve(s.discriminant(x*x-2*k*x+b*b,x),k))
  D=s.discriminant(x*x-2*k*x+h,x);E=s.discriminant(x*x-2*(k-a)*x+h,x)
  if l==5:return [s.solve(s.discriminant(x*x-2*t*x+k,x),k)[0] for t in (a,b)]
  return [s.solve(D,h)[0],s.solve(E,h)[0],s.solve(D-E,k)[0],s.solve(D,h)[0].subs(k,s.solve(D-E,k)[0])]
 if path=='complex-quadratic':
  if l==1:return ordered_roots(x*x+b*b)
  if l==2:return ordered_roots(F)
  if l==3:return ordered_roots(a*x*x+2*b*x+d*d)
  if l==4:return ordered_roots((x-a)**2+2*b*(x-a)+d*d)
  if l==5:
   K=s.solve(s.re((x*x-2*a*x+k).subs(x,z)),k)[0];return [K,*ordered_roots(x*x-2*a*x+K)]
  D=s.discriminant(x*x-2*h*x+b*b,x);return [*sorted(s.solve(D,h)),D/4,s.sqrt(s.Poly(x*x-2*h*x+b*b,x).TC())]
 if path=='conjugate-deduction':
  if l==1:return [s.conjugate(z)]
  if l==2:return [z,bool(s.simplify((x-z).subs(x,s.conjugate(z)))==0)]
  if l==3:return [*ordered_roots(F),-d]
  if l==4:return [s.conjugate(z),s.degree(F**2,x)]
  if l==5:
   P=s.Poly(F*(x-u),x);U=s.solve(P.all_coeffs()[1]+d,u)[0];return [*ordered_roots(F),U]
  degrees=[]
  for H in (b,0,b+1):
   roots={z,s.conjugate(z),a+H*I,a-H*I};degrees.append(len(roots))
  return [*sorted(s.solve(h*h-b*b,h)),*degrees]
 if path=='conjugate-factor':
  if l in (1,2):return [s.expand(z*s.conjugate(z))]
  if l==3:return [F]
  if l==4:
   C=s.solve((u*F).subs(x,a)-d*b*b,u)[0];return [C,s.expand(C*F)]
  if l==5:
   G=s.expand(F*((x+d)**2+1));Q,R=s.div(G,F,x);assert R==0;return [F,Q]
  P=(x-u)**2+b*b;eq=P.subs(x,a)-h;return [s.solve(s.discriminant(eq,u),h)[0],*s.solve(eq,u)]
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);return len(f)==len(g) and all((type(A) is bool and A==B) if type(B) is bool else (type(A) is not bool and s.simplify(s.sympify(A,locals={'x':x,'h':h,'k':k})-B)==0) for A,B in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
