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

if __name__=='__main__': unittest.main()
