"""Preserve independent original mathematics checks for marking-only changes."""
from calibration_r_oracle import check as roots
from calibration_z_oracle import check as product
from calibration_d_oracle import check as determinant
from calibration_h_oracle import check as scalar

CHECKS = {'root-sum-product': roots, 'cartesian-product': product,
          'det-two': determinant, 'scalar-product': scalar}


def check(p):
    return p['path'] in CHECKS and p['tier'] == 3 and CHECKS[p['path']](p)
