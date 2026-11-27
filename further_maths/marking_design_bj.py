"""Version-bound editorial evidence for ten priority successor designs."""
import hashlib
import json
from active_difficulty import Resolver, require, MARK_SUCCESSIONS
from difficulty_revision_bj import TARGETS
from difficulty_revision_bj_oracle import check
from marking_review import fingerprint

FROZEN_BATCH_SHA='5cb3450c6ca504a6cab67c2f3dfb3d305d3328940571bf80de4e1127ce060df8'
NOTES={
 'angle-units':('Convert either the bounds to degrees or the family to radians before isolating n.','The lower bound is inclusive and the upper bound exclusive; enumerate exactly two integers, checking neighbouring integers.','Three separate stages now receive method, method and accuracy credit.'),
 'argument-range':('Use tangent or exact sine/cosine with a nonnegative radial multiple; use the supporting line for the second point.','The negative real coordinate determines the original lower-left ray; the reversed point is in the upper-right quadrant and has the same tangent but a distinct argument.','Credit both reconstructions and the distinction between line and ray.'),
 'cartesian-to-polar':('Use the modulus equation or exact cosine and both compatible sine signs.','The real component has absolute value strictly less than the positive modulus; two nonzero imaginary components and arguments in opposite half-planes exhaust the solutions.','Retain separate method, accuracy and completeness credit for both branches and the final sign restriction.'),
 'complex-division':('Rationalise or equate components after multiplying by the known nonzero denominator.','The real and imaginary numerator equations are linear with nonzero slopes; neither quotient can vanish because the numerator has positive real part.','Credit the distinct equations and results for both axes, plus completeness.'),
 'conjugate-product':('Recover both signs from norm-square, then rationalise z divided by its conjugate or use z squared over its norm-square.','The norm is positive and the imaginary magnitude is nonzero. Conjugation of both numerator and denominator pairs the exact quotients.','Credit norm reconstruction, both signs, rationalisation and conjugation reasoning.'),
 'inverse-systems':('Use an adjugate, row reduction to obtain the inverse, or equivalent valid matrix inversion.','The three-by-three coefficient matrix is invertible, and the sum constraint has a nonzero coefficient of k. Independent augmented-system solution verifies uniqueness.','Separate inverse, symbolic solution, scalar condition, final values and verification.'),
 'related-solids':('Use the scalar triple product, base area times perpendicular height, or equivalent determinant scaling, then factor or complete the square.','Nondegenerate original solid makes the ratio well-defined; both edge fractions are nonnegative, the two roots are interior, the endpoints give zero, and the maximum is uniquely at one half.','Credit the two scale factors, both roots, completeness and the algebraic maximum.'),
 'solve-cubic':('Evaluate at the known root or compare coefficients of the conjugate-factor product; use division or matching coefficients for the linear factor.','Coefficient one makes the unknown constant unique; real coefficients force a distinct conjugate pair, and the remaining real root exhausts degree three.','Six explicit credits separate the coefficient and root stages; expanded substitution and factor verification support the worked solution.'),
 'solve-quartic':('Evaluate at the known root or compare coefficients of the factor product, then use polynomial division or equivalent coefficient matching and exact quadratic solving.','The two conjugate pairs have different real parts and nonzero imaginary parts. The real constant is unique and all four roots account for degree four.','Seven explicit credits separate substitution, constant, factor construction, quotient method and accuracy, quadratic solution and complete roots.'),
 'vector-plane':('Use elimination, inversion or equivalent simultaneous equations for the parameters, then cross product or an equivalent nonzero normal.','The two-coordinate coefficient matrix has nonzero determinant. Directions are independent and the recovered point satisfies the Cartesian equation.','Credit the coupled recovery, normal, equation and independent membership/uniqueness reasoning.'),
}

def records(resolver=None):
    r=resolver or Resolver()
    items=[r._resolve(p,t,v) for p,t in sorted(TARGETS) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BJ frozen batch changed')
    for item in items:
        p=item['payload']; path,t,v=p['path'],p['tier'],p['variant']; old=r._resolve_version(path,t,v,TARGETS[path,t]); alt,bound,allocation_note=NOTES[path]
        require(item['revision']=='FM-16BJ' and check(p) and old['scope']==item['scope'],'Invalid BJ item')
        require((old['marks'],item['marks'])==MARK_SUCCESSIONS[path,t,'bj'],'Mark succession mismatch')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Shared design checked and the exact variant oracle passes the successor facts. '+bound},
            'criterion_allocation':{'decision':'pass','evidence':allocation_note+' Proposed allocation remains editorial, not an examination-board mark scheme.'},
            'alternative_methods':{'decision':'pass','evidence':alt},
            'consequential_errors':{'decision':'pass','evidence':'Award independently demonstrated valid method and reasoning; a subsequent arithmetic slip need not remove earlier method credit. Exact required answers remain necessary for accuracy credit.'},
            'boundary_cases':{'decision':'pass','evidence':bound},
            'presentation':{'decision':'pass','evidence':'Shared prompt, answer and solution structure inspected; rendering and teacher approval remain pending.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if t==row['type'] else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(p['rubric'])]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'supersedes_fingerprint':fingerprint(old),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial priority progression review FM-16BJ (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for row in records():print(json.dumps(row,sort_keys=True))
