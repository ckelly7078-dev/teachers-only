"""FM-16BI: structural progression and source-reference audit, not calibration."""
import argparse
import collections
import json
from pathlib import Path
from active_difficulty import Resolver, require
from marking_review import inventory_entry
from marking_batch import read_batch, validate_batch

# Local locators: printed page, bullet ordinal on that page, NOT official IDs.
# Concept crosswalk to the supplied CCEA AS1 specification, section 3.2.
OUTCOMES = {
    'ALG.roots-coefficients': (9, 1), 'ALG.related-quadratic': (9, 2),
    'CPX.quadratic': (9, 3), 'CPX.cubic-quartic': (9, 4),
    'CPX.arithmetic': (9, 5), 'CPX.parts': (9, 6), 'CPX.conjugate': (9, 7),
    'CPX.conjugate-roots': (9, 8), 'CPX.argand': (9, 9),
    'CPX.radians': (9, 10), 'CPX.polar': (9, 11),
    'CPX.conversion': (10, 1), 'CPX.polar-arithmetic': (10, 2), 'CPX.loci': (10, 3),
    'MAT.arithmetic': (10, 4), 'MAT.scalar': (10, 5), 'MAT.identity': (10, 6),
    'MAT.transformation': (10, 7), 'MAT.composition': (10, 8),
    'MAT.invariants': (10, 9), 'MAT.determinant': (10, 10),
    'MAT.area-scale': (10, 11), 'MAT.zero-transformation': (10, 12),
    'MAT.singular': (10, 13), 'MAT.inverse-properties': (10, 14),
    'MAT.inverse': (11, 1), 'MAT.systems': (11, 2),
    'MAT.zero-system': (11, 3), 'MAT.geometry-system': (11, 4),
    'VEC.3d': (11, 5), 'VEC.line': (11, 6), 'VEC.plane': (11, 7),
    'VEC.scalar-product': (11, 8), 'VEC.perpendicular': (11, 9),
    'VEC.intersections': (11, 10), 'VEC.skew': (11, 11),
    'VEC.distance': (11, 12), 'VEC.plane-intersection': (11, 13),
    'VEC.vector-product': (12, 1), 'VEC.vector-properties': (12, 2),
    'VEC.area-volume': (12, 3),
}


def mark_transition(previous, current):
    """Compare mark ranges, not mathematical demand or measured difficulty."""
    require(len(previous) == len(current) == 3, 'Expected three variants per tier')
    require(all(type(x) is int and x > 0 for x in (*previous, *current)), 'Invalid marks')
    if min(current) < max(previous):
        return 'lower_or_overlap_marks'
    if min(current) == max(previous):
        return 'touching_marks'
    return 'strictly_higher_marks'


def audit(resolver=None, records=None):
    r = Resolver() if resolver is None else resolver
    concepts = {skill.rsplit('.', 1)[0] for skill, _, _ in r.bases.values()}
    require(concepts == set(OUTCOMES), 'Concept crosswalk coverage mismatch')
    expected_locators = {(p, b) for p, n in ((9, 11), (10, 14), (11, 13), (12, 3))
                         for b in range(1, n + 1)}
    require(set(OUTCOMES.values()) == expected_locators, 'Outcome locator coverage mismatch')
    designs, transitions, items = [], [], {}
    for path, (skill, _, _) in sorted(r.bases.items()):
        concept = skill.rsplit('.', 1)[0]
        page, bullet = OUTCOMES[concept]
        prior = None
        for tier in range(1, 7):
            group = [r._resolve(path, tier, v) for v in (1, 2, 3)]
            for item in group:
                require(inventory_entry(item)['status'] == 'typed_provisional', 'Untyped active item')
                require(item['id'] not in items, 'Duplicate active item')
                require(not r.eligible(path, tier, 'approved_exam'), 'Unexpected approval')
                items[item['id']] = item
            marks = [item['marks'] for item in group]
            scope = r.scope(path, tier)
            designs.append({'path': path, 'skill': skill, 'tier': tier, 'scope': scope,
                            'marks': marks, 'printed_page': page, 'page_bullet': bullet,
                            'alignment': 'concept_link_only', 'demand': 'editorial_not_empirical'})
            if prior is not None:
                transitions.append({'path': path, 'from_tier': tier - 1, 'to_tier': tier,
                                    'from_marks': prior, 'to_marks': marks,
                                    'screen': mark_transition(prior, marks)})
            prior = marks
    require(len(items) == 2106 and len(designs) == 702 and len(transitions) == 585, 'Coverage mismatch')
    ledger = None
    if records is not None:
        require({rec['id'] for rec in records} == set(items), 'Ledger coverage mismatch')
        ledger = validate_batch(records, r)
        require(ledger['statuses'] == {'editorial_review_recorded': 2106}, 'Open review decision')
        ledger = {'records': ledger['records'], 'basis': dict(collections.Counter(rec['review_basis'] for rec in records))}
    return {'skills': len(r.bases), 'concepts': len(concepts), 'items': len(items),
            'designs': designs, 'transitions': transitions,
            'transition_counts': dict(collections.Counter(x['screen'] for x in transitions)),
            'scope_counts': dict(collections.Counter(x['scope'] for x in designs)),
            'unequal_variant_mark_designs': sum(len(set(x['marks'])) != 1 for x in designs),
            'ledger': ledger, 'teacher_approved': 0, 'fm17_ready': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, help='Optional private current JSONL ledger')
    args = parser.parse_args()
    print(json.dumps(audit(records=read_batch(args.ledger) if args.ledger else None), indent=2, sort_keys=True))
