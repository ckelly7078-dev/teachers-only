"""Validate private source-specific marking routes without awarding learner marks."""
import copy
from active_difficulty import require
from knowledge_fm17 import printed_codes
from source_evidence_fm17 import part_signature


def bind_routes(bank, records):
    """Check exact source/part identity, allocations, and route-local exceptions.

    Stage links describe mathematical dependence, not automatic mark gates.
    Private criteria are editorial readings of the printed breakdown.
    """
    index = {}
    for record in records:
        key = (record['series'], record['number'], record['ordinal'])
        require(key in bank.parts and key not in index, 'Unknown or duplicate source part')
        part = bank.parts[key]
        require(record['part_signature'] == part_signature(bank, key), 'Stale source part')
        require(record['scheme_sha256'] == bank.sources[part['scheme_source']]['sha256'], 'Stale scheme')
        require(type(record['breakdown_page']) is int and record['breakdown_page'] > 0, 'Invalid source page')
        require(record['basis'] == 'editorial_reading_of_printed_breakdown' and record['automatic_award'] is False, 'Invalid evidence basis')
        routes = record['routes']
        require(isinstance(routes, list) and routes and routes[0]['id'] == 'primary', 'Missing primary route')
        seen_routes = set()
        for route in routes:
            rid = route['id']; stages = route['stages']; seen = set()
            require(isinstance(rid, str) and rid.strip() and rid not in seen_routes, 'Duplicate route')
            seen_routes.add(rid)
            allocation = printed_codes(' '.join(s['code'] for s in stages), part['marks'])
            if rid == 'primary':
                require(allocation == part['printed_allocation'], 'Primary codes differ from checked allocation')
            for i, (stage, allocation_row) in enumerate(zip(stages, allocation), 1):
                require(stage['id'] == f's{i}' and stage['id'] not in seen, 'Invalid stage identity')
                require(stage['marks'] == allocation_row['marks'] and type(stage['marks']) is int, 'Stage marks mismatch')
                require(isinstance(stage['criterion'], str) and stage['criterion'].strip(), 'Missing criterion')
                deps = stage['uses']
                require(isinstance(deps, list) and len(deps) == len(set(deps)) and set(deps) <= seen, 'Invalid mathematical dependence')
                rule = stage['partial_credit']
                require(rule is None or (stage['marks'] > 1 and isinstance(rule, str) and rule.strip()), 'Invalid partial-credit note')
                seen.add(stage['id'])
            for exc in route['exceptions']:
                require(exc['kind'] in ('follow_through', 'cap', 'acceptance', 'restriction'), 'Unknown exception')
                require(isinstance(exc['condition'], str) and exc['condition'].strip() and isinstance(exc['effect'], str) and exc['effect'].strip(), 'Missing exception evidence')
                refs = exc['stages']; require(isinstance(refs, list) and len(refs) == len(set(refs)) and set(refs) <= seen, 'Unknown exception stage')
                prior = exc['prior_part']
                if prior is not None:
                    require(isinstance(prior, list) and len(prior) == 3 and tuple(prior) in bank.parts and tuple(prior)[:2] == key[:2] and prior[2] < key[2], 'Invalid preceding part')
                cap = exc['max_marks']
                require((exc['kind'] == 'cap' and type(cap) is int and 0 <= cap < part['marks']) or (exc['kind'] != 'cap' and cap is None), 'Invalid cap')
                if cap is not None:
                    require(sum(s['marks'] for s in stages if s['id'] in refs) == cap, 'Cap stages do not sum to cap')
        index[key] = copy.deepcopy(record)
    return index


def part_routes(bank, index, key):
    """Return explicitly unavailable, rather than infer a rule from a code list."""
    require(key in bank.parts, 'Unknown or disputed source part')
    if key not in index:
        return {'status': 'printed_allocation_only', 'automatic_award': False, 'routes': []}
    record = index[key]
    require(record['part_signature'] == part_signature(bank, key), 'Stale route evidence')
    return {'status': 'source_breakdown_available', 'automatic_award': False, 'record': copy.deepcopy(record)}


def original_marking_context(bank, item_id, *, mode):
    """Give the existing marking engine version-bound original criteria and caveats.

    The returned material is private marking context, never a student score.
    No printed past-paper rules are transplanted to the original item.
    """
    from marking_review import fingerprint, validate_review
    require(isinstance(item_id, str) and item_id in bank.items, 'Unknown original item')
    item = bank.items[item_id]; p = item['payload']
    selected = bank.select(p['focus_skill'], p['tier'], mode=mode)
    require(any(r['item']['id'] == item_id for r in selected), 'Preview not eligible')
    review = bank.reviews[item_id]
    require(validate_review(item, review) == 'editorial_review_recorded', 'Unresolved original rubric')
    criteria = []
    for i, (rubric, row) in enumerate(zip(p['rubric'], review['allocation']), 1):
        require(row['marks'][rubric['type']] == rubric['marks'], 'Criterion type mismatch')
        criteria.append({'id': f'c{i}', 'type': rubric['type'], 'marks': rubric['marks'],
                         'criterion': rubric['criterion'], 'allocation_evidence': row['evidence']})
    return copy.deepcopy({'id': item_id, 'fingerprint': fingerprint(item), 'marks': item['marks'],
                          'marking_convention': 'original_provisional_M_A_R', 'criteria': criteria,
                          'checks': review['checks'], 'worked_solution_latex': p['worked_solution_latex'],
                          'final_answer_latex': p['final_answer_latex'], 'review_basis': review['review_basis'],
                          'automatic_award': False, 'exam_ready': False, 'release_allowed': False})
