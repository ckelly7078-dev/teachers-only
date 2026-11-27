"""Check preservation and exact mathematics of all 84 advanced algebra variants."""
import unittest
from active_difficulty import Resolver
from difficulty_revision_av import BANKS,TARGETS,base,revise
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver();self.assertEqual(len(TARGETS),26)
        for path in BANKS:
            for tier in (5,6):
                for v in (1,2,3):
                    with self.subTest(path=path,tier=tier,v=v):
                        item=r._resolve(path,tier,v);p=item['payload']
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        self.assertFalse(item["teacher_approved"])
                        if (path,tier) in TARGETS:
                            old=base(path).make(path,tier,v)
                            self.assertEqual(p,revise(path,tier,v))
                            self.assertLessEqual({k for k in old if old[k]!=p[k]},{'rubric','worked_solution_latex'})
                            self.assertEqual(item['marks'],sum(x['marks'] for x in old['rubric']))
                        else:self.assertEqual(item['revision'],'FM-16AF')
    def test_scope_unchanged(self):
        r=Resolver();self.assertEqual(r.scope('reciprocal',6),'enrichment_only');self.assertEqual(r.scope('cube-sums',6),'enrichment_only')
        self.assertFalse(r.eligible('reciprocal',6,'exam_candidate_preview'))
    def test_invalid_target(self):
        for p,t,v in [('reciprocal',6,1),('root-squares',6,1),('cube-sums',4,1),('cube-sums',5,True)]:
            with self.assertRaises(ValueError):revise(p,t,v)
    def test_boundary_criteria(self):
        self.assertIn('zero',revise('shifted-products',6,1)['rubric'][1]['criterion'].replace('k=0','zero'))
        self.assertIn('denominator sign',revise('root-ratios',6,1)['rubric'][1]['criterion'])
        self.assertIn('equal-magnitude',revise('squared-roots',6,1)['rubric'][-1]['criterion'])
if __name__=='__main__':unittest.main(verbosity=2)
