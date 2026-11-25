"""Integration tests use fictional mathematical content and a tiny real PDF."""
import base64
import csv
import hashlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from foundation.db import UNITS, connect, search
from foundation.ingest import anchors, audit, digest, extract, suggest
from foundation.practice import ModelUnavailable, SKILLS, generate, validate
from foundation.report import export
from foundation.review import Conflict, save
from foundation.server import application, credentials, dispatch

def pdf(pages):
    """Small standard PDF with explicit xref offsets so Poppler tests the real import path."""
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',b'',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for lines in pages:
        page = len(objs)+1
        kids.append(f'{page} 0 R')
        stream = b'BT /F1 11 Tf 50 740 Td 18 TL\n'
        for line in lines:
            literal = line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
            stream+=b'('+literal.encode()+b") Tj T*\n"
        stream+=b'ET'
        objs += [f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 800] /Resources << /Font << /F1 3 0 R >> >> /Contents {page+1} 0 R >>'.encode(),
                 f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream']
    objs[1]=f'<< /Type /Pages /Count {len(kids)} /Kids [{" ".join(kids)}] >>'.encode()
    output=bytearray(b'%PDF-1.4\n')
    offsets=[0]
    for i,obj in enumerate(objs,1):
        offsets.append(len(output))
        output.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    start=len(output)
    output.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for pos in offsets[1:]:
        output.extend(f'{pos:010d} 00000 n \n'.encode())
    output.extend(f'trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF'.encode())
    return bytes(output)


def archive(path,duplicate=False,scheme_code='GMC11',bad_hash=False):
    entries = []
    common=['General Certificate of Secondary Education 2024','Mathematics Foundation Tier',
            'With calculator','THURSDAY 16 MAY','19001']
    for kind,code,extra,body in [
        ('Question paper','GMC11',['TIME 1 hour 45 minutes.','The total mark for this paper is 1.'],['1   (a) Sample percentage exercise.','Answer [1]']),
        ('Mark scheme',scheme_code,['MARK SCHEME'],['1   (a) 40   A1'])]:
        data=pdf([common+[code]+extra,body])
        entries.append((kind,'M1/2024/Summer/'+kind+'.pdf',data))
        if duplicate and kind=='Question paper':
            entries.append((kind,'M1/2024/Summer/alias.pdf',data))
    with zipfile.ZipFile(path,'w') as z:
        src=io.StringIO()
        writer=csv.writer(src)
        writer.writerow(['Unit','Year','Series','Component','Document type','Source','Archive path','SHA256','Bytes'])
        for kind,name,data in entries:
            z.writestr(name,data)
            writer.writerow(['M1',2024,'Summer','Single paper',kind,'Fictional test',name,
                             '0'*64 if bad_hash else hashlib.sha256(data).hexdigest(),len(data)])
        z.writestr('00_INVENTORY.csv',src.getvalue())
        z.writestr('00_MISSING_DOCUMENTS.csv','Unit,Year,Series,Component,Document type\nM2,2024,Summer,Single paper,Mark scheme\n')


class FoundationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.path=self.root/'knowledge.sqlite'
        self.source=self.root/'sources.zip'
        self.db=connect(self.path,True)
        self.addCleanup(self.db.close)
        archive(self.source)

    def ingest(self,unit='M1'):
        with zipfile.ZipFile(self.source) as z:
            return audit(self.db,z,unit,digest(self.source)),extract(self.db,z,unit)

    def checked(self,skill='percentage'):
        self.ingest()
        qid=self.db.execute('SELECT id FROM questions').fetchone()[0]
        payload=dict(skill=skill,version=0,status='verified',marks=1,page=2,end_page=2,scheme_page=2,
                     annotation='Use the whole as denominator.',answer='40%',rules=[[dict(code='A1',evidence='Correct percentage.')]])
        save(self.db,qid,payload,'Test teacher')
        return qid,payload

    def test_documents_and_resume(self):
        first=self.ingest()
        self.assertEqual(first[0]['read'],2)
        self.assertEqual(first[1]['extracted_pairs'],1)
        paper=self.db.execute("SELECT * FROM documents WHERE kind='paper'").fetchone()
        self.assertEqual((paper['total_marks'],paper['duration_min'],paper['tier'],paper['code']),(1,105,'Foundation','GMC11'))
        with patch('foundation.ingest.pdf_pages',side_effect=AssertionError('Unexpected PDF read')):
            second=self.ingest()
        self.assertEqual(second[0]['skipped'],2)
        self.assertEqual(second[1]['skipped_pairs'],1)

    def test_duplicate_members_and_manifest_mismatch(self):
        archive(self.source,duplicate=True)
        self.ingest()
        self.assertEqual(self.db.execute('SELECT count(*) FROM files').fetchone()[0],3)
        self.assertEqual(self.db.execute('SELECT count(*) FROM documents').fetchone()[0],2)
        self.assertEqual(self.db.execute('SELECT status FROM pairs').fetchone()[0],'paired')
        archive(self.source,duplicate=True,bad_hash=True)
        self.ingest()
        self.assertEqual(self.db.execute('SELECT status FROM pairs').fetchone()[0],'review')

    def test_wrong_component_and_missing_material(self):
        archive(self.source,scheme_code='GMC21')
        self.assertEqual(self.ingest()[1]['extracted_pairs'],0)
        self.assertEqual(self.db.execute('SELECT status FROM pairs').fetchone()[0],'review')
        self.ingest('M2')
        self.assertEqual(self.db.execute("SELECT status FROM pairs WHERE unit='M2'").fetchone()[0],'missing')

    def test_markers_notation_and_pages(self):
        parsed=anchors(['cover',' 1\n (a) (i) x² − 3 = 0 [1]\n(ii) Solve [2]','(b) Draw [3]\n 2   End [1]'])
        self.assertEqual(parsed[1,'a.ii']['marks'],[2])
        self.assertEqual(parsed[1,'b']['page'],3)
        self.assertEqual(parsed[2,'']['marks'],[1])
        scheme=anchors(['cover','1  (a) 10   MA1, A1'],True)
        self.assertEqual(scheme[1,'a']['codes'],['MA1','A1'])
        self.assertEqual(suggest({'random','sample'},[('stats',{'random','sample'})]),'stats')
        self.assertIsNone(suggest({'random','sample'},[('a',{'random','sample'}),('b',{'random','sample'})]))

    def test_search_and_review_audit(self):
        self.ingest()
        self.assertEqual(search(self.path,'M1','percent'),[])
        qid,payload=self.checked()
        self.assertEqual(search(self.path,'M1','percent')[0]['id'],qid)
        self.assertEqual(search(self.path,'M2','percent'),[])
        with self.assertRaises(ValueError): search(self.path,'M3')
        with self.assertRaises(ValueError): search(self.path,'M1',limit=200)
        with self.assertRaises(Conflict):save(self.db,qid,payload,'Second teacher')
        with self.assertRaises(ValueError):save(self.db,qid,dict(payload,version=1,marks=2),'Test teacher')
        routes=[[dict(code='MA1',evidence='One route')],[dict(code='A1',evidence='Equivalent route')]]
        save(self.db,qid,dict(payload,version=1,status='review',rules=routes),'Second teacher')
        self.assertEqual(search(self.path,'M1','percent'),[])
        self.assertEqual(self.db.execute('SELECT count(*) FROM reviews').fetchone()[0],2)

    def test_restore_without_archive(self):
        self.checked()
        export(self.path,self.root/'backup')
        self.source.unlink()
        restored=self.root/'backup'/'foundation.sqlite'
        self.assertEqual(search(restored,'M1','percentage')[0]['answer'],'40%')
        for filename in ('inventory.csv','pairing.csv','missing.csv','extraction-checks.csv'):
            self.assertTrue((restored.parent/filename).is_file())
        with sqlite3.connect(restored) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')

    def test_generated_validation_and_approval(self):
        self.checked()
        with patch.dict(os.environ,{'KB_MODEL_KEY':''}):
            with self.assertRaises(ModelUnavailable):generate(self.path,'percentage','model')
        with self.assertRaises(ValueError):generate(self.path,'metric')
        draft=dispatch(self.path,'practice',{'skill':'percentage'},'Teacher A')
        self.assertEqual(len(draft['sources']),1)
        self.assertEqual(len(draft['rubric']),draft['marks'])
        with self.assertRaises(Conflict):dispatch(self.path,'approve',{'id':draft['id'],'question':'new'},'Teacher B')
        out=dispatch(self.path,'approve',{'id':draft['id'],'question':draft['question']},'Teacher A')
        self.assertEqual(out['state'],'approved')
        with self.assertRaises(Conflict):dispatch(self.path,'approve',{'id':draft['id'],'question':'new'},'Teacher A')
        for a in range(2,19):
            for b in range(2,19):
                for skill,ans in [('metric',50*a+8*b),('percentage',5*a),('finance',2000-75*a-15*b)]:
                    self.assertTrue(validate(skill,a,b,ans))
                    self.assertFalse(validate(skill,a,b,ans+1))

    def test_model_uses_bounded_metadata_and_checks_parameters(self):
        from foundation.practice import parameters
        self.checked()
        refs=search(self.path,'M1',skill='percentage')
        response=io.BytesIO(json.dumps({'choices':[{'message':{'content':'{"a":4,"b":8}'}}]}).encode())
        with patch.dict(os.environ,{'KB_MODEL_URL':'https://example.invalid/model','KB_MODEL_NAME':'test','KB_MODEL_KEY':'test'}),patch('urllib.request.urlopen',return_value=response) as call:
            self.assertEqual(parameters(refs,'percentage'),(4,8))
            sent=call.call_args.args[0].data
            self.assertLess(len(sent),1800)
            self.assertNotIn(b'denominator',sent)
            call.return_value=io.BytesIO(b'{"choices":[{"message":{"content":"{}"}}]}')
            with self.assertRaises(ModelUnavailable):parameters(refs,'percentage')

    def test_http_auth_private_paths_and_post_contract(self):
        self.checked()
        users=self.root/'users.json';users.write_text(json.dumps([credentials('Teacher','secret')]))
        token='Basic '+base64.b64encode(b'Teacher:secret').decode()
        def req(path,method='GET',auth='',body=None,mime='application/json',custom=True):
            raw=json.dumps(body or {}).encode()
            env={'PATH_INFO':path,'REQUEST_METHOD':method,'QUERY_STRING':'','HTTP_AUTHORIZATION':auth,
                 'CONTENT_TYPE':mime,'CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw)}
            if custom:env['HTTP_X_KB_REQUEST']='teacher'
            status=[]
            content=b''.join(application(env,lambda s,h:status.append(s)))
            return int(status[0][:3]),content
        with patch.dict(os.environ,{'KB_DB':str(self.path),'KB_USERS':str(users)}):
            self.assertEqual(req('/api/foundation/search')[0],401)
            self.assertEqual(req('/foundation/web/index.html')[0],401)
            self.assertEqual(req('/foundation/web/index.html',auth=token)[0],200)
            self.assertEqual(req('/private-data/foundation.sqlite',auth=token)[0],404)
            self.assertEqual(req('/api/foundation/practice','POST',token,{'skill':'percentage'},custom=False)[0],415)
            self.assertEqual(req('/api/foundation/practice','POST',token,{'skill':'percentage'})[0],200)
            code,data=req('/api/foundation/summary',auth=token)
            self.assertEqual(code,200)
            self.assertEqual([u['unit'] for u in json.loads(data)['units']],list(UNITS))
