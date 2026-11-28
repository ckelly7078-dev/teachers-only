"""Bind private note-level examination-to-subskill mappings to exact source evidence."""
import collections
import copy
import hashlib
import json
from active_difficulty import require

# Paraphrased from the introductions to the archived AS1 mark schemes.
# These principles require an item-specific marking route and human judgment.
CCEA_POLICY = {
    'method': 'Credit a correct method; incorrect methods do not earn method-based credit.',
    'working': 'Credit accurate working based on the valid method.',
    'combined': 'Keep a printed MW allocation combined; do not split it without evidence.',
    'alternative': 'Evaluate valid alternative approaches, subject to the task restrictions.',
    'follow_through': 'After penalising a working or transcription error, assess later dependent working using the candidate value when mathematically valid; do not penalise the same error again.',
    'easier_misread': 'A misread that reduces demand requires an item-specific cap and professional judgment.',
    'automatic_award': False,
}


def part_signature(bank, key):
    p = bank.parts[key]
    data = {'part': p, 'paper_sha256': bank.sources[p['paper_source']]['sha256'],
            'scheme_sha256': bank.sources[p['scheme_source']]['sha256']}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def bind_subskills(bank, records):
    """Accept only complete, private, note-derived mappings. No exact item equivalence."""
    seen = set(); by_skill = collections.defaultdict(list)
    for record in records:
        key = (record['series'],record['number'],record['ordinal'])
        require(key in bank.parts and key not in seen, 'Unknown or repeated source part')
        seen.add(key)
        require(record['basis'] == 'editorial_mapping_from_source_checked_note' and
                record['part_signature'] == part_signature(bank,key), 'Stale source mapping')
        skills = record['skills']
        require(isinstance(skills,list) and len(skills) == len(set(skills)), 'Duplicate or invalid subskills')
        require(isinstance(record['note'],str) and record['note'].strip(), 'Mapping rationale required')
        for skill in skills:
            require(skill in bank.skills and key in bank.links[bank.skills[skill]['concept_id']], 'Mapping exceeds source parent link')
            by_skill[skill].append(key)
    require(seen == set(bank.parts), 'Incomplete source part mapping')
    return dict(by_skill)


def enriched_evidence(bank, subskills, skill):
    context = bank.evidence(skill)
    direct = [bank.parts[key] for key in subskills.get(skill,[])]
    context.update(note_linked_parts=copy.deepcopy(direct),
                   note_linked_demand_counts=dict(collections.Counter(r['demand'] for r in direct)),
                   subskill_link_basis='editorial_mapping_from_source_checked_note' if direct else 'no_note_linked_part',
                   official_marking_policy=copy.deepcopy(CCEA_POLICY))
    return context
