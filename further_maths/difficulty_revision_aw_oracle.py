"""Preserve independent exact-fact checks of the underlying Cartesian questions."""
import importlib
from difficulty_revision_aw import BANKS,TARGETS


def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    suffix=BANKS[p['path']]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_oracle').check(p)
