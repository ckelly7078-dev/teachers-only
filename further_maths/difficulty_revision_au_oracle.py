"""Reuse the independent, original per-variant mathematical validators."""
import importlib
from difficulty_revision_au import BANKS,TARGETS

def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    suffix=BANKS[p['path']]
    oracle=importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_oracle')
    return oracle.check(p)
