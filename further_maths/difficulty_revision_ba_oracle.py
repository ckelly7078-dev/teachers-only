"""Exact degree congruences independently enumerate all admitted angles."""
from difficulty_revision_ad_oracle import check as prior_check

def check(p):
    if (p['path'],p['tier'])!=('angle-units',6) or p['variant'] not in (1,2,3):
        return False
    alpha=30*(p['variant']+1)
    first=[t for t in range(-180,901) if (t-alpha)%360==0]
    strict=[t for t in first if (t-alpha)%720==0]
    return prior_check(p) and p['facts']==list(map(str,first+strict))
