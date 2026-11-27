"""Preservation and boundary regression tests for matrix arithmetic marking."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bb import BANKS,TARGETS,base,revise
from marking_design_bb import records
from marking_batch import validate_batch
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),40)
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
                        else:self.assertEqual(item['revision'],'FM-16AS' if t==3 else 'FM-16AI')
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),123)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':123})
        self.assertTrue(all(not x['id'].startswith('CAL.det-two.T3.') for x in rows))

    def test_invalid_target(self):
        for key in [('det-two',3,1),('det-two',6,1),('matrix-products',True,1),('matrix-products',2,True)]:
            with self.assertRaises(ValueError):revise(*key)

    def test_ordered_divisors(self):
        for n,expected in [(6,4),(16,4),(20,6)]:
            pairs=[(p,p,r,r) for p in range(1,n+1) for r in range(1,n+1) if p*r==n and p!=r]
            self.assertEqual(len(pairs),expected)
            self.assertTrue(all(p*q!=0 and r*s0!=0 for p,q,r,s0 in pairs))

    def test_right_inverse_not_left(self):
        u,w=s.symbols('u w',real=True)
        for a in (2,3,4):
            b=a+2;C=s.Matrix([[1,0,a],[0,1,b]]);X=s.Matrix([[1-a*u,-a*w],[-b*u,1-b*w],[u,w]])
            self.assertEqual(s.simplify(C*X),s.eye(2))
            self.assertEqual(s.simplify((X*C)**2-X*C),s.zeros(3))
            n=s.Matrix([-a,-b,1]);self.assertEqual(C*n,s.zeros(2,1));self.assertNotEqual(n,s.zeros(3,1))

    def test_singular_and_zero_cases(self):
        k,h,p,q=s.symbols('k h p q',real=True)
        for a in (2,3,4):
            b=a+2;A=s.Matrix([[a,1],[k,b]])
            self.assertEqual(A.det(),a*b-k)
            self.assertEqual(A.subs(k,a*b)*s.Matrix([[p,q],[-a*p,-a*q]]),s.zeros(2))
            C=s.Matrix([[k,a],[h,-k]])
            self.assertEqual(s.simplify((C*C).subs(h,(1-k*k)/a)),s.eye(2))
            self.assertEqual(s.factor(h-h*(h-b)), -h*(h-b-1))

if __name__=='__main__':unittest.main()
