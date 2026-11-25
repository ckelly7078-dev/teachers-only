"""Test wall identity rather than simply checking the set of displayed numbers."""
import copy
import itertools
import math
import unittest
from foundation import geometry as g


class MeasurementTest(unittest.TestCase):
    def test_every_layout_and_parameter_combination(self):
        checked=0
        for a,b,c in itertools.product(range(2,19),repeat=3):
            for layout in g.LAYOUTS:
                for f in g.FAMILIES:
                    d=g.diagram(f,a,b,c,layout)
                    poly=d['polygon']
                    W=max(x for x,y in poly)-min(x for x,y in poly)
                    H=max(y for x,y in poly)-min(y for x,y in poly)
                    area=abs(sum(x*v-u*y for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1])))/2
                    if f=='l-shape':
                        w,h=a+b,b+c
                        if layout&4:w,h=h,w
                        expected_area=(a+b)*(b+c)-b*c
                        expected={'outer-width':(5,4,a+b),'outer-height':(0,5,b+c),
                                  'notch-width':(2,3,b),'notch-height':(1,2,c)}
                    elif f=='trapezium':
                        w,h=2*(a+b),c;expected_area=(2*a+w)*c/2
                        expected={'short-base':(0,1,2*a),'long-base':(3,2,w)}
                    else:
                        w,h,z=g.triangle_sides(a,b,c);expected_area=w*h
                        expected={'frame-width':(*( (0,1) if layout&2 else (3,2)),w),
                                  'frame-height':(*( (1,2) if layout&4 else (0,3)),h)}
                        self.assertEqual(w*w+h*h,z*z)
                    self.assertTrue(math.isclose(W/H,w/h,rel_tol=2e-5))
                    self.assertTrue(math.isclose(area/(W/w)**2,expected_area,rel_tol=2e-5))
                    boxes=[]
                    for m in d['measurements']:
                        if m['role'] in expected:
                            i,j,val=expected[m['role']]
                            self.assertEqual(m['source'],[poly[i],poly[j]])
                            self.assertEqual(m['value'],val)
                        else:
                            self.assertEqual(m['role'],'perpendicular-height')
                            self.assertEqual(m['value'],c)
                            p,q=m['source']
                            self.assertEqual(p[0],q[0]);self.assertAlmostEqual(abs(p[1]-q[1]),H,places=3)
                        x,y,t=d['labels'][m['label_index']]
                        # Conservative estimates at the renderer's 16px font size.
                        halfwidth=4.8*len(t)+2
                        box=(x-halfwidth,y-17,x+halfwidth,y+5)
                        self.assertTrue(0<=box[0]<box[2]<=480 and 0<=box[1]<box[3]<=280)
                        self.assertTrue(all(box[2]<=o[0] or box[0]>=o[2] or box[3]<=o[1] or box[1]>=o[3] for o in boxes))
                        boxes.append(box)
                    checked+=1
        self.assertEqual(checked,117912)

    def test_screenshot_values(self):
        d=g.diagram('l-shape',7,5,4,0)
        self.assertEqual({m['role']:m['value'] for m in d['measurements']},
                         {'outer-width':12,'outer-height':9,'notch-width':5,'notch-height':4})
        self.assertEqual(12*9-5*4,88)
        self.assertEqual(12-5,7); self.assertEqual(9-4,5)

    def test_reject_misplaced_values_and_broken_witnesses(self):
        original=g.diagram('l-shape',7,5,4,0)
        bad=[]
        d=copy.deepcopy(original);d['labels'][2][2]='4 m';bad.append(d)
        d=copy.deepcopy(original);d['labels'][2][0]+=20;bad.append(d)
        d=copy.deepcopy(original);d['guides'][4][0]+=10;bad.append(d)
        d=copy.deepcopy(original);d['dimension_lines'][6][2]+=10;bad.append(d)
        d=copy.deepcopy(original);d['dimension_lines'][7][0]+=10;bad.append(d)
        d=copy.deepcopy(original);d['measurements'][2]['source']=d['measurements'][0]['source'];bad.append(d)
        for d in bad:
            with self.assertRaises(ValueError):g.validate_measurements(d,'l-shape',7,5,4,0)
        # Equal-valued dimensions must retain their identities too.
        d=g.diagram('l-shape',5,5,5,0)
        d['measurements'][2]['role'],d['measurements'][3]['role']=d['measurements'][3]['role'],d['measurements'][2]['role']
        with self.assertRaises(ValueError):g.validate_measurements(d,'l-shape',5,5,5,0)
        d=g.diagram('trapezium',6,4,5,2);d['lines'][0][2]+=3
        with self.assertRaises(ValueError):g.validate_measurements(d,'trapezium',6,4,5,2)

if __name__=='__main__':unittest.main()
