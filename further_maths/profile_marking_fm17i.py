"""Tier-aware bounded partial original-rubric observations; no grading or source rules."""
import copy
import hashlib
import json
from itertools import permutations
from pathlib import Path
from active_difficulty import require
from engine_fm17d import reconcile_proposal
from marking_batch import read_batch
from marking_review import fingerprint
from profile_marking_fm17h import ProfileMarking, matches


def tier_matches(rule, value, target):
    """Compare heterogeneous exact sets without treating mismatched shapes as errors."""
    require(rule in ('equal', 'unordered', 'proportional', 'line'), 'Unsupported comparison rule')
    if rule != 'unordered':
        return matches(rule, value, target)
    require(isinstance(value, list) and isinstance(target, list)
            and len(value) == len(target) and 0 < len(target) <= 6, 'Invalid set representation')
    matrix = []
    for actual in value:
        row = []
        for expected in target:
            try:
                row.append(matches('equal', actual, expected))
            except ValueError:
                row.append(None)
        require(any(x is not None for x in row), 'Unsupported set member representation')
        matrix.append(row)
    return any(all(matrix[i][j] is True for i, j in enumerate(p))
               for p in permutations(range(len(target))))


class TierMarking:
    def __init__(self, engine, prior, records):
        self.engine, self.prior, self._profiles = engine, prior, {}
        for row in records:
            key = row['id']
            require(key in engine.bank.items and key not in self._profiles, 'Unknown or duplicate profile')
            item = engine.bank.items[key]
            p = item['payload']
            require(p['tier'] in (1, 2, 4, 5, 6) and row['tier'] == p['tier']
                    and row['revision'] == item['revision'] and row['fingerprint'] == fingerprint(item)
                    and row['basis'] == 'independent_prompt_observations', 'Stale or invalid profile')
            specs = row['criteria']
            require(isinstance(specs, list) and specs, 'Empty profile')
            seen = set()
            for spec in specs:
                n = spec['index']
                require(type(n) is int and 1 <= n <= len(p['rubric']) and n not in seen, 'Invalid criterion index')
                rubric = p['rubric'][n-1]
                require(set(spec) == {'index', 'type', 'marks', 'rule', 'expected'}
                        and spec['type'] == rubric['type'] == 'A' and spec['marks'] == rubric['marks'] == 1,
                        'Only explicitly checked single accuracy criteria supported')
                require(tier_matches(spec['rule'], spec['expected'], spec['expected']), 'Invalid reference')
                seen.add(n)
            self._profiles[key] = copy.deepcopy(row)

    @classmethod
    def from_bundle(cls, engine, root):
        prior = ProfileMarking.from_bundle(engine, root)
        folder = Path(root)/'FM17I'
        manifest = json.loads((folder/'runtime-manifest.json').read_text())
        require(manifest['checkpoint'] == 'FM-17I', 'Invalid manifest')
        file = folder/'profiles.jsonl'
        with file.open('rb') as stream:
            require(hashlib.file_digest(stream, 'sha256').hexdigest() == manifest['sha256']['profiles.jsonl'], 'Profile hash mismatch')
        rows = read_batch(file)
        require(len(rows) == manifest['profile_count'], 'Profile count mismatch')
        return cls(engine, prior, rows)

    def capability(self, item_id, *, mode, item_fingerprint):
        args = dict(mode=mode, item_fingerprint=item_fingerprint)
        result = self.prior.capability(item_id, **args)
        if item_id in self._profiles:
            specs = self._profiles[item_id]['criteria']
            n = len(self.engine.bank.items[item_id]['payload']['rubric'])
            result.update(structured_checks_available=True, basis='bounded_accuracy_observations',
                          coverage='full' if len(specs) == n else 'partial',
                          checked_criteria=[f"c{s['index']}" for s in specs], total_criteria=n)
        else:
            result['coverage'] = 'full' if result['structured_checks_available'] else 'none'
        return result

    def check_work(self, item_id, *, mode, item_fingerprint, work):
        args = dict(mode=mode, item_fingerprint=item_fingerprint)
        if item_id not in self._profiles:
            return self.prior.check_work(item_id, work=work, **args)
        context = self.engine.marking_context(item_id, **args)
        row = self._profiles[item_id]
        require(row['fingerprint'] == item_fingerprint, 'Stale profile')
        specs = {f"c{s['index']}": s for s in row['criteria']}
        require(isinstance(work, dict) and set(work) == set(specs), 'Unexpected observation fields')
        decisions = []
        for c in context['criteria']:
            key = c['id']
            spec = specs.get(key)
            status = 'uncertain'
            if spec is not None:
                require((c['type'], c['marks']) == (spec['type'], spec['marks']), 'Rubric mismatch')
                if work[key] is not None:
                    status = 'met' if tier_matches(spec['rule'], work[key], spec['expected']) else 'not_met'
            decisions.append(dict(criterion_id=key, status=status,
                                  evidence='Bounded accuracy observation compared.' if status != 'uncertain'
                                  else 'Unavailable or unsupported criterion evidence.'))
        result = reconcile_proposal(context, decisions)
        result['basis'] = 'bounded_accuracy_checks_with_unresolved_other_criteria'
        return result
