"""Single private dispatch contract for supported AS1 structured observations."""
from active_difficulty import require
import structured_math_fm17d as d
import structured_math_fm17e as e
import structured_math_fm17f as f
import structured_math_fm17g as g

_GROUPS = ((frozenset(('angle-units','root-sum-product','matrix-products')),d),
           (e.DESIGNS,e),(f.DESIGNS,f),(g.DESIGNS,g))
_REGISTRY = {path: checker for paths,checker in _GROUPS for path in paths}
require(len(_REGISTRY)==sum(len(paths) for paths,_ in _GROUPS),'Duplicate exact checker design')


def supported_designs():
    return tuple(sorted(_REGISTRY))


def _checker(item):
    p=item['payload']
    return _REGISTRY.get(p['path']) if p['tier']==3 else None


def capability(engine,item_id,*,mode,item_fingerprint):
    """Describe availability only; no reference answer or grading decision."""
    engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    item=engine.bank.items[item_id]; available=_checker(item) is not None
    return {'id':item_id,'fingerprint':item_fingerprint,'tier':item['payload']['tier'],
            'structured_checks_available':available,
            'basis':'bounded_structured_observations' if available else 'provisional_rubric_context_only',
            'automatic_award':False,'release_allowed':False}


def check_work(engine,item_id,*,mode,item_fingerprint,work):
    """Dispatch supported observations; do not guess a mark for other designs."""
    engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    checker=_checker(engine.bank.items[item_id])
    require(checker is not None,'Exact structured checker unavailable; use the provisional marking context')
    return checker.check_work(engine,item_id,mode=mode,item_fingerprint=item_fingerprint,work=work)
