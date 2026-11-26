"""Independent structured answer checks for FM-16AG."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1); b=a+2; h=s.Symbol('h',real=True)
    if path=='cartesian-sums':
        x,y=s.symbols('x y',real=True); u=x+s.I*y; w=a+b*s.I-u
        eq=s.expand(u*s.conjugate(u)-w*s.conjugate(w)); Y=s.solve(eq,y)[0]; d=s.expand((2*u-a-b*s.I)*s.conjugate(2*u-a-b*s.I)).subs(y,Y)
        X=s.solve(s.expand(d-h*h),x)[0]; Y=Y.subs(x,X)
        return [X,Y,a-X,b-Y,0,1,2]
    if path=='cartesian-to-polar':
        A=s.Matrix([a,b]); B=s.Matrix([a-a*s.sqrt(3),b+a]); C=s.Matrix([a-a*s.sqrt(3),b-a]); D=B-A; E=C-B
        return [D[0]+s.I*D[1],E[0]+s.I*E[1],D.norm(),s.atan2(D[1],D[0]),E.norm(),s.atan2(E[1],E[0])]
    raise ValueError(path)
def check(p):
    h=s.Symbol('h',real=True); f=p['facts']; g=expected(p['path'],p['variant'])
    return len(f)==len(g) and all(s.simplify(s.sympify(x,locals={'h':h})-y)==0 for x,y in zip(f,g))
