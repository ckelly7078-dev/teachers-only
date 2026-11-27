"""Keep the original independent mathematical check for each marking-only revision."""
from difficulty_revision_au_oracle import importlib,BANKS
from difficulty_revision_av import TARGETS


def check(p):
    if (p['path'],p['tier']) not in TARGETS:
        return False
    suffix=BANKS[p['path']]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_oracle').check(p)
