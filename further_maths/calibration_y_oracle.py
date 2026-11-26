"""Independent Cartesian intersection and polynomial-root calculations."""
import sympy as s
x,y,h,k=s.symbols('x y h k',real=True); I=s.I

def roots(P):
 return s.Poly(P,x).all_roots()
def sort_roots(P,order):
 R=roots(P);return [R[i] for i in order]
def oracle(path,l,v):
 a,b,d=map(s.Integer,(v+1,v+3,3*v+5)); z=a+b*I; F=s.expand((x-z)*(x-s.conjugate(z))); H=x*x+2*d*x+d*d+1
 if path=='distance-circle':
  if l==1:return [s.Abs(z)]
  if l==2:return [s.sqrt(b*b),b*b]
  if l==3:
   G=s.expand((x-a)**2+(y-b)**2-d*d);cx=s.solve(s.diff(G,x),x)[0];cy=s.solve(s.diff(G,y),y)[0];return [cx,cy,-G.subs({x:cx,y:cy})]
  if l==4:
   G=s.expand((x-a)**2+(y+b)**2-d*d);cx,cy=s.solve([s.diff(G,x),s.diff(G,y)],(x,y)).values();return [cx,cy,s.sqrt(-G.subs({x:cx,y:cy}))]
  if l==5:return s.solve((x-a)**2+b*b-d*d,x)
  A=x*x+y*y-b*b;B=(x-d)**2+y*y-h*h;X=s.solve(A-B,x)[0];Y=s.solve(A.subs(x,X),y)[0]**2;return [*sorted([d-b,d+b]),X,s.simplify(Y)]
 if path=='equidistant-locus':
  if l==1:return [s.Rational(2*a,2),s.Rational(2*b,2)]
  A=s.expand(x*x+y*y-(x-2*a)**2-y*y);X=s.solve(A,x)[0]
  if l==2:return [X,bool(A.subs({x:a,y:b})==0)]
  if l==3:
   G=s.expand(x*x+y*y-(x-2*a)**2-(y-2*b)**2)/4;return [G.coeff(x),G.coeff(y),-G.subs({x:0,y:0})]
  if l==4:
   Y=s.solve(x*x+y*y-x*x-(y-2*b)**2,y)[0];return [X,Y]
  if l==5:return [X+I*Y for Y in s.solve(X*X+y*y-d*d,y)]
  B=s.expand(x*x+y*y-(x-k)**2-(y-2*b*k)**2);Y=s.solve(B.subs(x,X),y)[0];C=s.expand(x*x+y*y-(x-k)**2-y*y).subs(x,X);return [X,Y,next(r for r in s.solve(C,k) if r!=0)]
 if path=='solve-cubic':
  G=s.expand((x+d)*F)
  if l==1:
   P=s.Poly(s.expand((x+d)*(x-a)*(x-b)),x);Q,R=s.div(P,s.Poly(x+d,x));assert R.is_zero;return Q.all_roots()
  if l in (2,3,4):return roots(G)
  if l==5:
   P=G-G.subs(x,0)+k;K=s.solve(P.subs(x,z),k)[0];return [K,*roots(P.subs(k,K))]
  b=b+v-1;G=s.expand((x-a)*((x-b)**2-h));Q,R=s.div(G,x-a,x);assert R==0;B=s.solve(Q.subs(x,a),h)[0];D=s.solve(s.discriminant(Q,x),h)[0];return [D,B,*s.solve(Q,x),a]
 if path=='solve-quartic':
  G=s.expand(F*H)
  if l==1:return roots((x*x-a*a)*(x*x-b*b))
  if l==2:return roots((x*x-a*a)*(x*x+b*b))
  if l==3:return sorted(roots(G),key=lambda r:(-float(s.re(r)),float(s.im(r))))
  if l==4:
   R=roots(s.expand(F*(x+d)*(x-b)));return [*sorted([r for r in R if not r.is_real],key=lambda r:float(s.im(r))),*[r for r in R if r.is_real]]
  if l==5:
   P=G-G.subs(x,0)+k;K=s.solve(P.subs(x,z),k)[0];return [K,*sorted(roots(P.subs(k,K)),key=lambda r:(-float(s.re(r)),float(s.im(r))))]
  P=s.expand(F*((x-a)**2-h));Q,R=s.div(P,F,x);assert R==0;D=s.solve(s.discriminant(Q,x),h)[0];B=s.solve(s.resultant(F,Q,x),h)[0];return [D,B,*roots(F),*s.solve(Q,x)]
 raise ValueError(path)

def check(obj):
 try:
  f=obj['facts'];g=oracle(obj['path'],obj['tier'],obj['variant']);return len(f)==len(g) and all((type(A) is bool and A==B) if type(B) is bool else (type(A) is not bool and s.simplify(s.sympify(A,locals={'x':x,'y':y,'h':h,'k':k})-B)==0) for A,B in zip(f,g))
 except (ValueError,TypeError,KeyError,s.SympifyError):return False
