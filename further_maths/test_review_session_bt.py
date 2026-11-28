import base64
import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from urllib.parse import urlencode

from active_difficulty import Resolver, require
from marking_review import fingerprint
from review_service_bq import application, credentials, save_review, CHECKS, mount_as1
from review_session_bt import actor_progress


class Catalogue:
    def __init__(self):
        r = Resolver()
        self.items = {i['id']: i for i in (r._resolve('angle-units', 1, 1),
                       r._resolve('complex-regions', 3, 1), r._resolve('angle-units', 3, 1))}
        self.pages = {k: {'fingerprint': fingerprint(i), 'revision': i['revision']} for k, i in self.items.items()}
        self.proof_sha256 = 'a' * 64
        self.bridge, self.watch, self.candidate = self.items

    def list_ids(self, mode):
        require(mode in ('learning_preview', 'exam_candidate_preview', 'approved_exam'), 'Invalid mode')
        return list(self.items) if mode == 'learning_preview' else [self.candidate] if mode == 'exam_candidate_preview' else []

    def get(self, key, mode):
        require(key in self.list_ids(mode), 'Ineligible')
        return {'item': self.items[key], 'fingerprint': self.pages[key]['fingerprint'], 'proof_sha256': self.proof_sha256}


class ActorProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = Catalogue()
        cls.users = [credentials(name, 'fixture-password') for name in ('Teacher-A', 'Teacher-B')]

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Path(directory.name) / 'observations.sqlite'

    def save(self, actor, key, **checks):
        item = self.cat.get(key, 'learning_preview')
        data = {'id': key, 'mode': 'learning_preview', 'fingerprint': item['fingerprint'],
                'proof_sha256': item['proof_sha256'], 'checks': dict.fromkeys(CHECKS, 'not_reviewed') | checks,
                'note': 'Disposable fictional observation.'}
        save_review(self.db, actor, item, data)

    def progress(self, actor='Teacher-A', mode='learning_preview'):
        return actor_progress(self.cat, self.db, actor, mode)

    def test_new_and_unconfigured_ledger_are_not_written(self):
        result = self.progress()
        self.assertEqual(result['counts'], {'needs_revision': 0, 'outstanding': 3, 'all_checks_observed_pass': 0})
        self.assertEqual(result['items'][0]['id'], self.cat.watch)
        self.assertFalse(self.db.exists())
        self.assertFalse(actor_progress(self.cat, None, 'Teacher-A', 'learning_preview')['recording_available'])
        self.assertFalse(result['teacher_approved'])

    def test_latest_explicit_decision_and_actor_isolation(self):
        key = self.cat.bridge
        self.save('Teacher-A', key, visual='revise')
        self.save('Teacher-B', key, **dict.fromkeys(CHECKS, 'pass'))
        self.save('teacher-a', key, **dict.fromkeys(CHECKS, 'pass'))
        self.save('Teacher-A', key, mathematics='pass')
        result = self.progress()
        self.assertEqual(result['items'][0]['id'], key)
        self.assertEqual(result['items'][0]['state'], 'needs_revision')
        self.assertEqual(result['items'][0]['checks']['visual'], 'revise')
        self.assertEqual(result['items'][0]['checks']['mathematics'], 'pass')
        self.assertEqual(result['counts']['all_checks_observed_pass'], 0)
        self.save('Teacher-A', key, **dict.fromkeys(CHECKS, 'pass'))
        self.save('Teacher-A', key)
        result = self.progress()
        self.assertEqual(result['counts']['all_checks_observed_pass'], 1)
        self.assertFalse(result['release_allowed'])
        self.assertNotIn('Teacher-B', json.dumps(result))
        self.assertNotIn('Disposable', json.dumps(result))

    def test_stale_rows_are_excluded_and_file_unchanged(self):
        key = self.cat.candidate
        for field in ('fingerprint', 'revision', 'proof_sha256'):
            self.save('Teacher-A', key, **dict.fromkeys(CHECKS, 'pass'))
            with closing(sqlite3.connect(self.db)) as db, db:
                db.execute('UPDATE observations SET ' + field + '=? WHERE seq=(SELECT max(seq) FROM observations)', ('stale',))
        before = self.db.read_bytes()
        result = self.progress()
        self.assertEqual(result['stale_observations_in_mode'], 3)
        self.assertEqual(result['counts']['outstanding'], 3)
        self.assertEqual(self.db.read_bytes(), before)

    def test_modes_and_malformed_evidence(self):
        self.save('Teacher-A', self.cat.watch, visual='revise')
        self.assertEqual([r['id'] for r in self.progress(mode='exam_candidate_preview')['items']], [self.cat.candidate])
        self.assertEqual(self.progress(mode='approved_exam')['items'], [])
        with self.assertRaises(ValueError): self.progress(mode='unknown')
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('UPDATE observations SET checks=?', ('{"visual":"approved"}',))
        with self.assertRaises(ValueError): self.progress()

    def request(self, query, actor=None, mounted=False):
        app = application(self.cat, self.users, self.db)
        if mounted: app = mount_as1(lambda env, start: [], app)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': ('/as1' if mounted else '') + '/api/progress',
               'QUERY_STRING': urlencode(query, doseq=True), 'wsgi.input': io.BytesIO()}
        if actor: env['HTTP_AUTHORIZATION'] = 'Basic ' + base64.b64encode((actor + ':fixture-password').encode()).decode()
        response = {}
        def start(status, headers): response.update(status=int(status.split()[0]), headers=dict(headers))
        response['body'] = json.loads(b''.join(app(env, start)))
        return response

    def test_authenticated_endpoint_and_no_impersonation(self):
        q = {'mode': 'learning_preview'}
        self.save('Teacher-B', self.cat.bridge, visual='revise')
        self.assertEqual(self.request(q)['status'], 401)
        self.assertEqual(self.request(q, 'other')['status'], 401)
        self.assertEqual(self.request(q | {'actor': 'Teacher-B'}, 'Teacher-A')['status'], 400)
        self.assertEqual(self.request({'mode': ['learning_preview', 'approved_exam']}, 'Teacher-A')['status'], 400)
        res = self.request(q, 'Teacher-A', mounted=True)
        self.assertEqual(res['status'], 200)
        self.assertEqual(res['headers']['Cache-Control'], 'private, no-store')
        self.assertEqual(res['body']['counts']['needs_revision'], 0)
        self.assertEqual(self.request(q, 'Teacher-B')['body']['counts']['needs_revision'], 1)
        self.assertEqual(self.request({'mode': 'approved_exam'}, 'Teacher-B')['body']['items'], [])

    def test_existing_wrong_database_is_not_treated_as_empty(self):
        self.db.touch()
        self.assertEqual(self.request({'mode': 'learning_preview'}, 'Teacher-A')['status'], 503)


if __name__ == '__main__':
    unittest.main()
