"""AZ preservation, exact facts, boundaries and frozen review evidence."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_az import BANKS,TARGETS,base,revise
from difficulty_revision_az_oracle import check
from marking_design_az import records
from marking_batch import validate_batch
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver();self.assertEqual(len(TARGETS),64)
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    with self.subTest(path=path,tier=tier,v=v):
                        item=r._resolve(path,tier,v);p=item['payload']
                        self.assertFalse(item['teacher_approved'])
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        if (path,tier) in TARGETS:
                            old=base(path).make(path,tier,v)
                            self.assertEqual(item['revision'],'FM-16AZ');self.assertTrue(check(p));self.assertEqual(p,revise(path,tier,v))
                            self.assertEqual(set(old),set(p))
                            fields={k for k in old if old[k]!=p[k]}
                            self.assertLessEqual(fields,{'rubric','worked_solution_latex','final_answer_latex'})
                            if 'final_answer_latex' in fields:
                                self.assertIn((path,tier),{('complex-regions',4),('polar-quotients',6)})
                                self.assertTrue(p['final_answer_latex'].startswith(old['final_answer_latex']))
                            self.assertEqual(item['marks'],sum(row['marks'] for row in old['rubric']))
                        else:
                            self.assertIn(item['revision'],{'FM-16AG','FM-16AN','FM-16AE','FM-16AD'})
                            tag,make,oracle=r.overlays[path,tier]
                            self.assertNotEqual(tag,'az');self.assertEqual(p,make(path,tier,v));self.assertTrue(oracle(p))

    def test_frozen_batch(self):
        r=Resolver();batch=list(records(r));self.assertEqual(len(batch),198)
        self.assertTrue(all(x['review_basis']=='shared_design_plus_variant_oracle' for x in batch))
        self.assertEqual(validate_batch(batch,r)['statuses'],{'editorial_review_recorded':198})

    def test_stale_evidence(self):
        r=Resolver();original=r._resolve
        def changed(p,t,v):
            i=original(p,t,v)
            if (p,t,v)==('distance-circle',1,1):i['payload']['likely_mistake']+=' changed'
            return i
        r._resolve=changed
        with self.assertRaisesRegex(ValueError,'frozen batch changed'):list(records(r))

    def test_invalid_targets(self):
        for p,t,v in [('cartesian-to-polar',4,1),('polar-products',5,1),('distance-circle',True,1),('distance-circle',1,True),('distance-circle',1,4),('distance-circle',1.0,1),('root-squares',1,1)]:
            with self.assertRaises(ValueError):revise(p,t,v)

    def test_polar_boundaries(self):
        for v in (1,2,3):
            a=v+1;theta=s.pi/[6,4,3][v-1];C=s.cos(theta);S=s.sin(theta)
            # Both positive radii recovered from an interior sum, boundary yields zero.
            for m,n in [(1,2),(2,0),(0,2),(0,0)]:
                h=(m-n)*C;k=(m+n)*S
                self.assertEqual(s.simplify((k/S+h/C)/2),m)
                self.assertEqual(s.simplify((k/S-h/C)/2),n)
                self.assertEqual(bool(s.simplify(k-s.tan(theta)*abs(h))>0),m>0 and n>0)
            delta=s.pi/[4,3,6][v-1]
            vals=[(j,(j*s.pi-delta)/3) for j in range(-8,9) if -s.pi<(j*s.pi-delta)/3<=s.pi]
            self.assertEqual([j for j,_ in vals],list(range(-2,4)))
            self.assertTrue(all(s.cos(3*x+delta)==(-1)**(j%2) and s.sin(3*x+delta)==0 for j,x in vals))
            q=s.Symbol('q');
            for H,count in [(-3,2),(-2,1),(0,2),(2,1),(3,2)]:
                roots=s.solve(q*q-H*q+1,q);self.assertEqual(len(roots),count)
                self.assertTrue(all(x!=0 and s.simplify(x+1/x)==H for x in roots))
                if abs(H)<=2:self.assertTrue(all(s.simplify(s.Abs(x))==1 for x in roots))
            phase=v*s.pi/4
            for t in [-2*s.pi,phase-s.pi,phase,phase+s.pi,2*s.pi]:
                raw=t-phase;out=raw+2*s.pi if raw<=-s.pi else raw-2*s.pi if raw>s.pi else raw
                self.assertTrue(-s.pi<out<=s.pi);self.assertEqual(s.exp(s.I*out),s.exp(s.I*raw))

    def test_locus_boundaries(self):
        for v in (1,2,3):
            a=v+1;b=v+3;d=3*a+2;r=b
            # distance-circle T6 uses d=3a+2 and r=a+2.
            for h,count in [(d-r-1,0),(d-r,1),(d,2),(d+r,1),(d+r+1,0)]:
                x=s.Rational(r*r+d*d-h*h,2*d);Y=r*r-x*x
                self.assertEqual(2 if Y>0 else 1 if Y==0 else 0,count)
            # Argument-rays T6: ray starts at a, centre at a+b plus positive height.
            k=b;vertical=2*a+3
            for h,count in [(vertical-1,0),(vertical,1),(s.sqrt(k*k+vertical*vertical),1),(vertical+ s.Rational(1,10),2)]:
                D=h*h-vertical*vertical
                roots=set() if D<0 else {k-s.sqrt(D),k+s.sqrt(D)}
                self.assertEqual(sum(bool(x>0) for x in roots),count)
            # Strict disk cap at the leftmost point excludes it; top point only for h<0.
            self.assertFalse(-a>-a);self.assertTrue(0>-a);self.assertFalse(0>0)
            for h in (s.Rational(a,2),0):
                lim=s.sqrt(a*a-h*h);x=h+s.Rational(1,10);y=s.sqrt(a*a-x*x)
                self.assertTrue(x>h and y<lim);self.assertEqual(s.simplify(x*x+y*y),a*a)

    def test_presentation_delimiters(self):
        r=Resolver()
        for p in BANKS:
            for t in range(1,7):
                for v in (1,2,3):
                    item=r._resolve(p,t,v)['payload']
                    for value in (item['question_latex'],item['final_answer_latex'],*item['worked_solution_latex']):
                        self.assertEqual(value.count('$')%2,0,(p,t,v,value))

if __name__=='__main__':unittest.main(verbosity=2)
