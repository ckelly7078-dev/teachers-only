"""Preservation check plus predecessor exact-fact oracle for BM."""
from importlib import import_module
from difficulty_revision_bm import TARGETS, revise


def check(p):
    key = p['path'], p['tier']
    if key not in TARGETS or type(p['variant']) is not int or p['variant'] not in (1, 2, 3):
        return False
    old = import_module('difficulty_revision_' + TARGETS[key]).revise(*key, p['variant'])
    return (p == revise(*key, p['variant']) and
            all(p[k] == old[k] for k in old if k != 'final_answer_latex') and
            import_module('difficulty_revision_' + TARGETS[key] + '_oracle').check(old))
