import base64
import io
import json
import os
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode
from review_service_bq import application, credentials, CHECKS, mount_as1, check_ledger_path
from calibration_bq import summarize
from active_difficulty import Resolver, require
from marking_review import fingerprint


class FakeCatalogue:
    def __init__(self):
        self.item=Resolver()._resolve('angle-units',1,1);self.key=self.item['id']
    def list_ids(self,mode):
        require(mode in ('learning_preview','approved_exam'),'Mode');return [self.key] if mode=='learning_preview' else []
    def get(self,key,mode):
        require(key in self.list_ids(mode),'Ineligible');return {'item':self.item,'mode':mode,'fingerprint':fingerprint(self.item),'proof_sha256':'a'*64,'page':1,'release_allowed':False,'exam_ready':False}
    def png(self,key,mode):self.get(key,mode);return b'fake-png-test-fixture'


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cat=FakeCatalogue();cls.user=credentials('fictional-test-teacher','test-password',b'test-salt-123456')
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'review.sqlite';self.app=application(self.cat,[self.user],self.db)
    def request(self,path,query=None,body=None,auth=True,csrf=True):
        raw=json.dumps(body).encode() if body is not None else b'';response={}
        env={'PATH_INFO':path,'QUERY_STRING':urlencode(query or {},doseq=True),'REQUEST_METHOD':'POST' if body is not None else 'GET','wsgi.input':io.BytesIO(raw),'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw))}
        if auth:env['HTTP_AUTHORIZATION']='Basic '+base64.b64encode(b'fictional-test-teacher:test-password').decode()
        if csrf:env['HTTP_X_AS1_REQUEST']='teacher'
        def start(status,headers):response.update(status=int(status.split()[0]),headers=dict(headers))
        response['body']=b''.join(self.app(env,start));return response
    def test_authentication_and_private_file_denial(self):
        for p in ('/','/app.js','/api/list','/api/page','/api/item','/api/review','/as1.sqlite'):
            self.assertEqual(self.request(p,auth=False)['status'],401)
        self.assertEqual(self.request('/as1.sqlite')['status'],404)
        self.assertEqual(self.request('/../as1.sqlite')['status'],404)
    def test_guard_applies_to_api_and_renderer(self):
        for path in ('/api/item','/api/page'):
            self.assertEqual(self.request(path,{'id':self.cat.key,'mode':'approved_exam'})['status'],400)
            res=self.request(path,{'id':self.cat.key,'mode':'learning_preview'});self.assertEqual(res['status'],200);self.assertEqual(res['headers']['Cache-Control'],'private, no-store')
        self.assertEqual(json.loads(self.request('/api/list',{'mode':'approved_exam'})['body'])['ids'],[])
        self.assertEqual(self.request('/api/list',{'mode':['learning_preview','approved_exam']})['status'],400)
    def test_review_is_observation_not_approval(self):
        data={'id':self.cat.key,'mode':'learning_preview','fingerprint':fingerprint(self.cat.item),'proof_sha256':'a'*64,'checks':{c:'not_reviewed' for c in CHECKS},'note':'Fictional test observation'}
        self.assertEqual(self.request('/api/review',body=data,csrf=False)['status'],415)
        self.assertEqual(self.request('/api/review',body={**data,'fingerprint':'0'*64})['status'],400)
        self.assertEqual(self.request('/api/review',body={**data,'proof_sha256':'b'*64})['status'],400)
        self.assertEqual(self.request('/api/review',body={**data,'teacher_approved':True})['status'],400)
        result=self.request('/api/review',body=data);self.assertEqual(result['status'],200);self.assertFalse(json.loads(result['body'])['teacher_approved'])
        with closing(sqlite3.connect(self.db)) as db:self.assertEqual(db.execute('select actor,item_id,fingerprint from observations').fetchall(),[('fictional-test-teacher',self.cat.key,data['fingerprint'])])
    def test_optional_mount_preserves_existing_paths(self):
        def fallback(env,start):
            start('200 OK',[]);return [env['PATH_INFO'].encode()]
        self.app=mount_as1(fallback,self.app)
        self.assertEqual(self.request('/foundation/web/index.html')['body'],b'/foundation/web/index.html')
        self.assertEqual(self.request('/as1')['status'],302)
        self.assertEqual(self.request('/as1/api/list',{'mode':'learning_preview'},auth=False)['status'],401)
        self.assertEqual(self.request('/as1/api/list',{'mode':'learning_preview'})['status'],200)
    def test_mounted_return_navigation_is_opt_in(self):
        self.assertNotIn(b'Foundation Mathematics Studio', self.request('/')['body'])
        self.app = mount_as1(lambda env, start: [], self.app)
        self.assertIn(b'href="/foundation/web/index.html"', self.request('/as1/')['body'])
        self.assertEqual(self.request('/as1/', auth=False)['status'], 401)

    def test_existing_ledger_must_be_distinct_from_foundation_data(self):
        source = Path(self.tmp.name) / 'foundation.sqlite'
        source.touch()
        alias = Path(self.tmp.name) / 'alias'
        os.link(source, alias)
        for path in (source, alias):
            with self.assertRaises(ValueError):
                check_ledger_path(path, [source])
        check_ledger_path(self.db, [source])

    def test_aggregate_calibration_rejects_missing_and_stale_data(self):
        item=self.cat.item;data={'id':item['id'],'fingerprint':fingerprint(item),'marks':item['marks'],'counts':[2,8]}
        result=summarize(item,data,minimum_attempts=20);self.assertEqual(result['facility'],0.8);self.assertFalse(result['minimum_attempts_met']);self.assertFalse(result['teacher_approved'])
        for bad in ({**data,'counts':[0,0]},{**data,'counts':[2,-1]},{**data,'fingerprint':'0'*64},{**data,'counts':[True,8]},{**data,'student':'not allowed'}):
            with self.assertRaises(ValueError):summarize(item,bad,minimum_attempts=20)
