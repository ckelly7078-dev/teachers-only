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

if __name__=='__main__':unittest.main()
