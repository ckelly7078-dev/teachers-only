"""Successor regression, preserved historical evidence, exact variants and migration guards."""
import copy
import json
import sqlite3
import unittest
from unittest.mock import patch
from active_difficulty import Resolver, MARK_SUCCESSIONS
from difficulty_revision_bj import TARGETS, revise
from difficulty_revision_bj_oracle import check
from marking_design_bj import records
from marking_batch import validate_batch
from marking_review import fingerprint, inventory_entry
from revision_history import replace_authorised, digest, verify_history, atomic

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=Resolver();cls.old=Resolver(historical_through='bh')
    def test_every_variant(self):
        self.assertEqual(len(TARGETS),10)
        ids=set()
        for p,t in TARGETS:
            for v in (1,2,3):
                old=self.old._resolve(p,t,v);new=self.r._resolve(p,t,v); x=new['payload'];ids.add(new['id'])
                self.assertEqual(new['id'],old['id']);self.assertEqual(new['scope'],old['scope']);self.assertFalse(new['teacher_approved'])
                self.assertEqual(new['revision'],'FM-16BJ');self.assertEqual(old['revision'],'FM-16'+TARGETS[p,t].upper())
                self.assertEqual((old['marks'],new['marks']),MARK_SUCCESSIONS[p,t,'bj']);self.assertTrue(check(x))
                self.assertEqual(set(x),set(old['payload']));self.assertEqual(inventory_entry(new)['status'],'typed_provisional')
                for key in ('path','tier','variant','focus_skill','origin','examination_source','assessment_role','difficulty_status'):
                    self.assertEqual(x[key],old['payload'][key])
                for val in (x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']):self.assertEqual(val.count('$')%2,0)
                if p in ('angle-units','solve-cubic','solve-quartic'):
                    for key in ('question_latex','final_answer_latex','facts'):self.assertEqual(x[key],old['payload'][key])
                else:self.assertNotEqual(x['question_latex'],old['payload']['question_latex'])
        self.assertEqual(len(ids),30)
    def test_exact_fact_tamper(self):
        for p,t in TARGETS:
            for v in (1,2,3):
                x=revise(p,t,v);x['facts'][0]='123456789'
                self.assertFalse(check(x),(p,t,v))
    def test_frozen_records(self):
        batch=list(records(self.r));self.assertEqual(len(batch),30)
        self.assertEqual(validate_batch(batch,self.r)['statuses'],{'editorial_review_recorded':30})
        for row in batch:
            parts=row['id'].split('.');old=self.old._resolve(parts[1],int(parts[2][1:]),int(parts[3][1:]))
            self.assertEqual(row['supersedes_fingerprint'],fingerprint(old))
            with self.assertRaisesRegex(ValueError,'Stale'):validate_batch([row],self.old)
    def test_historical_selection_closed(self):
        with self.assertRaisesRegex(ValueError,'Historical'):self.old.resolve('angle-units',5,1,mode='exam_candidate_preview')
        self.assertEqual(self.r.resolve('angle-units',5,1,mode='exam_candidate_preview')['revision'],'FM-16BJ')
        with self.assertRaises(ValueError):self.r.resolve('angle-units',5,1,mode='approved_exam')
        with self.assertRaises(ValueError):Resolver(historical_through='invented')
    def test_explicit_mark_succession(self):
        db=sqlite3.connect(':memory:');db.execute('pragma foreign_keys=on')
        db.execute('CREATE TABLE calibrated_pathway_questions(id TEXT PRIMARY KEY,payload TEXT,marks INTEGER,review_status TEXT)')
        db.execute('CREATE TABLE difficulty_revision_history(question_id TEXT REFERENCES calibrated_pathway_questions(id),old_payload TEXT,old_marks INTEGER,old_status TEXT,old_sha256 TEXT,revision TEXT,PRIMARY KEY(question_id,revision))')
        old=self.old._resolve('angle-units',5,1);status='exact_facts_checked_editorial_teacher_pending';payload=json.dumps(old['payload'])
        db.execute('INSERT INTO calibrated_pathway_questions VALUES (?,?,?,?)',(old['id'],payload,old['marks'],status))
        earlier=json.dumps(self.old._resolve_version('angle-units',5,1,'ab')['payload'])
        db.execute('INSERT INTO difficulty_revision_history VALUES (?,?,?,?,?,?)',(old['id'],earlier,2,status,digest(earlier),old['revision']))
        db.commit()
        with patch('revision_history.MARK_SUCCESSIONS',{}):
            with self.assertRaisesRegex(ValueError,'marking/scope'):replace_authorised(db,self.r,'angle-units',5,1,'bj')
        with self.assertRaises(RuntimeError):
            with atomic(db):replace_authorised(db,self.r,'angle-units',5,1,'bj');raise RuntimeError('abort')
        self.assertEqual(verify_history(db),1);self.assertEqual(db.execute('SELECT marks FROM calibrated_pathway_questions').fetchone(),(2,))
        new=replace_authorised(db,self.r,'angle-units',5,1,'bj');self.assertEqual(verify_history(db),2)
        row=db.execute('SELECT payload,marks FROM calibrated_pathway_questions').fetchone();self.assertEqual(json.loads(row[0]),new['payload']);self.assertEqual(row[1],3)
        with self.assertRaises(ValueError):replace_authorised(db,self.r,'angle-units',5,1,'bj')
        db.close()
    def test_invalid_targets(self):
        for p,t,v in [('angle-units',5,True),('angle-units',5,4),('angle-units',5.0,1),('solve-cubic',4,1),('root-squares',5,1)]:
            with self.assertRaises(ValueError):revise(p,t,v)
    def test_predecessor_immutability(self):
        for p,t in TARGETS:
            old=self.old._resolve(p,t,1);snap=copy.deepcopy(old);new=self.r._resolve(p,t,1);new['payload']['facts'].clear()
            self.assertEqual(self.old._resolve(p,t,1),snap)

if __name__=='__main__':unittest.main(verbosity=2)
