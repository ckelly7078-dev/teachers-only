import unittest
from knowledge_fm17 import KnowledgeBank, demand_profile
from marking_review import DIMENSIONS, fingerprint
from successor_bq import SuccessorResolver
from mark_routes_fm17b import original_marking_context


class OriginalContextTests(unittest.TestCase):
    def test_context_bound_to_original_guarded_item(self):
        bank = KnowledgeBank.__new__(KnowledgeBank)
        bank.resolver = SuccessorResolver([])
        items = [bank.resolver._resolve('complex-regions',3,v) for v in (1,2,3)]
        item = items[0]; key = item['id']; skill = item['payload']['focus_skill']
        bank.paths = {skill:'complex-regions'}; bank.items = {x['id']:x for x in items}
        bank.profiles = {x['id']:{} for x in items}
        review = {'id':key, 'fingerprint':fingerprint(item), 'reviewer':'fixture', 'review_basis':'individual_item_review',
                  'teacher_approved':False, 'checks':{d:{'decision':'pass','evidence':'fixture'} for d in DIMENSIONS},
                  'allocation':[{'criterion_index':i,'marks':{t:r['marks'] if t==r['type'] else 0 for t in ('M','A','R')},'evidence':'fixture'} for i,r in enumerate(item['payload']['rubric'])]}
        bank.reviews = {key:review}
        result = original_marking_context(bank,key,mode='learning_preview')
        self.assertEqual(sum(c['marks'] for c in result['criteria']),item['marks'])
        self.assertFalse(result['automatic_award']);self.assertFalse(result['release_allowed'])
        self.assertNotIn('source_parts',result)
        result['checks'].clear();self.assertTrue(review['checks'])
        for mode in ('exam_candidate_preview','approved_exam'):
            with self.assertRaises(ValueError): original_marking_context(bank,key,mode=mode)
        review['fingerprint']='stale'
        with self.assertRaises(ValueError): original_marking_context(bank,key,mode='learning_preview')


if __name__ == '__main__': unittest.main()
