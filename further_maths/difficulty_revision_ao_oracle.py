"""Independent exact structured checks for FM-16AO."""
import sympy as s


def expected(path,v):
    a=s.Integer(v+1);b=a+2;h,k,p,q=s.symbols('h k p q',real=True);x,y,z=s.symbols('x y z',real=True)
    if path=='line-plane-angle':
        n=s.Symbol('n',positive=True);eq=n*n-a*a-(p*n)**2-(q*n)**2;D=s.Poly(eq,n).nth(2);N=s.sqrt(-s.Poly(eq,n).nth(0))/s.sqrt(D)
        return [D,N,p*N,q*N,0,1,2,4]
    if path=='perpendicular-parameter':
        A=s.Matrix([-a,0,0]);B=s.Matrix([a,0,0]);C=s.Matrix([k,h,0]);eq=[(B-A).dot(C-A),(A-B).dot(C-B),(A-C).dot(B-C)]
        return [s.solve(eq[0],k)[0],s.solve(eq[1],k)[0],s.solve(eq[2],k)[1],0,4,3,2]
    if path=='scalar-product':
        w=s.Matrix([h,k,a]);u=s.Matrix([1,0,0]);v=s.Matrix([3,4,0]);boundary=s.expand(4*w.dot(u)**2-w.dot(w));upper=s.solve(v.dot(w),k)[0];lower=s.solve(boundary,k)[0];H=s.solve(boundary.subs(k,upper),h)[1]
        return [H,lower,upper]
    if path=='triangle-area':
        A=s.zeros(3,1);B=s.Matrix([a,0,0]);C=s.Matrix([0,a,0]);P=s.Matrix([x,y,h]);E=(B-A).cross(P-A);F=(C-A).cross(P-A);r=s.solve(E.dot(E)-a*a*b*b,y)[1];assert s.simplify(F.dot(F).subs(x,r)-a*a*b*b)==0
        Q=(C-B).cross(P-B);area=Q.dot(Q)/4;values=[s.sqrt(area.subs({x:r,y:r})),s.sqrt(area.subs({x:r,y:-r})),s.sqrt(area.subs({x:-r,y:-r}))];T=s.solve(r*r-a*a,h)[1]
        return [b,r,T,*values]
    raise ValueError(path)


def check(item):
    syms={n:s.Symbol(n,real=True) for n in ('h','k','p','q')};f=item['facts'];g=expected(item['path'],item['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
