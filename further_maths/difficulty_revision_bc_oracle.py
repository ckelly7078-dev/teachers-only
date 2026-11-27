"""Retain independent original matrix validators for unchanged mathematical facts."""
import importlib
from difficulty_revision_bc import BANKS,TARGETS


def check(p):
    return (p['path'],p['tier']) in TARGETS and importlib.import_module('calibration_'+BANKS[p['path']]+'_oracle').check(p)
