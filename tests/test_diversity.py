"""Tests for the batch-level diversity gate using a bounded model simulation."""
import json
import os
import unittest
from unittest.mock import patch
from foundation import studio_mixed as m, geometry as g

class DiversityTest(unittest.TestCase):
    def row(self,choice,d,a,b,c,wording=0,layout=None):
        u,f,_=choice
        return dict(unit=u,family=f,question=f'{f} {a} {b} {c}',marks=4,
                    mode='local',diagram=g.diagram(f,a,b,c,layout),
                    _diagram_seed=(a,b,c,wording,g.default_layout(a,b,c) if layout is None else layout))
    def test_repeated_geometry_repaired_and_history(self):
        choice=('M2','pythagoras',{})
        with patch.object(m,'make_question',side_effect=self.row):
            # All input questions use the same triangle and same layout; costs differ.
            initial=[self.row(choice,'standard',4,4,c,layout=0)|{'mode':'model'} for c in (4,6,8,10,12)]
            result=m.diversify(initial,[choice],'standard',set())
            self.assertEqual(len({x['diagram_key'] for x in result}),5)
            self.assertEqual(len({x['diagram_shape'] for x in result}),5)
            self.assertEqual(len({x['question'] for x in result}),5)
            self.assertTrue(any('locally varied' in x.get('model_role','') for x in result))
            self.assertTrue(all('_diagram_seed' not in x for x in result))
            old={x['diagram_key'] for x in result}
            later=m.diversify([self.row(choice,'standard',4,4,4,layout=0)],[choice],'standard',old.copy(),{x['diagram_shape'] for x in result})
            self.assertNotIn(later[0]['diagram_key'],old)
    def test_text_only_unchanged(self):
        row={'unit':'M1','family':'percent','question':'Find 20% of 60.','diagram':None,'mode':'local'}
        self.assertEqual(m.diversify([row],[], 'standard',set()),[row])
    def test_invalid_history(self):
        for x in ['not list',[True],['x'*24],['1'*24]*301]:
            with self.assertRaises(ValueError):m.diagram_history({'diagram_history':x})
        self.assertEqual(m.diagram_history({'diagram_history':['a'*24]}),{'a'*24})

if __name__=='__main__':unittest.main()
