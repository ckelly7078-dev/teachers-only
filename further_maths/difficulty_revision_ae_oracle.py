"""Independent symbolic checks for FM-16AE."""
import sympy as s
from difficulty_revision_ae import TARGETS

def expected(path,v):
    a=s.Integer(v+1); b=a+2; k,h,t=s.symbols('k h t',real=True); x,y,z=s.symbols('x y z',real=True)
    if path=='system-consistency':
        u=x+y+a*z; eq=[u,u+(k-a)*(x-y),u+(h-b)*(y-z)]; A,_=s.linear_eq_to_matrix(eq,(x,y,z))
        U=A.subs({k:a+1,h:b}).nullspace()[0]; U=U*2/U[2]
        V=A.subs({k:a,h:b+1}).nullspace()[0]; V=V/V[2]
        dims=[3-A.subs({k:K,h:H}).rank() for K,H in ((a+1,b+1),(a+1,b),(a,b+1),(a,b))]
        return [a,b,*U,*V,*dims]
    if path=='three-system':
        eq=[x+y+z-a,x+(k-a+1)*y+3*z-a-b,2*x+3*y+(k-a+1)*z-2*a-h]; A,B=s.linear_eq_to_matrix(eq,(x,y,z)); roots=s.solve(A.det(),k); compatibility=[]
        for K in roots:
            left=A.subs(k,K).T.nullspace()[0]; compatibility.append(s.solve(left.dot(B),h)[0])
        return [*roots,*compatibility,*(A.inv()*B)]
    if path=='three-plane-unique':
        P=s.Matrix([a,b,a+1]); Q=s.Matrix([2*a,b,a+1]); A,B=s.linear_eq_to_matrix([x+y-a-b,y+z-a-b-1,x+k*y+z-h],(x,y,z)); R=A.inv()*B; H=Q.dot(s.Matrix([1,k,1])); R=R.subs(h,H); roots=s.solve(s.cancel((R-P).dot(R-P)-3*b*b),k); out=[]
        for K in roots: out.extend([K,H.subs(k,K),*R.subs(k,K)])
        return out
    if path=='composition-order':
        S=s.Matrix([[1,k],[0,1]]); T=s.Matrix([[1,0],[h,1]]); u=s.Matrix([1,1]); target=s.Matrix([a+1,b+1]); first=s.solve(T*S*u-target,(k,h),dict=True)[0]; second=s.solve(S*T*u-target,(k,h),dict=True)[0]; C=(T*S).subs(first); R=(S*T).subs(second)
        return [first[k],first[h],*C,second[k],second[h],bool(s.simplify(R[1,0]*C[0,0]-C[1,0]*R[0,0])==0)]
    raise ValueError(path)

def check(p):
    h,k,t=s.symbols('h k t',real=True); f=p['facts']; g=expected(p['path'],p['variant'])
    return len(f)==len(g) and all((type(x) is bool and x==y) if type(y) is bool else (type(x) is not bool and s.simplify(s.sympify(x,locals={'h':h,'k':k,'t':t})-y)==0) for x,y in zip(f,g))
