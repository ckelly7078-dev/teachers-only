"""Private source-linked AS1 knowledge adapter; no student grading or release."""
import collections
import copy
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from active_difficulty import MODES, require
from marking_batch import read_batch
from marking_review import fingerprint, validate_review
from readiness_bo import conservative_preview_eligible
from successor_bq import SuccessorResolver

OFFICIAL_CODES = {'M': 'method', 'W': 'working', 'MW': 'combined_method_and_working'}
DEMAND = ('easy', 'medium', 'hard')


def printed_codes(text, marks):
    tokens = text.split()
    result = []
    for token in tokens:
        match = re.fullmatch(r'(MW|M|W)([1-9][0-9]*)', token)
        require(match is not None, 'Unrecognized printed code')
        code, n = match.groups()
        result.append({'code': code, 'marks': int(n), 'meaning': OFFICIAL_CODES[code]})
    require(result and sum(r['marks'] for r in result) == marks, 'Printed allocation mismatch')
    return result


def demand_profile(item, review):
    """Describe observed task/rubric features, not measured learner difficulty."""
    p = item['payload']; prompt = p['question_latex'].lower()
    types = collections.Counter()
    for row in p['rubric']:
        types[row['type']] += row['marks']
    return {'tier': p['tier'], 'role': p['assessment_role'], 'rationale': p['demand_rationale'],
            'marks': item['marks'], 'criterion_count': len(p['rubric']), 'criterion_marks': dict(types),
            'worked_step_count': len(p['worked_solution_latex']),
            'prompt_signals': {name: bool(re.search(pattern, prompt)) for name, pattern in {
                'justification': r'\b(prove|justify|explain|show|derive|verify)\b',
                'exhaustiveness': r'\b(all|every|completeness|exhaustive)\b',
                'restriction': r'\b(without|exclude|nonzero|non-zero|restriction|provided|unless)\b',
                'classification': r'\b(classify|distinguish|cases|classifications)\b',
                'unknown_recovery': r'\b(parameter|unknown|determine|recover|reconstruct)\b',
                'supplied_method': r'\b(using|use|by applying|by expanding)\b'}.items()},
            'marking_review': validate_review(item, review),
            'difficulty_basis': 'editorial_not_empirical'}


