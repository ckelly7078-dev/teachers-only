"""Resolve the fifteen version-bound complex-number presentation findings.

No mathematical fact, rubric, mark, scope or selection change is authorised.
"""
from importlib import import_module
import re
import sympy as s
from active_difficulty import require

TARGETS = {('argument-normalization', 4): 'az', ('cartesian-product', 3): 'as',
           ('cartesian-sums', 4): 'bk', ('conjugate-find', 3): 'aw',
           ('standard-cartesian', 5): 'aw', ('complex-quadratic', 4): 'ax',
           ('conjugate-deduction', 2): 'ax', ('distance-circle', 6): 'az',
           ('polar-geometry', 3): 'bk', ('polar-products', 5): 'an',
           ('polar-products', 6): 'az', ('polar-quotients', 4): 'az',
           ('polar-quotients', 6): 'az', ('polar-to-cartesian', 6): 'az',
           ('solve-quartic', 6): 'bk'}


def replace_once(text, old, new):
    require(text.count(old) == 1, 'Expected a single exact repair site')
    return text.replace(old, new, 1)


def revise(path, tier, variant):
    key = path, tier
    require(key in TARGETS and type(variant) is int and variant in (1, 2, 3), 'Invalid BM4 target')
    p = import_module('difficulty_revision_' + TARGETS[key]).revise(path, tier, variant)
    q, a, w = p['question_latex'], p['final_answer_latex'], p['worked_solution_latex']
    f = p['facts']
    if path == 'argument-normalization':
        q = replace_once(q, 'have arguments ', 'have arguments (given modulo $2\\pi$, not necessarily principal) ')
    elif path == 'cartesian-product':
        m = re.fullmatch(r'Expand \$(.+)\$ times \$(.+)\$ and write the result in Cartesian form\.', q)
        require(m is not None, 'Unexpected product prompt')
        q = 'Expand $(' + m[1] + r')(' + m[2] + ')$ and write the result in Cartesian form.'
    elif path == 'cartesian-sums':
        w[2] = replace_once(w[2], '2u=W+(u-b)', '$2u=w+(u-b)$')
    elif path == 'conjugate-find':
        expanded = s.conjugate(s.sympify(f[0]))
        a = 'Expanded product $' + s.latex(expanded) + '$; conjugate ' + a + '.'
    elif path == 'standard-cartesian':
        m = re.search(r'\$(.*?)\$/(\d+)', w[0]); require(m is not None, 'Unexpected numerator')
        w[0] = replace_once(w[0], m[0], r'$\frac{' + m[1] + '}{' + m[2] + '}$')
    elif path == 'complex-quadratic':
        u, v = map(s.sympify, f)
        a += '; sum $' + s.latex(s.simplify(u+v)) + '$, product $' + s.latex(s.simplify(u*v)) + '$.'
    elif path == 'conjugate-deduction':
        a = replace_once(a, 'Real coefficients are required for the conjugate-root theorem.',
                         'Real coefficients guarantee conjugate pairing for every nonreal root; particular complex-coefficient polynomials may also happen to contain a conjugate pair.')
    elif path == 'distance-circle':
        w[2] = replace_once(w[2], 'since d is positive', f'since the centre separation $d={3*variant+5}$ is positive')
    elif path == 'polar-geometry':
        a += ' The points are reflections of one another in the real axis.'
    elif key == ('polar-products', 5):
        w[-1] = replace_once(w[-1], 'simultaneous negation.', 'simultaneous negation $(z,w)\\mapsto(-z,-w)$ (not negation of the arguments).')
    elif key == ('polar-products', 6):
        delta = [s.pi/4, s.pi/3, s.pi/6][variant-1]
        w[1] = replace_once(w[1], 'Therefore theta=(n*pi-delta)/3.',
                            r'With the fixed offset $\delta=' + s.latex(delta) + r'$, therefore $\theta=(n\pi-\delta)/3$.')
    elif key == ('polar-quotients', 4):
        w[2] = replace_once(w[2], 'A+C-B', r'$\arg z+\arg u-\arg w$')
    elif key == ('polar-quotients', 6):
        polynomial = '$' + s.latex(s.sympify(f[0])) + '$'
        new = polynomial.replace('x', 'q')
        a = replace_once(a, polynomial, new)
        w[0] = replace_once(w[0], polynomial, new)
    elif path == 'polar-to-cartesian':
        theta = [s.pi/6, s.pi/4, s.pi/3][variant-1]
        w[0] = r'Let $\theta=' + s.latex(theta) + '$ be the argument of z (the first given angle). ' + w[0]
    elif path == 'solve-quartic':
        a = replace_once(a, 'otherwise four simple roots.',
                         f'for h>0, two simple real roots and two simple nonreal roots; for h<0 other than h={f[1]}, four simple nonreal roots.')
    p.update(question_latex=q, final_answer_latex=a, worked_solution_latex=w)
    return p
