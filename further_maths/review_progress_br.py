"""Private review reconciliation. Observations and calibration are not approval."""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from active_difficulty import require
from calibration_bq import summarize
from review_service_bq import CHECKS, PrivateCatalogue
from marking_review import fingerprint
from scope_review_bl import WATCH


def observation_rows(path):
    if path is None:
        return []
    path = Path(path).resolve()
    require(path.is_file(), 'Observation ledger does not exist')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute('SELECT seq,actor,item_id,fingerprint,revision,proof_sha256,checks,note FROM observations ORDER BY seq')]


def reconcile(items, proof_sha256, observations, calibration=(), *, minimum_attempts):
    require(type(minimum_attempts) is int and minimum_attempts > 1, 'Specify minimum attempts')
    fingerprints = {key: fingerprint(item) for key, item in items.items()}
    latest = {}; stale = 0; seen = set()
    for row in sorted(observations, key=lambda r: r['seq']):
        seq = row['seq']; key = row['item_id']; actor = row['actor']
        require(type(seq) is int and seq > 0 and seq not in seen and isinstance(actor, str) and bool(actor.strip()), 'Invalid observation identity')
        seen.add(seq)
        item = items.get(key)
        if item is None or row['fingerprint'] != fingerprints[key] or row['revision'] != item['revision'] or row['proof_sha256'] != proof_sha256:
            stale += 1; continue
        checks = json.loads(row['checks'])
        require(isinstance(checks, dict) and set(checks) == set(CHECKS) and all(v in ('pass', 'revise', 'not_reviewed') for v in checks.values()), 'Invalid observation checks')
        require(isinstance(row['note'], str) and 1 <= len(row['note'].strip()) <= 2000, 'Missing review evidence note')
        for check, value in checks.items():
            if value != 'not_reviewed':
                latest[key, actor, check] = value
    by_key = {}
    for (key, actor, check), value in latest.items():
        by_key.setdefault((key, check), set()).add(value)
    results = {}; calibration_seen = set(); missing = 0
    for row in calibration:
        key = row['id']
        require(key in items and key not in calibration_seen, 'Unknown or duplicate calibration item')
        calibration_seen.add(key)
        require(set(row) == {'id', 'fingerprint', 'marks', 'counts'} and row['fingerprint'] == fingerprints[key] and row['marks'] == items[key]['marks'], 'Stale calibration record')
        counts = row['counts']
        require(isinstance(counts, list) and len(counts) == items[key]['marks'] + 1, 'Invalid histogram length')
        if all(c is None for c in counts):
            missing += 1; continue
        results[key] = summarize(items[key], row, minimum_attempts=minimum_attempts)
    rows = []
    for key, item in items.items():
        states = {}
        for check in CHECKS:
            values = by_key.get((key, check), set())
            states[check] = 'conflict' if len(values) > 1 else next(iter(values), 'not_reviewed')
        p = item['payload']; watched = (p['path'], p['tier']) in WATCH
        rows.append({'id': key, 'fingerprint': fingerprints[key], 'revision': item['revision'], 'scope_watch': watched,
                     'checks': states, 'calibration': results.get(key), 'teacher_approved': False, 'exam_ready': False})
    def priority(r):
        states = set(r['checks'].values())
        return (0 if states & {'conflict', 'revise'} else 1 if r['scope_watch'] else 2 if r['revision'] == 'FM-16BQ' else 3,
                'not_reviewed' not in states, r['id'])
    rows.sort(key=priority)
    counts = {check: {status: sum(r['checks'][check] == status for r in rows) for status in ('not_reviewed', 'pass', 'revise', 'conflict')} for check in CHECKS}
    return {'items': len(rows), 'observations_received': len(seen), 'stale_observations': stale,
            'observation_counts': counts, 'scope_watches': sum(r['scope_watch'] for r in rows),
            'all_checks_pass_observations': sum(all(v == 'pass' for v in r['checks'].values()) for r in rows),
            'calibration_histograms_received': len(results), 'calibration_blank_templates': missing,
            'calibration_minimum_attempts_met': sum(r['minimum_attempts_met'] for r in results.values()),
            'minimum_attempts': minimum_attempts, 'proof_sha256': proof_sha256,
            'teacher_approved': 0, 'fm17_ready': False, 'release_allowed': False, 'items_by_priority': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--observations', type=Path)
    parser.add_argument('--calibration', type=Path)
    parser.add_argument('--minimum-attempts', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--editorial-bundle', type=Path, help='Directory containing the BS visual and scope registers')
    args = parser.parse_args()
    catalogue = PrivateCatalogue(args.bundle)
    calibration = [] if args.calibration is None else [json.loads(line) for line in args.calibration.read_text().splitlines() if line.strip()]
    report = reconcile(catalogue.items, catalogue.proof_sha256, observation_rows(args.observations), calibration, minimum_attempts=args.minimum_attempts)
    if args.editorial_bundle is not None:
        from marking_batch import read_batch
        from review_queue_bs import add_editorial_evidence
        report = add_editorial_evidence(report, read_batch(args.editorial_bundle / 'FM16BS-visual.jsonl'),
                                        read_batch(args.editorial_bundle / 'FM16BS-scope.jsonl'))
    with args.output.open('x') as f:
        json.dump(report, f, indent=2); f.write('\n')


if __name__ == '__main__':
    main()
