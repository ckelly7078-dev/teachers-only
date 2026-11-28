import copy
import unittest
from collections import defaultdict
from types import SimpleNamespace
from knowledge_fm17 import printed_codes
from source_evidence_fm17 import part_signature
from source_coverage_fm17c import SourceCoverage, route_signature


class SourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.k=('fixture',1,1); self.a=('fixture',2,1)
        part=dict(paper_source='p',scheme_source='s',paper_page=2,scheme_page=3,marks=2,
                  printed_allocation=printed_codes('M1 W1',2))
        self.bank=SimpleNamespace(parts={self.k:part,self.a:copy.deepcopy(part)},sources={'p':{'sha256':'p'},'s':{'sha256':'s'}},
                                  skills={'skill':{'concept_id':'parent'},'other':{'concept_id':'other'}},links=defaultdict(list,{'parent':[self.k]}))
        self.r=dict(series='fixture',number=1,ordinal=1,part_signature=part_signature(self.bank,self.k),scheme_sha256='s',breakdown_page=3,
                    basis='editorial_reading_of_printed_breakdown',automatic_award=False,
                    routes=[dict(id='primary',stages=[dict(id='s1',code='M1',marks=1,criterion='method',uses=[],partial_credit=None),
                                                     dict(id='s2',code='W1',marks=1,criterion='working',uses=['s1'],partial_credit=None)],exceptions=[])])
        self.amb=dict(series='fixture',number=2,ordinal=1,part_signature=part_signature(self.bank,self.a),scheme_sha256='s',scheme_page=3,
                      printed_allocation=copy.deepcopy(part['printed_allocation']),geometry='Fixture sketch',reason='No feature-level allocation',automatic_award=False)
        self.component=dict(series='fixture',number=1,ordinal=1,part_signature=part_signature(self.bank,self.k),skill='skill',route_id='primary',stage_ids=['s2'],
                            route_signature=route_signature(self.r),basis='editorial_component_of_printed_route',standalone_skill_assessment=False,
                            separate_marks=False,automatic_award=False,note='Fixture component')
        self.condition=dict(series='fixture',number=1,ordinal=1,part_signature=part_signature(self.bank,self.k),paper_sha256='p',paper_page=2,
                            kind='method_restriction',note='Fixture condition',automatic_award=False)

    def coverage(self): return SourceCoverage(self.bank,[self.r],[self.amb],[self.component],[self.condition])

    def test_complete_partition(self):
        c=self.coverage(); self.assertEqual(c.summary()['usable_parts'],2);self.assertEqual(c.summary()['ambiguous_marks'],2)
        self.assertEqual(c.part(self.k)['status'],'source_breakdown_available')
        self.assertEqual(c.part(self.a)['status'],'printed_allocation_ambiguous')
        self.assertEqual(c.part(self.a)['routes'],[]);self.assertFalse(c.part(self.k)['automatic_award'])
        self.assertEqual(c.part(self.k)['source_conditions'][0]['kind'],'method_restriction')
        self.assertFalse(c.skill_components('skill')[0]['separate_marks'])
        self.assertEqual(c.skill_components('other'),[])

    def test_incomplete_duplicate_or_stale_rejected(self):
        for ambiguous in ([],[self.amb,self.amb],[dict(self.amb,part_signature='stale')],
                          [dict(self.amb,scheme_sha256='wrong')],[dict(self.amb,printed_allocation=[])],
                          [dict(self.amb,automatic_award=True)],[dict(self.amb,reason='')]):
            with self.assertRaises(ValueError): SourceCoverage(self.bank,[self.r],ambiguous)
        with self.assertRaises(ValueError): self.coverage().part(('fixture',3,1))

    def test_component_is_neither_extra_marks_nor_unbound_skill(self):
        for changes in (dict(skill='other'),dict(stage_ids=['s3']),dict(route_signature='wrong'),
                        dict(separate_marks=True),dict(standalone_skill_assessment=True),dict(automatic_award=True)):
            with self.assertRaises(ValueError): SourceCoverage(self.bank,[self.r],[self.amb],[dict(self.component,**changes)])
        with self.assertRaises(ValueError): SourceCoverage(self.bank,[self.r],[self.amb],[self.component,self.component])

    def test_source_condition_requires_exact_paper(self):
        for changes in (dict(paper_sha256='stale'),dict(paper_page=3),dict(kind='award'),dict(automatic_award=True)):
            with self.assertRaises(ValueError): SourceCoverage(self.bank,[self.r],[self.amb],conditions=[dict(self.condition,**changes)])

    def test_private_results_are_copies_and_stale_evidence_fails(self):
        c=self.coverage();c.part(self.a)['ambiguity']['reason']='changed';c.skill_components('skill')[0]['stage_ids'].clear()
        self.assertEqual(c.part(self.a)['ambiguity']['reason'],self.amb['reason']);self.assertEqual(c.skill_components('skill')[0]['stage_ids'],['s2'])
        self.bank.parts[self.k]['marks']=3
        with self.assertRaises(ValueError): c.skill_components('skill')
        with self.assertRaises(ValueError): c.part(self.k)


if __name__=='__main__': unittest.main()
