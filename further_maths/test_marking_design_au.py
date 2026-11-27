"""Check all variants of explicitly reviewed AU marking designs."""
import unittest
from active_difficulty import Resolver
from difficulty_revision_au import TARGETS,base,revise
from difficulty_revision_au_oracle import check
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver();self.assertEqual(len(TARGETS),54)
        for path,tier in TARGETS:
            for v in (1,2,3):
                with self.subTest(path=path,tier=tier,v=v):
                    old=base(path).make(path,tier,v);new=revise(path,tier,v)
                    self.assertTrue(check(new))
                    self.assertLessEqual({k for k in old if old[k]!=new[k]}, {'rubric','likely_mistake','worked_solution_latex'})
                    item=r._resolve(path,tier,v);self.assertEqual(item['payload'],new)
                    self.assertEqual(item['marks'],sum(x['marks'] for x in old['rubric']))
                    self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                    self.assertFalse(item['teacher_approved'])
    def test_prior_layers_unchanged(self):
        r=Resolver()
        for path,tier,tag in [('root-sum-product',3,'AS'),('scaled-roots',4,'AF')]:
            self.assertNotIn((path,tier),TARGETS)
            for v in (1,2,3):self.assertEqual(r._resolve(path,tier,v)['revision'],'FM-16'+tag)
    def test_flagged_amendments(self):
        for v in (1,2,3):
            self.assertIn('cross term',revise('factor-connection',3,v)['likely_mistake'])
            self.assertIn('nonzero',revise('reciprocal',3,v)['worked_solution_latex'][0])
            self.assertIn('square-sum identity',revise('root-squares',3,v)['rubric'][0]['criterion'])
            self.assertIn('expanding the shifted product',revise('shifted-roots',3,v)['worked_solution_latex'][0])
    def test_invalid_target(self):
        for p,t,v in [('root-sum-product',3,1),('scaled-roots',4,1),('root-squares',5,1),('root-squares',1,True)]:
            with self.assertRaises(ValueError):revise(p,t,v)

if __name__=='__main__':unittest.main(verbosity=2)
