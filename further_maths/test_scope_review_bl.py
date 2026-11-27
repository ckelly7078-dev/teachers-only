import copy,unittest
from active_difficulty import Resolver
from scope_review_bl import bind,ENRICHMENT,WATCH,CONCEPT_METHOD
from consolidation_audit import OUTCOMES

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()
    def test_enrichment_all_variants(self):
        self.assertEqual(len(ENRICHMENT),13)
        for path in ENRICHMENT:
            for v in (1,2,3):
                row=bind(self.r,path,6,v);self.assertEqual(row['eligible_preview_modes'],['enrichment_preview']);self.assertFalse(row['exam_ready'])
    def test_watch(self):
        for p,t in WATCH:
            row=bind(self.r,p,t,1);self.assertEqual(row['decision'],'scope_confirmation_required');self.assertFalse(row['teacher_approved']);self.assertFalse(row['individual_scope_certified'])
    def test_source_map(self):
        self.assertEqual(set(CONCEPT_METHOD),set(OUTCOMES));self.assertEqual(len(OUTCOMES),41)
    def test_roles_and_no_approval(self):
        for t in range(1,7):
            row=bind(self.r,'inverse-three',t,1);self.assertFalse(row['exam_ready']);self.assertFalse(row['empirical_calibration'])
            self.assertEqual(row['decision'],'bridge_or_diagnostic_only' if t<=2 else 'challenge_only' if t==6 else 'representative_linked_candidate')
if __name__=='__main__':unittest.main(verbosity=2)
