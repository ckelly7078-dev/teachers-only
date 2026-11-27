import copy
import unittest
from marking_batch import validate_batch, unique_object
from marking_review import DIMENSIONS, inventory_entry


class Stub:
    def __init__(self):
        self.item = {'id':'CAL.example.T3.V1','revision':'FM-16AB','scope':'syllabus_linked_candidate','marks':2,'teacher_approved':False,'payload':{'rubric':[{'marks':2,'criterion':'Example','type':'M'}]}}
    def _key(self,p,t,v):
        if (p,t,v) != ('example',3,1): raise ValueError('Unknown item')
    def _resolve(self,p,t,v):
        return self.item


class Tests(unittest.TestCase):
    def setUp(self):
        self.r=Stub()
        self.record={'id':self.r.item['id'],'fingerprint':inventory_entry(self.r.item)['fingerprint'],'reviewer':'Example reviewer','review_basis':'individual_item_review','teacher_approved':False,'checks':{d:{'decision':'pass','evidence':'Example only'} for d in DIMENSIONS},'allocation':[{'criterion_index':0,'marks':{'M':2,'A':0,'R':0},'evidence':'Example only'}]}
    def test_batch(self):
        self.assertEqual(validate_batch([self.record],self.r)['statuses'],{'editorial_review_recorded':1})
    def test_duplicate(self):
        self.assertRaises(ValueError,validate_batch,[self.record,copy.deepcopy(self.record)],self.r)
    def test_empty(self):
        self.assertRaises(ValueError,validate_batch,[],self.r)
    def test_bad_id(self):
        self.record['id']='CAL.example.T0.V1';self.assertRaises(ValueError,validate_batch,[self.record],self.r)
    def test_unknown(self):
        self.record['id']='CAL.missing.T3.V1';self.assertRaises(ValueError,validate_batch,[self.record],self.r)
    def test_stale(self):
        self.r.item['payload']['rubric'][0]['criterion']='Changed';self.assertRaises(ValueError,validate_batch,[self.record],self.r)
    def test_type_change(self):
        self.record['allocation'][0]['marks']={'M':0,'A':2,'R':0};self.assertRaises(ValueError,validate_batch,[self.record],self.r)
        self.record['checks']['criterion_allocation']['decision']='revise';self.assertEqual(validate_batch([self.record],self.r)['statuses'],{'changes_requested':1})
    def test_duplicate_json_key(self):
        self.assertRaises(ValueError,unique_object,[('id',1),('id',2)])
    def test_no_mutation(self):
        before=copy.deepcopy(self.r.item);validate_batch([self.record],self.r);self.assertEqual(before,self.r.item)

if __name__=='__main__':unittest.main(verbosity=2)
