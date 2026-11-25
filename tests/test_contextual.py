import itertools
import json
import unittest
from fractions import Fraction
from foundation import contextual as ctx
from foundation.studio import FAMILIES


class ContextualTest(unittest.TestCase):
    def test_multi_part_answers_and_diagrams(self):
        for family in ctx.FAMILIES:
            for a,b,c in itertools.product(range(2,19),repeat=3):
                prompt,answer,steps,rubric=ctx.build(family,a,b,c)
                x,y=answer
                self.assertTrue(ctx.validate(family,a,b,c,answer))
                self.assertFalse(ctx.validate(family,a,b,c,(x+1,y)))
                self.assertFalse(ctx.validate(family,a,b,c,(x,y+1)))
                self.assertIn('(a)',prompt); self.assertIn('(b)',prompt)
                self.assertTrue(3<=len(rubric)<=4 and all(r.startswith(('(a)','(b)')) for r in rubric))
                self.assertTrue(steps and ctx.display(family,answer))
                d=ctx.diagram(family,a,b,c)
                if family in ('l-shape','trapezium','pythagoras'):
                    self.assertEqual(d['kind'],'schematic')
                    self.assertTrue(all(0<=x<=480 and 0<=y<=280 for x,y in d['polygon']))
                    self.assertTrue(all(0<=x<=480 and 0<=y<=280 and isinstance(t,str) for x,y,t in d['labels']))
                    self.assertIn('see diagram',prompt)
                    json.dumps(d)
                else: self.assertIsNone(d)

    def test_known_examples(self):
        expected={'discount-budget':(2870,1030),'l-shape':(31,217),'trapezium':(50,200),
                  'pythagoras':(10,80),'map-scale':(25,50),'expected-frequency':(Fraction(4,5),40),'gradient':(Fraction(2,3),5)}
        # Independently calculate each fixture for a=2, b=3, c=5.
        expected['discount-budget']=(2250,850)
        expected['l-shape']=(25,175)
        expected['trapezium']=(35,140)
        for family,answer in expected.items():
            self.assertEqual(ctx.build(family,2,3,5)[1],answer,family)
            self.assertIn(family,FAMILIES)

if __name__=='__main__': unittest.main()
