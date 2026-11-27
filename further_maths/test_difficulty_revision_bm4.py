"""FM-16BM continuation: verify all corrections, facts and historical routing."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bm4 import TARGETS, revise
from difficulty_revision_bm4_oracle import check
from solution_review_bm import screen


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Resolver()
        cls.old = Resolver(historical_through='bm')

    def test_all_amendments(self):
        for (p, t), tag in TARGETS.items():
            for v in (1, 2, 3):
                with self.subTest(p=p, t=t, v=v):
                    item = self.r._resolve(p, t, v)
                    prior = self.old._resolve(p, t, v)
                    self.assertEqual(item['revision'], 'FM-16BM4')
                    self.assertEqual(prior['revision'], 'FM-16'+tag.upper())
                    self.assertEqual({k: val for k, val in item.items() if k not in ('revision', 'payload')}, {k: val for k, val in prior.items() if k not in ('revision', 'payload')})
                    old, new = prior['payload'], item['payload']
                    self.assertNotEqual(old, new)
                    self.assertEqual({k: val for k, val in old.items() if k not in ('question_latex', 'final_answer_latex', 'worked_solution_latex')}, {k: val for k, val in new.items() if k not in ('question_latex', 'final_answer_latex', 'worked_solution_latex')})
                    self.assertTrue(check(new))
                    self.assertTrue(screen(item)['math_delimiters_checked'])

    def test_short_answer_mathematics(self):
        for v in (1, 2, 3):
            p = revise('conjugate-find', 3, v)
            product = s.expand((v+1+s.I)*(2*v+5-(v+3)*s.I))
            self.assertIn('$'+s.latex(product)+'$', p['final_answer_latex'])
            self.assertEqual(s.conjugate(product), s.sympify(p['facts'][0]))
            p = revise('complex-quadratic', 4, v)
            a,b=map(s.sympify,p['facts'])
            self.assertEqual(a+b,-4)
            self.assertEqual(s.simplify(a*b), [52,100,164][v-1])
            self.assertIn('sum $-4$',p['final_answer_latex'])
            self.assertIn('product $'+str([52,100,164][v-1])+'$',p['final_answer_latex'])
            p = revise('polar-geometry',3,v)
            a,b,_=map(s.sympify,p['facts']);self.assertEqual(s.conjugate(a),b)
            self.assertIn('reflections',p['final_answer_latex'])
            p=revise('solve-quartic',6,v)
            x=s.symbols('x'); a=v+1; b=v+3
            for h,expected in ((1,4),(0,3),(-b*b,2),(-b*b-1,4)):
                roots=s.roots(((x-a)**2+b*b)*((x-a)**2-h),x)
                self.assertEqual(len(roots),expected)
            self.assertIn('four simple nonreal roots',p['final_answer_latex'])

    def test_defined_parameters_and_grouping(self):
        for v in (1,2,3):
            for path,tier,needle in [('argument-normalization',4,'not necessarily principal'),('cartesian-product',3,')('),('cartesian-sums',4,'2u=w'),('standard-cartesian',5,r'\frac{'),('distance-circle',6,'centre separation'),('polar-products',5,r'\mapsto'),('polar-products',6,r'\delta='),('polar-quotients',4,r'\arg z+\arg u-\arg w'),('polar-quotients',6,'q^{2}'),('polar-to-cartesian',6,r'\theta='),('conjugate-deduction',2,'guarantee conjugate pairing')]:
                p=revise(path,tier,v)
                self.assertIn(needle,' '.join([p['question_latex'],p['final_answer_latex'],*p['worked_solution_latex']]))

    def test_reject_invalid_targets(self):
        for args in [('cartesian-product',1,1),('cartesian-product',3,True),('cartesian-product',3,4)]:
            with self.assertRaises(ValueError): revise(*args)


if __name__ == '__main__': unittest.main(verbosity=2)
