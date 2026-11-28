import copy
import unittest
from marking_review import fingerprint
from successor_bq import SuccessorResolver
from test_structured_math_fm17e import fixture
from profile_marking_fm17h import ProfileMarking, exact, matches


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.item=SuccessorResolver([])._resolve('argand-coordinates',3,1)
        self.engine=fixture(self.item); self.key=self.item['id']; self.fp=fingerprint(self.item)
        self.row=dict(id=self.key,fingerprint=self.fp,revision=self.item['revision'],basis='editorial_prompt_derived_observations',
                      criteria=[dict(field='point',type='A',marks=1,rule='equal',expected=['-2','4','labelled_axes']),
                                dict(field='quadrant',type='A',marks=1,rule='equal',expected='2')])
        self.work=dict(point=['-2','4','labelled_axes'],quadrant='2')

    def test_exact_radicals_and_rational_equivalence(self):
        a={'radical_terms':[['1','12'],['-1','3'],['-3','1']]}
        b={'radical_terms':[['-3','1'],['1','3']]}
        self.assertTrue(exact(a,b));self.assertFalse(exact({'radical_terms':[['-1','3'],['-3','1']]},b))
        self.assertTrue(exact({'radical_terms':[['1','8'],['-2','2']]},{'radical_terms':[]}))
        self.assertTrue(exact('2/4','1/2'))
        for bad in ({'radical_terms':[['1','0']]},{'radical_terms':[['1','10001']]},{'radical_terms':[['1','1/2']]},
                    {'radical_terms':[['1/0','3']]},{'radical_terms':[['1','3']]*9}, {'expression':'sqrt(3)'}):
            with self.assertRaises(ValueError):exact(bad,b)

    def test_nonzero_scaled_vectors_and_unordered_sets(self):
        self.assertTrue(matches('proportional',['-4','6','2'],['2','-3','-1']))
        self.assertFalse(matches('proportional',['0','0','0'],['2','-3','-1']))
        self.assertTrue(matches('directions',[['0','-3'],['4','0']],[['1','0'],['0','1']]))
        self.assertFalse(matches('directions',[['4','0'],['8','0']],[['1','0'],['0','1']]))
        self.assertTrue(matches('unordered',['-2','3'],['3','-2']));self.assertFalse(matches('unordered',['3','3'],['3','-2']))

    def test_equivalent_line_and_required_verification(self):
        line=[['1','2','3'],['2','-1','4'],'real_parameter']
        alternative=[['3','1','7'],['-4','2','-8'],'real_parameter']
        self.assertTrue(matches('line',alternative,line))
        for bad in ([['3','1','8'],alternative[1],alternative[2]],[alternative[0],['0','0','0'],alternative[2]],
                    [alternative[0],alternative[1],'positive_parameter']):
            self.assertFalse(matches('line',bad,line))
        self.assertTrue(matches('line_with_checks',[alternative,['0','0'],'rank_two'],[line,['0','0'],'rank_two']))
        self.assertFalse(matches('line_with_checks',[alternative,['1','0'],'rank_two'],[line,['0','0'],'rank_two']))

    def test_scaled_plane_needs_valid_substitution(self):
        target=[['2','-1','3'],'7',['2','0','1'],'7']
        scaled=[['-4','2','-6'],'-14',['2','0','1'],'-14']
        self.assertTrue(matches('plane_check',scaled,target))
        self.assertFalse(matches('plane_check',[scaled[0],scaled[1],scaled[2],'14'],target))
        self.assertFalse(matches('plane_check',[['0','0','0'],'0',scaled[2],'0'],target))

    def test_profile_binding_and_no_mutation(self):
        profile=ProfileMarking(self.engine,[self.row]); self.row['criteria'][0]['expected'].clear()
        args=dict(mode='learning_preview',item_fingerprint=self.fp)
        self.assertTrue(profile.capability(self.key,**args)['structured_checks_available'])
        self.assertEqual(profile.check_work(self.key,work=self.work,**args)['possible_total'],[2,2])
        result=profile.check_work(self.key,work={**self.work,'point':None},**args)
        self.assertEqual(result['possible_total'],[1,2]);self.assertFalse(result['automatic_award']);self.assertFalse(result['release_allowed'])
        self.assertEqual(profile.check_work(self.key,work={**self.work,'quadrant':'3'},**args)['possible_total'],[1,1])

    def test_stale_incomplete_and_invalid_profile_rejected(self):
        for records in ([],[self.row,self.row],[dict(self.row,fingerprint='wrong')],[dict(self.row,revision='wrong')],
                        [dict(self.row,criteria=self.row['criteria'][:1])],[dict(self.row,basis='invented')]):
            with self.assertRaises(ValueError):ProfileMarking(self.engine,records)
        for field,value in [('type','M'),('marks',2),('rule','unknown'),('field','quadrant')]:
            row=copy.deepcopy(self.row);row['criteria'][0][field]=value
            with self.assertRaises(ValueError):ProfileMarking(self.engine,[row])

    def test_invalid_work_and_ineligible_modes(self):
        profile=ProfileMarking(self.engine,[self.row]);args=dict(mode='learning_preview',item_fingerprint=self.fp)
        for work in ({},dict(self.work,extra='x'),dict(self.work,quadrant='1/0'),dict(self.work,point=['-2','4'])):
            with self.assertRaises(ValueError):profile.check_work(self.key,work=work,**args)
        for changes in (dict(mode='approved_exam'),dict(item_fingerprint='stale')):
            with self.assertRaises(ValueError):profile.check_work(self.key,work=self.work,**(args|changes))


if __name__=='__main__':unittest.main()
