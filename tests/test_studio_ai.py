import itertools
import json
import os
import unittest
from unittest.mock import patch
from foundation import studio, studio_ai as ai
import test_studio


def response(items):
    return {'status':'completed','output':[{'type':'message','content':[
        {'type':'output_text','text':json.dumps({'selection':items})}]}]}


class StudioAITest(unittest.TestCase):
    def setUp(self):
        fixture=test_studio.StudioTest(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.path=fixture.path
        self.env=patch.dict(os.environ,{'OPENAI_API_KEY':'fictional-test-key','KB_STUDIO_MODEL':'gpt-4.1-mini'})
        self.env.start(); self.addCleanup(self.env.stop)

    def test_all_curated_variants(self):
        for family in studio.FAMILIES:
            for a,b,c in itertools.product((2,8,18),repeat=3):
                q,ans,steps,rubric=studio.build(family,a,b,c)
                v=ai.variants({'question':q,'family':family})
                self.assertEqual(v[0],q)
                self.assertNotEqual(v[0],v[1])
                self.assertTrue(studio.validate(family,a,b,c,ans))

    def test_selected_drafts_and_request_allowlist(self):
        for unit in studio.UNITS:
            for entry in studio.catalog(self.path,unit):
                with patch.object(ai,'send',return_value=response([{'id':0,'variant':1},{'id':1,'variant':0}])) as send:
                    rows=ai.generate(self.path,unit,entry['family'],'standard',2)
                payload=send.call_args.args[0]; context=json.loads(payload['input'])
                self.assertEqual(set(context),{'unit','family','difficulty','count','skill','spec_page','reference_marks','evidence_level','candidates'})
                self.assertTrue(all(set(c)=={'id','wording','marks'} for c in context['candidates']))
                self.assertFalse(payload['store']); self.assertTrue(payload['text']['format']['strict'])
                self.assertEqual(len(rows),2); self.assertEqual(rows[0]['question'],context['candidates'][0]['wording'][1])
                self.assertTrue(all(r['mode']=='model' and r['unit']==unit and len(r['rubric'])==r['marks'] for r in rows))
                self.assertNotIn('fictional-test-key',json.dumps(payload))

    def test_selection_preserves_math_and_rejects_bad_output(self):
        pool=studio.generate(self.path,'M2','pythagoras',count=2,seed=5)
        rows=ai.selection(response([{'id':0,'variant':1},{'id':1,'variant':0}]),pool,2)
        for source,row in zip(pool,rows):
            for key in ('answer','solution','rubric','marks','diagram','sources','skill'):
                self.assertEqual(source[key],row[key])
        bad=[[],[{'id':0,'variant':0}],[{'id':0,'variant':0}]*2,
             [{'id':True,'variant':0},{'id':1,'variant':0}],
             [{'id':-1,'variant':0},{'id':1,'variant':0}],
             [{'id':2,'variant':0},{'id':1,'variant':0}],
             [{'id':0,'variant':2},{'id':1,'variant':0}],
             [{'id':0,'variant':0,'question':'new'},{'id':1,'variant':0}]]
        for items in bad:
            with self.assertRaises(ai.StudioAIUnavailable): ai.selection(response(items),pool,2)
        for r in ({'status':'incomplete'}, {'status':'completed','output':[{'type':'message','content':[{'type':'refusal'}]}]}, None):
            with self.assertRaises(ai.StudioAIUnavailable): ai.selection(r,pool,2)
        r=response([{'id':0,'variant':0},{'id':1,'variant':1}]); r['output'][0]['content'][0]['text']='{"selection":[],"selection":[]}'
        with self.assertRaises(ai.StudioAIUnavailable): ai.selection(r,pool,2)

    def test_no_key_and_invalid_request_never_call_service(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':''}),patch.object(ai,'send') as send:
            with self.assertRaises(ai.StudioAIUnavailable): ai.generate(self.path,'M1','percent')
            send.assert_not_called()
        with patch.object(ai,'send') as send:
            for args in [('M1','binary'),('M3','percent'),('M1','percent','standard',True),('M1','percent','standard',11)]:
                with self.assertRaises(ValueError): ai.generate(self.path,*args)
            send.assert_not_called()

    def test_http_transport_boundaries(self):
        from io import BytesIO
        from unittest.mock import MagicMock
        from urllib.error import URLError
        op=MagicMock(); op.open.return_value.__enter__.return_value=BytesIO(b'{"status":"completed"}')
        with patch('urllib.request.build_opener',return_value=op):
            self.assertEqual(ai.send({'model':'test'}),{'status':'completed'})
            req=op.open.call_args.args[0]
            self.assertEqual(req.full_url,ai.ENDPOINT)
            self.assertEqual(req.get_header('Authorization'),'Bearer fictional-test-key')
            self.assertEqual(op.open.call_args.kwargs['timeout'],20)
            op.open.return_value.__enter__.return_value=BytesIO(b'x'*(ai.MAX_RESPONSE+1))
            with self.assertRaises(ai.StudioAIUnavailable): ai.send({})
            op.open.side_effect=URLError('private service detail')
            with self.assertRaisesRegex(ai.StudioAIUnavailable,'AI service unavailable'): ai.send({})
        self.assertIsNone(ai.NoRedirect().redirect_request(None,None,302,None,None,'https://other.invalid'))

    def test_authenticated_http_persistence_and_fail_closed(self):
        import base64
        import io
        import sqlite3
        from contextlib import closing
        from foundation.server import application, credentials
        with closing(sqlite3.connect(self.path)) as db, db:
            db.executescript("""CREATE TABLE state(id INTEGER,summary TEXT);
            INSERT INTO state VALUES(1,'[]');
            CREATE TABLE practice_drafts(id INTEGER PRIMARY KEY,owner TEXT,data TEXT,state TEXT DEFAULT 'draft',approved TEXT);""")
        users=self.path.parent/'users.json'
        users.write_text(json.dumps([credentials('Teacher A','fake-a'),credentials('Teacher B','fake-b')]))
        def request(route,body=None,who='A',header=True):
            raw=json.dumps(body).encode() if body is not None else b''
            token='Basic '+base64.b64encode(f'Teacher {who}:fake-{who.lower()}'.encode()).decode() if who else ''
            env={'PATH_INFO':'/api/foundation/'+route,'REQUEST_METHOD':'POST' if body is not None else 'GET',
                 'HTTP_AUTHORIZATION':token,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),
                 'QUERY_STRING':'','wsgi.input':io.BytesIO(raw)}
            if header: env['HTTP_X_KB_REQUEST']='teacher'
            status=[]; result=b''.join(application(env,lambda s,h:status.append(s)))
            return int(status[0][:3]),json.loads(result)
        args={'unit':'M2','family':'pythagoras','count':2,'mode':'model'}
        with patch.dict(os.environ,{'KB_DB':str(self.path),'KB_USERS':str(users)}),patch.object(ai,'send') as send:
            self.assertEqual(request('studio',args,who=None)[0],401)
            self.assertEqual(request('studio',args,header=False)[0],415)
            self.assertEqual(request('studio',dict(args,mode='bad'))[0],400)
            with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
                self.assertFalse(request('summary')[1]['studio_ai_configured'])
                self.assertEqual(request('studio',args)[0],503)
                self.assertEqual(request('drafts')[1],[])
                self.assertEqual(request('studio',dict(args,mode='local'))[0],200)
                send.assert_not_called()
            self.assertTrue(request('summary')[1]['studio_ai_configured'])
            send.return_value=response([{'id':0,'variant':0}]*2)
            self.assertEqual(request('studio',args)[0],503)
            self.assertEqual(len(request('drafts')[1]),2)
            send.return_value=response([{'id':0,'variant':1},{'id':1,'variant':0}])
            code,rows=request('studio',args)
            self.assertEqual(code,200); self.assertEqual(len(rows),2)
            self.assertTrue(all(r['mode']=='model' and r['diagram'] for r in rows))
            self.assertEqual(len(request('drafts')[1]),4)
            self.assertEqual(request('drafts',who='B')[1],[])
            draft=rows[0]
            approval={'id':draft['id'],'question':draft['question']}
            self.assertEqual(request('approve',approval,who='B')[0],409)
            self.assertEqual(request('approve',dict(approval,question='Altered'))[0],409)
            self.assertEqual(request('approve',approval)[1]['state'],'approved')
            self.assertEqual(send.call_count,2)

if __name__=='__main__': unittest.main()
