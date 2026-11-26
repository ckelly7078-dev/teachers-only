"""Independent structured checks for FM-16AH."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1);b=a+2;h,x,U=s.symbols('h x U',real=True)
    if path=='modulus-constraints':
        eq=s.expand(U**2+(h-U)**2-a*a); roots=s.solve(eq,U); bounds=[s.solve(eq.subs(U,0),h)[1],s.solve(s.discriminant(eq,U),h)[1]]
        return [*bounds,roots[1],roots[0],0,4,8,4]
    if path=='conjugate-factor':
        F=s.expand((x-a-b*s.I)*(x-a+b*s.I));G=s.expand((x-U-b*s.I)*(x-U+b*s.I)); C=(F*G).subs(x,0);sol=s.solve(C-h,U)[1]
        return [C.subs(U,0),C.subs(U,a),sol,F,G.subs(U,sol),G.subs(U,-sol),1,2]
    raise ValueError(path)
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','x')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(a,locals=syms)-b)==0 for a,b in zip(f,g))
