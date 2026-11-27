"""Verify explicit predecessor and unchanged mathematical facts."""
from importlib import import_module
from difficulty_revision_bn9 import TARGETS, revise


def check(p):
    key=p['path'],p['tier'];v=p['variant']
    if key not in TARGETS or type(v) is not int or v not in (1,2,3):return False
    tag=TARGETS[key]
    old=import_module('difficulty_revision_'+tag).revise(*key,v)
    return (p==revise(*key,v) and set(p)==set(old) and all(p[k]==old[k] for k in old if k not in {'question_latex','final_answer_latex','worked_solution_latex'})
            and import_module('difficulty_revision_'+tag+'_oracle').check(old))
