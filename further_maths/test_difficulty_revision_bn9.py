"""All vector repairs preserve the prior exact facts and marking allocation."""
import unittest
import sympy as s
from active_difficulty import Resolver, SUCCESSIONS
from difficulty_revision_bn9 import TARGETS,revise
from difficulty_revision_bn9_oracle import check
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=Resolver();cls.old=Resolver(historical_through='bn5')
    def test_repairs(self):
        self.assertEqual(len(TARGETS),103)
        for key,tag in TARGETS.items():
            self.assertEqual(SUCCESSIONS[(*key,'bn9')],tag)
            for v in (1,2,3):
                with self.subTest(key=key,v=v):
                    old=self.old._resolve(*key,v);new=self.r._resolve(*key,v)
                    a,b=old['payload'],new['payload'];self.assertTrue(check(b))
                    self.assertEqual(new['revision'],'FM-16BN9');self.assertEqual(old['marks'],new['marks']);self.assertEqual(old['scope'],new['scope']);self.assertFalse(new['teacher_approved'])
                    changes={k for k in a if a[k]!=b[k]};self.assertTrue(changes);self.assertLessEqual(changes,{'question_latex','final_answer_latex','worked_solution_latex'})
                    self.assertEqual(inventory_entry(new)['status'],'typed_provisional')
                    for text in [b['question_latex'],b['final_answer_latex'],*b['worked_solution_latex']]:
                        self.assertEqual(text.count('$')%2,0);self.assertEqual(text.count(r'\begin{'),text.count(r'\end{'));self.assertFalse(any('\\' in part for part in text.split('$')[::2]))
    def test_closest_displacements(self):
        h=s.symbols('h',real=True);a=s.Matrix([1,1,0]);b=s.Matrix([1,0,1]);t,u=s.symbols('t u',real=True)
        for v in (1,2,3):
            item=self.r._resolve('line-line-distance',6,v)['payload'];self.assertIn(r'$(-t,t,t)$',item['worked_solution_latex'][2]);self.assertNotIn('(t,-t,-t)',item['worked_solution_latex'][2])
            for D in (v+3,-v-3):
                L=s.Matrix([t,t,0]);M=s.Matrix([h+u,0,D+u]);delta=L-M;sol=s.solve([delta.dot(a),delta.dot(b)],(t,u));T=(h-D)/3;U=-(h+2*D)/3
                self.assertEqual(s.simplify(sol[t]-T),0);self.assertEqual(s.simplify(sol[u]-U),0)
                self.assertEqual((delta.subs(sol)-s.Matrix([-T,T,T])).applyfunc(s.simplify),s.zeros(3,1));self.assertEqual((M.subs(sol)-s.Matrix([2*T,0,-T])).applyfunc(s.simplify),s.zeros(3,1))
                self.assertEqual(s.simplify(delta.subs(sol).dot(delta.subs(sol))-3*T*T),0)
                self.assertTrue(s.Matrix.hstack(a,b).rank()==2)
    def test_new_boundary_expressions(self):
        t,k,h=s.symbols('t k h',real=True)
        for v in (1,2,3):
            n=v+1;d=v+3;b=v+2;C=n*n+b*b;D=2*n*n+b*b
            expr=(1-2*t)*k*k+2*b*t*k-C*t
            self.assertEqual(s.simplify(s.discriminant(expr,k)-4*t*(C-D*t)),0)
            self.assertEqual(s.solve(expr.subs(t,s.Rational(1,2)),k),[s.Rational(C,2*b)])
            P=s.Matrix([0,0,d]);B=s.Matrix([n,0,0]);A=s.Matrix([0,n,0]);cross=(A-B).cross(P-B);self.assertEqual(s.simplify(cross.dot(cross)/4-n*n*s.Rational(1,4)*(2*d*d+n*n)),0)
            # Both displayed plane substitutions recover the constants identically.
            x,y,z=n-t,t,d-t;self.assertEqual(x+y,n);self.assertEqual(y+z,d)
            x,y,z=d-n*t,t,s.Rational(2*v+5,d);self.assertEqual(x+n*y,d);self.assertEqual(n*x+n*n*y+d*z,n*d+2*v+5)
            x,y,z=t,n-t,t+s.Rational(d+1,d);self.assertEqual(x+y,n);self.assertEqual(-(d-1)*x+y+d*z,n+d+1)
    def test_invalid(self):
        for args in [('unknown',2,1),('line-line-distance',6,True),('line-line-distance',6,4)]:
            with self.assertRaises(ValueError):revise(*args)

if __name__=='__main__':unittest.main(verbosity=2)
