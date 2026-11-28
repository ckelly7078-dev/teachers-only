import unittest
from marking_review import fingerprint
from successor_bq import SuccessorResolver
from test_structured_math_fm17e import encode,fixture
from marking_dispatch_fm17g import capability, check_work, supported_designs
from structured_math_fm17e import specifications as e
from structured_math_fm17f import specifications as f
from structured_math_fm17g import specifications as g


class DispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=SuccessorResolver([])

    def test_each_batch_dispatches(self):
        self.assertEqual(len(supported_designs()),65)
        for path,spec in [('det-two',e),('vector-plane',f),('solve-cubic',g)]:
            item=self.r._resolve(path,3,1);engine=fixture(item);args=dict(mode='learning_preview',item_fingerprint=fingerprint(item))
            work={k:encode(v) for _,k,v in spec(item)}
            self.assertTrue(capability(engine,item['id'],**args)['structured_checks_available'])
            self.assertEqual(check_work(engine,item['id'],work=work,**args)['possible_total'],[item['marks']]*2)
        item=self.r._resolve('root-sum-product',3,1);engine=fixture(item);args=dict(mode='learning_preview',item_fingerprint=fingerprint(item))
        work={'method':'other','operands':None,'answer':['0','0']}
        self.assertEqual(check_work(engine,item['id'],work=work,**args)['possible_total'],[0,1])

    def test_unsupported_does_not_award(self):
        for path,tier in [('det-two',4),('argand-coordinates',3)]:
            item=self.r._resolve(path,tier,1);engine=fixture(item);args=dict(mode='learning_preview',item_fingerprint=fingerprint(item))
            result=capability(engine,item['id'],**args);self.assertFalse(result['structured_checks_available']);self.assertFalse(result['automatic_award'])
            with self.assertRaises(ValueError):check_work(engine,item['id'],work={},**args)

    def test_stale_and_ineligible_rejected(self):
        item=self.r._resolve('solve-cubic',3,1);engine=fixture(item)
        for args in (dict(mode='learning_preview',item_fingerprint='stale'),dict(mode='approved_exam',item_fingerprint=fingerprint(item))):
            with self.assertRaises(ValueError):capability(engine,item['id'],**args)
            with self.assertRaises(ValueError):check_work(engine,item['id'],work={},**args)


if __name__=='__main__': unittest.main()
