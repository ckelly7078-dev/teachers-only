"""FM-16BG: line and plane equations, normals and angular relationships.
Keep the original variant-specific criteria; explicitly type each reviewed criterion.
"""
import importlib

BANKS={'vector-line-equation': 'i', 'cartesian-line': 'e', 'zero-direction': 'l', 'vector-plane': 'j', 'plane-cartesian': 'f', 'plane-normal': 'o', 'cross-normal': 'l', 'normal-dot-plane': 'm', 'line-line-angle': 'f', 'plane-plane-angle': 'c', 'line-plane-angle': 'b'}
DESIGNS={'vector-line-equation': ('A', 'RR', 'MA', 'MAA', 'MRA', 'RARAR'),
 'cartesian-line': ('A', 'RA', 'MA', 'MAA', 'MAA', 'MAARR'),
 'zero-direction': ('A', 'RA', 'MA', 'MAR', 'MAR', 'AARR'),
 'vector-plane': ('A', 'RR', 'MRA', 'MAAR', 'MAA', 'RMAAR'),
 'plane-cartesian': ('A', 'RR', 'MA', 'MAA', 'MAA', 'MAR'),
 'plane-normal': ('A', 'RR', 'AAR', 'MAA', 'MAA', 'MARAR'),
 'cross-normal': ('A', 'RR', 'AR', 'MAR', 'MAR', 'MARR'),
 'normal-dot-plane': ('A', 'RR', 'MA', 'AAA', 'MAR', 'MAARR'),
 'line-line-angle': ('A', 'RR', 'MA', 'MAA', 'MAR', 'MMAR'),
 'plane-plane-angle': ('MA', 'RAR', 'MA', 'MAAA', 'MAR', 'MAARR'),
 'line-plane-angle': ('MA', 'RR', 'MA', 'MMA', 'MAR', None)}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}

def base(path):
    suffix=BANKS[path]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_bank')

def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16BG')
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
