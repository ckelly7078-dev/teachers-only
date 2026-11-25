import json
import os
import unittest
from unittest.mock import patch
from foundation import studio_mixed as mixed, studio_ai


class MixedStudioTest(unittest.TestCase):
    def setUp(self):
        from test_studio import StudioTest
        fixture = StudioTest(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.path = fixture.path
        self.data = dict(units=['M1','M2'],topics=[{'unit':'M1','family':'percent'},
                        {'unit':'M2','family':'hcf'}],count=5,difficulty='standard',mode='local',info='')

    def test_local_coverage_and_unique_questions(self):
        rows = mixed.generate(self.path,self.data)
        self.assertEqual(len(rows),5)
        self.assertEqual({(r['unit'],r['family']) for r in rows},{('M1','percent'),('M2','hcf')})
        self.assertEqual(len({r['question'] for r in rows}),5)
        self.assertEqual([r['unit'] for r in rows],['M1','M2','M1','M2','M1'])
        self.assertTrue(all(r['marks']==len(r['rubric']) for r in rows))

    def test_reject_wrong_controls(self):
        for changes in [dict(units=[]),dict(units=['M1','M1']),dict(count=1),dict(count=True),
                        dict(topics=[{'unit':'M1','family':'percent'}]),
                        dict(topics=[{'unit':'M1','family':'percent'},{'unit':'M2','family':'binary'}]),
                        dict(topics=self.data['topics']*2),dict(info='Use small numbers'),dict(info='a'*501),
                        dict(difficulty='hard'),dict(mode='other')]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                mixed.generate(self.path,self.data|changes)

    def test_mock_ai_and_rejections(self):
        plan={'questions':[dict(topic=i%2,a=4+i,b=5+i,c=6,wording=0) for i in range(5)],'guidance':''}
        def response(p):
            return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(p)}]}]}
        with patch.dict(os.environ,{'KB_STUDIO_MODEL':'gpt-4.1','OPENAI_API_KEY':'test-not-real'}),patch.object(studio_ai,'send',return_value=response(plan)) as send:
            rows=mixed.generate(self.path,self.data|{'mode':'model','info':'Prefer extra percentages.'})
            self.assertEqual(len(rows),5); self.assertTrue(all(r['mode']=='model' for r in rows))
            self.assertEqual(send.call_count,1); self.assertFalse(send.call_args.args[0]['store'])
            self.assertIn('Prefer extra percentages.',send.call_args.args[0]['input'])
            self.assertNotIn('test-not-real',json.dumps(send.call_args.args[0]))
        choices, count, difficulty, _, _=mixed.design_request(self.path,self.data)
        for bad in [plan|{'questions':plan['questions'][:-1]},
                    plan|{'questions':[q|{'topic':0} for q in plan['questions']]},
                    plan|{'questions':[plan['questions'][0]]*5},
                    plan|{'questions':[plan['questions'][0]|{'a':99}]+plan['questions'][1:]},
                    plan|{'questions':[plan['questions'][0]|{'topic':True}]+plan['questions'][1:]},
                    plan|{'questions':[plan['questions'][0]|{'topic':2}]+plan['questions'][1:]}]:
            with self.assertRaises(studio_ai.StudioAIUnavailable):mixed.accept(response(bad),choices,count,difficulty)

if __name__=='__main__': unittest.main()
