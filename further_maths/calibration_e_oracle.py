"""Independent structured answer checks; no claim of automated prose/difficulty certification."""
import sympy as s
M=s.Matrix
k,h,t,c,x,r,j=s.symbols('k h t c x r j',real=True)

def oracle(path,l,v):
 a=v+1;b=v+2
 if path=='orientation':
  if l==1:return [-a*b]
  if l==2:
   R=s.diag(-1,1);return [R.det(),abs(R.det())*a]
  if l==3:
   D=M([[a,2],[1,-b]]).det();return [D,s.sign(D)]
  if l==4:
   A=M([[-a,1],[0,1]]);B=M([[1,0],[2,-b]]);D=(B*A).det();return [D,a*abs(D),s.sign(D)]
  if l==5:
   D=M([[k,a],[1,k]]).det();target=b*b-a;rr=s.solve(D-target,k)
   assert s.solveset(D+target,k,domain=s.S.Reals)==s.S.EmptySet
   return [*rr,s.sign(D.subs(k,rr[0]))]
  A=M([[k,a],[a,k-b]]);D=A.det();rr=s.solve(D,k);lo,hi=rr
  signs=[s.sign(D.subs(k,i)) for i in (lo-1,(lo+hi)/2,hi+1,lo)]
  assert all(A.subs(k,i).rank()==1 for i in rr)
  return [D,*rr,*signs]
 if path=='basis-images':
  A=M([[a,1],[-1,b]]);I=s.eye(2)
  if l==1:return list(M([a,b]))
  if l==2:return [A*I[:,0],A*I[:,1]]
  if l==3:return [M.hstack(A*I[:,0],A*I[:,1])]
  if l==4:
   U=M([[1,1],[1,-1]]);T=(A*U)*U.inv();return [T[:,0],T[:,1]]
  if l==5:
   U=M([[1,2],[a,b]]);T=(A*U)*U.inv();return [T,T*M([a,-b])]
  U=M([[1,a],[0,k]]);V=M([[a,a*a+h],[1,a+b*k]]);T=V*U.inv()
  rr,ss,tt,uu=s.symbols('rr ss tt uu',real=True);G=M([[rr,ss],[tt,uu]])
  eq=list(G*U-V);sol=s.linsolve([e.subs({k:0,h:0}) for e in eq],(rr,ss,tt,uu));free=next(iter(sol));G0=M(2,2,free).subs({ss:r,uu:j})
  assert s.linsolve([e.subs({k:0,h:1}) for e in eq],(rr,ss,tt,uu))==s.S.EmptySet
  assert G0.subs({r:4,j:7})*U.subs(k,0)==V.subs({k:0,h:0})
  return [T,G0,1,0]
 if path=='cartesian-line':
  if l==1:return s.solve(a+2*t-x,t)
  if l==2:return [(M([a,b,1])+t*M([0,2,1]))[0]]
  p=M([a,b,1]);d=M([2,-1,b]);line=p+t*d
  if l==3:return [line.subs(t,0),line.diff(t)]
  if l==4:return [line.subs(t,0),line.diff(t),line.subs(t,s.solve(line[2]-1-2*b,t)[0])]
  if l==5:
   Q=M([a,b+2,1+b]);d=Q-p;line=p+t*d;return [p,d,line.subs(t,s.solve(line[1]-b-6,t)[0])]
  line=p+t*M([1,k,0]);eq=line[1]-h
  sol=s.solve(eq,t)[0];assert s.solveset(eq.subs({k:0,h:b+1}),t,domain=s.S.Reals)==s.S.EmptySet
  assert s.solveset(eq.subs({k:0,h:b}),t,domain=s.S.Reals)==s.S.Reals
  return [line.subs(t,sol),0,1,2]
 if path=='triple-volume':
  u=M([a,0,0]);w=M([1,b,0]);z=M([1,2,2]);vol=lambda u,w,z:abs(M.hstack(u,w,z).det())
  if l==1:return [vol(M([a,0,0]),M([0,1,0]),M([0,0,b]))]
  if l==2:
   A=s.diag(a,1,1);B=A.copy();B.col_swap(0,1);return [B.det(),abs(B.det())]
  if l==3:return [vol(u,w,z)]
  if l==4:
   P=M([1,2,3]);Q=P+u;R=P+w;S=P+z;return [Q-P,R-P,S-P,vol(Q-P,R-P,S-P)]
  if l==5:
   D=M.hstack(u,w,M([1,2,k])).det();return sorted(set(s.solve(D-a*b*b,k)+s.solve(D+a*b*b,k)))
  D=M.hstack(u,M([1,k,0]),M([0,0,k-b])).det();vertex=s.solve(s.diff(D,k),k)[0];B=-D.subs(k,vertex)
  counts=[len(s.solveset(D**2-target**2,k,domain=s.S.Reals)) for target in (0,B/2,B,B+1)]
  for sign in (-1,1):
   assert all(s.simplify(D.subs(k,root)-sign*c)==0 for root in s.solve(D-sign*c,k))
  return [D,B,*counts]
 raise ValueError(path)

def equivalent(a,b):
 if isinstance(b,bool):return type(a) is bool and a==b
 local={str(z):z for z in (k,h,t,c,x,r,j)}
 if isinstance(b,s.MatrixBase):
  if not isinstance(a,dict) or set(a)!={'matrix'}:return False
  m=M([[s.sympify(e,locals=local) for e in row] for row in a['matrix']]);return m.shape==b.shape and all(s.simplify(e)==0 for e in m-b)
 return isinstance(a,str) and s.simplify(s.sympify(a,locals=local)-b)==0

def check(p):
 try:
  expected=oracle(p['path'],p['tier'],p['variant']);return len(expected)==len(p['facts']) and all(equivalent(a,b) for a,b in zip(p['facts'],expected))
 except (KeyError,ValueError,TypeError,s.SympifyError):return False
