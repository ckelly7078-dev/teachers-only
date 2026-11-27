"""Independent exact facts for BJ successor designs."""
import sympy as s
from importlib import import_module
from difficulty_revision_bj import TARGETS

def matrix_fact(mat):
    return {'matrix':[[str(mat[i,j]) for j in range(mat.cols)] for i in range(mat.rows)]}

def check(p):
    path,t,v=p['path'],p['tier'],p['variant']
    if (path,t) not in TARGETS or type(v) is not int or v not in (1,2,3): return False
    f=p['facts']; k=s.Symbol('k',real=True)
    if path in ('angle-units','solve-cubic','solve-quartic'):
        return import_module('difficulty_revision_'+TARGETS[path,t]+'_oracle').check(p)
    if path=='argument-range':
        z=s.sympify(f[0]); w=s.sympify(f[1]); angle=s.sympify(f[2]); target=-[5*s.pi/6,3*s.pi/4,2*s.pi/3][v-1]
        return s.re(z)==-(3*v+5) and s.simplify(s.arg(z)-target)==0 and w==-z and s.simplify(s.arg(w)-angle)==0 and s.simplify(s.tan(target)-s.tan(angle))==0
    if path=='cartesian-to-polar':
        y,theta,yy,theta2=map(s.sympify,f); radius=2*(v+1); real=[-2*s.sqrt(3),-3*s.sqrt(2),-4][v-1]
        return y<0 and yy>0 and {y,yy}==set(s.solve(real**2+k**2-radius**2,k)) and s.simplify(s.arg(real+s.I*y)-theta)==0 and s.simplify(s.arg(real+s.I*yy)-theta2)==0
    if path=='complex-division':
        kr,qr,ki,qi=map(s.sympify,f); a=v+1;b=v+3; expr=s.expand_complex((a+k*s.I)/(1+b*s.I)); re,im=expr.as_real_imag()
        return s.solve(im,k)==[kr] and s.solve(re,k)==[ki] and s.simplify(expr.subs(k,kr)-qr)==0 and s.simplify(expr.subs(k,ki)-qi)==0 and qr!=0 and qi!=0
    if path=='conjugate-product':
        yn,yp,qp,qn=map(s.sympify,f); x=v+1; norm=[53,90,137][v-1]
        return yn<0<yp and {yn,yp}==set(s.solve(x*x+k*k-norm,k)) and s.simplify(qp*(x-s.I*yp)-(x+s.I*yp))==0 and s.simplify(qn*(x-s.I*yn)-(x+s.I*yn))==0 and s.conjugate(qp)==qn
    if path=='inverse-systems':
        A=s.Matrix([[v+1,1,0],[1,v+3,1],[0,1,2*v+5]]); bs=[[6,8,35],[11,5,53],[18,0,75]][v-1]; total=[8,9,10][v-1]
        x,y,z=s.symbols('x y z'); solutions=s.linsolve([*(A*s.Matrix([x,y,z])-s.Matrix([bs[0],bs[1],k])),x+y+z-total],(x,y,z,k))
        if len(solutions)!=1:return False
        a,b,c,d=next(iter(solutions));return A.det()!=0 and d==s.sympify(f[0]) and f[1]==matrix_fact(s.Matrix([a,b,c])) and all(i.is_number for i in (a,b,c,d))
    if path=='related-solids':
        t1,t2,m,where=map(s.sympify,f); rho=[s.Rational(3,16),s.Rational(4,25),s.Rational(5,36)][v-1]
        # Unit tetrahedron: determinant ratio of the two scaled edges.
        ratio=s.det(s.diag(k,1-k,1)); return {t1,t2}==set(s.solve(ratio-rho,k)) and 0<t1<t2<1 and s.simplify(m-ratio-(k-where)**2)==0 and 0<where<1 and ratio.subs(k,where)==m
    if path=='vector-plane':
        a,b,c=map(s.sympify,f[:3]); P=s.Matrix([1,2,3]);u=s.Matrix([v+1,1,1]);h=s.Matrix([1,v+3,-1]); xy=[(6,1),(11,-4),(18,-11)][v-1]; W=s.Matrix([*xy,a]); n=s.Matrix([s.sympify(x[0]) for x in f[3]['matrix']]); C=s.sympify(f[4]); B=s.Matrix.hstack(u,h)
        return B[:2,:].det()!=0 and P+B*s.Matrix([b,c])==W and n!=s.zeros(3,1) and n.dot(u)==n.dot(h)==0 and n.dot(P)==n.dot(W)==C
    return False
