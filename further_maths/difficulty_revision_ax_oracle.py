"""Keep the independently derived original polynomial facts for AX overlays."""
import importlib
from difficulty_revision_ax import BANKS,TARGETS


def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    return importlib.import_module('calibration_'+BANKS[p['path']]+'_oracle').check(p)
