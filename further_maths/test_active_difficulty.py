"""Source-free regression tests for resolver routing and selection safeguards."""
import unittest
from active_difficulty import Resolver, MODES


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Resolver()

    def test_registry(self):
        self.assertEqual(len(self.r.bases), 117)
        self.assertEqual(len(self.r.overlays), 702)
        self.assertEqual(set(self.r.reviews), set(self.r.bases))

    def test_all_modes(self):
        counts = {m: 0 for m in MODES}
        for path in self.r.bases:
            for tier in range(1, 7):
                for mode in MODES:
                    counts[mode] += self.r.eligible(path, tier, mode)
                self.assertEqual(self.r.eligible(path, tier, 'exam_candidate_preview'), tier in (3, 4, 5))
                self.assertFalse(self.r.eligible(path, tier, 'approved_exam'))
        self.assertEqual(counts, {'learning_preview': 585, 'exam_candidate_preview': 351, 'challenge_preview': 104, 'enrichment_preview': 13, 'approved_exam': 0})

    def test_revisions(self):
        for path, tier, tag in [('complex-division',6,'BK'), ('composition-order',6,'AE'), ('scaled-roots',4,'AF'), ('cartesian-sums',6,'AG'), ('modulus-constraints',6,'AH'), ('collapse',6,'AI'), ('inverse-two',6,'BN5'), ('cross-product',6,'AK'), ('skew',6,'BN9'), ('polar-products',5,'BM4'), ('conjugate-find',6,'AN'), ('cartesian-product',6,'AN'), ('line-plane-angle',6,'BN9'), ('perpendicular-parameter',6,'BN9'), ('scalar-product',6,'BN9'), ('triangle-area',6,'BN9'), ('singular-condition',6,'AP'), ('justify-skew',6,'BN9'), ('line-line-distance',6,'BN9'), ('plane-intersection-direction',6,'BN9'), ('root-sum-product',3,'AS'), ('cartesian-product',3,'BM4'), ('det-two',3,'AS'), ('scalar-product',3,'AS'), ('root-squares',3,'AU'), ('root-squares',5,'AV'), ('combined-roots',6,'AV')]:
            mode = 'challenge_preview' if tier == 6 else 'exam_candidate_preview'
            item = self.r.resolve(path,tier,1,mode=mode)
            self.assertEqual(item['revision'], 'FM-16'+tag)
            self.assertFalse(item['teacher_approved'])
            self.assertEqual(item['id'], f'CAL.{path}.T{tier}.V1')

    def test_enrichment_isolation(self):
        for mode in MODES:
            if mode == 'enrichment_preview':
                self.assertEqual(self.r.resolve('angle-units',6,1,mode=mode)['scope'], 'enrichment_only')
            else:
                with self.assertRaises(ValueError): self.r.resolve('angle-units',6,1,mode=mode)

    def test_reject_invalid_requests(self):
        for path,tier,v,mode in [('unknown',3,1,'learning_preview'), ('skew',0,1,'learning_preview'), ('skew',True,1,'learning_preview'), ('skew',3,4,'learning_preview'), ('skew',3,True,'learning_preview'), ('skew',3,1,'unknown'), ('skew',3,1,'approved_exam'), ('skew',1,1,'exam_candidate_preview'), ('skew',2,1,'exam_candidate_preview'), ('skew',6,1,'exam_candidate_preview')]:
            with self.assertRaises(ValueError): self.r.resolve(path,tier,v,mode=mode)
        with self.assertRaises(TypeError): self.r.resolve('skew',3,1)

    def test_no_shared_payload(self):
        first = self.r.resolve('skew',3,1,mode='exam_candidate_preview')
        first['payload']['facts'].clear()
        second = self.r.resolve('skew',3,1,mode='exam_candidate_preview')
        self.assertTrue(second['payload']['facts'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
