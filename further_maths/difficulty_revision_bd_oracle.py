"""Retain independent original matrix fact validators."""
import importlib
from difficulty_revision_bd import BANKS,TARGETS

def check(p):
    suffix=BANKS[p['path']]
    return (p['path'],p['tier']) in TARGETS and importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_oracle').check(p)
