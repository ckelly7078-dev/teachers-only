import unittest
from foundation.expand import anchors, expected_count

class StructuralTests(unittest.TestCase):
    def test_cover_count(self):
        self.assertEqual(expected_count('Answer all thirty-three questions.'),33)
        self.assertEqual(expected_count('Answer all sixteen questions.'),16)
        self.assertIsNone(expected_count('No count given.'))
    def test_marked_parts(self):
        r=anchors(['Cover','   1    (a) sample [2]\n        (b) sample [1]\n   2    sample [3]'])
        self.assertEqual(sum(sum(x['marks']) for x in r.values()),6)
        self.assertEqual(r[(1,'a')]['marks'],[2])
        self.assertEqual(r[(2,'')]['marks'],[3])
    def test_scheme_codes_are_candidates_not_totals(self):
        r=anchors(['Cover','1    (a) Example M1 A1\n      Alternative MA2'],True)
        self.assertEqual(r[(1,'a')]['codes'],['M1','A1','MA2'])
        self.assertEqual(r[(1,'a')]['marks'],[])
if __name__=='__main__': unittest.main()
