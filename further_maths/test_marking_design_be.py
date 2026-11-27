"""Preservation checks and independent system and geometry boundary tests."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_be import BANKS,TARGETS,base,revise
from marking_design_be import records
from marking_review import inventory_entry
from marking_batch import validate_batch

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),50)
        retained={'system-consistency':'FM-16AE','three-plane-unique':'FM-16AE','three-system':'FM-16AE','inverse-systems':'FM-16AJ'}
        for p in BANKS:
            for t in range(1,7):
                for v in (1,2,3):
                    with self.subTest(p=p,t=t,v=v):
                        item=self.r._resolve(p,t,v);x=item['payload']
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        self.assertFalse(item['teacher_approved'])
                        if (p,t) in TARGETS:
                            old=base(p).make(p,t,v)
                            self.assertEqual({k for k in old if old[k]!=x[k]},{'rubric'})
                            self.assertEqual(item['marks'],sum(z['marks'] for z in old['rubric']))
                        else:self.assertEqual(item['revision'],retained[p])
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),162)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':162})

    def test_invalid_target(self):
        for key in [('system-consistency',6,1),('inverse-systems',6,1),('three-system',6,1),('nonunique-set',True,1),('nonunique-geometry',2,True)]:
            with self.assertRaises(ValueError):revise(*key)

    def facts(self,p,v):
        return self.r._resolve(p,6,v)['payload']['facts']

    def test_homogeneous_rank(self):
        for v in (1,2,3):
            a=v+1
            f=self.facts('system-consistency',v)
            U=s.Matrix(list(map(s.sympify,f[2:5])));V=s.Matrix(list(map(s.sympify,f[5:8])))
            for d,e in [(0,0),(1,0),(0,1),(1,1)]:
                A=s.Matrix([[1,1,a],[1+d,1-d,a],[1,1+e,a-e]])
                self.assertEqual(3-A.rank(),2-d-e)
                if e==0:self.assertEqual(A*U,s.zeros(3,1))
                if d==0:self.assertEqual(A*V,s.zeros(3,1))
            self.assertEqual(s.Matrix.hstack(U,V).rank(),2)

    def test_nonnegative_interval(self):
        h=s.Symbol('h');
        for v in (1,2,3):
            total=v+3; c=v+1
            f=self.facts('nonunique-set',v)
            self.assertEqual(s.sympify(f[1]),total*c)
            for b in (-1,0,s.Rational(total*c,2),total*c,total*c+1):
                hi=s.sympify(f[2]).subs(h,b);lo=max(0,s.sympify(f[3]).subs(h,b))
                self.assertEqual(hi>=lo,0<=b<=total*c)
                if lo<=hi:
                    self.assertEqual(lo==hi,b in (0,total*c))
                    for t in {lo,hi,(lo+hi)/2}:
                        x,y,z=total-b+(c-1)*t,b-c*t,t
                        self.assertTrue(min(x,y,z)>=0)
                        self.assertEqual(x+y+z,total);self.assertEqual(y+c*z,b)

    def test_two_variable_admissibility(self):
        k,h=s.symbols('k h');t=s.Symbol('t')
        for v in (1,2,3):
            n=v+1;f=self.facts('two-variable-system',v)
            candidate=s.Matrix(f[2]['matrix']).applyfunc(s.sympify)
            for a in (-2,0,1,3):
                for b in sorted({min(n,n*a)-1,n,n*a,max(n,n*a)+1}):
                    A=s.Matrix([[1,1],[a,1]]);B=s.Matrix([n,b]);
                    if a==1:
                        self.assertEqual(A.row_join(B).rank()==A.rank(),b==n)
                        if b==n:self.assertEqual(A*s.Matrix([t,n-t]),B)
                    else:
                        X=candidate.subs({k:a,h:b});self.assertEqual(A*X,B)
                        self.assertEqual(min(X)>=0,min(n,n*a)<=b<=max(n,n*a))

    def test_inverse_system_independence(self):
        k,h=s.symbols('k h')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('inverse-systems',v)
            A=s.Matrix([[a,1],[k,b]]); X=s.Matrix(list(map(s.sympify,f[1:3])));Y=s.Matrix(list(map(s.sympify,f[3:5])))
            self.assertEqual(s.simplify(A*X),s.Matrix([1,h]));self.assertEqual(s.simplify(A*Y),s.Matrix([2,2*h+1]))
            self.assertEqual(s.simplify(s.Matrix.hstack(X,Y).det()-1/A.det()),0)
            singular=A.subs(k,a*b)
            for c in (b,s.Rational(2*b-1,2),b+1):
                self.assertEqual(singular.row_join(s.Matrix([1,c])).rank()==1,c==b)
                self.assertEqual(singular.row_join(s.Matrix([2,2*c+1])).rank()==1,c==s.Rational(2*b-1,2))

    def test_two_singular_values(self):
        k,h=s.symbols('k h');t=s.Symbol('t')
        for v in (1,2,3):
            n=v+1;m=v+3;f=self.facts('three-system',v)
            A=s.Matrix([[1,1,1],[1,k-v,3],[2,3,k-v]]);B=s.Matrix([n,n+m,2*n+h]);X=s.Matrix(list(map(s.sympify,f[4:7])))
            self.assertEqual(s.factor(A.det()),(k-v)*(k-v-3));self.assertEqual(s.simplify(A*X),B)
            for p,c in [(v,-m),(v+3,s.Rational(m,2))]:
                R=A.subs(k,p);self.assertEqual(R.rank(),2)
                self.assertEqual(R.row_join(B.subs(h,c+1)).rank(),3)
                y=c-(p-v-2)*t;F=s.Matrix([n-y-t,y,t]);self.assertEqual(s.simplify(R*F),B.subs(h,c))

    def test_pairwise_geometry(self):
        k,h=s.symbols('k h');t=s.Symbol('t')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('inconsistent-geometry',v)
            A=s.Matrix([[1,0,0],[0,1,0],[k-a,1,0]]);B=s.Matrix([a,b,h+(k-a)*a]);
            for kval in (a,a+1):
                for hval in (b,b+1):
                    R=A.subs(k,kval);C=B.subs({k:kval,h:hval})
                    self.assertEqual(R.row_join(C).rank()==R.rank(),hval==b)
                    for idx,(i,j) in enumerate([(0,1),(0,2),(1,2)]):
                        P=R[[i,j],:];Q=C[[i,j],:];
                        if idx==2 and kval==a:
                            self.assertEqual(P.rank(),1);self.assertEqual(P.row_join(Q).rank()==1,hval==b);continue
                        point=s.Matrix(f[2+idx]['matrix']).applyfunc(s.sympify).subs({k:kval,h:hval})
                        self.assertEqual(P.rank(),2);self.assertEqual(P*point,Q)

    def test_nonunique_geometry_dimension(self):
        for v in (1,2,3):
            a,b,c=v+1,v+3,2*v+5;f=self.facts('nonunique-geometry',v)
            self.assertEqual(list(map(int,f[:3])),[a,b,c])
            for d in (0,1):
                A=s.Matrix([[1,0,0],[1,d,0],[1,d,0]])
                for delta in (0,1):
                    B=s.Matrix([a,a+d*b,a+d*b+delta]);self.assertEqual(A.row_join(B).rank()==A.rank(),delta==0)
                    self.assertEqual(3-A.rank(),2-d)

if __name__=='__main__':unittest.main(verbosity=2)
