"""Independent exact checks for BL new facts; unchanged facts delegate to predecessor."""
from importlib import import_module
import sympy as s
from difficulty_revision_bl import TARGETS,REGISTRY,NEW_DEMAND

def mat(o):return s.Matrix([[s.sympify(y) for y in row] for row in o['matrix']])
def eq(a,b):return s.simplify(a-b)==0

def check(p):
    path,t,v=p['path'],p['tier'],p['variant'];key=path,t
    if key not in TARGETS or type(v) is not int or v not in (1,2,3):return False
    if sum(x['marks'] for x in p['rubric'])!=REGISTRY[key][2]:return False
    if key not in NEW_DEMAND:return import_module('difficulty_revision_'+TARGETS[key]+'_oracle').check(p)
    f=p['facts'];k,h,t0=s.symbols('k h t');a=v+1;b=v+2
    if path=='inverse-three':
        K=s.sympify(f[0]);I,X=map(mat,f[1:]);A=s.Matrix([[1,a,0],[1,K,b],[0,1,1]]);B=s.Matrix([v+2,v+3,v+4]);G=s.Matrix([[1,a,0],[1,k,b],[0,1,1]])
        return A.det()!=0 and A*I==I*A==s.eye(3) and I[0,2]==a and A*X==B and s.solve(G.inv()[0,2]-a,k)==[K]
    if path=='locus-intersection':
        lo,hi,D,xp,yp,xm,ym=map(s.sympify,f);C=v+1;R=v+3
        return eq(lo,C-s.sqrt(2)*R) and eq(hi,C+s.sqrt(2)*R) and eq(D,2*R**2-(k-C)**2) and all(eq(x+y,k) and eq((x-C)**2+y*y,R*R) for x,y in ((xp,yp),(xm,ym))) and eq(xp-xm,s.sqrt(D)) and eq(D.subs(k,lo),0) and eq(D.subs(k,hi),0)
    if path=='point-line':
        foot=mat(f[0]);D,tp,tm=map(s.sympify,f[1:]);P=s.Matrix([2*v+2,0,v+3]);d=s.Matrix([1,1,0]);dist=lambda z:(z*d-P).dot(z*d-P)
        return foot==P.dot(d)/d.dot(d)*d and eq(D,(foot-P).dot(foot-P)) and eq(dist(tp),h) and eq(dist(tm),h) and eq(tp-tm,2*s.sqrt((h-D)/2)) and eq(dist(t0)-D,2*(t0-foot[0])**2)
    if path=='symmetric-parameter':
        ks=list(map(s.sympify,f[:2]));pairs=[list(map(s.sympify,x)) for x in f[2:]];D=2*v+5;P=a*k+v+3
        return set(ks)==set(s.solve(k*k-4*P-D*D,k)) and all(eq(x+y,j) and eq(x*y,P.subs(k,j)) and eq(y-x,D) for j,(x,y) in zip(ks,pairs)) and pairs[0][0]<0<pairs[0][1] and 0<pairs[1][0]<pairs[1][1]
    if path=='system-consistency':
        A=v+1;B=v+3;H=s.sympify(f[0]);X,L=map(mat,f[1:]);M=s.Matrix([[1,1,0],[0,1,1],[1,2,k]])
        return H==A+B and M.det()==k-1 and all(eq(i,0) for i in M*X-s.Matrix([A,B,h])) and all(eq(i,0) for i in M.subs(k,1)*L-s.Matrix([A,B,H])) and L[2]==t0 and M.subs(k,1).rank()==2 and M.subs(k,1).row_join(s.Matrix([A,B,H+1])).rank()==3
    return False
