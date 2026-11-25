import sqlite3, unittest
from foundation.evidence import counts, search
from foundation.report_topics import parse, tags

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        self.db.executescript('''CREATE TABLE examiner_reports(sha,filename,year,series);
        CREATE TABLE examiner_anchors(report_sha,unit,component,num,start_page,end_page,paper,status);
        CREATE TABLE examiner_notes(report_sha,unit,component,num,topic,note,review_status);
        CREATE TABLE pairs(paper,unit,component,year,series,status);
        CREATE TABLE skills(id,unit,label,page);
        CREATE TABLE examiner_skill_evidence(report_sha,unit,component,num,skill,status);
        INSERT INTO examiner_reports VALUES('report','report.pdf',2022,'Summer');
        INSERT INTO pairs VALUES('paper','M1','Single paper',2022,'Summer','paired');
        INSERT INTO examiner_anchors VALUES('report','M1','Single paper',1,7,8,'paper','linked');
        INSERT INTO examiner_anchors VALUES('report','M1','Single paper',2,8,8,'paper','review');
        INSERT INTO examiner_notes VALUES('report','M1','Single paper',1,'Percentages','Original teaching note','AI-assisted; not approved');
        INSERT INTO examiner_notes VALUES('report','M1','Single paper',2,'Percentages','Unlinked note','review');
        INSERT INTO skills VALUES('percentage','M1','Percentages and representations',8);
        INSERT INTO examiner_skill_evidence VALUES('report','M1','Single paper',1,'percentage','provisional');''')
    def tearDown(self):self.db.close()
    def test_search_and_citation(self):
        r=search(self.db,'M1','percentage');self.assertEqual(len(r),1);self.assertEqual(r[0]['start_page'],7);self.assertEqual(r[0]['num'],1);self.assertEqual(r[0]['notes'][0]['note'],'Original teaching note');self.assertNotIn('rules',r[0]);self.assertEqual(r[0]['skills'][0]['status'],'provisional')
    def test_unit_filter(self):self.assertEqual(search(self.db,'M2','percentage'),[])
    def test_skill_filter(self):self.assertEqual(len(search(self.db,'M1',skill='percentage')),1)
    def test_reject_invalid(self):
        for args in [('M3','',5),('M1','x'*161,5),('M1','',13)]:
            with self.assertRaises(ValueError):search(self.db,*args)
    def test_pair_revoked(self):
        self.db.execute("UPDATE pairs SET status='review'");self.assertEqual(search(self.db,'M1'),[])
    def test_old_checkpoint(self):
        self.db.execute('DROP TABLE examiner_anchors');self.assertEqual(search(self.db,'M1'),[]);self.assertEqual(counts(self.db,'M1')['reports'],0)
    def test_counts(self):self.assertEqual(counts(self.db,'M1'),{'reports':1,'examiner_anchors':1,'examiner_notes':1,'examiner_tagged':1})
    def test_tags_inherited(self):
        self.assertEqual(tags('Binary and percentages','M6',{'m6-binary','m6-from-m1-percentage'}),{'m6-binary','m6-from-m1-percentage'})
        self.assertEqual(tags('range of ability','M1',{'averages'}),set())
    def test_section_boundaries(self):
        text='\f'*6+'Assessment Unit M1 Foundation Tier\nQ1 Some evidence.\nAssessment Unit M3 Higher Tier\nQ1 No Foundation evidence.\nAssessment Unit M5 Foundation Tier Non-Calculator\nQ1 More evidence.'
        p=parse(text);self.assertEqual(set(p),{('M1','Single paper'),('M5','Paper 1')});self.assertEqual(p[('M1','Single paper')][1],(7,['Some evidence.']))
    def test_duplicate_heading(self):
        with self.assertRaises(ValueError):parse('\f'*6+'Assessment Unit M1 Foundation Tier\nQ1 First\nQ1 Duplicate')
if __name__=='__main__':unittest.main()
