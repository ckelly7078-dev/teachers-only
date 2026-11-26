"""Independent exact structured-answer checks for FM-16G."""
import sympy as s
from itertools import product
M=s.Matrix
k,h,t,u,x,y,z=s.symbols('k h t u x y z',real=True)

def oracle(path,l,v):
 a=v+1;b=v+2;c=v+3
 if path=='matrix-conformability':
  A=s.zeros(a,b);B=s.zeros(b,a) if l==2 else s.zeros(b,c)
  if l==1:return list(A.shape)
  if l==2:return [A.shape==B.shape,A.cols==B.rows,*(A*B).shape]
  if l==3:return [A.cols==B.rows,*(A*B).shape,B.cols==A.rows,A.shape==B.shape]
  if l==4:
   C=s.zeros(c,a);return [*B.shape,*(A*B).shape,*(A*B*C).shape]
  if l==5:
   C=s.zeros(c,b);return [*B.shape,*(B*C).shape,B.cols==A.rows]
  N=a*b if v!=2 else b*b
  # Exhaust positive dimensions bounded by N; equality of output shapes fixes q,s.
  rows=[]
  for p,r in product(range(1,N+1),repeat=2):
   if p*r!=N:continue
   AA=s.zeros(p,p);BB=s.zeros(p,r);CC=s.zeros(r,r)
   if (AA*BB+BB*CC).shape==(p,r) and BB.cols!=AA.rows:rows.append([p,p,r,r])
  return [M(rows),len(rows)]
 if path=='singular-condition':
  A=M([[k,a],[b,k]])
  if l==1:return sorted(s.solveset((x+a)*(x-b),x,domain=s.S.Reals),key=float)
  if l==2:
   B=M([[a,b],[2*a,2*b]]);return [B.det(),B.rank()<2]
  if l==3:return sorted(s.solveset(A.det(),k,domain=s.S.Reals),key=float)
  if l==4:
   B=M([[k-a,0],[1,k+b]]);rs1=sorted(s.solveset(B.det(),k,domain=s.S.Reals),key=float);rs2=sorted(s.solveset(A.det(),k,domain=s.S.Reals),key=float);assert len(s.solveset((A*B).det(),k,domain=s.S.Reals))==4;return rs1+rs2
  if l==5:
   B=M([[k,h],[1,k]]);C=M([[k-a,0],[1,k+b]]);return [x for pair in sorted(s.solve([B.det(),C.det()],(k,h)),key=lambda p:float(p[0])) for x in pair]
  b=2*a+1;B=M([[k-a,h],[1,k-b]]);D=s.expand(B.det());hc=s.solve(s.discriminant(D,k),h)[0];rc=s.solve(D.subs(h,hc),k)[0];return [D,hc,rc,*[len(s.solveset(D.subs(h,hh),k,domain=s.S.Reals)) for hh in (hc-1,hc,hc+1)]]
 if path=='line-intersection':
  P=M([a,0,0]);d=M([1,b,1]);Q=M([0,b*a,a]);e=M([1,0,0]);left=P+t*d;right=Q+u*e
  if l==1:
   r=s.solve([u-t-a,t-a],(t,u));return [r[t],r[u]]
  if l==2:
   A=M([1,a,0]);B=M([1,a,a]);return [A==B,(A-B).norm()]
  if l==3:
   r=s.solve(left-right,(t,u));return [r[t],r[u],left.subs(r)]
  if l==4:
   Q2=Q+M([0,0,1]);r=s.solve(left-Q2-u*e,(t,u));tt=s.solve(left[2]-Q2[2],t)[0];assert d.cross(e)!=s.zeros(3,1);return [bool(r),tt,left[1].subs(t,tt)-Q2[1]]
  if l==5:
   r=s.solve(left-M([u,h,a]),(t,h,u));return [r[t],r[h],r[u],left.subs(r)]
  # Exact general solutions of the nonparallel cases and residual height;
  # check parallel/coincident cases directly at both zero and nonzero heights.
  eq=M([t-u,-a-k*u,-h]);r=s.solve(eq[:2],(t,u));assert s.simplify(eq[2].subs(r))==-h
  assert not s.solve(eq.subs({k:0,h:0}),(t,u));assert not s.solve(eq.subs({k:0,h:1}),(t,u))
  zero=M([t-u,-k*u,-h]);assert s.solve(zero.subs(h,0),(t,u))=={t:0,u:0};assert s.solve(zero.subs({k:0,h:0}),(t,u))=={t:u};assert not s.solve(zero.subs({k:0,h:1}),(t,u));return [r[t],r[u],-eq[2],s.solve(zero[1],u)[0]]
 if path=='unit-vector':
  D=M([a,b,0]);E=M([a,b,c]);P=M([1,2,3]);Q=P+D
  if l==1:return [E.norm()]
  if l==2:return [(D/(a+b)).norm(),D.normalized()]
  if l==3:
   U=M([a,-b,c]).normalized();return [U,U.norm()]
  if l==4:
   U=(Q-P).normalized();return [U,P+2*(Q-P).norm()*U]
  if l==5:
   U=E.normalized();R=s.Symbol('R');length=s.solve(R*U[2]-2*c,R)[0];return [length,length*U]
  rr=s.solve([x-h,a*y-k],(x,y));expr=s.expand(1-x*x-y*y).subs(rr);assert s.solveset(z*z+1,z,domain=s.S.Reals)==s.EmptySet;return [expr,*[len(s.solveset(z*z-r,z,domain=s.S.Reals)) for r in (-1,0,1)]]
 raise ValueError(path)

def equivalent(a,b):
 local={str(z):z for z in (k,h,t,u,x,y,z)}
 if isinstance(b,bool):return type(a) is bool and a==b
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(e)==0 for e in m-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
