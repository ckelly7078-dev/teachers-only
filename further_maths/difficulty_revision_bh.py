"""FM-16BH: final vector intersections, distances, areas and volumes.
Retain original variant-specific criteria and explicitly type each reviewed criterion.
"""
import importlib

BANKS={'point-line': '', 'skew': '', 'line-plane-intersection': 'b', 'point-plane': 'b', 'line-line-distance': 'c', 'triangle-area': 'd', 'triple-volume': 'e', 'line-intersection': 'g', 'plane-intersection-direction': 'h', 'parallelogram-area': 'i', 'plane-common-point': 'k', 'related-solids': 'k', 'plane-intersection-line': 'm', 'justify-skew': 'p'}
DESIGNS={'point-line': ('MA', 'RR', 'MA', 'MA', 'MA', 'MRA'),
 'skew': ('MA', 'RR', 'RA', 'MR', 'RMA', None),
 'line-plane-intersection': ('MA', 'MR', 'MA', 'AMR', 'MRA', None),
 'point-plane': ('MA', 'AAR', 'MA', 'MAA', 'MAA', 'MRRA'),
 'line-line-distance': ('MA', 'RMR', 'MMA', 'MRA', 'MRA', None),
 'triangle-area': ('A', 'ARA', 'MA', 'MMA', 'MAR', None),
 'triple-volume': ('A', 'RR', 'MA', 'MMA', 'MAR', 'MARRA'),
 'line-intersection': ('MA', 'RA', 'MAA', 'MMR', 'MAA', 'RMAR'),
 'plane-intersection-direction': ('A', 'RR', 'MAR', 'MMR', 'MAR', None),
 'parallelogram-area': ('A', 'RA', 'MA', 'MAA', 'MAR', 'MMAR'),
 'plane-common-point': ('A', 'AR', 'MA', 'MAR', 'MMA', 'MMMA'),
 'related-solids': ('A', 'RA', 'MA', 'AAA', 'MR', 'MARR'),
 'plane-intersection-line': ('A', 'RA', 'MA', 'MAR', 'MMA', 'MAAR'),
 'justify-skew': ('AR', 'RR', 'RMR', 'MMR', 'RMR', None)}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}

def base(path):
    suffix=BANKS[path]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_bank')

def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16BH')
    p=base(path).make(path,tier,v)
    specs=DESIGNS[path][tier-1]
    if len(specs)!=len(p['rubric']) or any(r['marks']!=1 or 'type' in r for r in p['rubric']):
        raise ValueError('Unreviewed rubric structure')
    rub=[]
    for kind,old in zip(specs,p['rubric']):
        criterion=old['criterion']
        if kind=='M':criterion+=' Accept equivalent valid methods respecting explicit question restrictions; retain demonstrated method credit after a subsequent arithmetic slip.'
        elif kind=='A':criterion+=' Require the specified correct result; do not automatically award accuracy for an incorrect result.'
        else:criterion+=' Accept equivalent valid reasoning supported by the stated constraints.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
