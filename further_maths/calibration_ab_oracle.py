"""Independent exact checks for FM-16AB."""
import sympy as s
I=s.I

def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5));t,h,p,q=s.symbols('t h p q',real=True);z=a-b*I;w=d+a*I
 def parts(Z):return [s.simplify(s.re(Z)),s.simplify(s.im(Z))]
 if path=='identify-components':
  if l==1:
   P=s.Poly(a-b*t,t);return [P.nth(0),P.nth(1)]
  if l==2:return parts(-b*I)
  if l==3:return parts(z-w+b*I)
  if l==4:
   R,J=parts((a+b*I)*(t-a*I));return [R,J,s.solve(R-J,t)[0]]
  if l==5:
   R,J=parts((a+b*I)*(p+I*q));M=s.linear_eq_to_matrix([R-(a*a-b*d),J-(b*a+a*d)],p,q);sol=M[0].inv()*M[1];return [*sol,M[0].det()]
  Z=(t-d)**2-a*(a+1)+I*(t-d);R,J=parts(Z);rr=sorted(s.solve(R**2-J**2,t));return [*rr,*[s.sign(E.subs(t,T)) for T in rr for E in (R,J)]]
 if path=='standard-cartesian':
  if l==1:return [I**(4*v+2),I**(4*v+3)]
  if l==2:return sorted(s.roots(t*t+b*b),key=s.im,reverse=True)
  if l==3:return parts(z/w)
  if l==4:return parts(1/z+1/s.conjugate(z)+a*I)
  if l==5:
   Z=s.expand_complex((z/w)**2);return [*parts(Z),s.simplify(s.Abs(Z))]
  R,J=parts((t-a+b*I)/(t-a-b*I));T=s.solve(R-h,t);rad=s.simplify((T[1]-T[0])/2);return [R,J,s.solve(J,t)[0],R.subs(t,a),s.limit(R,t,s.oo),s.simplify(rad**2),s.simplify(J**2+R**2-h**2)]
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);local={x:s.Symbol(x,real=True) for x in ('t','h')};return len(f)==len(g) and all(s.simplify(s.sympify(A,locals=local)-B)==0 for A,B in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
