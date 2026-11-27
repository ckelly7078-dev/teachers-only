"""Version-bound preservation, allocation and independent matrix checks."""
import unittest
import sympy as s
from active_difficulty import Resolver, SUCCESSIONS, MARK_SUCCESSIONS
from difficulty_revision_bn5 import TARGETS, revise
from difficulty_revision_bn5_oracle import check
from marking_review import inventory_entry


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=Resolver();cls.old=Resolver(historical_through='bm4')

    def test_all_repairs(self):
        self.assertEqual(len(TARGETS),71)
        for key,tag in TARGETS.items():
            self.assertEqual(SUCCESSIONS[(*key,'bn5')],tag)
            for v in (1,2,3):
                with self.subTest(key=key,v=v):
                    old=self.old._resolve(*key,v);new=self.r._resolve(*key,v)
                    a,b=old['payload'],new['payload']
                    self.assertTrue(check(b));self.assertEqual(new['revision'],'FM-16BN5')
                    self.assertEqual(old['scope'],new['scope']);self.assertFalse(new['teacher_approved'])
                    changes={k for k in a if a[k]!=b[k]};self.assertTrue(changes)
                    allowed={'question_latex','final_answer_latex','worked_solution_latex'}
                    if key==('inverse-three',6):allowed.add('rubric')
                    self.assertLessEqual(changes,allowed)
                    self.assertEqual(new['marks'],8 if key==('inverse-three',6) else old['marks'])
                    self.assertEqual(inventory_entry(new)['status'],'typed_provisional')
                    for text in [b['question_latex'],b['final_answer_latex'],*b['worked_solution_latex']]:
                        self.assertEqual(text.count('$')%2,0)
                        self.assertEqual(text.count(r'\begin{'),text.count(r'\end{'))
                        # Newly repaired fragments may not introduce raw TeX commands outside math.
                        self.assertFalse(any('\\' in part for part in text.split('$')[::2]))

    def test_allocation_and_triangular_inverse(self):
        self.assertEqual(MARK_SUCCESSIONS[('inverse-three',6,'bn5')],(3,8))
        k,h=s.symbols('k h',real=True)
        for v in (1,2,3):
            item=self.r._resolve('inverse-three',6,v);f=item['payload']['facts'];a=v+1;b=v+2
            A=s.Matrix([[1,a,0],[0,k,b],[0,0,h]])
            def mat(x):return s.Matrix([[s.sympify(z,locals={'k':k,'h':h}) for z in row] for row in x['matrix']])
            self.assertEqual(s.sympify(f[0],locals={'k':k,'h':h}),A.det())
            self.assertEqual((A*mat(f[1])).applyfunc(s.simplify),s.eye(3))
            self.assertEqual(A.subs(k,0)*mat(f[2]),s.zeros(3,1))
            self.assertEqual((A.subs(h,0)*mat(f[3])).applyfunc(s.simplify),s.zeros(3,1))
            for kv,hv in ((0,0),(0,2),(3,0)):
                self.assertEqual(A.subs({k:kv,h:hv}).rank(),2)
            self.assertEqual(item['marks'],8)

    def test_reflection_and_line_boundaries(self):
        k,h,t=s.symbols('k h t',real=True)
        for v in (1,2,3):
            a,b=v+1,v+3;M=s.Matrix([[k-a,h],[h,a-k]])
            rho2=(k-a)**2+h*h
            self.assertEqual((M.T*M-rho2*s.eye(2)).applyfunc(s.simplify),s.zeros(2))
            self.assertEqual(M.subs({k:a,h:0}),s.zeros(2))
            self.assertEqual(M.subs({k:a-1,h:0})*s.Matrix([0,1]),s.Matrix([0,1]))
            N=s.Matrix([[1,a],[0,h]]);out=N*s.Matrix([t,k*t+b]);direction=out.diff(t)
            self.assertEqual(direction.subs({k:-s.Rational(1,a),h:0}),s.zeros(2,1))
            self.assertEqual(direction.subs(k,-s.Rational(1,a)),s.Matrix([0,-h/a]))
            self.assertEqual(out.subs({k:-s.Rational(1,a),h:0}),s.Matrix([a*b,0]))

    def test_invalid_targets(self):
        for args in [('unknown',2,1),('inverse-three',1,1),('inverse-three',6,True),('inverse-three',6,4)]:
            with self.assertRaises(ValueError):revise(*args)


if __name__=='__main__':unittest.main(verbosity=2)
