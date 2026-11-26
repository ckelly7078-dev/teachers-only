"""Independent symbolic checks for FM-16AJ."""
import sympy as s
def expected(path,v):
    a=s.Integer(v+1);b=a+2;k,h,r=s.symbols('k h r',real=True);l=s.Symbol('l',real=True)
    if path=='inverse-two':
        C=s.Matrix([[k,a],[b,l]]);J=C.inv();K=s.solve(J[0,0]+J[1,1],l)[0];Q=s.solve(J[0,1].subs(l,K)-r,k)[1];A=C.subs(l,K).subs(k,Q);B=J.subs(l,K).subs(k,Q).applyfunc(s.simplify)
        return [J[0,1].subs({k:0,l:0}),Q,*A,*B,0,1,2]
    if path=='inverse-systems':
        C=s.Matrix([[a,1],[k,b]]);B=s.Matrix([[1,2],[h,2*h+1]]);T=C.inv()*B;root=s.solve(C.det(),k)[0];left=C.subs(k,root).T.nullspace()[0];compat=[s.solve(left.dot(B[:,i]),h)[0] for i in range(2)]
        return [root,*T[:,0],*T[:,1],T.det(),*compat]
    raise ValueError(path)
def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('k','h','r')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
