"""Independent structured answers by explicit root and complex arithmetic."""
import sympy as s
x,h,k=s.symbols('x h k',real=True);I=s.I;pi=s.pi

def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,2*v+5,v+3));P=a*b;S=a+b
 roots=[a,b];F=s.prod(x-r for r in roots).expand()
 def poly(rs):return s.prod(x-r for r in rs).expand()
 def angle(z):return s.arg(s.expand_complex(z))
 def cis(t):return s.cos(t)+I*s.sin(t)
 if path=='combined-roots':
  if l==1:return [1/(b-d)]
  if l==2:return [next(r for r in [d,b] if r-d==0)]
  if l==3:return [poly([1/(r-d) for r in roots])]
  if l==4:return [poly([(a*r-d)**2 for r in roots])]
  if l==5:
   transformed=poly([1/(r-d) for r in roots]);return [poly([1/r+d for r in s.solve(transformed,x)])]
  # substitute the inverse map into transformed polynomial, clear denominators and normalize
  Q=s.expand((x-d)**2*((1/(x-d))**2-a/(x-d)+h)).cancel().expand();G=s.Poly(Q,x).monic().as_expr();return [G,s.solve(G.subs(x,0),h)[0]]
 if path=='shifted-products':
  if l in (1,2,3):return [F.subs(x,d)]
  if l==4:
   t=s.Symbol('t');rs=s.solve(F.subs(x,t)-F.subs(x,d),t);return [d,next(r for r in rs if r!=d)]
  if l==5:
   u,w=s.symbols('u w');G=x*x-u*x+w;sol=s.solve([G.subs(x,j)-F.subs(x,j) for j in (d,d+1)],(u,w));return [sol[u],sol[w],G.subs(sol)]
  u=s.Symbol('u');G=x*x-u*x+P;sumval=s.solve((G.subs(x,k)-P)/k,u)[0];G=G.subs(u,sumval);return [G,max(s.solve(s.discriminant(G,x),k))]
 if path=='polar-products':
  A=pi/(4,3,6)[v-1];B=3*pi/4;z=a*cis(A);w=b*cis(B)
  if l==1:return [A+B]
  if l==2:return [s.Abs(a*I*b)]
  if l==3:return [P,angle(z*w)]
  if l==4:return [d,angle(P*d*cis(pi/6)/(z*w))]
  if l==5:return [d,angle(a*d*cis(pi/3)/z)]
  # Solve sin(3theta+delta)=0 explicitly via periodic solution enumeration.
  return sorted({s.simplify((n*pi-A)/3) for n in range(-8,9) if -pi<(n*pi-A)/3<=pi})
 if path=='polar-quotients':
  A=-3*pi/4;B=pi/(4,3,6)[v-1];z=a*cis(A);w=b*cis(B)
  if l==1:return [a/b,A-B]
  if l==2:return [s.Integer(0)]
  if l==3:return [a/b,angle(z/w)]
  if l==4:return [a*d/b,angle(z*d*cis(pi/6)/w)]
  if l==5:return [a*d,angle(a*cis(A)*d*cis(pi/3))]
  Q=s.together(x+1/x-a*h).as_numer_denom()[0];Q=s.Poly(Q,x).monic().as_expr();return [Q,*sorted(s.solve(s.discriminant(Q,x),h))]
 raise ValueError(path)

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);actual=p['facts'];return len(actual)==len(expected) and all(type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'h':h,'k':k})-b)==0 for a,b in zip(actual,expected))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
