"""Independent exact structured checks, solving via roots and coordinates."""
import sympy as s
x,h,T=s.symbols('x h T',real=True);I=s.I;pi=s.pi

def oracle(path,l,v):
 a=s.Integer(v+1);b=s.Integer(2*v+5);d=s.Integer(v+3);p=a*b
 roots=[a,b];F=s.expand((x-a)*(x-b));u,w,t=s.symbols('u w t',real=True)
 if path=='reciprocal-sums':
  if l in (1,3):return [sum(1/r for r in roots)]
  if l==2:return [min(s.solve(x*(x-b),x))]
  if l==4:return [sum(1/r for r in s.solve(F.subs(x,x+d),x))]
  if l==5:
   P=s.Symbol('P');prod=s.solve(P*sum(1/r for r in roots)-sum(roots),P)[0];return [prod,x*x-sum(roots)*x+prod]
  G=x*x-p*h*x+p;return [G,s.solve(s.discriminant(G,x),h)[1]]
 if path=='cube-sums':
  if l==1:return [(-a)**3+b**3]
  if l in (2,3):return [sum(r**3 for r in s.solve(F,x))]
  if l==4:return [sum(r**3 for r in s.solve(F.subs(x,x+d),x))]
  if l==5:
   P=s.Symbol('P');prod=s.solve(sum(roots)**3-3*sum(roots)*P-sum(r**3 for r in roots),P)[0];return [prod,x*x-sum(roots)*x+prod]
  # symmetric polynomial via remainder of x^3 modulo quadratic, sum over roots
  G=x*x-T*x+p;rem=s.rem(x**3,G,x);g=s.expand(rem.coeff(x)*T+2*rem.subs(x,0));boundary=max(s.solve(s.discriminant(G,x),T));return [g.subs(T,boundary),g]
 if path=='argument-rays':
  if l==1:return [s.arg(a*I)]
  if l==2:return [s.solve(u-a,u)[0]]
  if l==3:return [a,s.tan(pi/4)]
  if l==4:
   sol=s.solve([w-(u-a),u-a-d],(u,w));return [sol[u]+I*sol[w]]
  if l==5:
   rr=s.solve((t+d)**2-b*b,t);return [a+max(rr)]
  expr=(t-d)**2+b*b-h*h;rr=s.solve(expr,t);return [b,s.sqrt(expr.subs({t:0,h:0})),rr[1],rr[0]]
 if path=='complex-regions':
  if l==1:return [next(r for r in [a-1,a,a+1] if a<=r<a+1)]
  if l==2:return [int(bool(s.Abs(a*I)<a))]
  if l==3:return [a,b]
  if l==4:return [s.integrate(2*s.sqrt(a*a-t*t),(t,0,a))]
  if l==5:
   U=s.solve(u*u+w*w-((u-2*d)**2+w*w),u)[0];rr=s.solve(U*U+w*w-d*d-a*a,w);return [U+I*rr[1],U+I*rr[0]]
  cut=s.solve((u-h-d)**2-(u-h+d)**2,u)[0];top=s.sqrt(a*a-cut*cut);return [-a,0,a,top]
 raise ValueError(path)

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);actual=p['facts'];return len(actual)==len(expected) and all(type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'h':h,'T':T})-b)==0 for a,b in zip(actual,expected))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
