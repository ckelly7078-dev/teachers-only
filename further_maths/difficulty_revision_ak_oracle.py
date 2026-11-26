"""Independent symbolic checks for FM-16AK."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1);b=a+2;h,k=s.symbols('h k',real=True);t=s.Symbol('t',real=True)
    if path=='cross-product':
        x,y,z=s.symbols('x y z',real=True);w=s.Matrix([x,y,z]);u=s.Matrix([1,a,0]);v=s.Matrix([0,1,b]);rhs=s.Matrix([k-a*b*h,b*h,-h]);eq=list(u.cross(w)-s.Matrix([a,-1,0]))+list(v.cross(w)-rhs);sol=s.solve(eq,(x,y,z,k),dict=True)[0];return [sol[k],sol[x],sol[y],sol[z]]
    if path=='line-plane-intersection':
        P=s.Matrix([a+t,b+k*t,t]);e=P[0]+P[1]-h;f=P[0]-P[1]-h;T=s.solve(e,t)[0];S=s.solve(f,t)[0];K=s.solve(s.diff(e,t),k)[0];J=s.solve(s.diff(f,t),k)[0];common=s.factor(s.together(T-S).as_numer_denom()[0]);return [T,S,*P.subs(t,T),*P.subs(t,S),K,J,s.solve(e.subs(k,K),h)[0],s.solve(f.subs(k,J),h)[0],s.solve(common,h)[0].__sub__(a)*k]
    raise ValueError(path)
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
