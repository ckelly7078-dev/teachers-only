"""FM-16BO: read-only readiness gates; not a release or teacher approval mechanism."""
import collections
from active_difficulty import Resolver, MODES, require
from marking_review import fingerprint, inventory_entry
from marking_batch import validate_batch
from scope_review_bl import WATCH, validate as validate_scope


def conservative_preview_eligible(resolver, path, tier, mode):
    """Optional guarded preview route, separate from legacy preview selection.

    Scope-watch tasks remain available for learning, not assessment previews.
    No call to this module grants approval or opens FM-17.
    """
    require(mode in MODES, 'Unknown selection mode')
    allowed = resolver.eligible(path, tier, mode)
    return bool(allowed and mode != 'approved_exam' and not
                (mode == 'exam_candidate_preview' and (path, tier) in WATCH))


def conservative_preview_resolve(resolver, path, tier, variant, *, mode):
    require(conservative_preview_eligible(resolver, path, tier, mode), 'Preview not eligible')
    return resolver.resolve(path, tier, variant, mode=mode)


def index(rows):
    result = {}
    for row in rows:
        require(row['id'] not in result, 'Duplicate evidence ID')
        result[row['id']] = row
    return result


def validate_evidence(marking, scopes, written, render, resolver=None):
    """Match actual current versions; validate structure, not reviewer judgments.

    render contains the 1278 separately stored matrix/vector screen rows.
    Algebra/complex compilation evidence is stored in written review records.
    Neither type of record is an individual visual certificate.
    """
    r = Resolver() if resolver is None else resolver
    mi, si, wi, ri = map(index, (marking, scopes, written, render))
    expected = {f'CAL.{p}.T{t}.V{v}' for p in r.bases for t in range(1,7) for v in (1,2,3)}
    require(len(expected) == 2106 and set(mi) == set(si) == set(wi) == expected, 'Incomplete review evidence')
    require(set(ri) == {key for key in expected if r.bases[key.split('.')[1]][0].startswith(('MAT.','VEC.'))}, 'Incomplete render evidence')
    m = validate_batch(marking, r)
    require(m['statuses'] == {'editorial_review_recorded':2106}, 'Unresolved marking decisions')
    s = validate_scope(scopes, r)
    result = collections.Counter()
    preview = collections.Counter({mode:0 for mode in MODES})
    notation = []
    for key in sorted(expected):
        _, path, t, v = key.split('.'); tier, variant = int(t[1:]), int(v[1:])
        item = r._resolve(path,tier,variant); fp = fingerprint(item)
        require(inventory_entry(item)['status'] == 'typed_provisional', 'Untyped rubric')
        w = wi[key]; require(w['written_text_review'] == 'direct_editorial_inspection', 'Missing direct review')
        require(not w.get('open_finding'), 'Outstanding recorded solution finding')
        rr = ri.get(key, w)
        for row in (mi[key],si[key],w,rr):
            require(row['fingerprint'] == fp and row['teacher_approved'] is False, 'Stale or approved evidence')
        require(w['revision'] == rr['revision'] == item['revision'], 'Revision mismatch')
        require(w['individual_solution_certified'] is False and w['visual_certified'] is False and w['exam_ready'] is False, 'Unexpected certification')
        if key not in ri:
            require(w['reference_compile_pass'] is True and w['page_geometry_pass'] is True, 'Missing prior proof evidence')
        else:
            require(rr['visual_certified'] is False, 'Unexpected visual certificate')
        result['written_review_records'] += 1
        result['reference_screen_records'] += 1
        result['written_register_visual_samples'] += bool(w.get('reference_visual_sample_inspected'))
        if rr.get('plain_notation_signals'):
            notation.append({'id':key,'revision':item['revision'],'fingerprint':fp,'signals':rr['plain_notation_signals']})
        for mode in MODES:
            preview[mode] += conservative_preview_eligible(r,path,tier,mode)
    require(preview['approved_exam'] == 0 and preview['exam_candidate_preview'] == 1020, 'Guarded preview counts mismatch')
    return {'evidence':dict(result),'scope_decisions':s['decisions'],'guarded_preview_counts':dict(preview),
            'notation_signals':notation,'scope_watch_count':len(WATCH)*3,'teacher_approved':0,
            'fm17_ready':False,'production_renderer_certified':False,'empirical_calibration_complete':False,
            'individual_visual_certification_complete':False}
