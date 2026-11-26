"""Independent coefficient comparison, roots and real/imaginary systems."""
import sympy as s
x,k,h,p=s.symbols('x k h p',real=True);u,vv,q=s.symbols('u vv q',real=True); I=s.I

def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,2*v+5,v+3));F=s.Poly((x-a)*(x-b),x);N=a*a+b*b;z=a+b*I
 if path=='factor-connection':
  if l==1:return [F.as_expr()]
  if l==2:return F.all_coeffs()[1:]
  if l==3:return s.Poly((a*x-d)*(b*x+1),x).all_coeffs()
  if l==4:
   eq=s.Poly((a*x+d)*(u*x+vv)-(a*x+d)*(b*x-1),x).all_coeffs();sol=s.solve(eq,(u,vv),dict=True)[0];return [sol[u],sol[vv]]
  if l==5:
   sol=s.solve([b*p+a*q-(a*d+b),p*q-d],(p,q));sol.sort(key=lambda pair:pair[0]!=1);return [j for pair in sol for j in pair]
  # Obtain the eliminated equation by the resultant, rather than hand substitution.
  G=s.resultant(b*p+a*q-h,p*q-d,q)*(-1);G=s.Poly(G,p).as_expr();return [G,*sorted(s.solve(s.discriminant(G,p),h))]
 if path=='symmetric-parameter':
  if l==1:return s.solve(a*k+d-(a*b+d),k)
  if l==2:return sorted(s.solve(s.discriminant(x*x-k*x+a*a,x),k))
  if l==3:return sorted(s.solve(k*k-2*a*b-(a*a+b*b),k))
  if l==4:
   K=s.solve((k+a)-b*k,k)[0];return [K,s.discriminant(x*x-(K+a)*x+b*K,x)]
  D=s.discriminant(x*x-k*x+a*k+d,x)
  if l==5:return sorted(s.solve(D-b*b,k))
  return [max(s.solve(D,k)),max(s.solve(D-h*h,k),key=lambda t:float(t.subs(h,0)))]
 if path=='conjugate-find':
  if l==1:return [s.conjugate(z)]
  if l==2:return [s.conjugate(a-b*I)]
  if l==3:return [s.expand((a-I)*(b+d*I))]
  Z=u+I*vv;target=b+d*I
  if l==4 or l==5:
   expr=Z+(a if l==4 else a*I)*s.conjugate(Z)-target;sol=s.solve([s.re(expr),s.im(expr)],(u,vv),dict=True)[0];return [Z.subs(sol)]
  expr=Z+k*s.conjugate(Z)-(a+I*h);eqs=[s.re(expr),s.im(expr)];sol=s.solve(eqs,(u,vv),dict=True)[0];return [Z.subs(sol),*sorted(s.solve(s.det(s.linear_eq_to_matrix(eqs,(u,vv))[0]),k))]
 if path=='conjugate-product':
  if l==1:return [s.Abs(z)**2]
  if l==2:return [s.expand(z*s.conjugate(z))]
  if l==3:return [s.expand_complex((d+I)/z)]
  if l==4:return sorted(s.solve((a+I*vv)*(a-I*vv)-N,vv))
  if l==5:
   sol=s.solve([u*u+vv*vv-N,(u+d)**2+vv*vv-((a+d)**2+b*b)],(u,vv));return [r+I*t for r,t in sorted(sol,key=lambda j:j[1])]
  ratio=((u+a)**2+vv*vv)/((u-a)**2+vv*vv);ratio=s.cancel(ratio.subs(vv**2,b*b-u*u));return [s.solve(ratio-h,u)[0],s.simplify(ratio.subs(u,-b)),s.simplify(ratio.subs(u,b))]
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);return len(f)==len(g) and all(type(a) is not bool and s.simplify(s.sympify(a,locals={'x':x,'k':k,'h':h,'p':p})-b)==0 for a,b in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
