"""FM-16AM: active AS1 resolver and read-only verification; not release approval."""
import argparse
import collections
import importlib
import json
import sqlite3
from pathlib import Path
from skill_detail import detail_map

BASES = ('', *('abcdefghijklmnopqrstuvwxyz'[1:]), 'aa', 'ab')
OVERLAYS = ('ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'an', 'ao', 'ap')
REVIEWS = ('af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al')
SCOPES = {'prerequisite_bridge_reviewed': 117, 'conceptual_diagnostic_reviewed': 117,
          'syllabus_linked_candidate': 351, 'challenge_candidate': 104, 'enrichment_only': 13}
MODES = {'learning_preview': {'prerequisite_bridge_reviewed', 'conceptual_diagnostic_reviewed', 'syllabus_linked_candidate'},
         'exam_candidate_preview': {'syllabus_linked_candidate'}, 'challenge_preview': {'challenge_candidate'},
         'enrichment_preview': {'enrichment_only'}, 'approved_exam': set()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Resolver:
    def __init__(self):
        self.bases, self.overlays, self.reviews = {}, {}, {}
        for suffix in BASES:
            name = 'calibration' + ('_' + suffix if suffix else '')
            bank = importlib.import_module(name + '_bank')
            oracle = importlib.import_module(name + '_oracle')
            for path, skill in bank.PATHS.items():
                require(path not in self.bases, 'Duplicate base: ' + path)
                self.bases[path] = (skill, bank.make, oracle.check)
        skills = {f'{concept}.{key}' for concept, entries in detail_map().items() for key, _ in entries}
        require(len(self.bases) == 117 and {x[0] for x in self.bases.values()} == skills, 'Skill coverage mismatch')
        for tag in OVERLAYS:
            bank = importlib.import_module('difficulty_revision_' + tag)
            oracle = importlib.import_module('difficulty_revision_' + tag + '_oracle')
            for path, tier in bank.TARGETS:
                require(path in self.bases and tier in range(1, 7), 'Invalid overlay target')
                require((path, tier) not in self.overlays, 'Overlapping revisions require explicit migration')
                self.overlays[path, tier] = (tag, bank.revise, oracle.check)
        require(len(self.overlays) == 33, 'Revision coverage mismatch')
        for tag in REVIEWS:
            review = importlib.import_module('difficulty_review_' + tag)
            for path, notes in review.NOTES.items():
                require(path in self.bases and path not in self.reviews and len(notes) == 6, 'Invalid review coverage')
                self.reviews[path] = review
        require(set(self.reviews) == set(self.bases), 'Missing scope review')
        require(collections.Counter(self.scope(p, t) for p in self.bases for t in range(1, 7)) == SCOPES, 'Scope counts mismatch')

    def _key(self, path, tier, variant=1):
        require(isinstance(path, str) and path in self.bases, 'Unknown pathway')
        require(type(tier) is int and tier in range(1, 7), 'Invalid tier')
        require(type(variant) is int and variant in (1, 2, 3), 'Invalid variant')

    def scope(self, path, tier):
        self._key(path, tier)
        return self.reviews[path].scope(path, tier)

    def eligible(self, path, tier, mode):
        require(isinstance(mode, str) and mode in MODES, 'Unknown selection mode')
        return self.scope(path, tier) in MODES[mode]

    def resolve(self, path, tier, variant, *, mode):
        self._key(path, tier, variant)
        require(self.eligible(path, tier, mode), 'Design not eligible for requested mode')
        return self._resolve(path, tier, variant)

    def _resolve(self, path, tier, variant):
        skill, make, check = self.bases[path]
        tag, make, check = self.overlays.get((path, tier), ('ab', make, check))
        p = make(path, tier, variant)
        require((p['path'], p['tier'], p['variant'], p['focus_skill']) == (path, tier, variant, skill), 'Item identity mismatch')
        require(p['origin'] == 'original' and p['examination_source'] is None, 'Origin mismatch')
        role = ('prerequisite_bridge' if tier == 1 else 'concept_diagnostic' if tier == 2 else 'direct_focus_task')
        require(p['assessment_role'] == role, 'Assessment role mismatch')
        require(check(p), f'Exact-fact check failed: {path}/{tier}/{variant}')
        rubric = p['rubric']
        require(bool(rubric) and all(type(r['marks']) is int and r['marks'] > 0 and r['criterion'] for r in rubric), 'Invalid rubric')
        return {'id': f'CAL.{path}.T{tier}.V{variant}', 'revision': 'FM-16' + tag.upper(), 'scope': self.scope(path, tier),
                'teacher_approved': False, 'marks': sum(r['marks'] for r in rubric), 'payload': p}

    def verify(self, database=None):
        stored, scopes = None, None
        if database is not None:
            with sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True) as db:
                require(db.execute('pragma integrity_check').fetchall() == [('ok',)], 'Database integrity failure')
                require(not db.execute('pragma foreign_key_check').fetchall(), 'Foreign key failure')
                rows = db.execute('select id,path_id,tier,variant,marks,assessment_role,payload,review_status from calibrated_pathway_questions').fetchall()
                stored = {r[0]: r[1:] for r in rows}
                scopes = {(p,t): (s,a) for p,t,s,a in db.execute('select path_id,tier,scope,teacher_approved from difficulty_design_scope')}
                require(len(rows) == len(stored) == 2106 and len(scopes) == 702, 'Stored coverage mismatch')
        counts = collections.Counter()
        modes = collections.Counter({m: 0 for m in MODES})
        prompts = set()
        for path in sorted(self.bases):
            for tier in range(1, 7):
                scope = self.scope(path, tier)
                if scopes is not None:
                    require(scopes[path, tier] == (scope, 0), 'Stored scope/approval mismatch')
                for variant in (1, 2, 3):
                    item = self._resolve(path, tier, variant)
                    p = item['payload']
                    q = p['question_latex']
                    require(q not in prompts, 'Duplicate active prompt')
                    prompts.add(q)
                    counts[item['revision']] += 1
                    for mode in MODES:
                        modes[mode] += self.eligible(path, tier, mode)
                    if stored is not None:
                        row = stored.pop(item['id'])
                        require(row[:5] == (path,tier,variant,item['marks'],p['assessment_role']) and json.loads(row[5]) == p and row[6] == 'exact_facts_checked_editorial_teacher_pending', 'Stored payload mismatch: ' + item['id'])
        require(len(prompts) == 2106 and sum(counts.values()) == 2106 and not stored, 'Active coverage mismatch')
        require(dict(modes) == {'learning_preview':1755, 'exam_candidate_preview':1053, 'challenge_preview':312, 'enrichment_preview':39, 'approved_exam':0}, 'Eligibility mismatch')
        return {'skills': len(self.bases), 'designs': 702, 'items': len(prompts), 'revisions': dict(counts), 'preview_counts': dict(modes), 'database_checked': database is not None, 'teacher_approved': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, help='Optional private SQLite checkpoint (read-only)')
    args = parser.parse_args()
    print(json.dumps(Resolver().verify(args.database), indent=2, sort_keys=True))
