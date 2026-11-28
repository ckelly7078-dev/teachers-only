import copy
import unittest
from marking_review import fingerprint
from successor_bq import SuccessorResolver
from test_structured_math_fm17e import encode, fixture
from structured_math_fm17f import DESIGNS, specifications, check_work


class ExtendedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.resolver=SuccessorResolver([])

    def setup_work(self,path):
        item=self.resolver._resolve(path,3,1)
        return item,{k:encode(v) for _,k,v in specifications(item)}

    def run_work(self,item,work,**kw):
        args=dict(mode='learning_preview',item_fingerprint=fingerprint(item),work=work)|kw
        return check_work(fixture(item),item['id'],**args)['possible_total']

    def test_all_designs_have_bound_exact_reference(self):
        for path in sorted(DESIGNS):
            for v in (1,2,3):
                item=self.resolver._resolve(path,3,v);work={k:encode(val) for _,k,val in specifications(item)}
                self.assertEqual(self.run_work(item,work),[item['marks']]*2,path)
                self.assertEqual(self.run_work(item,dict.fromkeys(work)),[0,item['marks']],path)

    def test_transformed_roots_follow_through(self):
        item,w=self.setup_work('scaled-roots');w['recover'][-1]=['7','12'];w['transform'][1]='7';w['coefficients']=['1','49','588']
        self.assertEqual(self.run_work(item,w),[2,2]);w['transform'][1]='8'
        self.assertEqual(self.run_work(item,w),[1,1]);w['recover']=None
        self.assertEqual(self.run_work(item,w),[1,2])
        item,w=self.setup_work('combined-roots');w['translate'][-1]=['2','0'];w['transform'][1:]=['2','0'];w['coefficients']=['1','0','0']
        self.assertEqual(self.run_work(item,w),[1,1])
        w['translate'][-1]=['2','-6'];w['transform'][1:]=['2','-6']
        self.assertEqual(self.run_work(item,w),[2,2])

    def test_root_and_factor_order(self):
        for path,field in [('conjugate-deduction','roots'),('conjugate-factor','factors')]:
            item,w=self.setup_work(path);w[field].reverse();self.assertEqual(self.run_work(item,w),[2,2]);w[field][0]=w[field][1]
            self.assertEqual(self.run_work(item,w),[1,1])

    def test_plane_accepts_equivalent_bases_but_not_a_line(self):
        item,w=self.setup_work('vector-plane');w['plane']=[['3','6','4'],['4','0','2'],['2','4','1'],'real_parameters']
        self.assertEqual(self.run_work(item,w),[2,3]);w['independence']=[['4','0','2'],['2','4','1'],['-8','0','16']]
        self.assertEqual(self.run_work(item,w),[3,3]);w['plane'][2]=['8','0','4']
        self.assertEqual(self.run_work(item,w),[1,2]);w['plane'][2]=['2','4','1'];w['plane'][0]=['3','6','5']
        self.assertEqual(self.run_work(item,w),[2,2]);w['plane'][0]=['3','6','4'];w['plane'][3]='positive_parameters'
        self.assertEqual(self.run_work(item,w),[2,2])

    def test_normal_verification_must_be_nonzero_and_consistent(self):
        item,w=self.setup_work('cross-normal');w['verification'][0]=['0','0','0'];self.assertEqual(self.run_work(item,w),[1,1])
        w['verification'][0]=['4','-2','8'];self.assertEqual(self.run_work(item,w),[1,2])
        w['normal']=['4','-2','8'];self.assertEqual(self.run_work(item,w),[1,1])

    def test_restrictions_and_exact_identity(self):
        item,w=self.setup_work('vector-line-equation');w['line'][2]='nonnegative_parameter';self.assertEqual(self.run_work(item,w),[1,1])
        item,w=self.setup_work('det-three');w['cofactors'][1][1]='1';self.assertEqual(self.run_work(item,w),[1,1])
        for args in (dict(mode='approved_exam'),dict(item_fingerprint='stale'),dict(work={**w,'answer':'1/0'}),dict(work={**w,'extra':None})):
            changed=dict(w);changed.update(args.pop('work',{})) if 'work' in args else None
            with self.assertRaises(ValueError):self.run_work(item,changed,**args)
        bad=copy.deepcopy(item);bad['payload']['facts']=['99']
        with self.assertRaises(ValueError):specifications(bad)
        with self.assertRaises(ValueError):specifications(self.resolver._resolve('det-three',4,1))


if __name__=='__main__':unittest.main()
