"""Use the original independent exact-fact checks for unchanged AZ questions."""
import importlib
from difficulty_revision_az import BANKS,TARGETS


def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    return importlib.import_module('calibration'+('_'+BANKS[p['path']] if BANKS[p['path']] else '')+'_oracle').check(p)
