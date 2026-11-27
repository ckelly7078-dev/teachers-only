import unittest
import sympy as s
from active_difficulty import Resolver
from solution_review_bn import split_math, items_for, proof


class Tests(unittest.TestCase):
    def test_matrix_syntax_and_safety(self):
        self.assertEqual(len(split_math(r'$\left[\begin{matrix}1 & 2\\h & 4\end{matrix}\right]$')), 3)
        for text in (r'$\input{bad}$', r'$\begin{array}1\end{array}$', r'$1&2$',
                     r'$\begin{matrix}1\end{pmatrix}$', r'$\begin{matrix}1$', r'$\frac{1}{2$'):
            with self.assertRaises(ValueError):
                split_math(text)

    def test_reference_coverage(self):
        tex, records = proof(items_for(Resolver()))
        self.assertEqual(len(records), 162)
        self.assertEqual(tex.count(r'\clearpage'), 162)
        self.assertTrue(all(not r['visual_certified'] and not r['teacher_approved'] for r in records))

    def test_advanced_boundaries(self):
        r = Resolver()
        k,h,u,w,p,q,z,j,t = s.symbols('k h u w p q r j t')
        def facts(path,v):
            return r._resolve(path,6,v)['payload']['facts']
        def mat(f): return s.Matrix(f['matrix']).applyfunc(s.sympify)
        def eq(a,b): self.assertEqual((a-b).applyfunc(s.simplify),s.zeros(*a.shape))
        for v in (1,2,3):
            a,b=v+1,v+3
            f=facts('matrix-add-subtract',v); A=s.Matrix([[a,h],[k,b]])
            S,K=mat(f[0]),mat(f[1]); eq(S+K,A); eq(S,S.T); eq(K,-K.T)
            for root in f[2:4]: self.assertEqual(s.simplify(S.det().subs(h,s.sympify(root)-k)),0)
            f=facts('matrix-conformability',v); n=(6,16,20)[v-1]
            self.assertEqual(mat(f[0]),s.Matrix([(d,d,n//d,n//d) for d in s.divisors(n) if d!=n//d]))
            f=facts('matrix-products',v); C=s.Matrix([[1,0,a],[0,1,b]]); X,N,P=map(mat,f)
            eq(C*X,s.eye(2)); eq(C*N,s.zeros(2,1)); eq(X*C,P); eq(P*P,P)
            f=facts('scalar-matrix',v); self.assertEqual(s.factor(h-h*(h-b)), -s.sympify(f[0])); self.assertEqual(int(f[1]),b+1)
            f=facts('identity-operations',v); A=s.Matrix([[k,a],[h,-k]])
            eq((A*A).subs(h,s.sympify(f[1])),s.eye(2))
            f=facts('zero-matrix',v); A=s.Matrix([[a,1],[k,b]])
            self.assertEqual(s.expand(A.det()-s.sympify(f[0])),0); eq(A.subs(k,int(f[1]))*mat(f[2]),s.zeros(2,1))
            f=facts('basis-images',v); U=mat(f[0]); eq(U*s.Matrix([1,0]),s.Matrix([a,1])); eq(U*s.Matrix([a,k]),s.Matrix([a*a+h,a+b*k- k]))
            f=facts('describe-transform',v); A=s.Matrix([[k-a,h],[h,a-k]]); rho=s.sympify(f[0]); eq(A.T*A,rho**2*s.eye(2)); self.assertEqual(s.simplify(A.det()-s.sympify(f[1])),0)
            for N in f[2:4]: eq(A*mat(N),rho*mat(N))
            f=facts('figure-images',v); A=s.Matrix([[1,a],[0,h]]); base,dir=map(mat,f[:2]); eq(A*s.Matrix([t,k*t+b]),base+t*dir)
            eq(dir.subs({k:s.sympify(f[2]),h:0}),s.zeros(2,1))


if __name__ == '__main__': unittest.main(verbosity=2)
