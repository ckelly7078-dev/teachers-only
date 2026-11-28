import unittest
from review_queue_bs import add_editorial_evidence


class EditorialQueueTests(unittest.TestCase):
    def setUp(self):
        item = dict(id='a', fingerprint='1' * 64, revision='fixture', scope_watch=True, checks={'visual':'not_reviewed'})
        other = dict(item, id='b', scope_watch=False)
        self.report = dict(items_by_priority=[item, other], proof_sha256='2' * 64, teacher_approved=0, release_allowed=False)
        self.row = dict(id='a', fingerprint=item['fingerprint'], revision='fixture', proof_sha256=self.report['proof_sha256'],
                        reviewer_kind='ai_editorial', teacher_approved=False, note='Fictional test evidence.')

    def test_priority_and_independent_counters(self):
        visual = dict(self.row, id='b', decision='revise')
        result = add_editorial_evidence(self.report, [visual], [dict(self.row, decision='learning_only')])
        self.assertEqual([r['id'] for r in result['items_by_priority']], ['b', 'a'])
        self.assertEqual(result['ai_visual_counts'], {'revise':1, 'uninspected':1})
        self.assertEqual(result['editorial_scope_counts'], {'learning_only':1})
        self.assertEqual(result['items_by_priority'][0]['checks'], {'visual':'not_reviewed'})
        self.assertFalse(result['release_allowed'])
        self.assertTrue(result['items_by_priority'][1]['scope_watch'])

    def test_rejects_stale_duplicate_empty_or_promoted_records(self):
        good = dict(self.row, decision='open')
        for scope in ([], [good, good], [dict(good, id='b')], [dict(good, decision='approved')]):
            with self.assertRaises(ValueError):
                add_editorial_evidence(self.report, [], scope)
        for field, value in [('fingerprint','stale'), ('revision','old'), ('proof_sha256','stale'),
                             ('teacher_approved',True), ('reviewer_kind','teacher'), ('note',' ')]:
            with self.assertRaises(ValueError):
                add_editorial_evidence(self.report, [dict(self.row, decision='inspected', **{field:value})], [good])
