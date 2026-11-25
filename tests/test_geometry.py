import itertools
import math
import unittest
from collections import Counter
from foundation import geometry as g

class GeometryTest(unittest.TestCase):
    def test_dimension_consistency(self):
        for a,b,c in itertools.product(range(2,19),repeat=3):
            for family in g.FAMILIES:
                layout=g.default_layout(a,b,c)
                d=g.diagram(family,a,b,c,layout)
                poly=d['polygon']
                W=max(x for x,y in poly)-min(x for x,y in poly)
                H=max(y for x,y in poly)-min(y for x,y in poly)
                labels=Counter(t for x,y,t in d['labels'])
                area=abs(sum(x*v-u*y for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1])))/2
                if family=='l-shape':
                    w,h=a+b,b+c
                    if layout&4:w,h=h,w
                    want=(a+b)*(b+c)-b*c
                    self.assertEqual(labels,Counter(f'{n} m' for n in (a+b,b+c,b,c)))
                elif family=='trapezium':
                    w,h=2*(a+b),c; want=(2*a+w)*h/2
                    self.assertEqual(labels,Counter(f'{n} m' for n in (2*a,w,h)))
                else:
                    w,h,z=g.triangle_sides(a,b,c);want=w*h
                    self.assertEqual(w*w+h*h,z*z)
                    self.assertEqual(labels,Counter([f'{w} m',f'{h} m','brace']))
                    x,y,u,v=d['lines'][0]
                    self.assertAlmostEqual(math.hypot(u-x,v-y),z*W/w,places=2)
                self.assertTrue(math.isclose(W/H,w/h,rel_tol=2e-5))
                self.assertTrue(math.isclose(area/(W/w)**2,want,rel_tol=2e-5))
                for x,y in poly+[p for l in d['lines']+d['dimension_lines']+d['guides'] for p in (l[:2],l[2:])]:
                    self.assertTrue(0<=x<=480 and 0<=y<=280)
                for x,y,t in d['labels']:
                    self.assertTrue(30<=x<=450 and 20<=y<=265)
    def test_layouts(self):
        for f in g.FAMILIES:
            diagrams=[g.diagram(f,5,6,8,l) for l in g.LAYOUTS]
            self.assertEqual(len({g.diagram_key(d) for d in diagrams}),8)
        self.assertEqual(g.triangle_sides(2,3,5),(6,8,10))
    def test_reject_bad_layout(self):
        for x in (-1,8,True,'0'):
            with self.assertRaises(ValueError):g.diagram('l-shape',5,6,8,x)

if __name__=='__main__':unittest.main()
