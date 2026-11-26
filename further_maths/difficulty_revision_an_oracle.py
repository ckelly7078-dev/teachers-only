"""Independent structured checks for FM-16AN."""
import sympy as s


def expected(path,v):
    a=s.Integer(v+1); b=a+2; h,k=s.symbols('h k',real=True); x,y=s.symbols('x y',real=True)
    if path=='polar-products':
        A=s.expand_complex(a*b*s.exp(5*s.pi*s.I/6)); B=s.expand_complex(a*b*s.exp(-s.pi*s.I/2))
        Z=s.Symbol("Z"); roots=s.solve(Z**2-s.expand(A*B/b**2),Z); z=next(s.expand_complex(r) for r in roots if s.re(s.expand_complex(r))>0); w=s.simplify(s.expand_complex(A/z))
        assert s.simplify(s.expand_complex(z*s.conjugate(w)-B))==0
        assert s.simplify(s.Abs(w)-b)==0
        return [a,s.Abs(w),s.arg(z),s.arg(w),s.arg(-z),s.arg(-w)]
    if path=='conjugate-find':
        eq=s.expand((x+s.I*y)**2+a*(x+s.I*y)+h-(x-s.I*y)); re,im=eq.as_real_imag(); real=s.Poly(re.subs(y,0),x); hi=s.solve(s.discriminant(real.as_expr(),x),h)[0]; X=s.solve(s.cancel(im/y),x)[0]; branch=re.subs(x,X); lo=s.solve(branch.subs(y,0),h)[0]; C=-real.nth(1)/2
        return [lo,hi,C,s.sqrt(hi-h),X,s.solve(branch,y)[1],2,4,3,2]
    if path=='cartesian-product':
        eq=s.expand((a+s.I*x)*(y+s.I*b)-h-s.I*k); re,im=eq.as_real_imag(); Y=s.solve(re,y)[0]; F=s.expand(a*im.subs(y,Y)); D=s.discriminant(F,x); roots=s.solve(F,x)
        return [D,roots[0],Y.subs(x,roots[0]),roots[1],Y.subs(x,roots[1]),0,1,2]
    raise ValueError(path)


def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
