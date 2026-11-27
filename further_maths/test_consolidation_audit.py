"""Test scope locators and conservative mark-screen semantics."""
import unittest
from consolidation_audit import OUTCOMES, mark_transition
from skill_detail import detail_map


class Tests(unittest.TestCase):
    def test_concept_coverage(self):
        self.assertEqual(set(OUTCOMES), set(detail_map()))
        self.assertEqual(len(OUTCOMES), 41)
        self.assertEqual(len(set(OUTCOMES.values())), 41)

    def test_transitions(self):
        self.assertEqual(mark_transition([2, 2, 2], [3, 3, 3]), 'strictly_higher_marks')
        self.assertEqual(mark_transition([2, 2, 2], [2, 2, 2]), 'touching_marks')
        self.assertEqual(mark_transition([3, 3, 3], [2, 2, 2]), 'lower_or_overlap_marks')
        self.assertEqual(mark_transition([2, 3, 4], [3, 4, 5]), 'lower_or_overlap_marks')

    def test_reject_invalid_mark_inputs(self):
        for left, right in (([1, 2], [3, 3, 3]), ([True, 2, 3], [3, 3, 3]),
                            ([0, 1, 2], [3, 3, 3]), ([1, 2, 3], [3, 3, 2.5])):
            with self.assertRaises(ValueError):
                mark_transition(left, right)


if __name__ == '__main__':
    unittest.main(verbosity=2)
