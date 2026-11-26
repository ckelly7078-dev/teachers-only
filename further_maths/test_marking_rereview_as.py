import unittest
from active_difficulty import Resolver
from difficulty_revision_as import BANKS, TARGETS, revise
from marking_batch import validate_batch
from marking_pilot_ar import records as prior
from marking_rereview_as import records
from marking_review import fingerprint, inventory_entry


class Tests(unittest.TestCase):
    def test_all_twelve(self):
        result = validate_batch(list(records()))
        self.assertEqual(result['statuses'], {'editorial_review_recorded': 12})
        self.assertEqual(result['teacher_approved'], 0)

    def test_prior_stale(self):
        r = Resolver()
        for record in prior():
            with self.assertRaises(ValueError):
                validate_batch([record], r)

    def test_preservation(self):
        r = Resolver()
        for path, tier in TARGETS:
            for v in (1, 2, 3):
                old = BANKS[path](path, tier, v)
                new = revise(path, tier, v)
                changed = {k for k in old if old[k] != new[k]}
                self.assertEqual(changed, {'rubric', 'likely_mistake'} if path == 'det-two' else {'rubric'})
                self.assertEqual(sum(x['marks'] for x in old['rubric']), 2)
                self.assertEqual(sum(x['marks'] for x in new['rubric']), 2)
                item = r.resolve(path, tier, v, mode='exam_candidate_preview')
                self.assertEqual(item['payload'], new)
                self.assertEqual(inventory_entry(item)['status'], 'typed_provisional')
                self.assertFalse(item['teacher_approved'])

    def test_misconception_and_method(self):
        for v in (1, 2, 3):
            self.assertNotIn('parameter', revise('det-two', 3, v)['likely_mistake'])
            self.assertIn('both signed root-coefficient ratios', revise('root-sum-product', 3, v)['rubric'][0]['criterion'])
            for path, tier in TARGETS:
                rubric = revise(path, tier, v)['rubric']
                self.assertEqual([x['type'] for x in rubric], ['M', 'A'])
                self.assertIn('arithmetic slip', rubric[0]['criterion'])

    def test_out_of_scope(self):
        for path, tier, v in [('det-two', 6, 1), ('unknown', 3, 1), ('det-two', 3, True)]:
            with self.assertRaises(ValueError):
                revise(path, tier, v)


if __name__ == '__main__':
    unittest.main(verbosity=2)
