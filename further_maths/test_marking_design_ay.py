"""AY preservation, geometry, angular boundaries and frozen review tests."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_ay import BANKS,TARGETS,base,revise
from difficulty_revision_ay_oracle import check
from difficulty_revision_ad import revise as ad_revise
from difficulty_revision_ah import revise as ah_revise
from marking_design_ay import records
from marking_batch import validate_batch
from marking_review import inventory_entry


class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver(historical_through='bh'); self.assertEqual(len(TARGETS),39)
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    with self.subTest(path=path,tier=tier,v=v):
                        item=r._resolve(path,tier,v); p=item['payload']
                        self.assertFalse(item['teacher_approved'])
                        if (path,tier) in TARGETS:
                            old=base(path).make(path,tier,v)
                            self.assertEqual(item['revision'],'FM-16AY')
                            self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                            self.assertTrue(check(p)); self.assertEqual(p,revise(path,tier,v))
                            self.assertEqual(set(old),set(p))
                            self.assertLessEqual({k for k in old if old[k]!=p[k]},{'rubric','worked_solution_latex'})
                            self.assertEqual(item['marks'],sum(row['marks'] for row in old['rubric']))
                        elif path=='modulus-constraints':
                            self.assertEqual(item['revision'],'FM-16AH');self.assertEqual(p,ah_revise(path,tier,v))
                        else:
                            if path=='angle-units':
                                self.assertEqual(item['revision'],'FM-16BA')
                                self.assertEqual(r._resolve_version(path,tier,v,'ad')['payload'],ad_revise(path,tier,v))
                            else:
                                self.assertEqual(item['revision'],'FM-16AD');self.assertEqual(p,ad_revise(path,tier,v))
                            self.assertEqual(inventory_entry(item)['status'],'typed_provisional')

    def test_frozen_batch(self):
        r=Resolver(historical_through='bh'); batch=list(records(r));self.assertEqual(len(batch),126)
        self.assertTrue(all(x['review_basis']=='shared_design_plus_variant_oracle' for x in batch))
        stale=[x for x in batch if x['id'].startswith('CAL.angle-units.T6.')]
        self.assertEqual(len(stale),3)
        for row in stale:
            with self.assertRaisesRegex(ValueError,'Stale'):validate_batch([row],r)
        self.assertEqual(validate_batch([x for x in batch if x not in stale],r)['statuses'],{'editorial_review_recorded':123})

    def test_stale_evidence(self):
        r=Resolver(historical_through='bh'); original=r._resolve
        def changed(path,tier,v):
            i=original(path,tier,v)
            if (path,tier,v)==('argand-coordinates',1,1): i['payload']['likely_mistake']+=' changed'
            return i
        r._resolve=changed
        with self.assertRaisesRegex(ValueError,'frozen batch changed'):list(records(r))

    def test_invalid_targets(self):
        for p,t,v in [('angle-units',6,1),('modulus-constraints',6,1),('argument-range',6,1),('argand-coordinates',True,1),('argand-coordinates',1,True),('argand-coordinates',1,4),('argand-coordinates',1.0,1),('root-squares',1,1)]:
            with self.assertRaises(ValueError):revise(p,t,v)

    def test_geometry_boundary(self):
        h,u,y=s.symbols('h u y',real=True)
        self.assertEqual(s.expand((h/2+u)**2+y*y-((h/2-u)**2+y*y)),2*h*u)
        for v in (1,2,3):
            a=v+1;b=v+3
            # Verify actual signed coordinates and parallelogram tests independently.
            self.assertEqual([tuple(s.sign(z) for z in (t-a,t-b)) for t in (a-1,a,a+1,b,b+1)],
                             [(-1,-1),(0,-1),(1,-1),(1,0),(1,1)])
            A=s.Matrix([a,b]); B=s.Matrix([h,a]);
            self.assertEqual(s.solve(s.det(s.Matrix.hstack(A,B)),h),[s.Rational(a*a,b)])
            self.assertEqual(s.solve(A.dot(B),h),[-b])
            for H in [-2*a,2*a,-a,a]:
                Y=s.sqrt(a*a-s.Rational(H*H,4))
                z=s.Rational(H,2)+s.I*Y;w=s.conjugate(z)
                self.assertEqual(s.simplify(z*w),a*a);self.assertEqual(s.simplify(z+w),H)
                self.assertEqual(z==w,abs(H)==2*a)
            self.assertEqual(s.solve(s.Eq(a*a-s.Rational((2*a+1)**2,4),y*y),y),[])

    def test_angle_boundary(self):
        for v in (1,2,3):
            a=v+1; b=a+2; phase=s.pi/[6,4,3][v-1]
            alpha=30*(v+1)
            candidates=[alpha+360*n for n in range(-5,6) if -180<=alpha+360*n<=900]
            self.assertEqual(candidates,[alpha,alpha+360,alpha+720])
            self.assertEqual([T for T in candidates if (s.Rational(T-alpha,2))%360==0],[alpha,alpha+720])
            # The two arctan constraints share one candidate, which belongs to quadrant IV.
            z=(b-1-a)+s.I*(b-1-a)*(-1)
            self.assertEqual(s.arg(z),-s.pi/4)
            self.assertEqual(s.arg((b-1-a)+s.I*(b-1-a)*(-1))!=3*s.pi/4,True)
            # Phase endpoints differ by pi; at zero the two roots differ by pi as well.
            self.assertEqual(s.cos(phase-phase),1);self.assertEqual(s.cos(phase+s.pi-phase),-1)
            roots=[s.Mod(phase+s.pi/2,2*s.pi),s.Mod(phase-s.pi/2,2*s.pi)]
            self.assertNotEqual(*roots);self.assertTrue(all(s.cos(t-phase)==0 for t in roots))

    def test_presentation_delimiters(self):
        r=Resolver(historical_through='bh')
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    p=r._resolve(path,tier,v)['payload']
                    for value in (p['question_latex'],p['final_answer_latex'],*p['worked_solution_latex']):
                        self.assertEqual(value.count('$')%2,0,(path,tier,v,value))

if __name__=='__main__': unittest.main(verbosity=2)
