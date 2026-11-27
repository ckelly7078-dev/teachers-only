"""Use the original independent exact-fact checks for unchanged AY questions."""
import importlib
from difficulty_revision_ay import BANKS,TARGETS


def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    return importlib.import_module('calibration_'+BANKS[p['path']]+'_oracle').check(p)
