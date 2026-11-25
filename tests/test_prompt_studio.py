import itertools
import json
import os
import unittest
from unittest.mock import patch
from foundation import shopping, studio, studio_prompt as prompt, studio_ai


def response(plan):
    return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(plan)}]}]}


def plan(**kw):
    return dict(supported=True,reason='',count=1,requested_marks=4,
                questions=[dict(family='shopping-discount',difficulty='standard',a=9,b=5,c=5)]) | kw


class PromptTest(unittest.TestCase):
    def test_shopping_exact_arithmetic(self):
        for a,b,c in itertools.product(range(2,19),repeat=3):
            q,ans,steps,rubric=shopping.build(a,b,c)
            self.assertTrue(shopping.validate(a,b,c,ans))
            for i in range(3):
                bad=tuple(v+(i==j) for j,v in enumerate(ans))
                self.assertFalse(shopping.validate(a,b,c,bad))
            self.assertEqual(len(rubric),4)
        self.assertEqual(shopping.build(9,5,5)[1],(4500,13500,500))

    def test_prompt_plans(self):
        from test_studio import StudioTest
        fixture=StudioTest();fixture.setUp();self.addCleanup(fixture.doCleanups)
        families={e['family']:e for e in studio.catalog(fixture.path,'M1')}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake-test-only','KB_STUDIO_MODEL':'gpt-4.1'}),patch.object(studio_ai,'send',return_value=response(plan())) as send:
            rows=prompt.author(fixture.path,'M1','One 4-mark bicycle discount question')
            self.assertEqual(rows[0]['answer'],'(a) £45.00; (b) £135.00; (c) £5.00')
            self.assertEqual(rows[0]['marks'],4)
            self.assertEqual(rows[0]['mode'],'model')
            payload=send.call_args.args[0]
            self.assertFalse(payload['store'])
            self.assertNotIn('fake-test-only',json.dumps(payload))
        for invalid in [plan(count=True),plan(requested_marks=3),plan(count=2),plan(questions=[dict(family='binary',difficulty='standard',a=9,b=5,c=5)]),plan(questions=[dict(family='shopping-discount',difficulty='standard',a=99,b=5,c=5)]),plan(questions=[dict(family='shopping-discount',difficulty='standard',a=True,b=5,c=5)]),plan(count=2,questions=plan()['questions']*2),plan(supported=False,questions=[],reason='Not supported')]:
            with self.assertRaises(studio_ai.StudioAIUnavailable):prompt.accept(response(invalid),'M1',families)
        with self.assertRaises(studio_ai.StudioAIUnavailable):prompt.accept({'status':'incomplete'},'M1',families)

    def test_builtin_example_schema_and_fallback(self):
        from test_studio import StudioTest
        fixture=StudioTest();fixture.setUp();self.addCleanup(fixture.doCleanups)
        q=plan()['questions'][0]
        valid=plan(count=3,questions=[dict(q,a=a) for a in (8,9,10)])
        invalid=plan(count=3,questions=[q]*3)
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake-test-only','KB_STUDIO_MODEL':'gpt-4.1'}):
            with patch.object(studio_ai,'send',return_value=response(valid)) as send:
                rows=prompt.author(fixture.path,'M1',prompt.SHOPPING_EXAMPLE)
                self.assertEqual(len(rows),3)
                self.assertTrue(all(r['mode']=='model' and r['marks']==4 for r in rows))
                schema=send.call_args.args[0]['text']['format']['schema']['properties']
                self.assertEqual(schema['count']['enum'],[3])
                self.assertEqual(schema['requested_marks']['enum'],[4])
                self.assertEqual(schema['questions']['items']['properties']['family']['enum'],['shopping-discount'])
                self.assertEqual(schema['questions']['items']['properties']['a']['enum'],list(range(4,13)))
            for failure in (response(invalid),response(plan()),response(plan(supported=False,questions=[],reason='declined')),{'status':'incomplete'}):
                with patch.object(studio_ai,'send',return_value=failure) as send:
                    rows=prompt.author(fixture.path,'M1',prompt.SHOPPING_EXAMPLE)
                    self.assertEqual(send.call_count,1)
                    self.assertEqual(len({r['question'] for r in rows}),3)
                    self.assertTrue(all(r['mode']=='local' and r['marks']==4 and 'locally instead' in r['generation_notice'] for r in rows))
            with patch.object(studio_ai,'send',return_value=response(invalid)):
                with self.assertRaisesRegex(prompt.InvalidPlan,'duplicate questions'):
                    prompt.author(fixture.path,'M1','Three four-mark shopping questions')

if __name__=='__main__':unittest.main()
