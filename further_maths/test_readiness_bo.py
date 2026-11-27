import unittest
from active_difficulty import Resolver, MODES
from readiness_bo import conservative_preview_eligible, conservative_preview_resolve, index
from scope_review_bl import WATCH

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=Resolver()

    def test_all_preview_modes(self):
        counts={mode:0 for mode in MODES}
        for p in self.r.bases:
            for t in range(1,7):
                for mode in MODES:
                    yes=conservative_preview_eligible(self.r,p,t,mode)
                    self.assertFalse(yes and not self.r.eligible(p,t,mode))
                    counts[mode]+=3*yes
        self.assertEqual(counts,{'learning_preview':1755,'exam_candidate_preview':1020,'challenge_preview':312,'enrichment_preview':39,'approved_exam':0})

    def test_scope_watch_and_approved_blocked(self):
        for path,tier in WATCH:
            with self.assertRaises(ValueError):
                conservative_preview_resolve(self.r,path,tier,1,mode='exam_candidate_preview')
            self.assertTrue(conservative_preview_eligible(self.r,path,tier,'learning_preview'))
        with self.assertRaises(ValueError):
            conservative_preview_resolve(self.r,'complex-regions',3,1,mode='approved_exam')

    def test_valid_preview_and_bad_input(self):
        p=next(p for p in self.r.bases if self.r.eligible(p,3,'exam_candidate_preview') and (p,3) not in WATCH)
        item=conservative_preview_resolve(self.r,p,3,1,mode='exam_candidate_preview')
        self.assertFalse(item['teacher_approved'])
        for path,tier,mode in [(p,3,'unknown'),(p,0,'learning_preview'),('missing',3,'learning_preview')]:
            with self.assertRaises(ValueError):
                conservative_preview_eligible(self.r,path,tier,mode)

    def test_duplicate_record(self):
        with self.assertRaises(ValueError):
            index([{'id':'x'},{'id':'x'}])

if __name__=='__main__':unittest.main(verbosity=2)
