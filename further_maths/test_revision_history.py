import copy,json,sqlite3,unittest
from unittest.mock import patch
from active_difficulty import Resolver
from marking_design_ba import records
from marking_batch import validate_batch
from revision_history import upgrade_history,replace_authorised,digest,verify_history,atomic

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.execute('pragma foreign_keys=on')
        self.db.execute('CREATE TABLE calibrated_pathway_questions(id TEXT PRIMARY KEY,payload TEXT,marks INTEGER,review_status TEXT)')
        self.db.execute('CREATE TABLE difficulty_revision_history(question_id TEXT PRIMARY KEY REFERENCES calibrated_pathway_questions(id),old_payload TEXT NOT NULL,old_marks INTEGER NOT NULL,old_status TEXT NOT NULL,old_sha256 TEXT NOT NULL,revision TEXT NOT NULL)')
        self.old=self.r._resolve_version('angle-units',6,1,'ad');self.id=self.old['id'];self.status='exact_facts_checked_editorial_teacher_pending'
        payload=json.dumps(self.old['payload']);self.db.execute('INSERT INTO calibrated_pathway_questions VALUES (?,?,?,?)',(self.id,payload,self.old['marks'],self.status))
        base=json.dumps(self.r._resolve_version('angle-units',6,1,'ab')['payload']);self.db.execute('INSERT INTO difficulty_revision_history VALUES (?,?,?,?,?,?)',(self.id,base,4,self.status,digest(base),'FM-16AD'));self.db.commit()
    def tearDown(self):self.db.close()
    def test_upgrade_and_succession(self):
        before=self.db.execute('SELECT * FROM difficulty_revision_history').fetchall();self.assertEqual(upgrade_history(self.db),1);self.assertEqual(upgrade_history(self.db),1)
        new=replace_authorised(self.db,self.r,'angle-units',6,1,'ba');self.assertEqual(new['revision'],'FM-16BA');self.assertEqual(verify_history(self.db),2)
        self.assertIn(before[0],self.db.execute('SELECT * FROM difficulty_revision_history').fetchall());self.assertEqual(new['payload'],json.loads(self.db.execute('SELECT payload FROM calibrated_pathway_questions').fetchone()[0]))
        self.assertEqual([x['type'] for x in new['payload']['rubric']],['M','R','A','R'])
        self.assertEqual({k for k in new['payload'] if new['payload'][k]!=self.old['payload'][k]},{'rubric'})
        with self.assertRaises(ValueError):replace_authorised(self.db,self.r,'angle-units',6,1,'ba')
    def test_rollback(self):
        before=self.db.execute('SELECT * FROM difficulty_revision_history').fetchall()
        with self.assertRaises(RuntimeError):
            with atomic(self.db):
                upgrade_history(self.db);replace_authorised(self.db,self.r,'angle-units',6,1,'ba');raise RuntimeError('abort')
        self.assertEqual(self.db.execute('SELECT * FROM difficulty_revision_history').fetchall(),before)
        self.assertEqual(json.loads(self.db.execute('SELECT payload FROM calibrated_pathway_questions').fetchone()[0]),self.old['payload'])
    def test_tamper_and_unknown_successor(self):
        self.db.execute("UPDATE difficulty_revision_history SET old_sha256='bad'")
        with self.assertRaisesRegex(ValueError,'hash mismatch'):upgrade_history(self.db)
        with self.assertRaisesRegex(ValueError,'Unauthorised'):replace_authorised(self.db,self.r,'angle-units',6,1,'az')
    def test_wrong_active_payload(self):
        upgrade_history(self.db);self.db.execute("UPDATE calibrated_pathway_questions SET payload='{}'")
        with self.assertRaisesRegex(ValueError,'predecessor mismatch'):replace_authorised(self.db,self.r,'angle-units',6,1,'ba')
        self.assertEqual(verify_history(self.db),1)
    def test_registry_authorisation(self):
        with patch('active_difficulty.SUCCESSIONS',{}):
            with self.assertRaisesRegex(ValueError,'authorisation'):Resolver()
        with patch('active_difficulty.SUCCESSIONS',{('angle-units',6,'ba'):'ab'}):
            with self.assertRaisesRegex(ValueError,'authorisation'):Resolver()
    def test_basis_and_stale(self):
        batch=list(records(self.r));self.assertEqual(validate_batch(batch,self.r)['statuses'],{'editorial_review_recorded':3})
        for invalid in (None,'invented',[],'individual_item_rereview'):
            row=copy.deepcopy(batch[0]);row.pop('supersedes_fingerprint');row['review_basis']=invalid
            with self.assertRaises(ValueError):validate_batch([row],self.r)
        row=copy.deepcopy(batch[0]);row['supersedes_fingerprint']=row['fingerprint']
        with self.assertRaises(ValueError):validate_batch([row],self.r)
        row=copy.deepcopy(batch[0]);row['fingerprint']=row['supersedes_fingerprint']
        with self.assertRaisesRegex(ValueError,'Stale'):validate_batch([row],self.r)

if __name__=='__main__':unittest.main()
