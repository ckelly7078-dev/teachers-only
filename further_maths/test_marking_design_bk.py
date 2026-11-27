"""Test BK explicit successors, mathematical invariants, and fail-closed evidence."""
import copy
import unittest
import sympy as s
from active_difficulty import Resolver,MARK_SUCCESSIONS
from difficulty_revision_bk import TARGETS,NEW_DEMAND,revise
from difficulty_revision_bk_oracle import check
from marking_design_bk import records
from marking_batch import validate_batch
from marking_review import fingerprint,inventory_entry

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.old=Resolver(historical_through='bj');cls.r=Resolver()
    def test_every_variant(self):
        self.assertEqual(len(TARGETS),32);self.assertEqual(len(NEW_DEMAND),13)
        for p,t in TARGETS:
            for v in (1,2,3):
                old=self.old._resolve(p,t,v);new=self.r._resolve(p,t,v);d=new['payload']
                self.assertEqual(old['revision'],'FM-16'+TARGETS[p,t].upper());self.assertEqual(new['revision'],'FM-16BK')
                self.assertEqual((old['marks'],new['marks']),MARK_SUCCESSIONS[p,t,'bk']);self.assertEqual(old['scope'],new['scope']);self.assertEqual(old['id'],new['id'])
                self.assertEqual(inventory_entry(new)['status'],'typed_provisional');self.assertTrue(check(d))
                self.assertEqual(set(old['payload']),set(d))
                for k in ('path','tier','variant','focus_skill','origin','examination_source','assessment_role','difficulty_status'):
                    self.assertEqual(d[k],old['payload'][k])
                for val in (d['question_latex'],d['final_answer_latex'],*d['worked_solution_latex']):self.assertEqual(val.count('$')%2,0)
                if (p,t) not in NEW_DEMAND:
                    for k in ('question_latex','final_answer_latex','facts'):self.assertEqual(d[k],old['payload'][k])
                else:self.assertNotEqual(d['question_latex'],old['payload']['question_latex'])
    def test_frozen_records(self):
        batch=list(records(self.r));self.assertEqual(len(batch),96);self.assertEqual(validate_batch(batch,self.r)['statuses'],{'editorial_review_recorded':96})
        for row in batch:
            _,p,t,v=row['id'].split('.');old=self.old._resolve(p,int(t[1:]),int(v[1:]))
            self.assertEqual(row['supersedes_fingerprint'],fingerprint(old))
        with self.assertRaisesRegex(ValueError,'Stale'):validate_batch([batch[0]],self.old)
    def test_historical_closed(self):
        with self.assertRaisesRegex(ValueError,'Historical'):self.old.resolve('polar-geometry',3,1,mode='learning_preview')
        self.assertEqual(self.r.resolve('polar-geometry',3,1,mode='learning_preview')['revision'],'FM-16BK')
        with self.assertRaises(ValueError):self.r.resolve('polar-geometry',3,1,mode='approved_exam')
    def test_invalid_targets(self):
        for p,t,v in [('polar-geometry',3,True),('polar-geometry',3,4),('polar-geometry',3.0,1),('polar-geometry',2,1)]:
            with self.assertRaises(ValueError):revise(p,t,v)
    def test_positive_ray(self):
        for v in (1,2,3):
            d=revise('locus-intersection',5,v);d['facts'][0]=str(-s.sympify(d['facts'][0]));self.assertFalse(check(d))
    def test_parameter_branches(self):
        for p in ('symmetric-parameter','plane-cartesian','exact-radians'):
            tier=4 if p=='symmetric-parameter' else 5
            for v in (1,2,3):
                d=revise(p,tier,v);d['facts'][0]=str(s.sympify(d['facts'][0])+1);self.assertFalse(check(d))
    def test_missing_component_and_opposite(self):
        for p in ('vector-components','unit-vector'):
            for v in (1,2,3):
                d=revise(p,5,v);d['facts'][1]=copy.deepcopy(d['facts'][0]);self.assertFalse(check(d))
    def test_mutation_and_marks(self):
        for p,t in TARGETS:
            a=self.r._resolve(p,t,1);old=copy.deepcopy(a);a['payload']['rubric'][0]['marks']+=1
            self.assertFalse(check(a['payload']));self.assertEqual(old,self.r._resolve(p,t,1))

if __name__=='__main__':unittest.main(verbosity=2)
