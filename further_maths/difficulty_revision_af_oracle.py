"""Independent symbolic checks for algebra revisions."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1); b=a+2; x,h,k,d=s.symbols('x h k d',real=True); m,c,u,w=s.symbols('m c u w')
    if path=='scaled-roots':
        F=2*(x-a)*(x-b); target=s.expand((x+a*b)*(x+b*b)); other=target+1
        eq=s.Poly(s.expand(2*(x-m*a)*(x-m*b)-2*target),x).all_coeffs(); sol=s.solve(eq,m,dict=True)[0][m]
        valid=bool(s.expand((x-sol*a)*(x-sol*b)-target)==0); invalid=bool(s.expand((x-sol*a)*(x-sol*b)-other)==0)
        return [sol,target,valid,invalid] if v%2 else [sol,target,invalid,valid]
    if path=='root-squares':
        C=a*a+b*b; S=s.Symbol('S',real=True); ss=s.solve(S*S-2*h-C,S); bounds=[s.solve(C+2*h,h)[0],s.solve(C-2*h,h)[0]]
        return [*bounds,x*x-ss[1]*x+h,x*x-ss[0]*x+h,1,2,bounds[1]]
    if path=='reciprocal':
        P=a*b
        # Derive using two symbolic distinct roots, then substitute their symmetric data.
        fixed=s.solve([c-u*(u-d),c-w*(w-d)],(c,d)); swapped=s.solve([c-w*(u-d),c-u*(w-d)],(c,d)); thresholds=s.solve(s.discriminant(x*x-k*x+P,x),k); repeat=s.solve(c-(k/2)*(k/2-d),c)[0]
        return [swapped[c].subs(u*w,P),swapped[d],fixed[c].subs(u*w,P),fixed[d].subs(u+w,k),*thresholds,repeat,k/2]
    raise ValueError(path)
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('x','h','k','d')}; f=p['facts']; g=expected(p['path'],p['variant'])
    return len(f)==len(g) and all((type(a) is bool and a==b) if type(b) is bool else (type(a) is not bool and s.simplify(s.sympify(a,locals=syms)-b)==0) for a,b in zip(f,g))
