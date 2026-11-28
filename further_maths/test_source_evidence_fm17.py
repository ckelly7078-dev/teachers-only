import unittest
from collections import defaultdict
from types import SimpleNamespace
from source_evidence_fm17 import bind_subskills, part_signature, enriched_evidence


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.key = ('fixture',1,1)
        p = dict(paper_source='p',scheme_source='s',demand='medium',note='fixture')
        self.bank = SimpleNamespace(parts={self.key:p},sources={'p':{'sha256':'p'},'s':{'sha256':'s'}},
            skills={'a.x':{'concept_id':'a'},'b.x':{'concept_id':'b'}},links=defaultdict(list,{'a':[self.key]}),
            evidence=lambda skill:{'skill':skill,'source_link_level':'parent_concept_only'})
        self.record = dict(series='fixture',number=1,ordinal=1,skills=['a.x'],basis='editorial_mapping_from_source_checked_note',
            part_signature=part_signature(self.bank,self.key),note='Fixture rationale.')

    def test_bound_source_evidence_separate_from_parent(self):
        index = bind_subskills(self.bank,[self.record])
        ctx = enriched_evidence(self.bank,index,'a.x')
        self.assertEqual(ctx['note_linked_demand_counts'],{'medium':1})
        self.assertFalse(ctx['official_marking_policy']['automatic_award'])
        self.assertEqual(enriched_evidence(self.bank,index,'b.x')['subskill_link_basis'],'no_note_linked_part')
        ctx['note_linked_parts'][0]['note'] = 'changed'
        self.assertEqual(self.bank.parts[self.key]['note'],'fixture')

    def test_stale_incomplete_and_outside_parent_rejected(self):
        for rows in ([],[self.record,self.record],[dict(self.record,part_signature='stale')],
                     [dict(self.record,skills=['b.x'])],[dict(self.record,skills=['a.x','a.x'])]):
            with self.assertRaises(ValueError): bind_subskills(self.bank,rows)
        self.bank.parts[self.key]['note'] = 'new version'
        with self.assertRaises(ValueError): bind_subskills(self.bank,[self.record])


if __name__ == '__main__': unittest.main()
