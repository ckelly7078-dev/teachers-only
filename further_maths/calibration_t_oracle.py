"""Independent exact checks via explicit root factors and Cartesian distance equations."""
import sympy as s
from calibration_t_bank import PATHS
x,h,m=s.symbols('x h m',real=True);R=s.Rational;I=s.I;pi=s.pi

def oracle(path,l,v):
 a=v+1;b=2*v+4;d=2*v+5
 def poly(rs):return s.expand(s.prod(x-r for r in rs))
 if path=='squared-roots':
  rs=[-a,b] if l in (1,5) else [a,b]
  if l==1:return [r**2 for r in rs]
  if l==2:return [sum(r**2 for r in rs),s.prod(r**2 for r in rs)]
  if l==3:return [poly([r**2 for r in rs])]
  if l==4:
   rr=[r-d for r in rs];return [sum(rr),s.prod(rr),poly([r**2 for r in rr])]
  if l==5:
   rr=[(j*a,k*b) for j in (-1,1) for k in (-1,1) if j*k<0 and j*a+k*b>0];return [poly(rr[0])]
  N=sum(r*r for r in rs);G=x*x-N*x+h;bound=s.solve(s.discriminant(G,x),h)[0];roots=s.solve(G,x);return [N,bound,roots[1],roots[0]]
 if path=='root-ratios':
  rs=[s.Integer(a),s.Integer(b)];rr=[rs[0]/rs[1],rs[1]/rs[0]]
  if l==1:return rr
  if l==2:return [s.Integer(1),s.Integer(1)]
  if l==3:return [poly(rr)]
  if l==4:
   u=s.solve(x/(a+b-x)+(a+b-x)/x-sum(rr),x);return [u[0]*u[1],poly(u)]
  if l==5:
   choices=[(j*a,k*b) for j in (-1,1) for k in (-1,1) if j*k<0 and j*a+k*b<0];return [poly(choices[0])]
  P=s.Symbol('P',real=True);G=x*x-d*x+P;T=s.solve(P*(h+2)-d*d,P)[0];return [T,s.discriminant(G,x).subs(P,T),-2,2]
 if path=='polar-geometry':
  if l==1:return [s.Abs(a*I),s.arg(a*I)]
  if l==2:return [s.Abs(-a*I),s.arg(-a*I)]
  if l in (3,4):
   T=([pi/6,pi/4,pi/3] if l==3 else [pi/3,pi/4,pi/6])[v-1];z=s.expand_complex(a*s.exp(I*T));w=s.expand_complex(a*s.exp(-I*T));return [z,w,s.arg(z/w)] if l==3 else [(z+w)/2,s.Abs(z-w)]
  if l==5:
   y=s.solve(a*a+x*x-(a*a+b*b),x);return [a+I*y[1],a+I*y[0]]
  y=s.Symbol('y',real=True);u=s.solve(x*x+y*y-((h-x)**2+y*y),x)[0];vals=s.solve(u*u+y*y-a*a,y);return [-2*a,0,2*a,u,vals[1]]
 if l==1:return [s.Abs(a+b*I)]
 if l==2:return [s.Abs(-a+b*I)]
 if l==3:return [s.Abs(-a+b*I),s.Abs(b+(a+b)*I)]
 if l==4:return [-a+I*min(s.solve(a*a+x*x-(a*a+b*b),x))]
 y=s.Symbol('y',real=True);r2=a*a+b*b if l==5 else a*a;other=(a-d)**2+b*b if l==5 else h*h
 u=s.solve((x-d)**2-x*x-(other-r2),x)[0];v2=s.factor(r2-u*u)
 if l==5:return [u+I*s.sqrt(v2),u-I*s.sqrt(v2)]
 bounds=sorted(t for t in s.solve(v2,h) if t>=0);return [*bounds,u,s.sqrt(v2)]

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);actual=p['facts']
  return len(actual)==len(expected) and all(type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'h':h,'m':m})-b)==0 for a,b in zip(actual,expected))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
