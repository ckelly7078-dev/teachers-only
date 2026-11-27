import unittest
from marking_review import DIMENSIONS,inventory_entry,validate_review

class Tests(unittest.TestCase):
    def setUp(self):
        self.item={'id':'example','revision':'FM-16AQ','scope':'challenge_candidate','marks':2,'teacher_approved':False,'payload':{'rubric':[{'marks':2,'criterion':'Example criterion'}]}}
        self.review={'id':'example','fingerprint':inventory_entry(self.item)['fingerprint'],'reviewer':'Example reviewer','review_basis':'individual_item_review','teacher_approved':False,'checks':{d:{'decision':'pass','evidence':'Example evidence'} for d in DIMENSIONS},'allocation':[{'criterion_index':0,'marks':{'M':1,'A':1,'R':0},'evidence':'Example rationale'}]}
    def test_inventory(self):
        self.assertEqual(inventory_entry(self.item)['status'],'needs_type_review');self.item['payload']['rubric'][0]['type']='M';self.assertEqual(inventory_entry(self.item)['status'],'typed_provisional')
    def test_record(self):
        self.assertEqual(validate_review(self.item,self.review),'editorial_review_recorded');self.review['checks']['presentation']['decision']='revise';self.assertEqual(validate_review(self.item,self.review),'changes_requested')
    def test_stale(self):
        self.item['payload']['rubric'][0]['criterion']='Changed';self.assertRaises(ValueError,validate_review,self.item,self.review)
    def test_missing_dimension(self):
        self.review['checks'].pop('alternative_methods');self.assertRaises(ValueError,validate_review,self.item,self.review)
    def test_wrong_total(self):
        self.review['allocation'][0]['marks']['A']=2;self.assertRaises(ValueError,validate_review,self.item,self.review)
    def test_approval(self):
        self.review['teacher_approved']=True;self.assertRaises(ValueError,validate_review,self.item,self.review)
    def test_essential_dimension(self):
        self.review['checks']['mathematical_correctness']['decision']='not_applicable';self.assertRaises(ValueError,validate_review,self.item,self.review)
    def test_empty_evidence(self):
        self.review['checks']['boundary_cases']['evidence']=' ';self.assertRaises(ValueError,validate_review,self.item,self.review)
if __name__=='__main__':unittest.main(verbosity=2)
