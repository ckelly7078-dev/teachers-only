"""Independent normal-space checks for FM-16AQ."""
import sympy as s

def expected(path,v):
    if path!='plane-intersection-direction': raise ValueError(path)
    a=s.Integer(v+1);b=a+2;h,k,m=s.symbols('h k m',real=True)
    D=s.Matrix([[1,h,0],[1,0,k]]);N=D.nullspace()[0];N=s.simplify(-h*N)
    point=s.Matrix([a,b,1]);return [*N,N.dot(point),s.Matrix([0,1,m]).dot(point),1,0]

def check(p):
    syms={n:s.Symbol(n,real=True) for n in ('h','k','m')};f=p['facts'];g=expected(p['path'],p['variant']);return len(f)==len(g) and all(s.simplify(s.sympify(x,locals=syms)-y)==0 for x,y in zip(f,g))
