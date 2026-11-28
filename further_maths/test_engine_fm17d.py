import copy
import unittest
from types import SimpleNamespace
from engine_fm17d import Engine, reconcile_proposal
from marking_review import fingerprint
from source_coverage_fm17c import route_signature
from source_proposal_fm17d import source_bounds
from structured_math_fm17d import check_work


class Fixture:
    def __init__(self):
        self.items={}
        for skill,path,marks in [('alpha','a',(2,3,4)),('beta','b',(1,2,3))]:
            for i,n in enumerate(marks,1):
                key=f'{path}{i}'
                self.items[key]={'id':key,'revision':'fixture','scope':'syllabus_linked_candidate','marks':n,'teacher_approved':False,
                    'payload':{'focus_skill':skill,'path':path,'tier':3,'question_latex':key,'final_answer_latex':'fixture',
                               'worked_solution_latex':['fixture'],'rubric':[{'type':'M','marks':n,'criterion':'fixture'}],
                               'demand_rationale':'fixture','assessment_role':'direct_focus_task'}}
        self.skills={s:{'label':s,'concept_id':s} for s in ('alpha','beta')}
        self.levels={3:{'label':'Procedure'}};self.links={'alpha':[], 'beta':[]};self.parts={}
    def select(self,skill,tier,*,mode):
        return [{'item':copy.deepcopy(i),'fingerprint':fingerprint(i),'mode':mode} for i in self.items.values()
                if i['payload']['focus_skill']==skill and tier==3 and mode=='learning_preview']


class EngineTests(unittest.TestCase):
    def setUp(self):
        bank=Fixture();pages=[dict(id=k,revision=i['revision'],fingerprint=fingerprint(i),page=n,marks=i['marks'],teacher_approved=False,reference_diagram=None)
                             for n,(k,i) in enumerate(bank.items.items(),1)]
        self.e=Engine(bank,{},SimpleNamespace(skill_components=lambda s:[]),pages,'a'*64)
        self.groups=[{'skill':'alpha','tier':3,'count':1},{'skill':'beta','tier':3,'count':2}]
    def test_exact_total_quota_exclusion_and_reproducibility(self):
        a=self.e.generate(self.groups,mode='learning_preview',total_marks=7,exclude_ids=['a1'],seed=10)
        self.assertEqual(a,self.e.generate(self.groups,mode='learning_preview',total_marks=7,exclude_ids=['a1'],seed=10))
        self.assertEqual(a['total_marks'],7); self.assertEqual(len(a['questions']),3)
        self.assertNotIn('a1',[r['item_id'] for r in a['questions']]);self.assertFalse(a['release_allowed'])
        for r in a['questions']:
            self.assertNotIn('source_parts',r);self.assertFalse(r['difficulty_calibrated']);self.assertEqual(r['state'],'draft')
            self.assertEqual(r['marks'],sum(c['marks'] for c in r['typed_rubric']))
        a['questions'][0]['typed_rubric'].clear();self.assertTrue(self.e.bank.items['a2']['payload']['rubric'])
    def test_invalid_requests_fail_closed(self):
        for kwargs in (dict(mode='approved_exam'),dict(mode='exam_candidate_preview'),dict(mode='learning_preview',total_marks=1),
                       dict(mode='learning_preview',total_marks=True),dict(mode='learning_preview',exclude_ids=['a1','a2','a3']),
                       dict(mode='learning_preview',seed=-1)):
            with self.assertRaises(ValueError):self.e.generate(self.groups,**kwargs)
        for groups in (self.groups+self.groups,[dict(skill='alpha',tier=True,count=1)],[dict(skill='alpha',tier=3,count=4)]):
            with self.assertRaises(ValueError):self.e.generate(groups,mode='learning_preview')
    def test_stale_reference_rejected(self):
        self.e.pages['a1']['fingerprint']='stale'
        with self.assertRaises(ValueError):self.e.generate([self.groups[0]],mode='learning_preview',total_marks=2)
    def test_uncertainty_not_implicit_partial_credit(self):
        c=dict(id='a',fingerprint='f',marks=3,criteria=[dict(id='c1',marks=1),dict(id='c2',marks=2)],automatic_award=False,release_allowed=False)
        rows=[dict(criterion_id='c1',status='met',evidence='fixture'),dict(criterion_id='c2',status='uncertain',evidence='fixture')]
        self.assertEqual(reconcile_proposal(c,rows)['possible_total'],[1,3])
        for bad in ([rows[0],rows[0]],[rows[0],dict(rows[1],status='partial')],[rows[0],dict(rows[1],evidence='')]):
            with self.assertRaises(ValueError):reconcile_proposal(c,bad)


