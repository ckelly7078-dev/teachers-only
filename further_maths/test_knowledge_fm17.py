import unittest
from knowledge_fm17 import KnowledgeBank, printed_codes, demand_profile
from active_difficulty import Resolver
from marking_review import fingerprint, DIMENSIONS


class KnowledgeTests(unittest.TestCase):
    def test_printed_codes_are_not_original_codes(self):
        self.assertEqual(printed_codes('M1 MW2 W1',4), [
            {'code':'M','marks':1,'meaning':'method'},
            {'code':'MW','marks':2,'meaning':'combined_method_and_working'},
            {'code':'W','marks':1,'meaning':'working'}])
        for text,n in [('M1 A1',2),('MW0',0),('M1 W1',3),('',0)]:
            with self.assertRaises(ValueError): printed_codes(text,n)

    def test_profile_bound_to_current_rubric(self):
        item = Resolver()._resolve('angle-units',1,1)
        review = {'id':item['id'],'fingerprint':fingerprint(item),'reviewer':'fixture',
            'review_basis':'individual_item_review','teacher_approved':False,
            'checks':{d:{'decision':'pass','evidence':'fixture'} for d in DIMENSIONS},
            'allocation':[{'criterion_index':i,'marks':{t:r['marks'] if r['type']==t else 0 for t in ('M','A','R')},'evidence':'fixture'} for i,r in enumerate(item['payload']['rubric'])]}
        p = demand_profile(item,review)
        self.assertEqual(sum(p['criterion_marks'].values()),item['marks'])
        self.assertEqual(p['difficulty_basis'],'editorial_not_empirical')
        with self.assertRaises(ValueError): demand_profile(item,{**review,'fingerprint':'stale'})

    def test_guarded_selection_no_private_context(self):
        from successor_bq import SuccessorResolver
        b = KnowledgeBank.__new__(KnowledgeBank); b.resolver = SuccessorResolver([])
        item = b.resolver._resolve('complex-regions',3,1); skill = item['payload']['focus_skill']
        b.paths = {skill:'complex-regions'}
        b.items = {i['id']:i for i in [b.resolver._resolve('complex-regions',3,v) for v in (1,2,3)]}
        b.profiles = {key:{} for key in b.items}
        self.assertEqual(b.select(skill,3,mode='exam_candidate_preview'),[])
        self.assertEqual(b.select(skill,3,mode='approved_exam'),[])
        result = b.select(skill,3,mode='learning_preview')
        self.assertEqual(len(result),3); self.assertFalse(result[0]['release_allowed'])
        self.assertNotIn('source_parts',result[0]); result[0]['item']['payload']['facts'].clear()
        self.assertTrue(b.items[result[0]['item']['id']]['payload']['facts'])
        with self.assertRaises(ValueError): b.select(skill,True,mode='learning_preview')


if __name__ == '__main__': unittest.main()
