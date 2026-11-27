import copy,unittest
import sympy as s
from active_difficulty import Resolver,MARK_SUCCESSIONS
from difficulty_revision_bl import TARGETS,NEW_DEMAND,revise
from difficulty_revision_bl_oracle import check
from marking_design_bl import records
from marking_review import fingerprint
from marking_batch import validate_batch
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver();cls.old=Resolver(historical_through='bk')
    def test_all_variants(self):
        self.assertEqual(len(TARGETS),11);self.assertEqual(len(NEW_DEMAND),5)
        for p,t in TARGETS:
            for v in (1,2,3):
                a=self.old._resolve(p,t,v);b=self.r._resolve(p,t,v);self.assertEqual(b['revision'],'FM-16BL');self.assertEqual(a['scope'],b['scope']);self.assertEqual((a['marks'],b['marks']),MARK_SUCCESSIONS[p,t,'bl']);self.assertTrue(check(b['payload']))
                if (p,t) not in NEW_DEMAND:self.assertEqual({k for k in a['payload'] if a['payload'][k]!=b['payload'][k]},{'rubric'})
                else:self.assertNotEqual(a['payload']['question_latex'],b['payload']['question_latex'])
    def test_ledger(self):
        batch=list(records(self.r));self.assertEqual(validate_batch(batch,self.r)['statuses'],{'editorial_review_recorded':33})
        for row in batch:
            _,p,t,v=row['id'].split('.');self.assertEqual(row['supersedes_fingerprint'],fingerprint(self.old._resolve(p,int(t[1:]),int(v[1:]))))
        with self.assertRaises(ValueError):validate_batch(batch,self.old)
    def test_mutated_facts(self):
        for p,t in NEW_DEMAND:
            a=revise(p,t,1);a['facts'][0]=copy.deepcopy(a['facts'][0]);
            if isinstance(a['facts'][0],dict):a['facts'][0]['matrix'][0][0]='999'
            else:a['facts'][0]='999'
            self.assertFalse(check(a))
    def test_locus_thresholds(self):
        k=s.Symbol('k')
        for v in (1,2,3):
            lo,hi,D=map(s.sympify,revise('locus-intersection',6,v)['facts'][:3]);self.assertEqual(s.simplify(D.subs(k,lo)),0);self.assertEqual(s.simplify(D.subs(k,hi)),0);self.assertTrue(D.subs(k,v+1)>0);self.assertTrue(s.simplify(D.subs(k,hi+1))<0)
    def test_system_rank(self):
        for v in (1,2,3):
            H=v+1+v+3;A=s.Matrix([[1,1,0],[0,1,1],[1,2,1]]);self.assertEqual(A.rank(),2);self.assertEqual(A.row_join(s.Matrix([v+1,v+3,H])).rank(),2);self.assertEqual(A.row_join(s.Matrix([v+1,v+3,H+1])).rank(),3)
    def test_distance_level(self):
        for v in (1,2,3):
            D=s.sympify(revise('point-line',6,v)['facts'][1]);t=s.Symbol('t',real=True);f=(t-2*v-2)**2+t*t+(v+3)**2
            for h,n in ((D-1,0),(D,1),(D+2,2)):self.assertEqual(len(s.solveset(f-h,t,domain=s.S.Reals)),n)
    def test_invalid_target(self):
        with self.assertRaises(ValueError):revise('inverse-three',5,True)
if __name__=='__main__':unittest.main(verbosity=2)
