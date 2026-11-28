"""Attach private editorial evidence to an existing teacher progress report."""
from collections import Counter
from active_difficulty import require


def add_editorial_evidence(report, visual, scope):
    """Validate the complete scope register and the inspected subset before use."""
    items = {row['id']: row for row in report['items_by_priority']}
    guarded = {key for key, row in items.items() if row['scope_watch']}

    def bind(records, decisions):
        result = {}
        for record in records:
            key = record['id']
            require(key in items and key not in result, 'Unknown or repeated editorial item')
            require(record['fingerprint'] == items[key]['fingerprint']
                    and record['revision'] == items[key]['revision']
                    and record['proof_sha256'] == report['proof_sha256'], 'Stale editorial evidence')
            require(record['reviewer_kind'] == 'ai_editorial' and record['teacher_approved'] is False
                    and record['decision'] in decisions and isinstance(record['note'], str)
                    and record['note'].strip(), 'Invalid editorial decision')
            result[key] = record['decision']
        return result

    inspections = bind(visual, {'inspected', 'revise'})
    dispositions = bind(scope, {'learning_only', 'open'})
    require(set(dispositions) == guarded, 'Incomplete guarded scope register')
    rows = [dict(row, ai_visual=inspections.get(row['id'], 'uninspected'),
                 editorial_scope=dispositions.get(row['id'])) for row in items.values()]

    def priority(row):
        teacher = set(row['checks'].values())
        if teacher & {'conflict', 'revise'}:
            return 0
        if row['ai_visual'] == 'revise':
            return 1
        if row['editorial_scope'] == 'open':
            return 2
        if row['ai_visual'] == 'uninspected':
            return 3
        return 4

    # The stable sort preserves the previous ordering within each priority.
    rows.sort(key=priority)
    return {**report, 'items_by_priority': rows, 'ai_visual_counts': dict(Counter(r['ai_visual'] for r in rows)),
            'editorial_scope_counts': dict(Counter(dispositions.values()))}
