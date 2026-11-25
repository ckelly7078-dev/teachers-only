import itertools
import sqlite3
import tempfile
import unittest
from pathlib import Path
from foundation.studio import FAMILIES, UNITS, DIFFICULTIES, build, validate, generate, catalog, skill_id

class StudioTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'fixture.sqlite'
        with sqlite3.connect(self.path) as db:
            db.executescript('''CREATE TABLE skills(id TEXT PRIMARY KEY,unit TEXT,label TEXT,page INTEGER);
            CREATE TABLE documents(sha TEXT,unit TEXT,year INTEGER,series TEXT,component TEXT);
            CREATE TABLE questions(id INTEGER,paper TEXT,scheme TEXT,num INTEGER,part TEXT,page INTEGER,scheme_page INTEGER,marks INTEGER,status TEXT,skill TEXT);
            CREATE TABLE pairs(paper TEXT,scheme TEXT,status TEXT);
            CREATE TABLE postings(qid INTEGER,unit TEXT,term TEXT);''')
            for label,origin,sid,units in FAMILIES.values():
                for unit in units:
                    db.execute('INSERT OR IGNORE INTO skills VALUES(?,?,?,?)',(skill_id(unit,origin,sid),unit,label,10))
            db.execute("INSERT INTO documents VALUES('p','M1',2024,'Summer','Single paper')")
            db.execute("INSERT INTO pairs VALUES('p','s','paired')")
            db.execute("INSERT INTO questions VALUES(1,'p','s',1,'a',2,2,1,'verified','percentage')")
            db.execute("INSERT INTO questions VALUES(2,'p','s',2,'a',3,3,1,'review','percentage')")
            db.executemany("INSERT INTO postings VALUES(?,'M1','*')",[(1,),(2,)])

    def test_parameter_domain(self):
        for family in FAMILIES:
            for a,b,c in itertools.product(range(2,19),repeat=3):
                q,ans,steps,rubric=build(family,a,b,c)
                self.assertTrue(validate(family,a,b,c,ans),(family,a,b,c))
                bad=(ans[0]+1,ans[1]) if isinstance(ans,tuple) else ans+1
                self.assertFalse(validate(family,a,b,c,bad),(family,a,b,c))
                self.assertTrue(q and steps and rubric)

    def test_batch_and_evidence_gate(self):
        for unit in UNITS:
            for family in catalog(self.path,unit):
                for difficulty in DIFFICULTIES:
                    rows=generate(self.path,unit,family['family'],difficulty,10,seed=4)
                    self.assertEqual(len({r['question'] for r in rows}),10)
                    self.assertTrue(all(r['marks']==len(r['rubric']) and r['unit']==unit for r in rows))
        row=generate(self.path,'M1','percent',seed=1)[0]
        self.assertEqual([r['id'] for r in row['sources']],[1])
        self.assertEqual(row['evidence_level'],'related-skill-source-checked')
        self.assertEqual(generate(self.path,'M1','area')[0]['evidence_level'],'specification-only')
        with sqlite3.connect(self.path) as db: db.execute("UPDATE pairs SET status='review'")
        self.assertEqual(generate(self.path,'M1','percent')[0]['sources'],[])

    def test_reject_invalid(self):
        for args in [('M1','binary'),('M3','percent'),('M6','bad'),('M1','percent','extreme'),('M1','percent','easy',11),('M1','percent','easy',True)]:
            with self.assertRaises(ValueError): generate(self.path,*args)
        with self.assertRaises(ValueError): catalog(self.path,'M4')

if __name__=='__main__': unittest.main()
