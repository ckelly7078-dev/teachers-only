"""Source-free synthetic tests for the FM-17I tier adapter."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from marking_review import fingerprint
from profile_marking_fm17i import TierMarking, tier_matches


class TierTests(unittest.TestCase):
    def setUp(self):
        self.item = dict(id='fixture', revision='test', scope='test', marks=3,
                         payload=dict(tier=4, rubric=[dict(type='M', marks=2), dict(type='A', marks=1)]))
        self.fp = fingerprint(self.item)
        self.row = dict(id='fixture', revision='test', tier=4, fingerprint=self.fp,
                        basis='independent_prompt_observations', criteria=[dict(index=2, type='A', marks=1,
                                                                                  rule='equal', expected='2/3')])
        self.engine = SimpleNamespace(bank=SimpleNamespace(items={'fixture': self.item}), marking_context=self.context)
        self.prior = SimpleNamespace(capability=self.capability, check_work=lambda *a, **kw: 'delegated')

    def context(self, item_id, *, mode, item_fingerprint):
        if item_id != 'fixture' or mode != 'learning_preview' or item_fingerprint != self.fp:
            raise ValueError('Invalid context')
        return dict(id=item_id, fingerprint=self.fp, marks=3, automatic_award=False, release_allowed=False,
                    criteria=[dict(id='c1', type='M', marks=2), dict(id='c2', type='A', marks=1)])

    def capability(self, *a, **kw):
        self.context(*a, **kw)
        return dict(structured_checks_available=False)

    def marker(self, records=None):
        return TierMarking(self.engine, self.prior, [self.row] if records is None else records)

    def run_work(self, value, marker=None, **kwargs):
        args = dict(mode='learning_preview', item_fingerprint=self.fp, work={'c2': value})
        args.update(kwargs)
        return (marker or self.marker()).check_work('fixture', **args)

    def test_correct_wrong_uncertain_and_flags(self):
        for value, bounds in [('4/6', [1, 3]), ('-2/3', [0, 2]), (None, [0, 3])]:
            result = self.run_work(value)
            self.assertEqual(result['possible_total'], bounds)
            self.assertEqual(result['criteria'][0]['status'], 'uncertain')
            for flag in ('automatic_award', 'teacher_approved', 'release_allowed'):
                self.assertFalse(result[flag])

    def test_capability_and_delegation(self):
        args = dict(mode='learning_preview', item_fingerprint=self.fp)
        result = self.marker().capability('fixture', **args)
        self.assertEqual((result['coverage'], result['checked_criteria']), ('partial', ['c2']))
        self.assertNotIn('expected', result)
        self.assertEqual(self.marker([]).capability('fixture', **args)['coverage'], 'none')
        self.assertEqual(self.run_work(None, marker=self.marker([])), 'delegated')

    def test_invalid_work_fails_closed(self):
        for kwargs in [dict(item_fingerprint='stale'), dict(mode='approved_exam'), dict(work={}),
                       dict(work={'c1': None, 'c2': '2/3'}), dict(work={'c2': 'eval()'})]:
            with self.assertRaises(ValueError):
                self.run_work(None, **kwargs)

    def test_invalid_records_and_copy(self):
        for field, value in [('index', 1), ('marks', 2), ('type', 'M'), ('rule', 'unknown')]:
            row = copy.deepcopy(self.row)
            row['criteria'][0][field] = value
            with self.assertRaises(ValueError):
                self.marker([row])
        with self.assertRaises(ValueError):
            self.marker([self.row, self.row])
        marker = self.marker()
        self.row['criteria'][0]['expected'] = '9'
        self.assertEqual(self.run_work('2/3', marker=marker)['possible_total'], [1, 3])

    def test_manifest_tamper_and_count(self):
        with tempfile.TemporaryDirectory() as tmp, patch('profile_marking_fm17i.ProfileMarking.from_bundle', return_value=self.prior):
            folder = Path(tmp)/'FM17I'
            folder.mkdir()
            file = folder/'profiles.jsonl'
            file.write_text(json.dumps(self.row)+'\n')
            mf = folder/'runtime-manifest.json'
            record = dict(checkpoint='FM-17I', profile_count=1, sha256={'profiles.jsonl': hashlib.sha256(file.read_bytes()).hexdigest()})
            mf.write_text(json.dumps(record))
            self.assertEqual(self.run_work('2/3', marker=TierMarking.from_bundle(self.engine, tmp))['possible_total'], [1, 3])
            mf.write_text(json.dumps(dict(record, profile_count=2)))
            with self.assertRaises(ValueError):
                TierMarking.from_bundle(self.engine, tmp)
            mf.write_text(json.dumps(record))
            file.write_text('{}\n')
            with self.assertRaises(ValueError):
                TierMarking.from_bundle(self.engine, tmp)

    def test_exact_sets_and_equivalent_geometry(self):
        target = ['2', ['complex', '0', '1']]
        self.assertTrue(tier_matches('unordered', list(reversed(target)), target))
        self.assertFalse(tier_matches('unordered', ['2', '2'], target))
        with self.assertRaises(ValueError):
            tier_matches('unordered', [None, '2'], target)
        self.assertTrue(tier_matches('equal', {'radical_terms': [['1', '8']]}, {'radical_terms': [['2', '2']]}))
        self.assertTrue(tier_matches('proportional', ['-2', '4', '6'], ['1', '-2', '-3']))
        self.assertFalse(tier_matches('proportional', ['0', '0', '0'], ['1', '-2', '-3']))
        self.assertTrue(tier_matches('line', [['3', '5'], ['-2', '-4'], 'all_real'], [['1', '1'], ['1', '2'], 'all_real']))


if __name__ == '__main__':
    unittest.main()
