"""Frozen shared-design matrix marking evidence, not teacher approval."""
import hashlib,json
from active_difficulty import Resolver,require
from difficulty_revision_bb import BANKS,DESIGNS
from marking_review import fingerprint

FROZEN_BATCH_SHA='bb7334e375fcc0b315ebaff3a5c565601a0c0a58d338609fdf0bb1b6ba86d4c3'
# Alternative approaches and mathematical restrictions inspected per design.
NOTES={
'matrix-conformability':(
 ('Read dimensions directly.','Rows precede columns.'),
 ('Use shape notation or verbal dimension rules.','Unequal orders prohibit addition but matched inner dimensions permit multiplication.'),
 ('Check each operation independently.','Product order matters; unequal orders prohibit addition.'),
 ('Infer the middle matrix by matching each adjacent pair.','Both products must be conformable, not merely ABC with arbitrary dimensions.'),
 ('Use the known row count to divide the number of entries.','Positive integral column count; reverse multiplication fails.'),
 ('Enumerate ordered factor pairs or positive divisors.','Equal factors are excluded; for 16 the square-root pair must be removed.')),
'matrix-add-subtract':(
 ('Use a number line or signed arithmetic.','Subtract rather than add.'),
 ('Compare both dimensions or demonstrate the missing entries.','C-C is defined and has the original rectangular order.'),
 ('Work entrywise or scale the whole matrix first.','Subtract in the stated order; preserve signs.'),
 ('Add/subtract equations or solve each pair of corresponding entries.','Division by two is reversible; verify both equations.'),
 ('Use the symmetry and trace equations in either order.','The two independent linear conditions fix both real parameters.'),
 ('Compare entries directly or use transpose identities.','Skew-symmetric diagonal entries vanish over the reals; the symmetric determinant has two distinct real branches.')),
'matrix-products':(
 ('Use a dot product or direct arithmetic.','Pair row and column entries in order.'),
 ('Demonstrate the row-column calculation.','Only the requested entry is needed.'),
 ('Use row-column multiplication or compute individual columns.','Output order is 2 by 2, not 3 by 3.'),
 ('Use elimination or substitution of the two scalar equations.','The coefficient determinant is nonzero for every variant; the prompt requires scalar equations.'),
 ('Solve column equations or use the row structure of C.','The given last row fixes X; the reverse product has order 3 by 3 and is not identity.'),
 ('Use the free last row, or solve column equations; rank or a null vector proves nonidentity.','All real parameter pairs are permitted; nonzero kernel vector rules out the reverse identity, and associativity proves idempotence.')),
'scalar-matrix':(
 ('Use signed multiplication or repeated addition.','Negative sign is retained.'),
 ('Explain entrywise scaling directly.','Off-diagonal entries are scaled too.'),
 ('Scale rows or every entry separately.','A negative scalar reverses every nonzero entry sign.'),
 ('Use any independent pair of entries and verify the rest.','A nonzero off-diagonal entry forces p; a diagonal then fixes q.'),
 ('Use determinant scaling or calculate the scaled determinant.','Both signs of k occur; the original and both scaled transformations have positive determinant.'),
 ('Compare entries or factor the resulting scalar condition.','Handle k=0 before division; h=0 and the nonzero root exhaust the remaining cases.')),
'identity-operations':(
 ('Divide by the nonzero multiplier or use the identity property.','Zero multiplier would not determine r uniquely.'),
 ('Use the identity property and compare diagonal entries.','Addition is not multiplication.'),
 ('Simplify first or multiply explicitly.','Both identities have the correct order.'),
 ('Match inner dimensions on either side.','Rectangular R needs different left and right orders; reversed orders do not work.'),
 ('Use the off-diagonal equation or solve triangular inverse entries.','The nonzero coefficient makes the parameter unique; verify the reverse product.'),
 ('Use A squared or an equivalent entrywise inverse identity.','The fixed off-diagonal coefficient is nonzero; A squared equals I iff the stated condition holds.')),
'zero-matrix':(
 ('Subtract the same number from both sides.','Additive identity is zero.'),
 ('Use entrywise addition and multiplication rules.','The displayed A is nonzero; the zero product has the correct order.'),
 ('Rearrange or solve entries directly.','All matrices have matching dimensions.'),
 ('Use direct multiplication or proportional columns.','Both factors are nonzero and A is singular; inverse cancellation is invalid.'),
 ('Use the zero image equation or determinant and kernel reasoning.','Nonzero test-vector component gives unique k; exactly one independent row remains.'),
 ('Use inverse cancellation for nonsingular A and solve each column otherwise.','At the singular value the column parameters are independent, including the zero matrix.')),
'det-two':(
 ('Multiply before subtracting.','Keep the sign of the difference.'),
 ('Evaluate both determinants directly or use alternation.','A row exchange changes sign, not magnitude.'),
 ('Use signed diagonal products or cofactor expansion.','The off-diagonal product is negative. Existing AS review retained.'),
 ('Use determinant multiplicativity after computing both given determinants.','The divisor is nonzero; do not recover A as the prompt forbids it.'),
 ('Use multiplicativity or compute BE directly.','Both signs of the nonzero root satisfy the signed determinant; B is nonsingular.'),
 ('Use sum and product or eliminate one entry to obtain an equivalent discriminant condition.','Negative, zero and positive discriminants give 0, 1 and 2 ordered pairs; invertibility depends separately on d and h. Existing AI rubric retained.')),
}


def records(resolver=None):
    r=Resolver() if resolver is None else resolver
    # AS det-two T3 already has frozen individual re-review evidence.
    items=[r._resolve(p,t,v) for p in sorted(BANKS) for t in range(1,7) if (p,t)!=('det-two',3) for v in (1,2,3)]
    manifest=[(i['id'],fingerprint(i)) for i in items]
    require(len(items)==123 and hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()==FROZEN_BATCH_SHA,'BB frozen batch changed; re-review required')
    for item in items:
        p=item['payload']; alternate,boundary=NOTES[p['path']][p['tier']-1]; rubric=p['rubric']
        require(all(row.get('type') in ('M','A','R') for row in rubric),'Unexpected untyped BB rubric')
        checks={
            'mathematical_correctness':{'decision':'pass','evidence':'Representative mathematical design and all variant prompts and final answers inspected; independent exact-fact oracle passed this variant: '+json.dumps(p['facts'],ensure_ascii=False)},
            'criterion_allocation':{'decision':'pass','evidence':'Design-specific provisional M/A/R allocation retains original total; existing AI typed det-two T6 retained.'},
            'alternative_methods':{'decision':'pass','evidence':alternate},
            'consequential_errors':{'decision':'pass','evidence':'Retain independently demonstrated valid method or reasoning after arithmetic slips; require correct stated accuracy results, with no automatic accuracy for an incorrect result.'},
            'boundary_cases':{'decision':'pass','evidence':boundary},
            'presentation':{'decision':'pass','evidence':'Representative worked solution and all variant prompts and final answers inspected; structural checks only, not rendered or individual written-solution certification.'},
        }
        allocation=[{'criterion_index':i,'marks':{t:row['marks'] if row['type']==t else 0 for t in ('M','A','R')},'evidence':row['criterion']} for i,row in enumerate(rubric)]
        yield {'id':item['id'],'fingerprint':fingerprint(item),'review_basis':'shared_design_plus_variant_oracle','reviewer':'AI editorial matrix arithmetic FM-16BB (teacher approval pending)','teacher_approved':False,'checks':checks,'allocation':allocation}

if __name__=='__main__':
    for record in records():print(json.dumps(record,sort_keys=True))
