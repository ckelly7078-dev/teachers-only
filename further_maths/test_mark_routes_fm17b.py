import copy
import unittest
from types import SimpleNamespace
from knowledge_fm17 import printed_codes
from source_evidence_fm17 import part_signature
from mark_routes_fm17b import bind_routes, part_routes


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.key = ('fixture', 1, 1)
        p = dict(paper_source='p', scheme_source='s', marks=2, printed_allocation=printed_codes('M1 W1', 2))
        self.bank = SimpleNamespace(parts={self.key:p}, sources={'p':{'sha256':'p'},'s':{'sha256':'s'}})
        self.row = dict(series='fixture', number=1, ordinal=1, part_signature=part_signature(self.bank,self.key),
                        scheme_sha256='s', breakdown_page=3, basis='editorial_reading_of_printed_breakdown', automatic_award=False,
                        routes=[dict(id='primary', stages=[dict(id='s1',code='M1',marks=1,criterion='method',uses=[],partial_credit=None),
                                                          dict(id='s2',code='W1',marks=1,criterion='working',uses=['s1'],partial_credit=None)],
                                     exceptions=[dict(kind='cap',condition='fixture',effect='method only',stages=['s1'],prior_part=None,max_marks=1)])])

    def test_valid_routes_and_missing_evidence(self):
        index = bind_routes(self.bank,[self.row]); self.assertEqual(part_routes(self.bank,index,self.key)['status'],'source_breakdown_available')
        self.assertEqual(part_routes(self.bank,{},self.key)['status'],'printed_allocation_only')
        self.assertFalse(part_routes(self.bank,index,self.key)['automatic_award'])
        index[self.key]['routes'][0]['stages'][0]['criterion'] = 'changed'
        self.assertEqual(self.row['routes'][0]['stages'][0]['criterion'],'method')

    def test_invalid_fingerprint_and_duplicate(self):
        for rows in ([self.row,self.row],[dict(self.row,part_signature='stale')],[dict(self.row,scheme_sha256='wrong')],[dict(self.row,automatic_award=True)]):
            with self.assertRaises(ValueError): bind_routes(self.bank,rows)

    def test_allocation_dependency_and_cap_fail_closed(self):
        for edit in ('code','dependency','cap','unknown_stage','partial'):
            row = copy.deepcopy(self.row); route = row['routes'][0]
            if edit=='code': route['stages'][0]['code']='MW1'
            elif edit=='dependency': route['stages'][0]['uses']=['s2']
            elif edit=='cap': route['exceptions'][0]['max_marks']=0
            elif edit=='unknown_stage': route['exceptions'][0]['stages']=['s3']
            else: route['stages'][0]['partial_credit']='invented partial credit'
            with self.assertRaises(ValueError): bind_routes(self.bank,[row])

    def test_alternatives_not_added_to_primary_total(self):
        row = copy.deepcopy(self.row)
        row['routes'].append(dict(id='alternative',stages=[dict(id='s1',code='MW2',marks=2,criterion='alternative',uses=[],partial_credit=None)],exceptions=[]))
        self.assertEqual(len(bind_routes(self.bank,[row])[self.key]['routes']),2)
        row['routes'][1]['stages'][0]['code']='MW3'
        with self.assertRaises(ValueError): bind_routes(self.bank,[row])

    def test_stale_part_after_binding(self):
        index = bind_routes(self.bank,[self.row]);self.bank.parts[self.key]['marks']=3
        with self.assertRaises(ValueError): part_routes(self.bank,index,self.key)


if __name__ == '__main__': unittest.main()