class KnowledgeBank:
    """Load verified private material once; expose original previews by exact skill.

    Source-linked evidence stays internal. Concept links do not establish exact
    subskill or item equivalence. No automatic conversion M/W/MW -> M/A/R.
    """
    def __init__(self, database, edits, reviews, *, resolver=None):
        self.resolver = SuccessorResolver(edits) if resolver is None else resolver
        self.resolver.verify(database)
        self.items = {}; self.profiles = {}; self.reviews = {}; self.paths = {}
        records = {r['id']: r for r in reviews}
        require(len(records) == len(reviews) == 2106, 'Incomplete marking evidence')
        with closing(sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)) as db:
            db.row_factory = sqlite3.Row
            self.skills = {r['id']: dict(r) for r in db.execute('SELECT a.id,a.concept_id,a.label,s.spec_source,s.spec_page,s.elaboration_source,s.elaboration_page FROM assessable_skills a JOIN concepts c ON c.id=a.concept_id JOIN skills s ON s.id=c.skill_id')}
            self.levels = {r['tier']: dict(r) for r in db.execute('SELECT * FROM difficulty_level_rubric')}
            self.sources = {r['id']: dict(r) for r in db.execute('SELECT id,filename,kind,sha256 FROM sources')}
            self.parts = {}; self.links = collections.defaultdict(list)
            for r in db.execute('SELECT p.*,d.demand,d.rationale,d.status AS demand_status FROM part_reviews p JOIN part_demand d USING(series,number,ordinal)'):
                row = dict(r); key = (row['series'], row['number'], row['ordinal'])
                require(row['demand'] in DEMAND and row['demand_status'] == 'provisional_not_calibrated', 'Invalid demand evidence')
                row['printed_allocation'] = printed_codes(row['mark_codes'], row['marks'])
                self.parts[key] = row
            for series, number, ordinal, concept in db.execute('SELECT * FROM part_skills ORDER BY series,number,ordinal,skill_id'):
                key = (series, number, ordinal)
                require(key in self.parts, 'Missing part evidence')
                self.links[concept].append(key)
            self.disputed = [dict(r) for r in db.execute('SELECT * FROM source_review_issues')]
            require(not any((r['series'],r['number'],r['ordinal']) in self.parts for r in self.disputed), 'Disputed marking leaked into evidence')
            self.report_notes = collections.defaultdict(list)
            for r in db.execute('SELECT * FROM skill_report_observations ORDER BY id'):
                self.report_notes[r['skill_id']].append(dict(r))
            self.teaching = {r['skill_id']: json.loads(r['payload']) for r in db.execute('SELECT skill_id,payload FROM skill_teaching_entries')}
            self.prerequisites = collections.defaultdict(list)
            for skill, prior in db.execute('SELECT skill_id,prerequisite_id FROM detailed_prerequisite_edges ORDER BY skill_id,prerequisite_id'):
                self.prerequisites[skill].append(prior)
        for path in sorted(self.resolver.bases):
            for tier in range(1,7):
                for variant in (1,2,3):
                    item = self.resolver._resolve(path,tier,variant); key = item['id']; skill = item['payload']['focus_skill']
                    require(skill in self.skills and self.paths.setdefault(skill,path) == path, 'Invalid skill pathway')
                    review = records.pop(key); profile = demand_profile(item,review)
                    require(profile['marking_review'] == 'editorial_review_recorded', 'Unresolved rubric review')
                    require(all(a['marks'][c['type']] == c['marks'] for a,c in zip(review['allocation'],item['payload']['rubric'])), 'Rubric allocation differs')
                    self.items[key] = item; self.profiles[key] = profile; self.reviews[key] = review
        require(not records and len(self.paths) == len(self.skills) == 117, 'Incomplete knowledge coverage')

    @classmethod
    def from_bundle(cls, root):
        root = Path(root)
        return cls(root/'as1.sqlite', read_batch(root/'FM16BQ-successor-edits.jsonl'),
                   read_batch(root/'FM16BQ-current-review-ledger.jsonl'))

    def evidence(self, skill):
        """Private teacher/engine context, not for public response or grading."""
        require(skill in self.skills, 'Unknown skill')
        info = self.skills[skill]; parts = [self.parts[k] for k in self.links[info['concept_id']]]
        return copy.deepcopy({'skill': info, 'teaching': self.teaching[skill],
            'prerequisites': self.prerequisites[skill], 'source_link_level': 'parent_concept_only',
            'source_parts': parts, 'source_demand_counts': dict(collections.Counter(p['demand'] for p in parts)),
            'examiner_observations': self.report_notes[skill],
            'disputed_source_parts': [r for r in self.disputed if info['concept_id'] in json.loads(r['skill_ids'])],
            'official_code_mapping': OFFICIAL_CODES, 'empirical_calibration': False})

    def select(self, skill, tier, *, mode):
        """Return original-only candidates, never private source extracts."""
        require(skill in self.paths and type(tier) is int and 1 <= tier <= 6 and mode in MODES, 'Invalid selection')
        path = self.paths[skill]
        if not conservative_preview_eligible(self.resolver,path,tier,mode):
            return []
        result = []
        for v in (1,2,3):
            key = f'CAL.{path}.T{tier}.V{v}'; item = self.items[key]
            result.append(copy.deepcopy({'item': item, 'fingerprint': fingerprint(item),
                'difficulty': self.profiles[key], 'marking_convention': 'original_provisional_M_A_R',
                'mode': mode, 'release_allowed': False, 'exam_ready': False}))
        return result

    def transition_screen(self):
        """Report overlaps for demand review; no marks-only reclassification."""
        result = []
        for skill,path in sorted(self.paths.items()):
            for tier in range(1,6):
                left = [self.profiles[f'CAL.{path}.T{tier}.V{v}'] for v in (1,2,3)]
                right = [self.profiles[f'CAL.{path}.T{tier+1}.V{v}'] for v in (1,2,3)]
                marks_l = [p['marks'] for p in left]; marks_r = [p['marks'] for p in right]
                result.append({'skill': skill, 'from_tier': tier, 'to_tier': tier+1,
                    'from_marks': marks_l, 'to_marks': marks_r,
                    'mark_ranges_touch_or_overlap': min(marks_r) <= max(marks_l),
                    'same_prompt_signals': [a['prompt_signals'] == b['prompt_signals'] for a,b in zip(left,right)],
                    'from_rationales': sorted(set(p['rationale'] for p in left)),
                    'to_rationales': sorted(set(p['rationale'] for p in right)),
                    'difficulty_basis': 'screen_only_no_reclassification'})
        return result
