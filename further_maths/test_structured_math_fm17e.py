import copy
import unittest
from fractions import Fraction
from types import SimpleNamespace
from active_difficulty import Resolver
from successor_bq import SuccessorResolver
from marking_review import fingerprint
from structured_math_fm17e import DESIGNS, specifications, check_work


def encode(value):
    if isinstance(value,(int,Fraction)): return str(value)
    if isinstance(value,(list,tuple)): return [encode(v) for v in value]
    return value


def fixture(item):
    key=item['id']; fp=fingerprint(item)
    context={'id':key,'fingerprint':fp,'marks':item['marks'],'automatic_award':False,'release_allowed':False,
             'criteria':[dict(id=f'c{i}',type=r['type'],marks=r['marks']) for i,r in enumerate(item['payload']['rubric'],1)]}
    def marking_context(k,*,mode,item_fingerprint):
        if k!=key or item_fingerprint!=fp or mode!='learning_preview': raise ValueError('Invalid fixture identity')
        return context
    return SimpleNamespace(bank=SimpleNamespace(items={key:item}),marking_context=marking_context)


class StructuredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver=SuccessorResolver([])

    def item(self,path,v=1):
        return self.resolver._resolve(path,3,v)

    def run_work(self,item,observations,**kwargs):
        args=dict(mode='learning_preview',item_fingerprint=fingerprint(item),work=observations)|kwargs
        return check_work(fixture(item),item['id'],**args)['possible_total']

    def test_cube_consequential_error_retains_both_methods(self):
        item=self.item('cube-sums')
        work=dict(coefficient_ratios=[[['9','1'],['14','1']],['8','14']],identity_work=['S_cubed_minus_3SP','8','14'],answer='176')
        self.assertEqual(self.run_work(item,work),[2,2])
        work['identity_work'][1]='7';self.assertEqual(self.run_work(item,work),[1,1])
        work['coefficient_ratios']=None;self.assertEqual(self.run_work(item,work),[0,2])

    def test_inverse_wrong_determinant_and_inconsistent_verification(self):
        item=self.item('inverse-two')
        work={k:encode(v) for _,k,v in specifications(item)}
        self.assertEqual(self.run_work(item,work),[3,3])
        work['verification'][0],work['verification'][1]=work['verification'][1],work['verification'][0]
        self.assertEqual(self.run_work(item,work),[3,3])
        work['inverse_work'][-2:]=['8','8'];work['answer']=[['1/2','-1/8'],['-1/8','1/4']]
        self.assertEqual(self.run_work(item,work),[1,2])
        work['verification']=[[['2','1'],['1','4']],work['answer'],[['7/8','0'],['0','7/8']]]
        self.assertEqual(self.run_work(item,work),[1,1])
        work['inverse_work'][-1]='7';self.assertEqual(self.run_work(item,work),[0,0])

    def test_cartesian_product_signed_method_and_wrong_answer(self):
        item=self.item('cartesian-product');work={'expansion':[['2','4'],['8','-2'],'i_squared_minus_one'],'answer':['24','27']}
        self.assertEqual(self.run_work(item,work),[1,1]);work['expansion'][1][1]='2'
        self.assertEqual(self.run_work(item,work),[0,0]);work['expansion']=None
        self.assertEqual(self.run_work(item,work),[0,1])

    def test_cross_product_component_credit(self):
        item=self.item('cross-product');work={'component_1':'8','component_2':'4','component_3':'1'}
        self.assertEqual(self.run_work(item,work),[2,2]);work['component_2']=None
        self.assertEqual(self.run_work(item,work),[2,3])

    def test_reject_stale_ineligible_and_unbounded_inputs(self):
        item=self.item('det-two');work={'diagonal_products':[['2','3'],['-2','3']],'answer':'12'}
        for kwargs in (dict(item_fingerprint='stale'),dict(mode='approved_exam'),dict(work={**work,'answer':'1/0'}),dict(work={**work,'answer':True}),dict(work={**work,'extra':1})):
            with self.assertRaises(ValueError):self.run_work(item,work,**kwargs)
        bad=copy.deepcopy(item);bad['payload']['facts']=['13']
        with self.assertRaises(ValueError):specifications(bad)
        with self.assertRaises(ValueError):specifications(self.resolver._resolve('det-two',4,1))

    def test_composition_wrong_order(self):
        item=self.item('composition-order');work={k:encode(v) for _,k,v in specifications(item)}
        self.assertEqual(self.run_work(item,work),[2,2]);work['ordered_factors'].reverse();work['answer']=[['4','2'],['0','1']]
        self.assertEqual(self.run_work(item,work),[0,0])

    def test_equivalent_operand_orders_and_monic_form(self):
        for path,field in [('det-two','diagonal_products'),('scalar-product','component_products'),('cartesian-product','expansion'),('root-squares','identity_work')]:
            item=self.item(path);work={k:encode(v) for _,k,v in specifications(item)}
            if path=='det-two':
                for term in work[field]:term.reverse()
            elif path=='scalar-product':
                work[field].reverse()
                for term in work[field]:term.reverse()
            elif path=='cartesian-product':work[field][0],work[field][1]=work[field][1],work[field][0]
            else:work[field][0]=[['6','1'],['8','1']]
            self.assertEqual(self.run_work(item,work),[item['marks']]*2)

    def test_parallel_requires_signed_multiplier(self):
        item=self.item('zero-cross');work={'cross_product':['0','0','0'],'parallel_work':['parallel','5',['2','4','1'],['-10','-20','-5']]}
        self.assertEqual(self.run_work(item,work),[1,1]);work['parallel_work'][1]='-5'
        self.assertEqual(self.run_work(item,work),[2,2])


if __name__=='__main__':unittest.main()