class SourceTests(unittest.TestCase):
    def test_explicit_caps_partial_and_single_route(self):
        record={'routes':[{'id':'primary','stages':[{'id':'s1','marks':1,'partial_credit':None},{'id':'s2','marks':2,'partial_credit':'one per feature'}],
                           'exceptions':[{'kind':'cap','stages':['s1'],'max_marks':1}]},
                          {'id':'other','stages':[{'id':'s1','marks':3,'partial_credit':None}],'exceptions':[]}]}
        cov=SimpleNamespace(part=lambda k:{'status':'source_breakdown_available','record':record})
        rows=[dict(stage_id='s1',status='met',partial_marks=None,evidence='fixture'),dict(stage_id='s2',status='partial',partial_marks=1,evidence='fixture')]
        def run(rows=rows,**kw):return source_bounds(cov,('x',1,1),signature=route_signature(record),route_id='primary',observations=rows,**kw)
        self.assertEqual(run()['possible_total'],[2,2]);self.assertFalse(run()['automatic_award'])
        exception=[dict(index=0,evidence='fixture')]
        with self.assertRaises(ValueError):run(exceptions=exception)
        self.assertEqual(run([rows[0],dict(rows[1],status='uncertain',partial_marks=None)],exceptions=exception)['possible_total'],[1,1])
        record['routes'][0]['stages'][1]['partial_credit']=None
        with self.assertRaises(ValueError):run()
        with self.assertRaises(ValueError):source_bounds(cov,('x',1,1),signature='stale',route_id='primary',observations=rows)
        with self.assertRaises(ValueError):source_bounds(cov,('x',1,1),signature=route_signature(record),route_id='other',observations=rows)


class StructuredTests(unittest.TestCase):
    def test_root_correct_method_arithmetic_slip_and_other_method(self):
        p={'tier':3,'path':'root-sum-product','question_latex':'Without solving the equation $2 x^{2} - 7 x + 4$ = 0, calculate the sum and product of its roots.','facts':['7/2','2']}
        c=dict(id='fixture',fingerprint='f',marks=2,criteria=[dict(id='c1',type='M',marks=1),dict(id='c2',type='A',marks=1)],automatic_award=False,release_allowed=False)
        e=SimpleNamespace(bank=SimpleNamespace(items={'fixture':{'payload':p}}),marking_context=lambda *a,**kw:c)
        def run(method,operands,answer):return check_work(e,'fixture',mode='learning_preview',item_fingerprint='f',work=dict(method=method,operands=operands,answer=answer))['possible_total']
        self.assertEqual(run('ratio',[['7','2'],['4','2']],['7/2','3']),[1,1])
        self.assertEqual(run('monic',[['7/2','1'],['2','1']],['7/2','2']),[2,2])
        self.assertEqual(run('other',None,['7/2','2']),[1,2])
        self.assertEqual(run('ratio',[['-7','2'],['4','2']],['-7/2','2']),[0,0])
        self.assertEqual(run('ratio',[['7','0'],['4','2']],['7/2','2']),[1,1])


if __name__=='__main__': unittest.main()
