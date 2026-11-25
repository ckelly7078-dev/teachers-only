"""Offline routing checks: no live API requests."""
import json
import os
import unittest
from unittest.mock import patch
from foundation import studio_mixed as mixed


class HybridModeTest(unittest.TestCase):
    def setUp(self):
        self.text = ('M1','percent',{'family':'percent','label':'Percentages'})
        self.diagram = ('M2','pythagoras',{'family':'pythagoras','label':'Pythagoras'})
        self.trap = ('M2','trapezium',{'family':'trapezium','label':'Trapezium'})
        patch.object(mixed,'make_question',side_effect=self.make_row).start()
        self.addCleanup(patch.stopall)

    @staticmethod
    def make_row(choice,d,a,b,c,wording=0):
        u,f,_ = choice
        return dict(unit=u,family=f,question=f'{f}: {a},{b},{c}',marks=2,
                    rubric=['M1','A1'],mode='local',
                    diagram={'kind':'schematic'} if f in ('pythagoras','trapezium') else None)

    @staticmethod
    def response(payload):
        data = json.loads(payload['input'])
        topics, n = data['topics'], data['count']
        assert all(t['diagram'] for t in topics)
        plan = dict(questions=[dict(topic=i%len(topics),a=4+i,b=4,c=4,wording=0)
                               for i in range(n)],guidance='')
        return dict(status='completed',output=[dict(type='message',content=[
            dict(type='output_text',text=json.dumps(plan))])])

    def test_text_only_no_availability_or_send(self):
        with patch.object(mixed.studio_ai,'available',side_effect=AssertionError('No availability check')), patch.object(mixed.studio_ai,'send',side_effect=AssertionError('No API')):
            rows = mixed.hybrid_batch([self.text],5,'standard','Use examples')
        self.assertEqual(len(rows),5)
        self.assertTrue(all(r['mode']=='local' for r in rows))
        self.assertIn('no API request',rows[0]['generation_notice'])

    def test_mixed_one_diagram_only_call(self):
        with patch.dict(os.environ,{'KB_STUDIO_MODEL':'gpt-4.1'}), patch.object(mixed.studio_ai,'available',return_value=True), patch.object(mixed.studio_ai,'send',side_effect=self.response) as send:
            rows = mixed.hybrid_batch([self.text,self.diagram],5,'standard','Use small numbers')
        self.assertEqual(send.call_count,1)
        self.assertEqual([r['mode'] for r in rows],['local','model','local','model','local'])
        self.assertEqual(len({r['question'] for r in rows}),5)
        self.assertNotIn('Percentages',send.call_args.args[0]['input'])
        self.assertIn('Use small numbers',send.call_args.args[0]['input'])
        self.assertIn('3 local question(s), 2 AI-designed',rows[0]['generation_notice'])

    def test_diagram_only(self):
        with patch.dict(os.environ,{'KB_STUDIO_MODEL':'gpt-4.1'}), patch.object(mixed.studio_ai,'available',return_value=True), patch.object(mixed.studio_ai,'send',side_effect=self.response) as send:
            rows = mixed.hybrid_batch([self.diagram,self.trap],4,'standard','')
        self.assertEqual(send.call_count,1)
        self.assertTrue(all(r['mode']=='model' and r['diagram'] for r in rows))
        self.assertEqual({r['family'] for r in rows},{'pythagoras','trapezium'})

    def test_unavailable_diagrams_fail_without_partial_batch(self):
        with patch.object(mixed.studio_ai,'available',return_value=False), patch.object(mixed.studio_ai,'send',side_effect=AssertionError('No API')):
            with self.assertRaises(mixed.studio_ai.StudioAIUnavailable):
                mixed.hybrid_batch([self.text,self.diagram],5,'standard','')


if __name__=='__main__':
    unittest.main()
