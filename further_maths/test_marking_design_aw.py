"""AW preservation, routing, exact mathematics and frozen evidence checks."""
import unittest
from active_difficulty import Resolver
from difficulty_revision_aw import BANKS,TARGETS,base,revise
from marking_design_aw import records,PRESERVE
from marking_batch import validate_batch
from marking_review import inventory_entry

class Tests(unittest.TestCase):
    def test_all_variants(self):
        r=Resolver(); self.assertEqual(len(TARGETS),36)
        retained={('cartesian-product',3):'AS',('cartesian-product',4):'AD',('cartesian-product',6):'AN',('complex-division',6):'AD',('cartesian-sums',6):'AG',('conjugate-find',6):'AN'}
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    with self.subTest(path=path,tier=tier,v=v):
                        item=r._resolve(path,tier,v); p=item['payload']
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        self.assertFalse(item['teacher_approved'])
                        if (path,tier) in TARGETS:
                            old=base(path).make(path,tier,v)
                            self.assertEqual(item['revision'],'FM-16AW')
                            self.assertEqual(p,revise(path,tier,v))
                            self.assertEqual(set(old),set(p))
                            self.assertLessEqual({k for k in old if old[k]!=p[k]},{'rubric','worked_solution_latex'})
                            self.assertEqual(item['marks'],sum(row['marks'] for row in old['rubric']))
                        else:
                            self.assertEqual(item['revision'],'FM-16'+retained[path,tier])
    def test_frozen_review_batch(self):
        r=Resolver(); batch=list(records(r)); self.assertEqual(len(batch),123)
        self.assertTrue(all(x['review_basis']=='shared_design_plus_variant_oracle' for x in batch))
        self.assertTrue(all(not x['id'].startswith('CAL.cartesian-product.T3.') for x in batch))
        self.assertEqual(validate_batch(batch,r)['statuses'],{'editorial_review_recorded':123})
    def test_frozen_review_rejects_changed_payload(self):
        r=Resolver(); original=r._resolve
        def changed(path,tier,v):
            i=original(path,tier,v)
            if (path,tier,v)==('identify-components',1,1):i['payload']['likely_mistake']+=' changed'
            return i
        r._resolve=changed
        with self.assertRaisesRegex(ValueError,'frozen batch changed'):list(records(r))
    def test_invalid_targets(self):
        for p,t,v in [('cartesian-product',3,1),('cartesian-sums',6,1),('conjugate-find',6,1),('identify-components',True,1),('identify-components',1,True),('identify-components',1,4),('root-squares',1,1)]:
            with self.assertRaises(ValueError):revise(p,t,v)
    def test_boundary_and_scope(self):
        r=Resolver()
        self.assertEqual(r.scope('conjugate-product',6),'enrichment_only')
        self.assertEqual(r.scope('standard-cartesian',6),'enrichment_only')
        self.assertFalse(r.eligible('conjugate-product',6,'exam_candidate_preview'))
        self.assertIn('h=1',revise('standard-cartesian',6,1)['rubric'][2]['criterion'])
        self.assertIn('negative radii',revise('identify-components',6,1)['rubric'][-1]['criterion'])
        self.assertIn('closed attainable range',revise('conjugate-product',6,1)['rubric'][3]['criterion'])
    def test_presentation_delimiters(self):
        r=Resolver()
        for path in BANKS:
            for tier in range(1,7):
                for v in (1,2,3):
                    p=r._resolve(path,tier,v)['payload']
                    for value in (p['question_latex'],p['final_answer_latex'],*p['worked_solution_latex']):
                        self.assertEqual(value.count('$')%2,0,(path,tier,v,value))

if __name__=='__main__':unittest.main(verbosity=2)
