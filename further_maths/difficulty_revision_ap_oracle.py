"""Independent exact checks for FM-16AP."""
import sympy as s

def expected(path,v):
    a=s.Integer(v+1);b=a+2;h,k,t,u=s.symbols('h k t u',real=True)
    if path=='singular-condition':
        A=s.Matrix([[1,a],[k,-1]]);B=s.Matrix([[h,1],[1,k]]);C=A*B;sol=s.solve(list(C),(k,h),dict=True)[0]
        return [A.det(),B.det(),sol[k],sol[h],*C]
    if path=='justify-skew':
        L=s.Matrix([t,t,0]);M=s.Matrix([u,a+k*u,h+u]);E=L-M;xy=s.solve(list(E[:2]),(t,u));yz=s.solve(list(E[1:]),(t,u));condition=s.factor(E[0].subs(yz));root=s.solve(condition,h)[0]
        return [xy[t],yz[u],yz[t],s.simplify(root*(k-1)),*L.subs(t,-h)]
    if path=='line-line-distance':
        out=[];ds=[]
        for d in (b,-b):
            E=s.Matrix([t-h-u,t,-d-u]);F=E.dot(E);sol=s.solve([s.diff(F,t),s.diff(F,u)],(t,u));out.extend([sol[t],sol[u]]);ds.append(s.sqrt(s.factor(F.subs(sol))))
        return [*out,*ds,b,-b]
    raise ValueError(path)

def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
