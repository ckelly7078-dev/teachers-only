"""Private AS1 generator/marking contract; no UI, persistence, or grade release."""
import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from active_difficulty import MODES, require
from final_fm16 import load_final_bank
from marking_batch import read_batch
from marking_review import fingerprint
from mark_routes_fm17b import original_marking_context
from source_coverage_fm17c import SourceCoverage
from source_evidence_fm17 import bind_subskills


class Engine:
    def __init__(self, bank, links, coverage, pages, proof_sha256):
        self.bank = bank
        self.links = links
        self.coverage = coverage
        self.proof_sha256 = proof_sha256
        self.pages = {row['id']: copy.deepcopy(row) for row in pages}
        require(len(self.pages) == len(pages) == len(bank.items) and set(self.pages) == set(bank.items), 'Incomplete reference index')
        require(sorted(row['page'] for row in pages) == list(range(1, len(pages)+1)), 'Invalid reference pages')
        for key, row in self.pages.items():
            item = bank.items[key]
            require(row['fingerprint'] == fingerprint(item) and row['revision'] == item['revision']
                    and row['marks'] == item['marks'] and row['teacher_approved'] is False, 'Stale reference page')

    @classmethod
    def from_bundle(cls, root):
        root = Path(root); final = root/'FM16FINAL'
        manifest = json.loads((final/'FM16FINAL-runtime-manifest.json').read_text())
        for name in ('FM16FINAL-page-index.jsonl', 'FM16FINAL-teacher-preview.pdf'):
            with (final/name).open('rb') as f:
                require(hashlib.file_digest(f, 'sha256').hexdigest() == manifest['sha256'][name], 'Reference hash mismatch')
        bank = load_final_bank(final)
        links = bind_subskills(bank, read_batch(root/'FM17A-subskill-mappings.jsonl'))
        coverage = SourceCoverage(bank, *[read_batch(root/name) for name in (
            'FM17C-source-mark-routes.jsonl','FM17C-ambiguous-allocations.jsonl',
            'FM17C-route-component-links.jsonl','FM17C-source-conditions.jsonl')])
        return cls(bank, links, coverage, read_batch(final/'FM16FINAL-page-index.jsonl'),
                   manifest['sha256']['FM16FINAL-teacher-preview.pdf'])

    def source_profile(self, skill):
        """Counts are coverage evidence, never a numerical conversion to bank tiers."""
        require(isinstance(skill, str) and skill in self.bank.skills, 'Unknown skill')
        parent = self.bank.skills[skill]['concept_id']
        direct = set(self.links.get(skill, []))
        components = {(r['series'],r['number'],r['ordinal']) for r in self.coverage.skill_components(skill)}
        return {'note_linked_parts': len(direct), 'component_linked_parts': len(components),
                'parent_linked_parts': len(set(self.bank.links[parent])),
                'note_linked_demand': dict(Counter(self.bank.parts[k]['demand'] for k in direct)),
                'specific_route_parts': sum(self.coverage.part(k)['status']=='source_breakdown_available' for k in direct | components),
                'basis': 'note_link' if direct else 'route_component' if components else 'parent_specification_only',
                'difficulty_calibrated': False}

    def _row(self, selected):
        item=selected['item']; p=item['payload']; skill=p['focus_skill']; page=self.pages[item['id']]
        require(page['fingerprint']==selected['fingerprint'], 'Stale generation reference')
        # Foundation Studio field names are preserved, but the AS1 row is a
        # distinct private draft contract, not a GCSE family or a persisted draft.
        return {'unit':'AS1', 'family':p['path'], 'label':self.bank.skills[skill]['label'],
                'skill':skill, 'question':p['question_latex'], 'answer':p['final_answer_latex'],
                'solution':copy.deepcopy(p['worked_solution_latex']),
                'rubric':[f"{r['type']}{r['marks']}: {r['criterion']}" for r in p['rubric']],
                'typed_rubric':copy.deepcopy(p['rubric']), 'marks':item['marks'],
                'difficulty':p['tier'], 'difficulty_label':self.bank.levels[p['tier']]['label'],
                'demand_rationale':p['demand_rationale'], 'assessment_role':p['assessment_role'],
                'source_evidence':self.source_profile(skill),
                'reference':{'page':page['page'], 'proof_sha256':self.proof_sha256,
                             'diagram_present':page['reference_diagram'] is not None,
                             'teacher_solution_proof':True},
                'item_id':item['id'], 'fingerprint':selected['fingerprint'], 'revision':item['revision'],
                'mode':selected['mode'], 'state':'draft', 'teacher_approved':False,
                'exam_ready':False, 'release_allowed':False, 'difficulty_calibrated':False}

    def generate(self, groups, *, mode, total_marks=None, exclude_ids=(), seed=0):
        """Exact skill/tier quotas; bounded distinct selection, never silent fallback."""
        require(isinstance(mode,str) and mode in MODES and mode!='approved_exam', 'Draft preview mode required')
        require(isinstance(groups,list) and 1<=len(groups)<=10, 'Choose one to ten skill/tier groups')
        require(type(seed) is int and 0<=seed<2**32, 'Invalid seed')
        require(isinstance(exclude_ids,(list,tuple)) and len(exclude_ids)<=len(self.bank.items)
                and all(isinstance(k,str) and k in self.bank.items for k in exclude_ids), 'Invalid exclusions')
        excluded=set(exclude_ids); seen=set(); count=0; choices=[]
        for g in groups:
            require(isinstance(g,dict) and set(g)=={'skill','tier','count'}, 'Invalid group')
            skill,tier,n=(g[k] for k in ('skill','tier','count'))
            require(isinstance(skill,str) and skill in self.bank.skills and type(tier) is int and 1<=tier<=6
                    and type(n) is int and 1<=n<=3 and (skill,tier) not in seen, 'Invalid or duplicate group')
            seen.add((skill,tier)); count+=n
            candidates=[r for r in self.bank.select(skill,tier,mode=mode) if r['item']['id'] not in excluded]
            require(len(candidates)>=n,'Insufficient eligible distinct variants')
            candidates.sort(key=lambda r:hashlib.sha256(f"{seed}:{r['item']['id']}".encode()).hexdigest())
            choices.append(list(itertools.combinations(candidates,n)))
        require(count<=10, 'Choose at most ten questions')
        if total_marks is not None:
            require(type(total_marks) is int and 1<=total_marks<=80, 'Invalid total marks')
        # At most 10 groups and 80 marks: dynamic programming avoids exponential search.
        paths={0:[]}
        for combos in choices:
            updated={}
            for subtotal,selected in paths.items():
                for combo in combos:
                    marks=subtotal+sum(r['item']['marks'] for r in combo)
                    if total_marks is None or marks<=total_marks:
                        updated.setdefault(marks,selected+list(combo))
            paths=updated
        require(bool(paths) and (total_marks is None or total_marks in paths), 'Exact mark total unavailable')
        chosen=paths[total_marks] if total_marks is not None else next(iter(paths.values()))
        rows=[self._row(r) for r in chosen]
        require(len({r['item_id'] for r in rows})==count, 'Duplicate generated question')
        return {'questions':rows, 'total_marks':sum(r['marks'] for r in rows),
                'mode':mode, 'state':'draft', 'release_allowed':False}

    def marking_context(self, item_id, *, mode, item_fingerprint):
        require(isinstance(item_id,str) and item_id in self.bank.items, 'Unknown original item')
        require(fingerprint(self.bank.items[item_id])==item_fingerprint, 'Stale item fingerprint')
        return original_marking_context(self.bank,item_id,mode=mode)


