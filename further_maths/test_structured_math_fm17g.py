import copy
import unittest
from marking_review import fingerprint
from successor_bq import SuccessorResolver
from test_structured_math_fm17e import encode, fixture
from structured_math_fm17g import DESIGNS, specifications, check_work


class StructuredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=SuccessorResolver([])

    def setup_work(self,path,v=1):
        item=self.r._resolve(path,3,v);return item,{k:encode(z) for _,k,z in specifications(item)}

    def run_work(self,item,work,**kw):
        args=dict(mode='learning_preview',item_fingerprint=fingerprint(item),work=work)|kw
        return check_work(fixture(item),item['id'],**args)

    def test_all_designs_full_and_uncertain(self):
        for path in sorted(DESIGNS):
            for v in (1,2,3):
                item,w=self.setup_work(path,v)
                self.assertEqual(self.run_work(item,w)['possible_total'],[item['marks']]*2,path)
                self.assertEqual(self.run_work(item,dict.fromkeys(w))['possible_total'],[0,item['marks']],path)

    def test_polynomial_division_order_and_consequential_work(self):
        item,w=self.setup_work('solve-cubic')
        w['reduction_1'][3]=['0','-5','-12','160']
        w['reduction_2']=[['1','8'],['0','-5','-12','160'],'-5',['0','0','28','160']]
        w['reduction_3']=[['1','8'],['0','0','28','160'],'28',['0','0','0','-64']]
        w['quotient_and_remainder']=[['1','-5','28'],['0','0','0','-64']]
        w['quadratic_method']=[['1','-5','28'],'-87','2','both_branches'];w['roots']=[['-8','0'],['2','4'],['2','-5']]
        self.assertEqual(self.run_work(item,w)['possible_total'],[3,3])
        w['reduction_1']=None;self.assertEqual(self.run_work(item,w)['criteria'][1]['status'],'uncertain')
        w['reduction_2'][0]=['1','-8'];self.assertEqual(self.run_work(item,w)['criteria'][1]['status'],'not_met')

    def test_equivalent_elimination_and_non_elimination(self):
        item,w=self.setup_work('two-variable-system')
        w['eliminate']=[['-1','2'],['0','7','-49']]
        self.assertEqual(self.run_work(item,w)['possible_total'],[3,3])
        w['eliminate']=[['2','0'],['4','2','2']]
        self.assertEqual(self.run_work(item,w)['possible_total'],[2,2])
        w['eliminate']=[['-1','2'],['0','7','49']]
        self.assertEqual(self.run_work(item,w)['possible_total'],[2,2])

    def test_equivalent_normal_with_matching_verification(self):
        item,w=self.setup_work('plane-intersection-direction');w['direction']=['-12','6','-2'];w['verification'][0]=w['direction']
        self.assertEqual(self.run_work(item,w)['possible_total'],[3,3])
        w['verification'][0]=['6','-3','1'];self.assertEqual(self.run_work(item,w)['possible_total'],[2,3])
        w['direction']=['0','0','0'];w['verification'][0]=w['direction'];self.assertEqual(self.run_work(item,w)['possible_total'],[1,1])

    def test_exact_sign_and_root_order(self):
        item,w=self.setup_work('singular-condition');w['signed_root_squares'].reverse();w['determinant_equation']=['-2','0','12']
        self.assertEqual(self.run_work(item,w)['possible_total'],[2,2]);w['signed_root_squares'][0]=w['signed_root_squares'][1]
        self.assertEqual(self.run_work(item,w)['possible_total'],[1,1])
        for path,field in [('triangle-area','signed_area_square'),('point-line','signed_distance_square')]:
            item,w=self.setup_work(path);w[field][0]='-1';self.assertEqual(self.run_work(item,w)['possible_total'],[1,1])

    def test_inverse_verification_and_stale_reference(self):
        item,w=self.setup_work('inverse-three');w['verification'][0],w['verification'][1]=w['verification'][1],w['verification'][0]
        self.assertEqual(self.run_work(item,w)['possible_total'],[4,4]);w['answer'][0][0]='1'
        self.assertEqual(self.run_work(item,w)['possible_total'],[2,3])
        for args in (dict(item_fingerprint='stale'),dict(mode='approved_exam')):
            with self.assertRaises(ValueError):self.run_work(item,w,**args)
        bad=copy.deepcopy(item);bad['payload']['facts']=[{'matrix':[['0']]}]
        with self.assertRaises(ValueError):specifications(bad)


if __name__=='__main__': unittest.main()
