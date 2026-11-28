"""FM-16AM: active AS1 resolver and read-only verification; not release approval."""
import argparse
import collections
import importlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from skill_detail import detail_map

BASES = ('', *('abcdefghijklmnopqrstuvwxyz'[1:]), 'aa', 'ab')
OVERLAYS = ('ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'an', 'ao', 'ap', 'aq', 'as', 'au', 'av', 'aw', 'ax', 'ay', 'az', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'bj', 'bk', 'bl', 'bm', 'bm4', 'bn5', 'bn9')
# Each successor must name its exact current predecessor; no implicit overwrite.
SUCCESSIONS = {('angle-units', 6, 'ba'): 'ad', ('angle-units', 5, 'bj'): 'ay', ('argument-range', 5, 'bj'): 'ay', ('cartesian-to-polar', 5, 'bj'): 'az', ('complex-division', 5, 'bj'): 'aw', ('conjugate-product', 4, 'bj'): 'aw', ('inverse-systems', 5, 'bj'): 'be', ('related-solids', 5, 'bj'): 'bh', ('solve-cubic', 5, 'bj'): 'ax', ('solve-quartic', 5, 'bj'): 'ax', ('vector-plane', 5, 'bj'): 'bg', ('polar-geometry', 3, 'bk'): 'ay', ('argand-displacement', 4, 'bk'): 'ay', ('cartesian-sums', 4, 'bk'): 'aw', ('cross-product', 4, 'bk'): 'bf', ('det-area', 4, 'bk'): 'bd', ('fixed-invariant', 4, 'bk'): 'bc', ('invariant-lines', 4, 'bk'): 'bc', ('inverse-three', 4, 'bk'): 'bd', ('line-line-distance', 4, 'bk'): 'bh', ('plane-intersection-direction', 4, 'bk'): 'bh', ('point-line', 4, 'bk'): 'bh', ('symmetric-parameter', 4, 'bk'): 'au', ('system-consistency', 4, 'bk'): 'be', ('basis-images', 5, 'bk'): 'bc', ('exact-radians', 5, 'bk'): 'ay', ('line-line-distance', 5, 'bk'): 'bh', ('locus-intersection', 5, 'bk'): 'az', ('plane-cartesian', 5, 'bk'): 'bg', ('plane-intersection-direction', 5, 'bk'): 'bh', ('point-line', 5, 'bk'): 'bh', ('polar-quotients', 5, 'bk'): 'az', ('unit-vector', 5, 'bk'): 'bf', ('vector-components', 5, 'bk'): 'bf', ('vector-line-equation', 5, 'bk'): 'bg', ('verify-roots', 5, 'bk'): 'ax', ('argument-range', 6, 'bk'): 'ad', ('complex-division', 6, 'bk'): 'ad', ('conjugate-product', 5, 'bk'): 'aw', ('related-solids', 6, 'bk'): 'bh', ('solve-cubic', 6, 'bk'): 'ax', ('solve-quartic', 6, 'bk'): 'ax', ('vector-plane', 6, 'bk'): 'bg'}
SUCCESSIONS.update({('inverse-three', 5, 'bl'): 'bd', ('locus-intersection', 6, 'bl'): 'az', ('plane-cartesian', 6, 'bl'): 'bg', ('point-line', 6, 'bl'): 'bh', ('symmetric-parameter', 5, 'bl'): 'av', ('system-consistency', 5, 'bl'): 'be', ('verify-roots', 6, 'bl'): 'ax', ('cube-sums', 4, 'bl'): 'au', ('matrix-equation', 5, 'bl'): 'bd', ('plane-plane-angle', 5, 'bl'): 'bg', ('scaled-roots', 5, 'bl'): 'av'})
SUCCESSIONS.update({('cube-sums', 2, 'bm'): 'au', ('shifted-products', 2, 'bm'): 'au', ('scaled-roots', 6, 'bm'): 'av', ('shifted-products', 6, 'bm'): 'av'})
# Exact, separately authorised old/new mark totals. All other successions preserve marks.
SUCCESSIONS.update({('argument-normalization', 4, 'bm4'): 'az', ('cartesian-product', 3, 'bm4'): 'as', ('cartesian-sums', 4, 'bm4'): 'bk', ('conjugate-find', 3, 'bm4'): 'aw', ('standard-cartesian', 5, 'bm4'): 'aw', ('complex-quadratic', 4, 'bm4'): 'ax', ('conjugate-deduction', 2, 'bm4'): 'ax', ('distance-circle', 6, 'bm4'): 'az', ('polar-geometry', 3, 'bm4'): 'bk', ('polar-products', 5, 'bm4'): 'an', ('polar-products', 6, 'bm4'): 'az', ('polar-quotients', 4, 'bm4'): 'az', ('polar-quotients', 6, 'bm4'): 'az', ('polar-to-cartesian', 6, 'bm4'): 'az', ('solve-quartic', 6, 'bm4'): 'bk'})

SUCCESSIONS.update({('composition-order', 2, 'bn5'): 'bc', ('composition-order', 3, 'bn5'): 'bc', ('composition-order', 4, 'bn5'): 'bc', ('composition-order', 5, 'bn5'): 'bc', ('composition-compute', 4, 'bn5'): 'bc', ('composition-compute', 5, 'bn5'): 'bc', ('orientation', 4, 'bn5'): 'bd', ('fixed-points', 2, 'bn5'): 'bc', ('fixed-invariant', 4, 'bn5'): 'bk', ('fixed-invariant', 5, 'bn5'): 'bc', ('invariant-lines', 2, 'bn5'): 'bc', ('invariant-lines', 4, 'bn5'): 'bk', ('det-two', 2, 'bn5'): 'bb', ('det-three', 2, 'bn5'): 'bd', ('det-three', 6, 'bn5'): 'bd', ('det-area', 2, 'bn5'): 'bd', ('det-area', 4, 'bn5'): 'bk', ('det-area', 6, 'bn5'): 'bd', ('det-classification', 2, 'bn5'): 'bd', ('singular-condition', 2, 'bn5'): 'bd', ('singular-condition', 4, 'bn5'): 'bd', ('collapse', 1, 'bn5'): 'bd', ('collapse', 2, 'bn5'): 'bd', ('inverse-two', 1, 'bn5'): 'bd', ('inverse-two', 3, 'bn5'): 'bd', ('inverse-two', 6, 'bn5'): 'aj', ('inverse-product', 2, 'bn5'): 'bd', ('inverse-three', 3, 'bn5'): 'bd', ('inverse-three', 5, 'bn5'): 'bl', ('inverse-three', 6, 'bn5'): 'bd', ('inverse-identities', 2, 'bn5'): 'bd', ('inverse-identities', 3, 'bn5'): 'bd', ('matrix-equation', 1, 'bn5'): 'bd', ('matrix-equation', 2, 'bn5'): 'bd', ('system-consistency', 2, 'bn5'): 'be', ('system-classification', 1, 'bn5'): 'be', ('system-classification', 2, 'bn5'): 'be', ('nonunique-set', 5, 'bn5'): 'be', ('three-plane-unique', 2, 'bn5'): 'be', ('three-plane-unique', 3, 'bn5'): 'be', ('two-variable-system', 2, 'bn5'): 'be', ('inverse-systems', 2, 'bn5'): 'be', ('inverse-systems', 4, 'bn5'): 'be', ('inverse-systems', 6, 'bn5'): 'aj', ('three-system', 2, 'bn5'): 'be', ('inconsistent-geometry', 1, 'bn5'): 'be', ('inconsistent-geometry', 4, 'bn5'): 'be', ('nonunique-geometry', 2, 'bn5'): 'be', ('nonunique-geometry', 4, 'bn5'): 'be', ('nonunique-geometry', 6, 'bn5'): 'be', ('basis-images', 2, 'bn5'): 'bc', ('basis-images', 5, 'bn5'): 'bk', ('describe-transform', 2, 'bn5'): 'bc', ('describe-transform', 5, 'bn5'): 'bc', ('describe-transform', 6, 'bn5'): 'bc', ('figure-images', 2, 'bn5'): 'bc', ('figure-images', 4, 'bn5'): 'bc', ('figure-images', 5, 'bn5'): 'bc', ('figure-images', 6, 'bn5'): 'bc', ('identity-operations', 1, 'bn5'): 'bb', ('identity-operations', 4, 'bn5'): 'bb', ('identity-operations', 5, 'bn5'): 'bb', ('matrix-add-subtract', 2, 'bn5'): 'bb', ('matrix-add-subtract', 6, 'bn5'): 'bb', ('matrix-conformability', 2, 'bn5'): 'bb', ('matrix-products', 2, 'bn5'): 'bb', ('matrix-products', 3, 'bn5'): 'bb', ('scalar-matrix', 2, 'bn5'): 'bb', ('scalar-matrix', 5, 'bn5'): 'bb', ('scalar-matrix', 6, 'bn5'): 'bb', ('zero-matrix', 2, 'bn5'): 'bb'})

SUCCESSIONS.update({('vector-components', 2, 'bn9'): 'bf', ('vector-components', 4, 'bn9'): 'bf', ('vector-components', 6, 'bn9'): 'bf', ('vector-combinations', 2, 'bn9'): 'bf', ('vector-combinations', 5, 'bn9'): 'bf', ('vector-combinations', 6, 'bn9'): 'bf', ('unit-vector', 2, 'bn9'): 'bf', ('unit-vector', 4, 'bn9'): 'bf', ('unit-vector', 5, 'bn9'): 'bk', ('scalar-product', 6, 'bn9'): 'ao', ('perpendicular-test', 3, 'bn9'): 'bf', ('perpendicular-test', 4, 'bn9'): 'bf', ('perpendicular-test', 6, 'bn9'): 'bf', ('perpendicular-parameter', 2, 'bn9'): 'bf', ('perpendicular-parameter', 5, 'bn9'): 'bf', ('perpendicular-parameter', 6, 'bn9'): 'ao', ('cross-product', 4, 'bn9'): 'bk', ('cross-product', 5, 'bn9'): 'bf', ('cross-order', 2, 'bn9'): 'bf', ('cross-order', 4, 'bn9'): 'bf', ('cross-order', 6, 'bn9'): 'bf', ('cross-linearity', 2, 'bn9'): 'bf', ('cross-linearity', 3, 'bn9'): 'bf', ('cross-linearity', 5, 'bn9'): 'bf', ('cross-linearity', 6, 'bn9'): 'bf', ('zero-cross', 3, 'bn9'): 'bf', ('zero-cross', 4, 'bn9'): 'bf', ('vector-line-equation', 2, 'bn9'): 'bg', ('vector-line-equation', 4, 'bn9'): 'bg', ('vector-line-equation', 6, 'bn9'): 'bg', ('cartesian-line', 2, 'bn9'): 'bg', ('cartesian-line', 4, 'bn9'): 'bg', ('zero-direction', 2, 'bn9'): 'bg', ('zero-direction', 4, 'bn9'): 'bg', ('zero-direction', 6, 'bn9'): 'bg', ('vector-plane', 3, 'bn9'): 'bg', ('vector-plane', 4, 'bn9'): 'bg', ('vector-plane', 6, 'bn9'): 'bk', ('plane-cartesian', 2, 'bn9'): 'bg', ('plane-cartesian', 4, 'bn9'): 'bg', ('plane-cartesian', 5, 'bn9'): 'bk', ('plane-cartesian', 6, 'bn9'): 'bl', ('plane-normal', 2, 'bn9'): 'bg', ('plane-normal', 3, 'bn9'): 'bg', ('plane-normal', 4, 'bn9'): 'bg', ('cross-normal', 3, 'bn9'): 'bg', ('cross-normal', 4, 'bn9'): 'bg', ('cross-normal', 6, 'bn9'): 'bg', ('normal-dot-plane', 2, 'bn9'): 'bg', ('normal-dot-plane', 3, 'bn9'): 'bg', ('normal-dot-plane', 4, 'bn9'): 'bg', ('normal-dot-plane', 5, 'bn9'): 'bg', ('normal-dot-plane', 6, 'bn9'): 'bg', ('line-line-angle', 5, 'bn9'): 'bg', ('line-line-angle', 6, 'bn9'): 'bg', ('plane-plane-angle', 2, 'bn9'): 'bg', ('plane-plane-angle', 3, 'bn9'): 'bg', ('plane-plane-angle', 6, 'bn9'): 'bg', ('line-plane-angle', 2, 'bn9'): 'bg', ('line-plane-angle', 4, 'bn9'): 'bg', ('line-plane-angle', 5, 'bn9'): 'bg', ('line-plane-angle', 6, 'bn9'): 'ao', ('line-intersection', 2, 'bn9'): 'bh', ('line-intersection', 4, 'bn9'): 'bh', ('line-plane-intersection', 6, 'bn9'): 'ak', ('point-line', 2, 'bn9'): 'bh', ('point-line', 3, 'bn9'): 'bh', ('point-line', 5, 'bn9'): 'bk', ('point-line', 6, 'bn9'): 'bl', ('skew', 4, 'bn9'): 'bh', ('skew', 6, 'bn9'): 'al', ('point-plane', 2, 'bn9'): 'bh', ('point-plane', 4, 'bn9'): 'bh', ('point-plane', 5, 'bn9'): 'bh', ('point-plane', 6, 'bn9'): 'bh', ('line-line-distance', 2, 'bn9'): 'bh', ('line-line-distance', 6, 'bn9'): 'ap', ('triangle-area', 5, 'bn9'): 'bh', ('triangle-area', 6, 'bn9'): 'ao', ('triple-volume', 6, 'bn9'): 'bh', ('plane-intersection-direction', 3, 'bn9'): 'bh', ('plane-intersection-direction', 5, 'bn9'): 'bk', ('plane-intersection-direction', 6, 'bn9'): 'aq', ('parallelogram-area', 3, 'bn9'): 'bh', ('parallelogram-area', 4, 'bn9'): 'bh', ('parallelogram-area', 5, 'bn9'): 'bh', ('parallelogram-area', 6, 'bn9'): 'bh', ('plane-common-point', 2, 'bn9'): 'bh', ('plane-common-point', 4, 'bn9'): 'bh', ('plane-common-point', 5, 'bn9'): 'bh', ('plane-common-point', 6, 'bn9'): 'bh', ('related-solids', 2, 'bn9'): 'bh', ('related-solids', 5, 'bn9'): 'bj', ('related-solids', 6, 'bn9'): 'bk', ('plane-intersection-line', 1, 'bn9'): 'bh', ('plane-intersection-line', 2, 'bn9'): 'bh', ('plane-intersection-line', 3, 'bn9'): 'bh', ('plane-intersection-line', 4, 'bn9'): 'bh', ('plane-intersection-line', 5, 'bn9'): 'bh', ('plane-intersection-line', 6, 'bn9'): 'bh', ('justify-skew', 1, 'bn9'): 'bh', ('justify-skew', 4, 'bn9'): 'bh', ('justify-skew', 6, 'bn9'): 'ap'})

MARK_SUCCESSIONS = {('angle-units', 5, 'bj'): (2, 3), ('argument-range', 5, 'bj'): (2, 5), ('cartesian-to-polar', 5, 'bj'): (3, 5), ('complex-division', 5, 'bj'): (2, 6), ('conjugate-product', 4, 'bj'): (2, 5), ('inverse-systems', 5, 'bj'): (3, 6), ('related-solids', 5, 'bj'): (2, 6), ('solve-cubic', 5, 'bj'): (3, 6), ('solve-quartic', 5, 'bj'): (3, 7), ('vector-plane', 5, 'bj'): (3, 6), ('polar-geometry', 3, 'bk'): (2, 4), ('argand-displacement', 4, 'bk'): (3, 5), ('cartesian-sums', 4, 'bk'): (2, 4), ('cross-product', 4, 'bk'): (3, 5), ('det-area', 4, 'bk'): (2, 4), ('fixed-invariant', 4, 'bk'): (3, 5), ('invariant-lines', 4, 'bk'): (3, 5), ('inverse-three', 4, 'bk'): (4, 6), ('line-line-distance', 4, 'bk'): (3, 5), ('plane-intersection-direction', 4, 'bk'): (3, 5), ('point-line', 4, 'bk'): (2, 4), ('symmetric-parameter', 4, 'bk'): (3, 5), ('system-consistency', 4, 'bk'): (2, 5), ('basis-images', 5, 'bk'): (3, 5), ('exact-radians', 5, 'bk'): (3, 5), ('line-line-distance', 5, 'bk'): (3, 5), ('locus-intersection', 5, 'bk'): (2, 5), ('plane-cartesian', 5, 'bk'): (3, 6), ('plane-intersection-direction', 5, 'bk'): (3, 5), ('point-line', 5, 'bk'): (2, 5), ('polar-quotients', 5, 'bk'): (3, 5), ('unit-vector', 5, 'bk'): (3, 5), ('vector-components', 5, 'bk'): (3, 5), ('vector-line-equation', 5, 'bk'): (3, 5), ('verify-roots', 5, 'bk'): (3, 5), ('argument-range', 6, 'bk'): (4, 6), ('complex-division', 6, 'bk'): (5, 7), ('conjugate-product', 5, 'bk'): (4, 5), ('related-solids', 6, 'bk'): (4, 7), ('solve-cubic', 6, 'bk'): (4, 7), ('solve-quartic', 6, 'bk'): (4, 8), ('vector-plane', 6, 'bk'): (5, 7)}
MARK_SUCCESSIONS.update({('inverse-three', 5, 'bl'): (3, 7), ('locus-intersection', 6, 'bl'): (3, 6), ('plane-cartesian', 6, 'bl'): (3, 6), ('point-line', 6, 'bl'): (3, 6), ('symmetric-parameter', 5, 'bl'): (3, 6), ('system-consistency', 5, 'bl'): (3, 6), ('verify-roots', 6, 'bl'): (4, 6), ('cube-sums', 4, 'bl'): (2, 4), ('matrix-equation', 5, 'bl'): (3, 5), ('plane-plane-angle', 5, 'bl'): (3, 4), ('scaled-roots', 5, 'bl'): (3, 4)})
REVIEWS = ('af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al')
SCOPES = {'prerequisite_bridge_reviewed': 117, 'conceptual_diagnostic_reviewed': 117,
          'syllabus_linked_candidate': 351, 'challenge_candidate': 104, 'enrichment_only': 13}
MODES = {'learning_preview': {'prerequisite_bridge_reviewed', 'conceptual_diagnostic_reviewed', 'syllabus_linked_candidate'},
         'exam_candidate_preview': {'syllabus_linked_candidate'}, 'challenge_preview': {'challenge_candidate'},
         'enrichment_preview': {'enrichment_only'}, 'approved_exam': set()}


MARK_SUCCESSIONS.update({('inverse-three', 6, 'bn5'): (3, 8)})


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Resolver:
    def __init__(self, *, historical_through=None):
        # Explicit, read-only historical evidence view; never a selection route.
        require(historical_through is None or historical_through in ('bh', 'bj', 'bk', 'bl', 'bm', 'bm4', 'bn5'), 'Unknown historical view')
        self.historical_through = historical_through
        tags = OVERLAYS if historical_through is None else OVERLAYS[:OVERLAYS.index(historical_through)+1]
        successions = SUCCESSIONS if historical_through is None else {key: value for key, value in SUCCESSIONS.items() if key[2] in tags}
        self.bases, self.overlays, self.reviews, self.versions = {}, {}, {}, {}
        used_successions = set()
        for suffix in BASES:
            name = 'calibration' + ('_' + suffix if suffix else '')
            bank = importlib.import_module(name + '_bank')
            oracle = importlib.import_module(name + '_oracle')
            for path, skill in bank.PATHS.items():
                require(path not in self.bases, 'Duplicate base: ' + path)
                self.bases[path] = (skill, bank.make, oracle.check)
        skills = {f'{concept}.{key}' for concept, entries in detail_map().items() for key, _ in entries}
        require(len(self.bases) == 117 and {x[0] for x in self.bases.values()} == skills, 'Skill coverage mismatch')
        for tag in tags:
            bank = importlib.import_module('difficulty_revision_' + tag)
            oracle = importlib.import_module('difficulty_revision_' + tag + '_oracle')
            for path, tier in bank.TARGETS:
                require(path in self.bases and tier in range(1, 7), 'Invalid overlay target')
                key = (path, tier)
                succession = (path, tier, tag)
                previous = self.overlays.get(key)
                if previous is not None:
                    require(successions.get(succession) == previous[0], 'Overlapping revisions require exact predecessor authorisation')
                    used_successions.add(succession)
                else:
                    require(succession not in successions, 'Authorised predecessor missing')
                self.overlays[key] = (tag, bank.revise, oracle.check)
                self.versions[path, tier, tag] = self.overlays[key]
        require(used_successions == set(successions), 'Unused succession authorisation')
        require(len(self.overlays) == 702, 'Revision coverage mismatch')
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
        require(self.historical_through is None, 'Historical resolver cannot select questions')
        self._key(path, tier, variant)
        require(self.eligible(path, tier, mode), 'Design not eligible for requested mode')
        return self._resolve(path, tier, variant)

    def _resolve(self, path, tier, variant):
        self._key(path, tier, variant)
        tag = self.overlays.get((path, tier), ('ab',))[0]
        return self._resolve_version(path, tier, variant, tag)

    def _resolve_version(self, path, tier, variant, tag):
        # Internal historical audit only; never a preview selection route.
        self._key(path, tier, variant)
        skill, make, check = self.bases[path]
        if tag != 'ab':
            require((path, tier, tag) in self.versions, 'Unknown item revision')
            tag, make, check = self.versions[path, tier, tag]
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
            with closing(sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)) as db:
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
