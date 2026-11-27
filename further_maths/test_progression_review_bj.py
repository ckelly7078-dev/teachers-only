"""Fail closed on stale or unapproved demand evidence."""
import copy
import unittest
from active_difficulty import Resolver
from progression_review_bj import bind, validate, PRIORITIES

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.old=Resolver(historical_through='bh');cls.r=Resolver(historical_through='bj')
    def test_version_binding(self):
        old=bind(self.old,'solve-quartic',4,'successor_implemented','Coefficient and complete root construction','priority_all_variants')
        new=bind(self.r,'solve-quartic',4,'successor_implemented','Coefficient and complete root construction','priority_all_variants')
        self.assertEqual(old['left_fingerprints'],new['left_fingerprints']);self.assertNotEqual(old['right_fingerprints'],new['right_fingerprints'])
        self.assertEqual(old['to_marks'],[3]*3);self.assertEqual(new['to_marks'],[7]*3)
    def test_invalid_review_rejected(self):
        row=bind(self.old,'angle-units',4,'successor_implemented','Integer interval derivation','priority_all_variants')
        for key,value in [('teacher_approved',True),('empirical_calibration',True),('note',''),('right_fingerprints',['stale']*3),('decision','invented')]:
            bad=copy.deepcopy(row);bad[key]=value
            with self.assertRaises(ValueError):validate([bad],self.old,self.r)
        with self.assertRaisesRegex(ValueError,'Duplicate'):validate([row,row],self.old,self.r)
        with self.assertRaisesRegex(ValueError,'coverage'):validate([row],self.old,self.r)
    def test_priority_registry(self):
        self.assertEqual(len(PRIORITIES),11);self.assertIn(('solve-cubic',3),PRIORITIES);self.assertIn(('solve-cubic',4),PRIORITIES)

if __name__=='__main__':unittest.main()
