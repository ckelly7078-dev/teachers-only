"""FM-16AZ: provisional polar conversion, arithmetic and locus marking."""
import importlib

BANKS={'polar-to-cartesian':'r','cartesian-to-polar':'r','zero-exception':'aa',
       'polar-products':'v','polar-quotients':'v','argument-normalization':'s',
       'distance-circle':'y','equidistant-locus':'y','argument-rays':'u',
       'complex-regions':'u','locus-intersection':''}
# One requirement per original mark; the two existing typed cells are retained.
DESIGNS={
 'polar-to-cartesian':(
 'A:Correct exact cosine.|A:Correct exact sine.',
 'R:Explain the quadrant-II negative real and positive imaginary signs.|M:Apply the modulus to cosine and sine respectively.|A:Correct exact Cartesian number.',
 'M:Use the modulus times cosine and sine to form both components.|A:Correct signed exact real component.|A:Correct signed exact imaginary component.',
 'A:Correct first Cartesian number.|A:Correct second Cartesian number.|A:Correct exact sum by component addition.',
 'M:Relate real part to positive modulus times cosine.|A:Recover the correct positive modulus.|A:Give the exact Cartesian form.|R:Justify uniqueness from nonzero cosine and the fixed argument.',
 'M:Represent both factors with unknown positive moduli and the specified directions.|M:Form independent real and imaginary component equations.|A:Recover both exact moduli.|R:Derive the strict feasibility inequality and explain zero-modulus boundary and impossibility below it.|A:Give both exact Cartesian numbers, with uniqueness from the linear solution.'),
 'cartesian-to-polar':(
 'M:Use Pythagoras on the two coordinates.|A:Correct exact distance.',
 'R:Identify quadrant II and why the tangent ratio alone is insufficient.|M:Adjust the reference angle by the correct half-turn or use quadrant-aware inverse tangent.|A:Correct principal argument.',
 'A:Correct exact modulus.|M:Find the exact reference angle with correct quadrant.|A:Correct principal argument.',
 None,
 'M:Use the squared modulus equation to recover the squared imaginary component.|A:Select the correct negative component and thus the unique number.|A:Correct exact principal argument with quadrant adjustment.',
 'M:Form the squared imaginary-component equation.|R:Exclude the region with negative radicand.|A:Give both interior polar solutions with distinct arguments.|A:Give both boundary solutions with arguments zero and pi respectively.|R:Prove completeness and exclude minus pi from the principal interval.'),
 'zero-exception':(
 'M:Cancel both Cartesian components.|A:Correct zero modulus.',
 'A:Correct zero modulus.|R:Explain that zero has no direction and no defined argument.',
 'M:Use the condition that both components must vanish.|A:Correct unique parameter.|R:State that the resulting zero has undefined argument.',
 'A:Correct excluded denominator parameter.|A:Correct zero-numerator parameter with nonzero denominator.|R:Explain that zero has undefined argument, distinct from an undefined quotient.',
 'R:Exclude moduli below the fixed positive real component, including negative values.|A:Give the single boundary number and both distinct interior numbers with correct counts.|R:Explain why no admissible solution is zero.',
 'R:State the original denominator exclusion for all values of the other parameter.|M:Cancel the common factor only on the original domain.|A:Give the exact modulus and unique zero pair.|R:Classify argument-defined pairs and justify why cancellation cannot restore the excluded line.'),
 'polar-products':(
 'A:Correct exact radian sum.',
 'R:State the product-of-moduli rule rather than addition.|A:Correct product modulus.',
 'A:Correct product modulus.|M:Add arguments and normalize by full turns.|A:Correct complete polar form in the requested range.',
 'M:Divide the specified product modulus by the product of the known moduli.|M:Subtract both known arguments from the specified product argument.|A:Correct complete polar form with principal argument.',
 None,
 'M:Form the product modulus and linked argument.|M:Express the real-product condition as an integer multiple of pi.|R:Derive the exhaustive integer range from the half-open interval.|A:Give every exact angle and signed real product.|R:Justify sign by integer parity and completeness.'),
 'polar-quotients':(
 'A:Correct exact modulus quotient and unnormalized signed angle difference.',
 'A:Identify zero as the denominator.|R:Explain why division by zero is undefined.',
 'A:Correct quotient modulus.|M:Subtract denominator argument from numerator argument and normalize.|A:Correct complete polar form.',
 'M:Rewrite the nested quotient as zu/w or an equivalent valid calculation.|A:Correct exact modulus.|A:Correct normalized argument and complete polar form.',
 'M:Use the positive modulus and specified argument to determine the unique quotient.|M:Multiply by the known denominator, combining moduli and angles correctly.|A:Correct complete polar numerator, with verification and uniqueness from reversibility.',
 'M:Substitute the nonzero quotient and derive the equivalent quadratic.|A:Find the discriminant thresholds and both repeated-root boundary cases, including moduli and arguments.|A:Give both interior unit-modulus quotients and their exact arguments.|A:Give both exterior real reciprocal quotients, their moduli and principal arguments.|R:Prove nonzero roots, recover all numerators and establish completeness.'),
 'argument-normalization':(
 'M:Use two pi radians per full turn.|A:Correct exact radian angle.',
 'A:Correct principal argument pi.|R:Explain the full-turn equivalence and exclusion of minus pi.',
 'M:Add or subtract an integer number of full turns.|A:Correct exact angle in the half-open interval.',
 'A:Correct product argument with normalization shown.|M:Subtract the divisor argument from the product angle, using equivalent wrapped or unwrapped angles.|A:Correct normalized quotient argument.',
 'M:Set the doubled angle equal to the specified principal argument modulo two pi.|M:Divide to obtain the full integer family.|A:Give both exact permitted angles.|R:Verify both and exclude all other integers using the interval.',
 'M:Obtain the raw quotient angle.|A:Determine both exact wrap boundaries.|A:Correct first interval and wrapped expression, including the lower boundary.|A:Correct middle interval and unwrapped expression, including the upper boundary.|R:Give the final interval and expression and justify exhaustive disjoint coverage and the choice of pi at both wraps.'),
 'distance-circle':(
 'A:Correct exact Euclidean distance.',
 'A:Correct positive radius, not its square.|A:Correct squared Cartesian circle equation.',
 'M:Express the displacement from the specified centre in components.|A:Correct Cartesian circle equation, centre and radius.',
 'M:Complete both squares with the correct constant adjustments.|A:Correct squared circle equation.|A:Correct centre and positive radius.',
 'M:Set imaginary component to zero and substitute in the circle.|M:Obtain the correct squared real displacement.|A:Give both exact real intersections and justify that no other roots occur.',
 'M:Exclude negative second radius and subtract the two squared-distance equations.|A:Give the exact real coordinate and both signed imaginary-component expressions.|R:Derive the exact closed admissible radius range.|R:Classify two interior intersections and single tangencies, and verify original unsquared distances.'),
 'equidistant-locus':(
 'A:Correct ordered midpoint coordinates.',
 'M:Use equal squared distances or perpendicular-bisector geometry.|A:Give the entire line and correctly verify the stated nonreal point.',
 'M:Square both nonnegative distances.|M:Expand and cancel quadratic terms to obtain a linear relation.|A:Correct Cartesian bisector equation.',
 'M:Derive the first bisector equation.|M:Derive the independent second bisector equation.|A:Give the unique common point with verification.',
 'M:Determine the perpendicular bisector.|M:Substitute into the circle to determine the squared imaginary component.|A:Give both exact intersections, retaining both signs.',
 'A:Give the fixed bisector.|M:Derive the moving-site equation by subtracting squared distances.|R:Handle coincident sites at zero separately and give the unique nonzero-parameter point.|R:Classify the real moving-site family completely, including identical bisectors and distinct parallel lines.'),
 'argument-rays':(
 'A:Correct principal argument in radians.',
 'A:Correct positive-real ray relative to the specified origin.|R:Identify the excluded endpoint with undefined argument and reject the opposite ray.',
 'A:Correct ray origin.|M:Use the specified angle to determine slope and direction.|A:Correct Cartesian equation and strict direction restriction.',
 'M:Form the first ray equation and direction inequality.|M:Form the second ray equation and direction inequality.|A:Give the exact intersection and verify both strict inequalities.',
 'M:Parameterize the positive ray with a strictly positive parameter.|M:Solve the absolute-distance equation, retaining both candidates initially.|A:Give the unique admissible point and reject the candidate off the ray.',
 'M:Parameterize the ray with a strictly positive parameter and exclude negative radii.|M:Form the equivalent squared-distance equation.|A:Classify no-intersection and tangent cases.|A:Give both parameter roots and the exact threshold separating two from one admissible point.|R:Explain excluded zero parameter at the threshold and verify completeness in the original constraints.'),
 'complex-regions':(
 'A:Correct value satisfying both endpoint restrictions.',
 'A:Correct modulus and nonmembership decision.|R:Explain exclusion by the strict inequality.',
 'A:Correct closed right half-plane and labelled vertical boundary.|A:Correct open lower half-plane and labelled excluded horizontal boundary.|A:Correct sketch of their intersection, including exclusion of the corner and horizontal edge.',
 'A:Correct disk centre and radius.|M:Use half-disk geometry and obtain the exact area.|R:State the included open-ended circular arc and excluded entire diameter.',
 'M:Derive the perpendicular bisector by subtracting squared distances.|A:Give both exact circle intersections.|A:Give the correct strict closer-to-origin half-plane with justification.',
 'M:Subtract squared distances to obtain the strict linear inequality.|A:Correct classification of empty, whole and proper nonempty regions with exact endpoints.|A:Correct supremum and attainment for nonpositive parameter.|A:Correct supremum for positive parameter below radius.|R:Prove least upper bound using admissible approaching points and explain nonattainment on the excluded boundary.'),
 'locus-intersection':(
 'M:Use squared Cartesian displacements and Pythagoras.|A:Correct squared distance.',
 'A:Correct centre and radius.|R:Explain that the centre has zero distance and is excluded for positive radius.',
 'M:Substitute the vertical line in the squared circle equation.|A:Give both exact Cartesian intersections.',
 'M:Derive the perpendicular bisector of the distinct centres.|A:Give both exact points and explain the strictly positive squared imaginary component.',
 'M:Use the argument to select a positive ray from the circle centre.|A:Give the exact point from the positive radius and verify the imaginary condition and uniqueness.',
 'M:Substitute the line coordinate into the squared circle equation.|A:Give the exact interior interval, both signed solutions and both tangent points.|R:Classify zero, one and two solutions by radicand sign and justify completeness.')}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    suffix=BANKS[path]
    return importlib.import_module('calibration'+('_'+suffix if suffix else '')+'_bank')


