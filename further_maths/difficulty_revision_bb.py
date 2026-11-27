"""FM-16BB: matrix arithmetic and determinant marking, not teacher approval."""
import importlib

BANKS={'matrix-conformability':'g','matrix-add-subtract':'n','matrix-products':'n','scalar-matrix':'j','identity-operations':'i','zero-matrix':'j','det-two':'d'}
# Each tuple is a reviewed design's one-mark requirements, not a worked example.
DESIGNS={
'matrix-conformability':(
 ('A:Correct order, rows before columns.',),
 ('R:Explain why addition requires equal orders and is undefined.','A:Identify valid AB and its correct order using the matched inner dimensions.'),
 ('A:Correct AB order.','R:Explain why BA is undefined using inner dimensions.','R:Explain why addition is undefined using both orders.'),
 ('M:Use AB conformability to determine the row count of B.','A:Give the complete order of B using the stated column count.','A:Give both product orders, checking the intermediate dimension.'),
 ('M:Use the entry count and the outer dimensions to recover the order of B.','A:Give the valid BC order.','R:Exclude BA using unequal inner dimensions.'),
 ('M:Derive p=q and r=s from equal product orders.','M:Derive the positive integer product constraint and exclude p=r.','A:List every admissible ordered quadruple, including reversed factor orders.','R:Prove sufficiency and exhaustion by positive divisor enumeration, excluding equal factors.')),
'matrix-add-subtract':(
 ('A:Correct signed difference.',),
 ('R:Explain that matching row counts alone do not permit addition.','A:Identify that C-C is defined (the zero matrix of the same order).'),
 ('M:Scale B and subtract corresponding entries in the correct order.','A:Give the complete exact matrix.'),
 ('A:Correct X from the sum of the two equations or an equivalent method.','A:Correct Y from their difference or an equivalent method.','R:Verify both original equations.'),
 ('M:Equate the two off-diagonal entries of the sum.','M:Form the equation for the specified diagonal sum.','A:Give both exact parameters and the complete matrix, justifying uniqueness by the independent equations.'),
 ('M:Derive the forced decomposition by transposition or entry comparison.','A:Give both exact matrices and demonstrate their defining properties and uniqueness.','M:Form the determinant condition for the symmetric part.','A:Give both exact singular branches and establish that they are exhaustive.')),
'matrix-products':(
 ('A:Correct sum of the two signed products.',),
 ('R:Explain that a matrix entry uses a row and a column, not corresponding positions.','A:Give the correct top-left entry.'),
 ('A:State the correct output dimensions.','M:Use valid row-column multiplication for the entries.','A:Give the complete exact product.'),
 ('M:Form both scalar equations in the correct product order.','A:Give both entries of the recovered row.','R:Verify the product against the specified row.'),
 ('M:Form the row equations using the prescribed last row and identity target.','A:Give the complete X satisfying the identity equation.','A:Give the complete reverse product and justify why it is not the larger identity.'),
 ('M:Parameterise the last row and equate both rows of CX to the identity.','A:Give the complete two-parameter family and verify CX=I.','R:Use a nonzero null vector or rank argument to rule out XC=I.','R:Prove idempotence using associativity and establish exhaustion of all possible X.')),
'scalar-matrix':(
 ('M:Apply the scalar independently to the signed numbers.','A:Give both signed products.'),
 ('R:Explain why scaling only diagonal entries is incorrect.','A:Give the full corrected matrix.'),
 ('M:Multiply each entry by the stated negative scalar.','A:Give the complete exact matrix.'),
 ('A:Recover p using a nonzero off-diagonal entry.','A:Recover q from a diagonal entry.','R:Verify all four entries and establish uniqueness.'),
 ('M:Use det(kA)=k squared times det(A).','A:Obtain the exact squared scalar from the absolute determinant.','A:Give both signed scalars and correct orientation for both.'),
 ('R:Classify both zero-A cases without dividing by zero.','M:For nonzero k, obtain the forced scalar from the upper-left entry.','M:Derive and solve the remaining diagonal condition.','A:Give all admissible nonzero-k cases and justify sufficiency and exclusion of other values.')),
'identity-operations':(
 ('A:Correct multiplier one.','R:Explain why multiplication by one leaves any nonzero number unchanged.'),
 ('R:Explain identity multiplication leaves A unchanged.','R:Explain identity addition changes only the diagonal entries.','A:Give the two correct results and distinguish them.'),
 ('M:Use the correctly sized identity on each side to simplify.','A:Give the exact matrix.'),
 ('A:Identify the row and column dimensions of R.','R:Derive the two required identity orders and explain why swapping fails.','A:Give the unchanged matrix product.'),
 ('M:Form the vanishing off-diagonal condition from AB.','A:Give the unique exact parameter.','R:Verify BA is the identity at that value.'),
 ('M:Calculate the square, accounting for off-diagonal cancellation.','M:Equate the diagonal expression to one using the involution condition.','A:Give the full exact parameter family.','R:Prove necessity and sufficiency and that the square identity implies invertibility.')),
'zero-matrix':(
 ('A:Correct additive identity zero.',),
 ('A:Give the unchanged sum and explain entrywise addition of zero.','A:Give the zero product and explain why each row-column sum vanishes.'),
 ('M:Rearrange the matrix equation to isolate X.','A:Give the exact sum matrix.'),
 ('M:Compute the product or show both columns are annihilated.','A:Give the zero product and zero determinant.','R:Identify both factors as nonzero and explain why inverse cancellation is invalid.'),
 ('M:Form the equation from the second component of the zero image.','A:Give the unique parameter, using the nonzero coefficient.','A:Give the full real one-parameter null-vector family, justified by the dependent rows.'),
 ('R:Use invertibility away from the exceptional parameter to force B=O.','M:At the singular parameter derive the independent column constraint.','A:Give the entire two-parameter family.','R:Verify all solutions and identify exactly when nonzero B exists.')),
'det-two':(
 ('A:Correct signed arithmetic result.',),
 ('A:Correct original determinant.','A:Correct determinant after the row exchange.','R:Explain the sign reversal under a row swap.'),
 None,
 ('A:Correct signed determinant of AB.','A:Correct nonzero determinant of B.','M:Use determinant multiplicativity and division by the nonzero determinant to give the exact determinant of A without recovering A.'),
 ('M:Form the determinant expressions for B and E.','M:Use multiplicativity to obtain the equation for the squared parameter.','A:Give both distinct exact real roots.','R:Use the nonzero determinant to justify invertibility in both cases and exhaust all roots.'),
 None),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    return importlib.import_module('calibration_'+BANKS[path]+'_bank')


def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16BB')
    p=base(path).make(path,tier,v)
    specs=DESIGNS[path][tier-1]
    if len(specs)!=len(p['rubric']) or any(r['marks']!=1 or 'type' in r for r in p['rubric']):
        raise ValueError('Unreviewed rubric structure')
    rub=[]
    for spec in specs:
        kind,criterion=spec.split(':',1)
        if kind=='M':criterion+=' Accept an equivalent valid method respecting the question restrictions; retain demonstrated method credit after a subsequent arithmetic slip.'
        elif kind=='A':criterion+=' Require the specified correct result; do not automatically award accuracy for an incorrect result.'
        else:criterion+=' Accept equivalent valid reasoning supported by the stated constraints.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
