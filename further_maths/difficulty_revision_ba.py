"""FM-16BA: marking-only successor to the AD angle-congruence enrichment design."""
from difficulty_revision_ad import revise as prior

TARGETS={('angle-units',6)}
CRITERIA=(
 ('M','Convert the interval bounds and express the first congruence as a general integer family in consistent units. Accept either unit system and retain demonstrated method credit after a subsequent arithmetic slip.'),
 ('R','Show that the original half-angle condition modulo pi is automatic for that entire integer family.'),
 ('A','Give all three correct admissible degree values and check that the inclusive interval admits exactly those integers.'),
 ('R','Derive the even-integer restriction for the stricter modulus 2pi and give exactly the two surviving values. Accept equivalent valid congruence reasoning; do not award final accuracy automatically for an incorrect result.'),
)

def revise(path,tier,v):
    if (path,tier) not in TARGETS or type(tier) is not int or type(v) is not int or v not in (1,2,3):
        raise ValueError('Not FM-16BA')
    p=prior(path,tier,v)
    if len(p['rubric'])!=4 or any(row['marks']!=1 or 'type' in row for row in p['rubric']):
        raise ValueError('Unexpected predecessor allocation')
    p['rubric']=[{'type':t,'marks':1,'criterion':c} for t,c in CRITERIA]
    return p