def reconcile_proposal(context, decisions):
    """Aggregate externally supplied criterion observations, not assess student work.

    No inferred follow-through or splitting a grouped award. An unresolved mark
    remains an interval. Evidence text is not evaluated or persisted here.
    """
    require(context['automatic_award'] is False and context['release_allowed'] is False,'Invalid marking context')
    criteria={r['id']:r for r in context['criteria']}
    require(sum(r['marks'] for r in criteria.values())==context['marks'], 'Invalid context marks')
    require(isinstance(decisions,list) and len(decisions)==len(criteria),'Every criterion requires a decision')
    seen=set(); low=high=0; rows=[]
    for row in decisions:
        require(isinstance(row,dict) and set(row)=={'criterion_id','status','evidence'},'Invalid proposal fields')
        key=row['criterion_id']; status=row['status']; evidence=row['evidence']
        require(isinstance(key,str) and key in criteria and key not in seen,'Unknown or repeated criterion')
        require(status in ('met','not_met','uncertain') and isinstance(evidence,str) and 0<len(evidence.strip())<=2000,'Evidence required')
        seen.add(key); cap=criteria[key]['marks']; bounds={'met':(cap,cap),'not_met':(0,0),'uncertain':(0,cap)}[status]
        low+=bounds[0]; high+=bounds[1]
        rows.append({'criterion_id':key,'status':status,'possible_marks':list(bounds),'evidence':evidence})
    return {'id':context['id'],'fingerprint':context['fingerprint'],'possible_total':[low,high],
            'maximum_marks':context['marks'],'criteria':rows,'basis':'supplied_observations_not_verified_work',
            'automatic_award':False,'teacher_approved':False,'release_allowed':False}
