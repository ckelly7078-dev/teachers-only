"""FM-16BC: transformation, composition and invariance marking; provisional."""
import importlib

BANKS={'composition-order':'b','invariant-lines':'b','fixed-points':'c','basis-images':'e','composition-compute':'f','figure-images':'i','fixed-invariant':'k','describe-transform':'p'}
DESIGNS={
'composition-order':(
 ('M:Add the specified number first.','A:Correct final product.'),
 ('A:Correct image for A then B.','A:Correct image for B then A.','R:Explain that the rightmost matrix acts first on column vectors.'),
 ('M:Use the product BA in the correct order.','A:Correct complete composition matrix.'),
 ('M:Transform the direction of the original line in the stated order.','A:Give the correct composition matrix and verify its action on the direction.','A:Give the complete image line through the origin.'),
 ('M:Form the coordinate equation for the stated composition.','A:Recover the exact shear parameter.','A:Give the correct image in the reversed order.'),None),
'invariant-lines':(
 ('M:Use the slope to determine a direction with nonzero horizontal component.','A:Give any correct nonzero direction vector.'),
 ('R:Show the x-axis maps onto itself since the horizontal multiplier is nonzero.','R:Use the image of (1,0) to show it is not fixed pointwise.'),
 ('M:Require the image direction to be a nonzero scalar multiple of the original.','R:Exclude directions with both coordinates nonzero because the diagonal factors differ.','A:Give both coordinate axes and verify they map onto themselves.'),
 ('M:Relate original and image coordinates using the matrix.','A:Give the complete image line equation.','R:Compare slope or intercept to show it is not invariant.'),
 ('M:Form the collinearity equation for finite slopes without dividing by the slope.','A:Find both exact finite slopes.','R:Reject the vertical direction and establish onto invariance and completeness.'),None),
'fixed-points':(
 ('A:Correct solution of the linear equation.',),
 ('A:Give the correct image of (1,0) as a counterexample.','R:Show the origin is the only fixed point on the x-axis using the nonunit multiplier.'),
 ('M:Equate image and original first coordinates.','R:Check the second coordinate equation is consistent.','A:Give the complete fixed-point set with x unrestricted.'),
 ('A:Give the correct image of the specified point.','M:Equate general image and original coordinates to obtain the fixed line.','R:Compute the displacement and demonstrate parallelism to the fixed line.'),
 ('A:Recover the exact parameter from the first coordinate.','R:Check the second coordinate condition.','M:Form the remaining fixed-point equation for arbitrary coordinates.','A:Give the complete line through the specified nonzero point.'),
 ('M:Form both fixed-point equations.','R:Classify h not equal to one, distinguishing k equal to one from k not equal to one.','A:Give the x-axis when both parameters equal one.','A:Give the correct spanning direction when h is one and k is not one.','R:Exclude the whole plane and establish exhaustive cases.')),
'basis-images':(
 ('A:Correct ordered coefficients in the linear combination.',),
 ('A:Correct first basis image.','A:Correct second basis image.','R:Explain why columns, not rows, give the images.'),
 ('A:Correct matrix with both images as columns.',),
 ('M:Use linearity and the sum and difference of the input vectors.','A:Correct first basis image.','A:Correct second basis image.'),
 ('R:Demonstrate the two given inputs are independent.','M:Use both image equations to recover the correct matrix.','A:Give the correct matrix and predicted image, with uniqueness from independence.'),
 ('M:Use linearity to obtain the equation for the unknown second column.','A:Give the unique matrix for nonzero k.','R:Derive the consistency condition when k is zero.','A:Give the unrestricted second-column family when both parameters vanish and no solution otherwise.','R:Verify sufficiency and exhaustion.')),
'composition-compute':(
 ('M:Use the correct anticlockwise rotation rule.','A:Correct image coordinates.'),
 ('A:Correct image in the first order.','A:Correct image in the reverse order, demonstrating the images differ.'),
 ('M:Select BA for A followed by B.','A:Correct complete matrix.'),
 ('A:Correct composition matrix.','M:Use the original line equation to parameterise or eliminate original coordinates.','A:Correct image line equation in X,Y, covering the whole line.'),
 ('M:Form UA=C and solve by right multiplication with the inverse or equivalent equations.','A:Correct complete U.','R:Verify the image of the specified point using both successive and composite actions.'),
 ('M:Compute both products in the correct orders.','A:Give the necessary and sufficient entry conditions and recovered parameters for each order.','R:Derive the overlap condition and prove both directions of the classification.')),
'figure-images':(
 ('A:Correct image with only the horizontal coordinate scaled.',),
 ('R:Explain why multiplying by a coordinate basis column selects a matrix column.','A:Give both correct basis images.'),
 ('M:Use row-column multiplication with the specified input.','A:Correct image coordinates.'),
 ('A:Correct images of all three vertices.','M:Use two distinct image points or the transformed direction to derive the line.','A:Correct complete image line equation.'),
 ('R:Establish unique recovery using the nonzero determinant or independent image equations.','A:Recover the correct original vertex.','A:Correct original triangle area.'),
 ('M:Parameterise the original line and obtain the image base point and direction.','A:Give the exact point in the zero-direction case.','A:Give the vertical line with nonzero vertical direction.','A:Give the nonvertical line equation when the horizontal direction is nonzero.','R:Prove the cases exhaust all parameters and cover the entire image.')),
'fixed-invariant':(
 ('A:Correct membership conclusion supported by substitution.',),
 ('R:Distinguish setwise invariance from pointwise fixation.','A:Correct image of the specified nonzero point.'),
 ('A:Correct image line equation.','R:Explain the entire vertical line maps onto itself.','R:Explain why nonzero vertical coordinates move.'),
 ('A:Correct image equation and pointwise classification for the x-axis.','A:Correct image equation and noninvariance of the other horizontal line.','A:Correct image equation and setwise-only classification of the vertical line.'),
 ('M:Require the image direction to be a nonzero multiple of the original and derive the parameter equation.','A:Give the unique exact parameter.','R:Use the nonunit multiplier to show only the origin is fixed on that line.'),
 ('R:Classify identity and zero vertical multiplier separately, including collapse to the x-axis.','R:Establish onto invariance but not pointwise fixation for all vertical lines in the nonzero nonunit case.','M:Compare original and image nonvertical line coefficients to force zero slope and intercept.','R:Identify the pointwise fixed lines and prove completeness over all affine lines.')),
'describe-transform':(
 ('A:Correct image of the first basis vector.','A:Correct image of the second basis vector.'),
 ('A:Correct image of the test point.','R:Identify reflection in y=x and justify it by fixed and reversed perpendicular directions or equivalent reasoning.'),
 ('M:Use basis images or the standard rotation matrix to identify the action.','A:Give the correct centre and angle under the anticlockwise convention.'),
 ('M:Form the reflection and rotation matrices and compose in the stated order.','A:Give the correct scaled composite matrix.','R:Identify the scale and reflection axis using the fixed direction of the normalized matrix.'),
 ('M:Find independent fixed and perpendicular reversed directions.','M:Form the two image equations for the unknown matrix.','A:Give the exact reflection matrix and justify uniqueness using the independent basis.'),
 ('R:Identify the zero map and derive the common squared column length and orthogonality.','M:Normalize by the positive scale and establish determinant negative one.','A:Give a valid nonzero fixed-axis direction, including the exceptional branch.','R:Show the perpendicular direction is reversed, proving reflection.','R:Classify pure reflection and other positive scales, and establish completeness.')),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}

def base(path):
    return importlib.import_module('calibration_'+BANKS[path]+'_bank')

def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16BC')
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
