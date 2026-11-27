"""FM-16BD: determinant, collapse and inverse marking; provisional."""
import importlib

BANKS={'det-area':'','orientation':'e','collapse':'b','collapse-parameter':'l','det-three':'c','inverse-two':'b','inverse-three':'f','inverse-product':'d','inverse-identities':'m','singular-condition':'g','det-classification':'o','matrix-equation':'h'}
# Explicit allocation for each mathematical design. None preserves prior typed work.
DESIGNS={
'det-area':(
 ('M:Multiply perpendicular side lengths.','A:Correct unsigned area.'),
 ('R:Explain the negative determinant using the reflection matrix or reversal of orientation.','R:Explain unchanged unsigned area using the absolute determinant.'),
 ('M:Evaluate the determinant and use its absolute value as area multiplier.','A:Correct image area.'),
 ('A:Correct composition matrix in the specified order.','A:Correct image area and orientation from the signed determinant.'),
 ('M:Form the absolute determinant equation from the area ratio.','A:Give both exact parameter values.','R:Identify orientation at each value from its determinant sign.'),
 ('M:Obtain both squared-parameter branches from the absolute determinant equation.','R:At zero multiplier identify two roots and show rank-one collapse.','A:Correct counts in all three positive-multiplier regimes.','R:Justify coinciding branches, zero square at the threshold and exclusion of negative squares.')),
'orientation':(
 ('A:Correct signed product.',),
 ('R:Explain reversal using the negative determinant or reflected vertex order.','R:Explain unchanged unsigned area using unit absolute determinant or reflection isometry.'),
 ('A:Correct signed determinant.','R:Correct orientation classification from its sign.'),
 ('M:Use the individual determinants or correctly compose the matrices.','A:Correct determinant of the composition.','A:Correct unsigned image area and orientation.'),
 ('M:Equate the signed determinant to the positive area ratio.','A:Both exact real roots.','R:Show the negative determinant equation has no real root.'),
 ('M:Form the determinant quadratic.','A:Both exact real boundaries.','R:Justify positive outside and negative inside the roots.','R:At both roots explain rank-one zero-area collapse.','R:Give the complete orientation classification including equality cases.')),
'collapse':(
 ('M:Compare both components by a common scale.','A:Correct multiplier and parallel conclusion.'),
 ('A:Correct nonzero image of the first basis vector.','R:Use that image to refute the zero-map claim.'),
 ('M:Write the general image as a scalar multiple of a fixed nonzero direction.','A:Correct image line with every point attained.'),
 ('A:Complete kernel equation.','M:Substitute the specified input line into the mapping.','A:Correct full image line, with the image parameter unrestricted.'),
 ('M:Set the determinant to zero and identify the nonzero column.','A:Correct unique parameter and image line.','A:Complete kernel, justified by the general image.'),None),
'collapse-parameter':(
 ('A:Correct signed determinant.',),
 ('A:Correct nonzero basis-vector image.','R:Identify the entire x-axis and show every horizontal coordinate occurs.'),
 ('M:Form and set the determinant equal to zero.','A:Correct parameter, with zero area multiplier.'),
 ('M:Form the determinant equation.','A:Both exact roots.','R:Give each full image line and justify it using a nonzero spanning column.'),
 ('M:Require a zero discriminant for the determinant quadratic.','A:Correct parameter and repeated root.','R:Give the image line using a nonzero column and justify uniqueness.'),
 ('M:Derive the determinant equation and its discriminant.','A:Correct root counts, threshold and exact roots.','R:Identify the full image span using the always nonzero column.','R:Derive the complete kernel span from the first equation and determinant dependence.','R:Prove exhaustion of all cases, including the repeated root.')),
'det-three':(
 ('A:Correct signed two-by-two determinant.',),
 ('R:Explain that a single row exchange negates the determinant.','A:Correct signed determinant after exchange.'),
 ('M:Use signed first-row cofactor expansion.','A:Correct determinant.'),
 ('M:Apply a determinant-preserving row addition to obtain the specified zero.','A:Correct transformed matrix.','A:Correct determinant.','R:Conclude invertibility from nonzero determinant.'),
 ('M:Derive the determinant polynomial.','A:Correct unique root.','R:Exhibit a nonzero two-by-two minor.','R:Use zero determinant and the minor to establish rank exactly two.'),
 ('M:Derive and factor the determinant.','A:All three exact singular parameters.','R:Exhibit an everywhere nonzero two-by-two minor.','R:Classify rank two at the roots and three elsewhere, proving completeness.')),
'inverse-two':(
 ('A:Correct solution of the scalar equation.','R:Explain cancellation by multiplication by a nonzero reciprocal.'),
 ('A:Correct upper-right entry of the proposed product.','R:Use the nonzero off-diagonal entry to reject the inverse.'),
 ('M:Calculate the nonzero determinant and apply an inverse method.','A:Correct full inverse.','R:Verify the product is the identity.'),
 ('A:Correct full inverse with nonzero determinant.','M:Apply the inverse to the image vector.','A:Correct original point.'),
 ('M:Form the inverse-entry equation with nonzero denominator.','A:Correct unique parameter.','A:Correct complete inverse at an admissible parameter.'),None),
'inverse-three':(
 ('M:Substitute the specified value of y into the equation for x.','A:Correct ordered solution.'),
 ('A:Correct nonzero product entry.','R:Give the corrected inverse entry and justify the correction using the identity product.'),
 ('M:Begin a valid inverse method, such as elimination with a general right-hand side.','M:Complete the elimination or equivalent adjugate calculation.','A:Correct full inverse.','R:Verify by multiplication.'),
 ('M:Use a valid method to obtain the inverse.','A:Correct full inverse.','A:Correct solution vector from the inverse.','R:Verify in the original system.'),
 ('M:Require nonzero determinant and derive the specified inverse-entry expression.','A:Correct admissible parameter.','A:Correct full inverse with identity verification.'),
 ('A:Correct nonzero-determinant condition and complete inverse.','R:For zero k derive the complete homogeneous solution line for every h.','R:For nonzero k and zero h derive the other complete solution line and exhaust singular cases.')),
'inverse-product':(
 ('M:Undo the last multiplication by division.','A:Correct original number.'),
 ('A:Select the correct supplied candidate.','R:Explain reversal of inverse multiplication order.','R:Distinguish the candidates using their different entries or an identity check.'),
 ('M:Use the inverse-product rule in reverse order with correct individual inverses.','A:Correct complete inverse product.'),
 ('A:Correct intermediate vector by undoing A.','A:Correct original vector by undoing B.','R:Check the two successive forward images.'),
 ('M:Invert the given inverse product to recover AB.','A:Correct A by right multiplication by the inverse of B.','R:Verify the recovered product inverse.'),
 ('R:Establish the nonzero parameter requirement for both inverses.','M:Reduce the inverse equality to commutation.','M:Compare the off-diagonal entries of the products.','A:Correct complete parameter conditions.','R:Prove sufficiency and exclude the undefined case.')),
'inverse-identities':(
 ('A:Correct reciprocal.',),
 ('R:Explain that the multiplicative identity rather than the zero matrix is required.','A:Give both products as the identity of the specified size.'),
 ('R:Use the inverse-of-inverse identity and give its correct matrix.','R:Use associativity and adjacent inverse cancellation and give the other correct matrix.'),
 ('M:Replace the double inverse and cancel the adjacent B factors.','M:Cancel adjacent A factors to obtain the inverse of B.','A:Correct final matrix.'),
 ('M:Invert the equation or apply the reverse product rule.','A:Correct recovered matrix AB.','R:Prove existence and uniqueness using invertibility and reversible operations.'),
 ('M:Require nonzero k and form the inverse or equivalent matrix equation.','A:Correct c and both diagonal-compatible k values.','R:Derive the off-diagonal condition and distinguish its two branches.','R:Give all parameter triples and verify necessity and sufficiency.')),
'singular-condition':(
 ('M:Apply the zero-product property.','A:Both exact roots.'),
 ('R:Identify row dependence or an equivalent counterargument to the claim.','A:Correct zero determinant and singular classification.'),
 ('M:Form the zero determinant equation.','A:Both exact real roots.'),
 ('M:Factor the product determinant using multiplicativity.','A:All exact roots with their corresponding singular factor.','R:Prove the roots are distinct and no other parameters work.'),
 ('M:Find both roots of the second determinant.','A:Both ordered parameter pairs using the first determinant equation.','R:Verify both determinants vanish and prove exhaustion.'),None),
'det-classification':(
 ('A:Correct signed determinant.',),
 ('R:Identify row dependence.','R:Use zero determinant to explain singularity despite nonzero entries.'),
 ('A:Correct determinant and classification of A.','A:Correct determinant and classification of B.','A:Correct determinant and classification of C.'),
 ('M:Find the three individual determinants without multiplying the matrices.','A:Correct product determinants and invertibility decisions.','R:Explain why determinant multiplicativity gives the same decisions on reversal.'),
 ('M:Derive both signed determinant polynomials.','R:Prove C is never singular over the reals.','A:Both exact parameters and correct classification at each.'),
 ('M:Derive both determinant expressions.','A:Correct two zero-determinant curves.','R:Find their unique intersection.','A:Correct both, only B, only C and neither conditions.','R:Prove the four cases exhaust the parameter plane.')),
'matrix-equation':(
 ('A:Correct solution with the nonzero divisor justification.',),
 ('M:Use left multiplication to cancel A.','A:Select the correct supplied candidate.','R:Explain uniqueness from invertibility and why the other distinct candidate fails.'),
 ('M:Find a valid inverse of A.','A:Correct X in the required order.','R:Verify AX equals B.'),
 ('M:Find the inverse of C.','A:Correct X by right multiplication.','A:Correct Y by left multiplication.','R:Verify both equations and compare the matrices.'),
 ('M:Derive X as a function of the parameter.','A:Correct unique parameter and full symmetric matrix.','R:Verify AX equals B and prove uniqueness.'),
 ('R:Exclude singular A because B is invertible or by its nonzero second row.','A:Correct unique candidate for nonzero k.','M:Reduce the second equation to commutation of A and B.','A:Correct parameter conditions from the commutator.','R:Establish necessity, sufficiency and uniqueness.')),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}

def base(path):
    suffix=BANKS[path]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_bank')

def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16BD')
    p=base(path).make(path,tier,v)
    specs=DESIGNS[path][tier-1]
    if len(specs)!=len(p['rubric']) or any(r['marks']!=1 or 'type' in r for r in p['rubric']):
        raise ValueError('Unreviewed rubric structure')
    rub=[]
    for spec in specs:
        kind,criterion=spec.split(':',1)
        if kind=='M':criterion+=' Accept equivalent valid methods respecting explicit question restrictions; retain demonstrated method credit after a subsequent arithmetic slip.'
        elif kind=='A':criterion+=' Require the specified correct result; do not automatically award accuracy for an incorrect result.'
        else:criterion+=' Accept equivalent valid reasoning supported by the stated constraints.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
