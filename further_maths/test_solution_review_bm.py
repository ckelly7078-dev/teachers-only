"""Tests of the read-only reference-rendering screen and its evidence limits."""
import unittest
from active_difficulty import Resolver
from solution_review_bm import split_math, tex_text, log_flags, proof, screen


class TestSolutionScreen(unittest.TestCase):
    def test_literal_notation_preserved(self):
        self.assertEqual(tex_text('a^2 < 4; $x^2$'), r'a\textasciicircum{}2 \textless{} 4; $x^2$')
        self.assertEqual(tex_text(r'\input{test}'), r'\textbackslash{}input\{test\}')

    def test_reject_unsafe_or_invalid_math(self):
        for text in ('$x', '$$', r'$\input{test}$', r'$x\$y$', r'$x&y$', r'$x\%y$'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                split_math(text)

    def test_log_flags_bind_item(self):
        log = 'FMITEM:CAL.root-squares.T1.V1\nOverfull \\hbox (2pt too wide)\nFMITEM:CAL.root-squares.T1.V2\nMissing character: x\n'
        seen, flags = log_flags(log)
        self.assertEqual(seen, ['CAL.root-squares.T1.V1', 'CAL.root-squares.T1.V2'])
        self.assertEqual(len(flags[seen[0]]), 1)
        self.assertEqual(len(flags[seen[1]]), 1)

    def test_record_is_not_certification(self):
        r = Resolver()
        item = r._resolve('root-squares', 2, 1)
        rec = screen(item)
        self.assertIn('plain_power', rec['plain_notation_signals']['step_2'])
        self.assertTrue(rec['oracle_checked'])
        self.assertFalse(rec['individual_solution_certified'])
        self.assertFalse(rec['visual_certified'])
        self.assertFalse(rec['exam_ready'])
        tex, rows = proof([item])
        self.assertIn('FMITEM:' + item['id'], tex)
        self.assertEqual(rows[0]['expected_page'], 1)
        self.assertEqual(rows[0]['fingerprint'], rec['fingerprint'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