def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16AZ')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    if path=='polar-products' and tier==3 or path=='polar-quotients' and tier==3:
        steps[1]+=' Use whole turns of 2pi; a raw angle of -pi is represented by pi.'
    if path=='polar-to-cartesian' and tier==4:
        steps[0]='Use z=m(cos(theta)+i sin(theta)) for each number. '+steps[0]
    if path=='polar-quotients' and tier==5:
        steps[-1]+=' Since w is nonzero, multiplication by w is invertible, so no other numerator is possible.'
    if path=='complex-regions' and tier==3:
        steps[-1]+=' On labelled real and imaginary axes, draw the vertical boundary solid below the horizontal boundary, draw the horizontal edge dashed to its right, and shade their common right-and-below region.'
    if path=='complex-regions' and tier==4:
        # The original short answer omitted the explicitly requested boundary statement.
        p['final_answer_latex']+='; right semicircular arc excluding its endpoints included; diameter excluded.'
    if path=='polar-quotients' and tier==6:
        # Complete the short answer without changing any existing mathematical result.
        a=v+1
        p['final_answer_latex']+=f' At h=+/-2/{a}, the quotient is respectively +1 or -1, modulus 1 and principal argument 0 or pi. Outside the bounds, q=({a}h +/- sqrt({a*a}h^2-4))/2, modulus |q| and principal argument 0 for positive q or pi for negative q.'
    if path=='equidistant-locus' and tier==6:
        steps[-1]+=' Distinct parallel bisectors have no common point; at the identical-site value the entire fixed line remains.'
    old=p['rubric']; design=DESIGNS[path][tier-1].split('|')
    if len(design)!=len(old) or any(row['marks']!=1 or 'type' in row for row in old):
        raise ValueError('Unreviewed AZ rubric structure')
    rub=[]
    for spec in design:
        kind,criterion=spec.split(':',1)
        if kind=='M':
            criterion+=' Accept equivalent valid methods respecting the question restrictions. Retain independently demonstrated method credit after an arithmetic slip.'
        elif kind=='A':
            criterion+=' Require the specified correct result; do not automatically award accuracy for an incorrect result.'
        else:
            criterion+=' Accept equivalent valid reasoning; require conclusions to follow from the stated constraints.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
