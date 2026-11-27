import json
import tempfile
import unittest
from pathlib import Path
from active_difficulty import Resolver
from marking_review import fingerprint
from review_service_bq import CHECKS, save_review
from review_progress_br import observation_rows, reconcile


class ProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resolver = Resolver()
        cls.item = resolver._resolve('angle-units', 1, 1)
        cls.watch = resolver._resolve('complex-regions', 3, 1)
        cls.key = cls.item['id']; cls.items = {x['id']: x for x in (cls.item, cls.watch)}
        cls.proof = 'a' * 64

    def row(self, seq, actor, visual='not_reviewed', **overrides):
        return dict(seq=seq, actor=actor, item_id=self.key, fingerprint=fingerprint(self.item), revision=self.item['revision'],
                    proof_sha256=self.proof, checks=json.dumps({c: visual if c == 'visual' else 'not_reviewed' for c in CHECKS}), note='Fictional test only') | overrides

    def report(self, rows=(), calibration=()):
        return reconcile(self.items, self.proof, rows, calibration, minimum_attempts=20)

    def test_empty_and_scope_priority(self):
        r = self.report(); self.assertEqual(r['items'], 2); self.assertEqual(r['scope_watches'], 1)
        self.assertEqual(r['items_by_priority'][0]['id'], self.watch['id']); self.assertEqual(r['observation_counts']['visual']['not_reviewed'], 2)
        self.assertFalse(r['fm17_ready']); self.assertEqual(r['teacher_approved'], 0)

    def test_stale_and_conflicting_reviews(self):
        r = self.report([self.row(1, 'a', 'pass'), self.row(2, 'b', 'revise'), self.row(3, 'c', 'pass', proof_sha256='b'*64)])
        self.assertEqual(r['stale_observations'], 1); self.assertEqual(r['observation_counts']['visual']['conflict'], 1)
        self.assertEqual(r['items_by_priority'][0]['id'], self.key); self.assertFalse(r['release_allowed'])

    def test_latest_explicit_decision_per_actor(self):
        r = self.report([self.row(1, 'a', 'revise'), self.row(2, 'a', 'pass'), self.row(3, 'a')])
        self.assertEqual(r['observation_counts']['visual']['pass'], 1)
        self.assertEqual(r['all_checks_pass_observations'], 0)

    def test_invalid_and_duplicate_rows(self):
        for rows in ([self.row(1, 'a'), self.row(1, 'b')], [self.row(1, 'a', 'approved')], [self.row(1, 'a', 'pass', note='')]):
            with self.assertRaises(ValueError): self.report(rows)

    def test_calibration_blank_real_and_stale(self):
        row = {'id': self.key, 'fingerprint': fingerprint(self.item), 'marks': 1, 'counts': [None, None]}
        r = self.report(calibration=[row]); self.assertEqual(r['calibration_blank_templates'], 1); self.assertEqual(r['calibration_histograms_received'], 0)
        r = self.report(calibration=[row | {'counts': [5, 15]}]); self.assertEqual(r['calibration_minimum_attempts_met'], 1)
        self.assertFalse(r['fm17_ready']); self.assertEqual(r['teacher_approved'], 0)
        for rows in ([row, row], [row | {'fingerprint': '0'*64}], [row | {'counts': [None, 20]}]):
            with self.assertRaises(ValueError): self.report(calibration=rows)

    def test_read_only_real_ledger_schema(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'observations.sqlite'
            item = {'item': self.item, 'fingerprint': fingerprint(self.item), 'proof_sha256': self.proof}
            data = {'id': self.key, 'mode': 'learning_preview', 'fingerprint': fingerprint(self.item), 'proof_sha256': self.proof,
                    'checks': {c: 'pass' for c in CHECKS}, 'note': 'Fictional fixture only'}
            save_review(path, 'test-actor', item, data)
            before = path.read_bytes(); report = self.report(observation_rows(path)); self.assertEqual(path.read_bytes(), before)
            self.assertEqual(report['all_checks_pass_observations'], 1); self.assertEqual(report['teacher_approved'], 0)
            with self.assertRaises(ValueError): observation_rows(Path(d) / 'missing.sqlite')


if __name__ == '__main__':
    unittest.main()
