"""Independent checks by linear equations, not the cross product construction."""
import sympy as s
def expected(path,v):
    if path!='skew': raise ValueError(path)
    a=s.Integer(v+1); b=a+2; h,k=s.symbols('h k',real=True); n,m,t,u=s.symbols('n m t u',real=True)
    sol=s.solve([n-a,n-k+m],(n,m)); N=s.Matrix([sol[n],-1,sol[m]])
    C=N.dot(s.Matrix([0,h,b])); cross=s.solve([t-u,a*t-h-k*u,b+u],(t,u,h),dict=True)[0]
    return [*N,C,cross[h],cross[t],a*cross[t],0]
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k')}; f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
