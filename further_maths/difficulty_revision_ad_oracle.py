"""Independent fact and boundary checks for the FM-16AD overlay."""
import sympy as s
from calibration_z_oracle import check as old_z_check
from difficulty_revision_ad import revise, TARGETS

def expected(path,v):
    a=s.Integer(v+1); b=a+2; h,k,t=s.symbols('h k t',real=True); X,Y=s.symbols('X Y',real=True)
    if path=='complex-division':
        P=s.expand((a+s.I*k)*(X+s.I*Y)-(2*a*X+s.I*h)); equations=[s.re(P),s.im(P)]
        sol=s.solve(equations,(X,Y)); mat,_=s.linear_eq_to_matrix(equations,(X,Y)); singular=s.solve(mat.det(),k)
        return [sol[X],sol[Y],singular[1],singular[0],True,False]
    if path=='cartesian-product':
        P=s.expand((a+s.I*b)*(1+s.I*t)); T=s.solve(s.re(P)-s.im(P),t)[0]; Z=P.subs(t,T)
        return [T,Z,bool(s.re(Z)>0)]
    if path=='argument-range':
        P=h-a+s.I*(h-a)*(h-b); zeros=s.solve(s.im(P),h); R=s.cancel(s.im(P)/s.re(P)); H=s.solve(R+1,h)[0]
        return [zeros[0],zeros[1],s.atan(R)+s.pi,s.atan(R),H,bool(H<a)]
    raise ValueError(path)

def check(p):
    if p['path']=='angle-units':return old_z_check(p) and 'enrichment' in p['demand_rationale'].lower()
    h,k,t=s.symbols('h k t',real=True)
    f=p['facts']; g=expected(p['path'],p['variant'])
    return len(f)==len(g) and all((type(x) is bool and x==y) if type(y) is bool else (type(x) is not bool and s.simplify(s.sympify(x,locals={'h':h,'k':k,'t':t})-y)==0) for x,y in zip(f,g))
