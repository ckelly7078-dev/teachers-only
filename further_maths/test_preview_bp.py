import unittest
from active_difficulty import MODES
from preview_bp import PreviewCatalogue
from scope_review_bl import WATCH


class PreviewBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = PreviewCatalogue()
        cls.ids = {mode: cls.catalogue.list_ids(mode=mode) for mode in MODES}

    def test_discovery_counts_and_uniqueness(self):
        self.assertEqual({k: len(v) for k, v in self.ids.items()},
                         {'learning_preview': 1755, 'exam_candidate_preview': 1020,
                          'challenge_preview': 312, 'enrichment_preview': 39, 'approved_exam': 0})
        for ids in self.ids.values():
            self.assertEqual(len(ids), len(set(ids)))

    def test_all_scope_watch_variants_blocked_on_both_paths(self):
        exam_ids = set(self.ids['exam_candidate_preview'])
        learning_ids = set(self.ids['learning_preview'])
        for path, tier in WATCH:
            for variant in (1, 2, 3):
                item_id = f'CAL.{path}.T{tier}.V{variant}'
                self.assertNotIn(item_id, exam_ids)
                self.assertIn(item_id, learning_ids)
                with self.assertRaises(ValueError):
                    self.catalogue.get(item_id, mode='exam_candidate_preview')
                self.assertFalse(self.catalogue.get(item_id, mode='learning_preview')['release_allowed'])

    def test_all_discovered_items_retrieve_with_no_release(self):
        for mode, ids in self.ids.items():
            for item_id in ids:
                result = self.catalogue.get(item_id, mode=mode)
                self.assertEqual(result['item']['id'], item_id)
                self.assertEqual(result['mode'], mode)
                self.assertIs(result['release_allowed'], False)
                self.assertIs(result['exam_ready'], False)
                self.assertIs(result['item']['teacher_approved'], False)

    def test_isolation_and_approved_mode(self):
        for mode in ('challenge_preview', 'enrichment_preview'):
            item = self.ids[mode][0]
            with self.assertRaises(ValueError):
                self.catalogue.get(item, mode='exam_candidate_preview')
        for mode in ('learning_preview', 'exam_candidate_preview', 'challenge_preview', 'enrichment_preview'):
            with self.assertRaises(ValueError):
                self.catalogue.get(self.ids[mode][0], mode='approved_exam')
        for item in self.ids['enrichment_preview']:
            with self.assertRaises(ValueError):
                self.catalogue.get(item, mode='learning_preview')

    def test_invalid_inputs_fail_closed(self):
        item = self.ids['learning_preview'][0]
        for mode in (None, [], 'exam', 'unknown'):
            with self.assertRaises(ValueError):
                self.catalogue.list_ids(mode=mode)
            with self.assertRaises(ValueError):
                self.catalogue.get(item, mode=mode)
        for item_id in (None, [], '', 'CAL.missing.T1.V1', 'CAL.angle-units.T0.V1', 'CAL.angle-units.T1.V4', 'CAL.angle-units.T1.V1\n'):
            with self.assertRaises(ValueError):
                self.catalogue.get(item_id, mode='learning_preview')


if __name__ == '__main__':
    unittest.main()
