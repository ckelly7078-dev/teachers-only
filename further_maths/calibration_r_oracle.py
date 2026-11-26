"""Independent exact checks: polynomial root identities, linear solves, and complex exponential/argument."""
import sympy as s
from calibration_r_bank import PATHS
x,h,k=s.symbols('x h k',real=True)
I=s.I;pi=s.pi;R=s.Rational

def oracle(path,l,v):
 a=v+1;b=v+3;d=2*v+5
 def sums(P):
  roots=s.Poly(P,x).all_roots();return [s.simplify(sum(roots)),s.simplify(s.prod(roots))]
 def monic(roots):return s.Poly.from_list([1,-sum(roots),s.prod(roots)],x).as_expr().expand()
 if path=='root-sum-product':
  if l==1:return [s.Poly.from_list([1,b-a,-a*b],x).as_expr()]
  if l==2:return sums(2*x*x+b*x-d)
  if l==3:return sums(a*x*x-d*x+b)
  if l==4:
   u,w=s.symbols('u w',real=True);sol=s.solve([u+w-a-b,(u-w)**2-(a-b)**2],(u,w))[0];S,P=sum(sol),s.prod(sol);return [S,P,-S,P]
  if l==5:
   u=s.symbols('u',positive=True);root=s.solve(b*u*u-b*a*a,u)[0];roots=[root,b*root];return [sum(roots),s.prod(roots),*roots]
  P=x*x-(k-b)*x+a*a;lo,hi=sorted(s.solve(s.discriminant(P,x),k));return [lo,hi,s.solve(P.subs(k,hi),x)[0],s.solve(P.subs(k,lo),x)[0]]
 if path=='quadratic-from-roots':
  if l==1:return [monic([a,d])]
  if l==2:return [monic([-a,b]),s.expand(2*monic([-a,b]))==monic([-a,b])]
  if l==3:return [x*x-d*x-a*b]
  if l==4:
   u,w=s.symbols('u w',real=True);sol=s.solve([u+w-a+b,u*u+w*w-a*a-b*b],(u,w))[0];return [sum(sol),s.prod(sol),monic(sol)]
  if l==5:
   sol=s.solve([x+h-b-d,x-h-(d-b)],(x,h));roots=[sol[x],sol[h]];return [s.prod(roots),monic(roots)]
  # roots r and r+d, solve the product constraint and form both equations
  u=s.symbols('u',real=True);sol=s.solve(u*(u+d)-h,u);polys=[s.expand((x-z)*(x-z-d)) for z in sol];bound=s.solve(s.discriminant(u*(u+d)-h,u),h)[0];return [bound,polys[1],polys[0]]
 th=[pi/6,pi/4,pi/3][v-1];r=2*a
 def z(m,t):return s.simplify(s.expand_complex(m*s.exp(I*t)))
 if path=='polar-to-cartesian':
  if l==1:return [s.re(z(1,th)),s.im(z(1,th))]
  if l==2:return [z(r,th),z(r,pi-th)]
  if l==3:return [z(r,-pi+th)]
  if l==4:return [z(r,th),z(b,-th),z(r,th)+z(b,-th)]
  if l==5:
   m=s.symbols('m',real=True);T=pi-th;sol=s.solve(s.re(z(m,T))-s.re(z(r,T)),m)[0];return [sol,z(sol,T)]
  m,n=s.symbols('m n',real=True);A=z(m,th);B=z(n,pi-th);sol=s.solve([s.re(A+B)-h,s.im(A+B)-k],(m,n));boundary=s.solve(sol[m],k)[0];return [sol[m],sol[n],s.simplify(-boundary/h),A.subs(sol),B.subs(sol)]
 A=s.re(z(r,th));B=s.im(z(r,th));Z=-A+I*B
 def polar(z):return [s.simplify(s.Abs(z)),s.simplify(s.arg(z))]
 if l==1:return [s.Abs(a+I*b)]
 if l==2:return [s.atan(B/(-A)),s.arg(Z)]
 if l==3:return polar(s.conjugate(Z))
 if l==4:return polar(Z)+polar(s.conjugate(Z))
 if l==5:
  y=s.symbols('y',negative=True);sol=s.solve(A*A+y*y-r*r,y)[0];return [sol,s.arg(-A+I*sol)]
 # derive the range from the discriminant of the Cartesian equation and angle from cos theta
 y=s.symbols('y',real=True);bounds=sorted(s.solve(s.discriminant(y*y+h*h-r*r,y),h));return [*bounds,s.acos(h/r),-s.acos(h/r),s.arg(-r),s.arg(r)]

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);actual=p['facts']
  return len(actual)==len(expected) and all((type(a) is bool and a==b) if type(b) is bool else (type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'h':h,'k':k})-b)==0) for a,b in zip(actual,expected))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
