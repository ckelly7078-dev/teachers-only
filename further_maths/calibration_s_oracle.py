"""Exact independent checks using transformed factors, trigonometric identities and modular arithmetic."""
import sympy as s
from calibration_s_bank import PATHS
x,h,m=s.symbols('x h m',real=True);pi=s.pi;R=s.Rational

def oracle(path,l,v):
 a=v+1;b=2*v+4;d=2*v+5
 roots=[a,b]
 def poly(rs):return s.expand(s.prod(x-r for r in rs))
 def scale(t):return [r*t for r in roots]
 def shift(t):return [r+t for r in roots]
 if path=='scaled-roots':
  if l==1:return scale(d)
  if l==2:return [sum(scale(d)),s.prod(scale(d))]
  if l==3:return [poly(scale(-d))]
  if l==4:return [-a*b,poly([(-b)*(a*r) for r in roots])]
  if l==5:
   choices=s.solve(s.prod(scale(m))-d*d*a*b,m);t=next(t for t in choices if poly(scale(t)).coeff(x,1)>0);return [t,poly(scale(t))]
  G=poly(scale(m));D=s.discriminant(G,x);return [D.coeff(m,2),s.solve(D-h,m)[1],G]
 if path=='shifted-roots':
  if l==1:return shift(-d)
  if l==2:return [poly(shift(d))]
  if l==3:return [poly(shift(-d))]
  if l==4:
   t=s.solve(sum(shift(m))-(a+b+2*d),m)[0];G=poly(shift(t));return [t,G,s.discriminant(G,x)]
  if l==5:
   t=next(t for t in s.solve(s.prod(shift(m))-(a+d)*(b+d),m) if min(shift(t))>0);return [t,poly(shift(t))]
  eq=s.prod(shift(m))-h;bound=s.solve(s.discriminant(eq,m),h)[0];return [bound,*s.solve(eq,m)]
 def norm(T):
  u=s.Mod(T/pi,2);return (u-2 if u>1 else u)*pi
 if path=='argument-normalization':
  if l==1:return [a*360*pi/180]
  if l==2:return [s.arg(-1)]
  if l==3:return [norm(R(2*d+1,4)*pi)]
  if l==4:
   A=R(3,4)*pi;B=R(2*v+3,8)*pi;C=-R(3,4)*pi;return [norm(A+B),norm(A+B-C)]
  if l==5:
   T=R(v,4)*pi;return sorted(set(norm(T/2+n*pi) for n in range(2)))
  A=R(v,4)*pi;t=s.Symbol('t',real=True);return [s.solve(t-A+pi,t)[0],s.solve(t-A-pi,t)[0]]
 T=[pi/6,pi/4,pi/3][v-1]
 z=s.expand_complex(s.exp(s.I*T));C=s.re(z);N=s.im(z)
 if l==1:return [C,N]
 if l==2:
  z=s.expand_complex(-1/z);return [s.re(z),s.im(z)]
 if l==3:return [s.re((a+s.I*b)*z)]
 if l==4:return [s.simplify(a*b*s.exp(s.I*T)*s.exp(s.I*(pi/2-T)))]
 if l==5:return [pi-s.asin(N)]
 A=a*C;B=a*N;M=s.sqrt(A*A+B*B);phi=s.arg(A+s.I*B);return [M,phi,-M,M,phi-s.acos(h/M),phi+s.acos(h/M)]

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);actual=p['facts']
  return len(actual)==len(expected) and all(type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'h':h,'m':m})-b)==0 for a,b in zip(actual,expected))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
