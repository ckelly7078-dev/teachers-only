"""Preservation checks and independent determinant/inverse boundary tests."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bd import BANKS,TARGETS,base,revise
from marking_design_bd import records
from marking_review import inventory_entry
from marking_batch import validate_batch

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver(historical_through='bh')

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),69)
        retained={'collapse':'FM-16AI','inverse-two':'FM-16AJ','singular-condition':'FM-16AP'}
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
        rows=list(records(self.r));self.assertEqual(len(rows),216)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':216})

    def test_invalid_target(self):
        for key in [('collapse',6,1),('inverse-two',6,1),('singular-condition',6,1),('det-area',True,1),('orientation',2,True)]:
            with self.assertRaises(ValueError):revise(*key)

    def test_area_thresholds(self):
        for a in (2,3,4):
            for c,n in [(0,2),(s.Rational(a,2),4),(a,3),(a+1,2)]:
                roots={sign*s.sqrt(z) for z in (a+c,a-c) if z>=0 for sign in (-1,1)}
                self.assertEqual(len(roots),n)
                for k in roots:
                    M=s.Matrix([[k,a],[1,k]])
                    self.assertEqual(s.simplify(abs(M.det())-c),0)
                    if c==0:self.assertEqual(M.rank(),1)

    def test_collapse_repeated_root_and_kernel(self):
        for a,b in [(2,4),(3,5),(4,6)]:
            threshold=-s.Rational(b*b,4*a)
            for h in (threshold-1,threshold,threshold+1):
                k=s.symbols('k',real=True);roots=s.solve(k*k-b*k-a*h,k)
                self.assertEqual(len(roots),0 if h<threshold else 1 if h==threshold else 2)
                for z in roots:
                    M=s.Matrix([[z,a],[h,z-b]])
                    self.assertEqual(M.rank(),1)
                    self.assertEqual(s.simplify(M*s.Matrix([a,-z])),s.zeros(2,1))
                    self.assertNotEqual(M[:,1],s.zeros(2,1))

    def test_rank_three_boundaries(self):
        k=s.symbols('k',real=True)
        for a in (2,3,4):
            M=s.Matrix([[k,a,0],[a,k,a],[0,a,k]])
            self.assertEqual(s.factor(M.det()),k*(-2*a*a+k*k))
            self.assertEqual(M.extract([0,1],[1,2]).det(),a*a)
            for z in (0,a*s.sqrt(2),-a*s.sqrt(2)):
                self.assertEqual(M.subs(k,z).rank(),2)
            self.assertEqual(M.subs(k,1).rank(),3)

    def test_inverse_singular_branches(self):
        for a,b in [(2,3),(3,4),(4,5)]:
            for k,h in [(0,0),(0,2),(3,0),(3,2),(-1,2)]:
                M=s.Matrix([[1,a,0],[0,k,b],[0,0,h]])
                if k*h:
                    N=s.Matrix([[1,-s.Rational(a,k),s.Rational(a*b,h*k)],[0,s.Rational(1,k),-s.Rational(b,h*k)],[0,0,s.Rational(1,h)]])
                    self.assertEqual(M*N,s.eye(3))
                else:
                    d=s.Matrix([-a,1,0]) if k==0 else s.Matrix([s.Rational(a*b,k),-s.Rational(b,k),1])
                    self.assertEqual(M*d,s.zeros(3,1));self.assertEqual(len(M.nullspace()),1)

    def test_commutation_and_inverse_identity(self):
        k,h=s.symbols('k h',real=True)
        for a in (2,3,4):
            A=s.Matrix([[a,1],[0,k]]);B=s.Matrix([[a+1,h],[0,a+1]])
            self.assertEqual(s.expand((A*B-B*A)[0,1]),a*h-h*k)
            self.assertEqual(A.subs(k,0).rank(),1)
            for z,j in [(s.Rational(1,a),0),(s.Rational(1,a),3),(a,0),(a,3)]:
                C=s.Matrix([[a,j],[0,z]]);self.assertEqual(C+C.inv()==(a+s.Rational(1,a))*s.eye(2),z==s.Rational(1,a) or j==0)

    def test_product_zero_boundary(self):
        for a in (2,3,4):
            for h,k in [(-a,-s.Rational(1,a)),(0,-s.Rational(1,a)),(2,s.Rational(1,2)),(0,0)]:
                A=s.Matrix([[1,a],[k,-1]]);B=s.Matrix([[h,1],[1,k]]);P=A*B
                both=A.det()==B.det()==0
                self.assertEqual(P==s.zeros(2),both)
                self.assertEqual(P.det()==0,A.det()==0 or B.det()==0)

if __name__=='__main__':unittest.main()
