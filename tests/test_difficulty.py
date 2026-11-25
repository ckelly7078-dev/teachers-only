import copy
import itertools
import re
import unittest
from foundation import composite, difficulty, studio, studio_mixed as mixed


class DifficultyTest(unittest.TestCase):
    def test_progression_every_family(self):
        for family,(_,_,_,units) in studio.FAMILIES.items():
            choice=(units[0],family,{'spec_page':10})
            easy,medium,hard=[mixed.make_question(choice,d,5,5,5) for d in ('easy','standard','challenge')]
            self.assertEqual(len({r['question'] for r in (easy,medium,hard)}),3,family)
            self.assertGreater(hard['marks'],medium['marks'],family)
            self.assertLessEqual(easy['marks'],medium['marks'],family)
            for row in (easy,medium,hard):
                self.assertEqual(row['marks'],len(row['rubric']))
                self.assertTrue(row['difficulty_features'])
                parts=re.findall(r'\(([a-z])\)\s',row['question'])
                if parts:
                    self.assertEqual(set(parts),{r[1] for r in row['rubric'] if r.startswith('(')},family)

    def test_composite_all_supported_parameters(self):
        for level,(lo,hi) in mixed.DOMAINS.items():
            for a,b,c in itertools.product(range(lo,hi+1),repeat=3):
                answer=composite.answers(level,a,b,c)
                self.assertTrue(composite.validate(level,a,b,c,answer))
                for i in range(len(answer)):
                    self.assertFalse(composite.validate(level,a,b,c,tuple(v+int(i==j) for j,v in enumerate(answer))))
                for layout in range(8):
                    d=composite.diagram(level,a,b,c,layout)
                    self.assertTrue(composite.validate_diagram(d,level,a,b,c,layout))
                    # Conservative text bounds for 16px centred, horizontal or
                    # vertical dimension text, including a small stroke margin.
                    boxes=[]
                    for (x,y,t),angle in zip(d['labels'],d['label_angles']):
                        w,h=8*len(t)+4,18
                        if angle: w,h=h,w
                        box=(x-w/2,y-h/2,x+w/2,y+h/2)
                        self.assertTrue(0<=box[0] and box[2]<=480 and 0<=box[1] and box[3]<=280)
                        for b2 in boxes:
                            self.assertFalse(min(box[2],b2[2])-max(box[0],b2[0])>1 and min(box[3],b2[3])-max(box[1],b2[1])>1,(level,a,b,c,layout,box,b2))
                        boxes.append(box)
                    # Every edge measurement is attached to a named wall.
                    m={m['role']:m['value'] for m in d['measurements']}
                    widths,heights=composite.profile(level,a,b,c)
                    if level=='easy':
                        self.assertEqual(set(m),{'strip-1-width','strip-2-width','left-height','right-height'})
                        self.assertEqual(answer[0],m['strip-1-width']*m['left-height']+m['strip-2-width']*m['right-height'])
                        self.assertEqual(len(d['construction_lines']),1)
                    elif level=='standard':
                        self.assertEqual(set(m),{'overall-width','strip-1-width','left-height','right-height'})
                        self.assertEqual(answer[0],m['strip-1-width']*m['left-height']+(m['overall-width']-m['strip-1-width'])*m['right-height'])
                    else:
                        self.assertEqual(set(m),{'overall-width','strip-1-width','strip-3-width','left-height','right-height','first-step-height'})
                        middle_width=m['overall-width']-m['strip-1-width']-m['strip-3-width']
                        # The side of the step relative to the known baseline
                        # supplies direction; no length is estimated visually.
                        by_role={m['role']:m for m in d['measurements']}
                        n=by_role['overall-width']['normal'];p,q=by_role['first-step-height']['source']
                        direction=sum((v-u)*z for u,v,z in zip(p,q,n))
                        middle_height=m['left-height']+(m['first-step-height'] if direction<0 else -m['first-step-height'])
                        self.assertEqual((middle_width,middle_height),(widths[1],heights[1]))
                        self.assertEqual(answer[0],m['strip-1-width']*m['left-height']+middle_width*middle_height+m['strip-3-width']*m['right-height'])

    def test_label_mutations_rejected(self):
        d=composite.diagram('challenge',9,12,10,7)
        for mutation in ('label','edge','witness','tick','role','angle'):
            bad=copy.deepcopy(d)
            if mutation=='label':bad['labels'][0][2]='999 m'
            if mutation=='edge':bad['measurements'][0]['source'][0][0]+=5
            if mutation=='witness':bad['guides'][0][0]+=5
            if mutation=='tick':bad['dimension_lines'][1][0]+=5
            if mutation=='role':bad['measurements'][0]['role']='right-height'
            if mutation=='angle':bad['label_angles'][0]=45
            with self.assertRaises(ValueError):composite.validate_diagram(bad,'challenge',9,12,10,7)

    def test_diagram_batches_and_prior_history(self):
        choice=('M1','l-shape',{'spec_page':14})
        for level in ('easy','standard','challenge'):
            rows=mixed.local_batch([choice],10,level)
            self.assertEqual(len({mixed.question_key(r) for r in rows}),10)
            rows=mixed.diversify(rows,[choice],level,set())
            self.assertEqual(len({r['diagram_key'] for r in rows}),10)
            used={r['diagram_key'] for r in rows}
            new=mixed.diversify(mixed.local_batch([choice],10,level),[choice],level,used.copy(),{r['diagram_shape'] for r in rows})
            self.assertTrue(used.isdisjoint(r['diagram_key'] for r in new))

if __name__=='__main__':unittest.main()
