"""Synthetic source-free tests for method certificates and explicit split credit."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from marking_review import fingerprint
from reasoning_fm17j import ReasoningMarking, certificate, product_followthrough, product_pair_credit


class Certificates(unittest.TestCase):
    def test_alternatives_and_unknown(self):
        spec={'rule':'alternatives','target':{'first':['equal',['2','3']], 'second':['proportional',['2','3']]}}
        self.assertEqual(certificate(spec,{'method':'first','evidence':['2','3']}),'met')
        self.assertEqual(certificate(spec,{'method':'second','evidence':['-4','-6']}),'met')
        self.assertEqual(certificate(spec,{'method':'first','evidence':['3','2']}),'not_met')
        self.assertEqual(certificate(spec,{'method':'other','evidence':None}),'uncertain')
        self.assertEqual(certificate(spec,None),'uncertain')
        with self.assertRaises(ValueError):certificate(spec,{'method':'other','evidence':['2','3']})

    def test_elimination_scaled_or_reversed(self):
        spec={'rule':'row_combination','target':{'rows':[['1','1','4'],['2','3','9']],'row':['0','1','1']}}
        for weights,row in [(['-2','1'],['0','1','1']),(['4','-2'],['0','-2','-2'])]:
            self.assertEqual(certificate(spec,{'multipliers':weights,'row':row}),'met')
        for weights,row in [(['0','0'],['0','0','0']),(['1','1'],['0','1','1']),(['-2','1'],['0','1','2'])]:
            self.assertEqual(certificate(spec,{'multipliers':weights,'row':row}),'not_met')

    def test_dependency_requires_conclusion(self):
        spec={'rule':'row_dependency','target':{'rows':[['1','2','4'],['3','6','13']],'consistent':False,'conclusion':'no_solution'}}
        correct={'multipliers':['-3','1'],'residual':'1','conclusion':'no_solution'}
        self.assertEqual(certificate(spec,correct),'met')
        self.assertEqual(certificate(spec,{**correct,'conclusion':'unique'}),'not_met')
        self.assertEqual(certificate(spec,{**correct,'residual':'0'}),'not_met')
        self.assertEqual(certificate(spec,{**correct,'multipliers':['0','0']}),'not_met')

    def test_row_addition_multiple_routes(self):
        spec={'rule':'row_addition','target':[['2','1'],['4','3']]}
        for value in [dict(destination=1,source=0,scale='-2',matrix=[['2','1'],['0','1']]),dict(destination=0,source=1,scale='-1/2',matrix=[['0','-1/2'],['4','3']])]:
            self.assertEqual(certificate(spec,value),'met')
        self.assertEqual(certificate(spec,{**value,'matrix':[['0','0'],['4','3']]}),'not_met')
        with self.assertRaises(ValueError):certificate(spec,{**value,'destination':True})

    def test_complete_line_not_just_one_point(self):
        spec={'rule':'affine_line_proof','target':[['1','2','0','4'],['0','0','1','3']]}
        v=dict(point=['4','0','3'],direction=['-2','1','0'],substitutions=[['4','0'],['3','0']],conclusion='complete_line_two_independent_equations')
        self.assertEqual(certificate(spec,v),'met')
        self.assertEqual(certificate(spec,{**v,'point':['2','1','3'],'direction':['4','-2','0']}),'met')
        self.assertEqual(certificate(spec,{**v,'direction':['0','0','0']}),'not_met')
        self.assertEqual(certificate(spec,{**v,'point':['3','0','3']}),'not_met')
        self.assertEqual(certificate(spec,{**v,'conclusion':'some_points'}),'not_met')


class ProductTests(unittest.TestCase):
    spec={'target':['2','3']}
    comp=['2','3','6']
    xeq={'variable':'x','coefficients':['3','1','-2','12']}
    yeq={'variable':'y','coefficients':['2','-1','-3','18']}
    xroots={'discriminant':['1','24','-144'],'roots':[['-1/6','-1/6'],['-1/6','1/6']], 'reconstruction':[['1/4','-1/4'],['1/4','1/4']]}
    yroots={'discriminant':['1','24','-144'],'roots':[['1/4','1/4'],['1/4','-1/4']], 'reconstruction':[['-1/6','1/6'],['-1/6','-1/6']]}

    def test_both_eliminations_and_scale(self):
        for eq in (self.xeq,self.yeq,{'variable':'x','coefficients':['-6','-2','4','-24']}):
            self.assertEqual(product_followthrough(self.spec,eq,self.comp),('met',False))
        self.assertEqual(product_followthrough(self.spec,self.xeq,['2','3','7']),('not_met',False))
        self.assertEqual(product_followthrough(self.spec,self.xeq,['1','3','6']),('uncertain',False))
        self.assertEqual(product_followthrough(self.spec,self.xeq,None),('uncertain',False))
        self.assertEqual(product_followthrough(self.spec,{'variable':'x','coefficients':['0']*4},self.comp),('not_met',False))

    def test_split_credit_and_branch_order(self):
        for eq,roots in ((self.xeq,self.xroots),(self.yeq,self.yroots)):
            self.assertEqual(product_pair_credit(self.spec,roots,self.comp,eq),(['met','met'],False))
            self.assertEqual(product_pair_credit(self.spec,{**roots,'reconstruction':None},self.comp,eq),(['met','uncertain'],False))
            self.assertEqual(product_pair_credit(self.spec,{**roots,'reconstruction':roots['reconstruction'][::-1]},self.comp,eq),(['met','not_met'],False))
            self.assertEqual(product_pair_credit(self.spec,{**roots,'roots':[roots['roots'][0]]*2},self.comp,eq),(['not_met','uncertain'],False))
        self.assertEqual(product_pair_credit(self.spec,self.xroots,self.comp,None),(['uncertain','uncertain'],False))

    def test_explicit_followthrough_only(self):
        comp=['2','3','7'];eq={'variable':'x','coefficients':['3','1','-2','14']};roots={**self.xroots,'discriminant':['1','24','-168']}
        self.assertEqual(product_followthrough(self.spec,eq,comp),('met',True))
        self.assertEqual(product_pair_credit(self.spec,roots,comp,eq),(['met','met'],True))
        self.assertEqual(product_pair_credit(self.spec,self.xroots,comp,eq),(['not_met','uncertain'],False))
        self.assertEqual(product_pair_credit(self.spec,roots,['2','4','7'],eq),(['uncertain','uncertain'],False))


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.item=dict(id='fixture',revision='test',scope='test',marks=2,payload=dict(tier=2,path='synthetic',rubric=[dict(type='M',marks=1,criterion='Synthetic method.'),dict(type='A',marks=1,criterion='Synthetic answer.')]))
        self.fp=fingerprint(self.item)
        self.profile=dict(id='fixture',revision='test',fingerprint=self.fp,basis='prompt_bound_method_certificates',criteria=[dict(index=1,type='M',marks=1,rule='alternatives',target={'multiply':['equal',['2','3']]},reference=dict(method='multiply',evidence=['2','3']))])
        self.engine=SimpleNamespace(bank=SimpleNamespace(items={'fixture':self.item}),marking_context=self.context)
        self.prior=SimpleNamespace(capability=self.old_cap,check_work=self.old_work)
        self.args=dict(mode='learning_preview',item_fingerprint=self.fp)
        self.valid=dict(accuracy={'c2':'6'},reasoning={'c1':self.profile['criteria'][0]['reference']})
    def context(self,id,*,mode,item_fingerprint):
        if id!='fixture' or mode!='learning_preview' or item_fingerprint!=self.fp:raise ValueError('Invalid context')
        return dict(id=id,fingerprint=self.fp,marks=2,automatic_award=False,release_allowed=False,criteria=[dict(id='c1',type='M',marks=1),dict(id='c2',type='A',marks=1)])
    def old_cap(self,*a,**kw):
        self.context(*a,**kw);return dict(structured_checks_available=True,checked_criteria=['c2'],coverage='partial')
    def old_work(self,*a,work,**kw):
        from engine_fm17d import reconcile_proposal
        c=self.context(*a,**kw)
        if set(work)!={'c2'}:raise ValueError('Unexpected fields')
        status='uncertain' if work['c2'] is None else 'met' if work['c2']=='6' else 'not_met'
        return reconcile_proposal(c,[dict(criterion_id='c1',status='uncertain',evidence='No method'),dict(criterion_id='c2',status=status,evidence='Synthetic check')])
    def marker(self,rows=None):return ReasoningMarking(self.engine,self.prior,[self.profile] if rows is None else rows)
    def test_preserve_accuracy_only_and_correct_answer_wrong_method(self):
        m=self.marker();self.assertEqual(m.check_work('fixture',work={'c2':'6'},**self.args),self.old_work('fixture',work={'c2':'6'},**self.args))
        self.assertEqual(m.capability('fixture',**self.args)['coverage'],'full')
        for method,answer,bounds in [(None,'6',[1,2]),({'method':'multiply','evidence':['3','3']},'6',[1,1]),(self.valid['reasoning']['c1'],'5',[1,1]),(self.valid['reasoning']['c1'],'6',[2,2])]:
            result=m.check_work('fixture',work={'reasoning':{'c1':method},'accuracy':{'c2':answer}},**self.args)
            self.assertEqual(result['possible_total'],bounds)
            self.assertFalse(any(result[k] for k in ('automatic_award','release_allowed','teacher_approved')))
    def test_gates_and_profiles(self):
        for args in [dict(self.args,mode='approved_exam'),dict(self.args,item_fingerprint='stale')]:
            with self.assertRaises(ValueError):self.marker().check_work('fixture',work=self.valid,**args)
        for work in [dict(self.valid,extra=True),dict(self.valid,reasoning={}),dict(self.valid,accuracy={})]:
            with self.assertRaises(ValueError):self.marker().check_work('fixture',work=work,**self.args)
        bad=copy.deepcopy(self.profile);bad['criteria'][0]['marks']=2
        with self.assertRaises(ValueError):self.marker([bad])
        with self.assertRaises(ValueError):self.marker([self.profile,self.profile])
    def test_manifest_tamper(self):
        with tempfile.TemporaryDirectory() as root,patch('reasoning_fm17j.TierMarking.from_bundle',return_value=self.prior):
            p=Path(root)/'FM17J';p.mkdir();f=p/'profiles.jsonl';f.write_text(json.dumps(self.profile)+'\n')
            manifest=dict(checkpoint='FM-17J',profile_count=1,sha256={'profiles.jsonl':hashlib.sha256(f.read_bytes()).hexdigest()});(p/'runtime-manifest.json').write_text(json.dumps(manifest))
            self.assertEqual(ReasoningMarking.from_bundle(self.engine,root).check_work('fixture',work=self.valid,**self.args)['possible_total'],[2,2])
            f.write_text('{}\n')
            with self.assertRaises(ValueError):ReasoningMarking.from_bundle(self.engine,root)


if __name__=='__main__':unittest.main()
