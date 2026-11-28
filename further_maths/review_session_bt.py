"""Read-only, actor-specific progress for guarded teacher previews.

This is an observation aid, not certification or an examination-release gate.
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from active_difficulty import require
from scope_review_bl import WATCH


CHECKS = ('visual', 'mathematics', 'marking', 'scope', 'difficulty')
STATES = ('needs_revision', 'outstanding', 'all_checks_observed_pass')


def actor_progress(catalogue, ledger, actor, mode):
    """Use only the authenticated actor, current item/proof, and allowed IDs."""
    require(isinstance(actor, str) and bool(actor.strip()), 'Teacher identity required')
    ids = catalogue.list_ids(mode)
    eligible = set(ids)
    require(len(eligible) == len(ids), 'Duplicate preview IDs')
    latest = {}
    stale = 0
    if ledger is not None:
        path = Path(ledger).resolve()
        if path.exists():
            require(path.is_file(), 'Invalid observation ledger')
            with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
                # Never select notes, actor names, or other teachers' observations.
                rows = db.execute('SELECT item_id,fingerprint,revision,proof_sha256,checks '
                                  'FROM observations WHERE actor=? COLLATE BINARY ORDER BY seq', (actor,))
                for key, fingerprint, revision, proof, raw in rows:
                    if key not in eligible:
                        continue
                    page = catalogue.pages[key]
                    if (fingerprint != page['fingerprint'] or revision != page['revision']
                            or proof != catalogue.proof_sha256):
                        stale += 1
                        continue
                    checks = json.loads(raw)
                    require(isinstance(checks, dict) and set(checks) == set(CHECKS)
                            and all(v in ('pass', 'revise', 'not_reviewed') for v in checks.values()),
                            'Invalid observation checks')
                    current = latest.setdefault(key, {})
                    for check, value in checks.items():
                        if value != 'not_reviewed':
                            current[check] = value
    counts = dict.fromkeys(STATES, 0)
    result = []
    for key in ids:
        checks = {c: latest.get(key, {}).get(c, 'not_reviewed') for c in CHECKS}
        values = set(checks.values())
        state = ('needs_revision' if 'revise' in values else
                 'all_checks_observed_pass' if values == {'pass'} else 'outstanding')
        counts[state] += 1
        item = catalogue.items[key]
        p = item['payload']
        result.append({'id': key, 'state': state, 'checks': checks,
                       'scope_watch': (p['path'], p['tier']) in WATCH})
    # A revision request outranks a new review. Scope watches and successors
    # come first within the same state, but never bypass mode eligibility.
    result.sort(key=lambda r: (STATES.index(r['state']), not r['scope_watch'],
                               catalogue.pages[r['id']]['revision'] != 'FM-16BQ', r['id']))
    return {'mode': mode, 'recording_available': ledger is not None,
            'proof_sha256': catalogue.proof_sha256, 'counts': counts,
            'stale_observations_in_mode': stale, 'items': result,
            'release_allowed': False, 'teacher_approved': False}
