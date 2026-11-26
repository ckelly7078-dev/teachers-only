"""Independent symbolic checks for FM-16AI."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1); b=a+2; h,k,d=s.symbols('h k d',real=True); x,y=s.symbols('x y',real=True)
    if path=='collapse':
        c,e=s.symbols('c e'); A=s.Matrix([[c,1],[e,b]]); A=A.subs(s.solve(A*s.Matrix([1,-a]),(c,e))); U=A[:,1]; V=A.nullspace()[0]; V=V/V[0]; X=s.Matrix([0,s.solve((A*s.Matrix([0,y]))[0]-h,y)[0]])
        return [*A,*X,*V,U[1]/U[0]]
    if path=='invariant-lines':
        A=s.Matrix([[1,a],[0,1]]); R=A-s.eye(2); fixed=s.solve((R*s.Matrix([x,y]))[0],y)[0]; displaced=s.solve((R*s.Matrix([x,y]))[0]-h,y)[0]
        return [*A,fixed,displaced]
    if path=='det-two':
        A=s.Matrix([[x,a],[b,y]]); Y=s.solve((A+s.eye(2)).det()-A.det()-h+d,y)[0]; poly=s.Poly(d-A.det().subs(y,Y),x); S=-poly.nth(1); P=poly.nth(0); D=s.discriminant(poly.as_expr(),x); roots=s.solve(poly.as_expr(),x)
        return [S,P,D,*roots,0,1,2]
    raise ValueError(path)
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k','d')}; f=p['facts']; g=expected(p['path'],p['variant']); return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
