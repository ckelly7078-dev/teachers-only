"""AX exact mathematics, marking allocation, preservation and evidence tests."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_ax import BANKS,TARGETS,base,revise
from difficulty_revision_ah import revise as ah_revise
from difficulty_revision_ax_oracle import check
from marking_design_ax import records
from marking_batch import validate_batch
from marking_review import inventory_entry


class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver(); self.assertEqual(len(TARGETS),41)
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    with self.subTest(path=path,tier=tier,v=v):
                        item=r._resolve(path,tier,v); p=item['payload']
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        self.assertFalse(item['teacher_approved'])
                        if (path,tier) in TARGETS:
                            old=base(path).make(path,tier,v)
                            self.assertEqual(item['revision'],'FM-16AX')
                            self.assertEqual(p,revise(path,tier,v))
                            self.assertTrue(check(p))
                            self.assertEqual(set(old),set(p))
                            self.assertLessEqual({k for k in old if old[k]!=p[k]},{'rubric','worked_solution_latex'})
                            self.assertEqual(item['marks'],sum(row['marks'] for row in old['rubric']))
                        else:
                            self.assertEqual((path,tier),('conjugate-factor',6))
                            self.assertEqual(item['revision'],'FM-16AH')
                            self.assertEqual(p,ah_revise(path,tier,v))

    def test_frozen_review_batch(self):
        r=Resolver(); batch=list(records(r))
        self.assertEqual(len(batch),126)
        self.assertTrue(all(x['review_basis']=='shared_design_plus_variant_oracle' for x in batch))
        self.assertEqual(validate_batch(batch,r)['statuses'],{'editorial_review_recorded':126})

    def test_frozen_review_rejects_changed_payload(self):
        r=Resolver(); original=r._resolve
        def changed(path,tier,v):
            i=original(path,tier,v)
            if (path,tier,v)==('complex-discriminant',1,1):
                i['payload']['likely_mistake']+=' changed'
            return i
        r._resolve=changed
        with self.assertRaisesRegex(ValueError,'frozen batch changed'):
            list(records(r))

    def test_invalid_targets(self):
        for p,t,v in [('conjugate-factor',6,1),('complex-quadratic',True,1),('complex-quadratic',1,True),('complex-quadratic',1,4),('complex-quadratic',1.0,1),('root-squares',1,1)]:
            with self.assertRaises(ValueError): revise(p,t,v)

    def test_boundary_multiplicities(self):
        x=s.Symbol('x'); r=Resolver()
        def counts(P):
            roots=s.roots(P,x)
            self.assertEqual(sum(roots.values()),s.degree(P,x))
            return sorted(roots.values()),sum(root.is_real is True for root in roots)
        for v in (1,2,3):
            a,b=v+1,v+3; centre=b+v-1; collision=(centre-a)**2
            f=r._resolve('solve-cubic',6,v)['payload']['facts']
            self.assertEqual([s.sympify(n) for n in f[:2]],[0,collision])
            for h,expected in [(-1,([1,1,1],1)),(0,([1,2],2)),(collision,([1,2],2)),(collision+1,([1,1,1],3))]:
                self.assertEqual(counts((x-a)*((x-centre)**2-h)),expected)
            F=(x-a)**2+b*b
            f=r._resolve('solve-quartic',6,v)['payload']['facts']
            self.assertEqual([s.sympify(n) for n in f[:2]],[0,-b*b])
            for h,expected in [(0,([1,1,2],1)),(-b*b,([2,2],0)),(-b*b-1,([1,1,1,1],0)),(1,([1,1,1,1],2))]:
                self.assertEqual(counts(F*((x-a)**2-h)),expected)
            f=r._resolve('conjugate-factor',6,v)['payload']['facts']; N=a*a+b*b
            self.assertEqual([s.sympify(n) for n in f[:2]],[N*b*b,N*N])
            self.assertEqual(counts(F**2),([2,2],0))
            self.assertEqual(counts(F*((x+a)**2+b*b)),([1,1,1,1],0))

    def test_specific_derivations(self):
        x=s.Symbol('x')
        for v in (1,2,3):
            a,b,d=v+1,v+3,3*v+5
            P=s.Poly((x+d)*((x-a)**2+b*b),x)
            self.assertEqual(P.eval(-d),0)
            terms=[c*(-d)**(3-j) for j,c in enumerate(P.all_coeffs())]
            step=revise('verify-roots',1,v)['worked_solution_latex'][0]
            self.assertIn(' + '.join(f'({t})' for t in terms)+' = 0',step)
            Q=s.Poly((x-a)**2+2*b*(x-a)+d*d,x)
            A,B,C=Q.all_coeffs()
            step=revise('complex-quadratic',4,v)['worked_solution_latex'][-1]
            self.assertIn(f'linear coefficient {B} and constant {C}',step)
            self.assertIn(f'sum {-B/A} and product {C/A}',step)
            self.assertIn('quadratic formula',revise('complex-quadratic',3,v)['worked_solution_latex'][1])
            self.assertIn('exactly two',revise('conjugate-deduction',4,v)['worked_solution_latex'][0])

    def test_presentation_delimiters(self):
        r=Resolver()
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    p=r._resolve(path,tier,v)['payload']
                    for value in (p['question_latex'],p['final_answer_latex'],*p['worked_solution_latex']):
                        self.assertEqual(value.count('$')%2,0,(path,tier,v,value))


if __name__=='__main__': unittest.main(verbosity=2)
