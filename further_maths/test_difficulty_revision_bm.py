import unittest
from active_difficulty import Resolver
from difficulty_revision_bm import TARGETS
from difficulty_revision_bm_oracle import check

class TestBM(unittest.TestCase):
    def test_preservation(self):
        r=Resolver()
        for (path,tier),tag in TARGETS.items():
            for v in (1,2,3):
                old=r._resolve_version(path,tier,v,tag); new=r._resolve(path,tier,v)
                self.assertEqual(new['revision'],'FM-16BM')
                self.assertEqual(new['marks'],old['marks'])
                self.assertEqual(new['scope'],old['scope'])
                self.assertEqual({k for k in old['payload'] if old['payload'][k]!=new['payload'][k]}, {'final_answer_latex'})
                self.assertTrue(check(new['payload']))
                self.assertFalse(check(old['payload']))
    def test_mixed_terms(self):
        r=Resolver()
        for v in (1,2,3):
            a,b=v+1,2*v+5; c=v+3
            self.assertIn('$'+str((a+b)**3-a**3-b**3)+'$',r._resolve('cube-sums',2,v)['payload']['final_answer_latex'])
            self.assertIn('$'+str((a-c)*(b-c)-a*b-c*c)+'$',r._resolve('shifted-products',2,v)['payload']['final_answer_latex'])
