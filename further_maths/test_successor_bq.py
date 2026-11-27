import unittest
from active_difficulty import Resolver
from marking_review import fingerprint
from successor_bq import SuccessorResolver, apply_spans, equivalent_span, safe_parts, revise, fields


class SuccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Resolver()._resolve('angle-units',1,1)
        text=fields(cls.base['payload'])['step_1']; start=text.index('pi/180')
        cls.record={'id':cls.base['id'],'predecessor_revision':cls.base['revision'],'predecessor_fingerprint':fingerprint(cls.base),'edits':{'step_1':[{'start':start,'end':start+6,'old':'pi/180','new':r'$\pi/180$'}]}}

    def test_star_not_product(self):
        self.assertTrue(equivalent_span('Q*(x)',r'$Q^{*}(x)$'))
        self.assertFalse(equivalent_span('Q*(x)',r'$Q\cdot(x)$'))
        self.assertTrue(equivalent_span('a*b',r'$a\cdot b$'))

    def test_strict_inequality_preserved(self):
        self.assertFalse(equivalent_span('h<2',r'$h\leq 2$'))
        self.assertFalse(equivalent_span('a^2',r'$a^3$'))
        self.assertTrue(equivalent_span('h<=2',r'$h\leq 2$'))
        self.assertFalse(equivalent_span('sqrt(h+1)',r'$\sqrt{h-1}$'))

    def test_unsafe_tex_rejected(self):
        for text in (r'$\input{secret}$',r'$\end{document}$',r'$x^12$',r'$x^-1$',r'$x$',):
            if text == r'$x$': self.assertEqual(safe_parts(text)[1],'x')
            else:
                with self.assertRaises(ValueError):safe_parts(text)

    def test_successor_preserves_facts(self):
        out=revise(self.base,self.record)
        self.assertEqual(out['revision'],'FM-16BQ');self.assertNotEqual(fingerprint(out),fingerprint(self.base))
        self.assertEqual(out['payload']['facts'],self.base['payload']['facts']);self.assertEqual(out['payload']['rubric'],self.base['payload']['rubric']);self.assertEqual(out['marks'],self.base['marks']);self.assertFalse(out['teacher_approved'])
        self.assertIn(r'$\pi/180$',out['payload']['worked_solution_latex'][0])
        with self.assertRaises(ValueError):revise(out,self.record)

    def test_guard_retained_and_duplicate_rejected(self):
        r=SuccessorResolver([self.record]); self.assertEqual(r.guarded(self.base['id'],'learning_preview')['item']['revision'],'FM-16BQ')
        with self.assertRaises(ValueError):r.guarded('CAL.complex-regions.T3.V1','exam_candidate_preview')
        with self.assertRaises(ValueError):r.guarded(self.base['id'],'approved_exam')
        with self.assertRaises(ValueError):SuccessorResolver([self.record,self.record])

    def test_definition_does_not_prescribe_rank_method(self):
        item=Resolver()._resolve('det-three',5,1);rec={'id':item['id'],'predecessor_revision':item['revision'],'predecessor_fingerprint':fingerprint(item),'edits':{},'definition':'rank_rows'}
        out=revise(item,rec);self.assertTrue(out['payload']['question_latex'].startswith(item['payload']['question_latex']));self.assertNotIn('minor',out['payload']['question_latex']);self.assertEqual(out['payload']['rubric'],item['payload']['rubric'])
