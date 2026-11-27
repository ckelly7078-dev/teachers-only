"""Complete short answers already justified by the existing worked solutions."""
from importlib import import_module
from active_difficulty import require
import sympy as s

TARGETS = {('cube-sums', 2): 'au', ('shifted-products', 2): 'au',
           ('scaled-roots', 6): 'av', ('shifted-products', 6): 'av'}


def revise(path, tier, variant):
    key = path, tier
    require(key in TARGETS and type(variant) is int and variant in (1, 2, 3), 'Invalid BM target')
    p = import_module('difficulty_revision_' + TARGETS[key]).revise(path, tier, variant)
    a, b = variant + 1, 2 * variant + 5
    if key == ('cube-sums', 2):
        extra = f'; the omitted mixed terms total ${3*a*b*(a+b)}$.'
    elif key == ('shifted-products', 2):
        extra = f'; the omitted mixed term is ${-(variant+3)*(a+b)}$.'
    elif path == 'scaled-roots':
        extra = (' At $h=0$ there is one equation, with a repeated zero root. '
                 'For $h>0$ there are two distinct equations: both roots are positive for $m>0$ '
                 'and both negative for $m<0$.')
    else:
        threshold = s.latex(2*s.sqrt(a*b))
        extra = (f' Repeated roots occur for $k=0$ at $S=\\pm {threshold}$, '
                 f'or for nonzero $k=\\pm {threshold}$. All other admissible equations have distinct roots.')
    p['final_answer_latex'] += extra
    return p
