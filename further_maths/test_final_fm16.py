import copy
import unittest
from final_fm16 import FinalResolver, TARGETS, REVISION, check, replacement
from successor_bq import SuccessorResolver
from marking_review import fingerprint
from readiness_bo import conservative_preview_eligible
from scope_review_bl import WATCH

class FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=SuccessorResolver([]); cls.new=FinalResolver([])

    def test_successor_and_preserved_roles(self):
        for v in (1,2,3):
            a=self.old._resolve('invariant-lines',5,v); b=self.new._resolve('invariant-lines',5,v)
            self.assertIn(b['id'],TARGETS);self.assertEqual(b['revision'],REVISION)
            self.assertEqual((a['marks'],b['marks']),(3,5));self.assertNotEqual(fingerprint(a),fingerprint(b))
            self.assertEqual(a['scope'],b['scope']);self.assertFalse(b['teacher_approved']);self.assertTrue(check(b))
            for k in ('path','focus_skill','assessment_role','origin','tier','variant','examination_source'):
                self.assertEqual(a['payload'][k],b['payload'][k])
            with self.assertRaises(ValueError): replacement(b)

    def test_wrong_predecessor_and_facts(self):
        a=self.old._resolve('invariant-lines',5,1);a['payload']['facts']=[]
        with self.assertRaises(ValueError): replacement(a)
        b=self.new._resolve('invariant-lines',5,1)
        for key,value in [('vertical_invariant',True),('pointwise_fixed','all'),('determinant',0)]:
            bad=copy.deepcopy(b);bad['payload']['facts'][key]=value
            with self.assertRaises(ValueError): check(bad)

    def test_untargeted_and_guard(self):
        for t in (1,2,3,4,6):
            for v in (1,2,3): self.assertEqual(self.old._resolve('invariant-lines',t,v),self.new._resolve('invariant-lines',t,v))
        for p,t in WATCH:
            self.assertTrue(conservative_preview_eligible(self.new,p,t,'learning_preview'))
            self.assertFalse(conservative_preview_eligible(self.new,p,t,'exam_candidate_preview'))
        self.assertFalse(conservative_preview_eligible(self.new,'invariant-lines',5,'approved_exam'))
