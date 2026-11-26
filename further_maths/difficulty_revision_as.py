"""FM-16AS: apply the twelve inspected pilot marking decisions only."""
from calibration_r_bank import make as roots
from calibration_z_bank import make as product
from calibration_d_bank import make as determinant
from calibration_h_bank import make as scalar

BANKS = {'root-sum-product': roots, 'cartesian-product': product,
         'det-two': determinant, 'scalar-product': scalar}
TARGETS = {(path, 3) for path in BANKS}

METHODS = {
    'root-sum-product': 'Apply both signed root-coefficient ratios: minus linear coefficient over leading coefficient, and constant over leading coefficient. Equivalent monic or factor-coefficient method accepted.',
    'cartesian-product': 'Complete signed four-term expansion, or equivalent real and imaginary component formula, using i squared = -1.',
    'det-two': 'Use main-diagonal product minus off-diagonal product with their signs, or equivalent cofactor expansion.',
    'scalar-product': 'Multiply all corresponding components and form their signed sum, or equivalent row-column multiplication.',
}


def revise(path, tier, v):
    if (path, tier) not in TARGETS or type(v) is not int or v not in (1, 2, 3):
        raise ValueError('Not FM-16AS')
    p = BANKS[path](path, tier, v)
    p['rubric'] = [
        {'type': 'M', 'marks': 1, 'criterion': METHODS[path] + ' Retain method credit for a subsequent arithmetic slip, but not an incorrect method.'},
        {'type': 'A', 'marks': 1, 'criterion': 'Give the complete exact result: ' + p['final_answer_latex'] + ' No accuracy credit for an incorrect final result.'},
    ]
    if path == 'det-two':
        p['likely_mistake'] = 'Adding the diagonal products instead of subtracting the signed off-diagonal product, or taking the absolute value.'
    return p
