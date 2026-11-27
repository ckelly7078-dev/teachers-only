"""FM-16AY: Argand, radian and modulus/argument marking designs."""
import importlib

BANKS={'argand-coordinates':'aa','argand-displacement':'aa','angle-units':'z',
       'exact-radians':'s','polar-geometry':'t','modulus-constraints':'t','argument-range':'z'}
DESIGNS={
 'argand-coordinates':(
  ('A:Correct horizontal coordinate in the first position.','A:Correct signed vertical coordinate in the second position.'),
  ('A:Correct ordered pair with real coordinate first.','A:State the real-valued imaginary component, not a multiple of i.'),
  ('A:Correct plotted point on labelled real and imaginary axes, with correct ordered pair.','A:Correct quadrant.'),
  ('A:Correct original point and real-axis reflection plotted and labelled, with correct reflected coordinates.','A:Correct imaginary-axis reflection plotted and labelled, with correct coordinates.','A:Correct coordinates after both reflections.'),
  ('M:Use the midpoint relation to recover the unknown endpoint.','A:Give the exact endpoint and correctly plot both endpoints on labelled axes.','A:Correct quadrant of the recovered point.'),
  ('M:Eliminate the parameter and sketch the full supporting line on labelled axes.','M:Identify both component zeros and their order.','A:Correct lower interval and negative imaginary-axis boundary.','A:Correct middle interval and quadrant.','A:Correct positive real-axis boundary and upper interval.','R:Show the two component zeros are distinct, so the origin and quadrant II are not attained; establish exhaustive cases.')),
 'argand-displacement':(
  ('A:Correct positive real component.','A:Correct negative imaginary component.'),
  ('M:Use endpoint minus start for the directed displacement.','A:Correct signed Cartesian displacement.'),
  ('M:Use vector addition and directed subtraction in the correct order, graphically or by components.','A:Correct coordinates of the sum.','A:Correct coordinates of the second-to-first displacement.'),
  ('M:Use opposite directed sides or an equivalent parallelogram construction.','A:Correct fourth vertex and origin-to-vertex diagonal.','A:Correct directed displacement from A to B.'),
  ('M:Add the specified sum and difference to obtain twice the first arrow.','M:Subtract the difference from the sum to obtain twice the second arrow.','A:Give both exact endpoints with a valid geometric construction or explanation of the diagonal-halving relationship.'),
  ('A:Correct Cartesian expression for C.','M:Apply the zero determinant or equivalent parallel-side test and obtain the degeneracy parameter.','M:Apply the zero scalar-product or equivalent perpendicular-side test and obtain the rectangle parameter.','R:Verify both sides are nonzero, the two parameters differ and all other values yield neither case.')),
 'angle-units':(
  ('A:Correct exact radian angle.',),
  ('M:Use the radians-to-degrees conversion factor, not its reciprocal.','A:Correct exact degree measure.'),
  ('A:Correct signed degree angle without reducing modulo a turn.',),
  ('A:Correct signed conversion of the second rotation to degrees or the first to radians.','M:Add the two signed angles in a common unit.','A:Correct exact net angle in both degrees and radians.'),
  ('M:Convert the bounds to common units and form the correct inclusive/exclusive integer inequality.','A:Give all and only the admissible integers.'),
  None),
 'exact-radians':(
  ('A:Both exact trigonometric values correct.',),
  ('R:Identify the quadrant and justify opposite cosine and sine signs.','A:Give both correct signed exact values.'),
  ('M:Substitute both exact special-angle values into the expression.','A:Simplify to the correct exact result.'),
  ('M:Determine both moduli and arguments using exact trigonometry.','M:Use angle addition and multiply the moduli.','A:Give the exact Cartesian product and explain the vanishing real part using cosine of pi/2.'),
  ('M:Obtain the exact reference angle from the given sine.','R:Use the sign conditions to select quadrant II and exclude all other quadrants and axes.','A:Give the unique exact radian solution.'),
  ('M:Rewrite the expression as a positive amplitude times a shifted cosine using the supplied identity.','R:Derive the necessary amplitude bound and exclude outside values.','A:Give the two exact single-solution boundary angles, one at each endpoint.','A:Give both exact interior branches using inverse cosine.','R:Reduce each to the required half-open interval and prove distinctness and exhaustion.')),
 'polar-geometry':(
  ('A:Correct positive distance from the origin.','A:Correct anticlockwise quarter-turn radian angle.'),
  ('A:Correct nonnegative modulus, justified as distance.','A:Correct signed principal argument, justified by the negative imaginary axis.'),
  ('A:Give both exact Cartesian numbers.','R:Describe reflection in the real axis and give the correct smaller angular separation.'),
  ('A:Correct exact midpoint on the real axis from symmetry.','M:Use perpendicular half-chord geometry and exact trigonometry.','A:Correct full chord length without expanding a modulus squared.'),
  ('R:Use the nonzero midpoint radius to prove the chord is vertical.','M:Apply Pythagoras to determine the two signed imaginary coordinates.','A:Give both exact points and justify uniqueness of the unordered pair.'),
  ('R:Use the midpoint radius bound to exclude all values outside the diameter range.','R:Classify both extreme midpoint cases, giving the single coincident-endpoint pair.','R:Classify the zero midpoint case as all diameters, giving the entire infinite family.','A:Give both exact ordered pairs for a nonzero strictly interior midpoint.','R:Prove the chord direction is forced and verify both pairs and exhaustion.')),
 'modulus-constraints':(
  ('A:Correct exact positive hypotenuse length.',),
  ('A:Correct simplified Euclidean modulus.','R:Explain why adding absolute component sizes is not Euclidean distance.'),
  ('A:Correct first exact modulus.','A:Correct second exact modulus.'),
  ('M:Form the squared-modulus equation.','A:Use the strict negative imaginary component to select the correct complex number.','R:Verify the modulus by substitution.'),
  ('M:Form both squared-distance equations.','M:Eliminate one squared-distance term to recover the unique real coordinate.','A:Give both exact complex numbers, with verification and completeness from the two equations.'),
  None),
 'argument-range':(
  ('A:Correct zero principal argument.',),
  ('M:Obtain the exact reference angle from the component ratio.','A:Give the correct principal angle and justify its quadrant.'),
  ('M:Obtain the exact reference angle from the absolute component ratio.','A:Give the correct quadrant-II argument in the requested interval.'),
  ('M:Form the correct directed displacement B minus A.','M:Determine the quadrant and exact reference or principal angle.','A:Give the correct argument in the requested half-open interval.'),
  ('M:Use the tangent relation with the specified nonzero real part to recover the imaginary component.','A:Give the exact Cartesian number and verify the correct ray, not the opposite ray.'),
  None),
}
TARGETS={(p,t) for p,rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    return importlib.import_module('calibration_'+BANKS[path]+'_bank')


def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16AY')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    if path=='argand-coordinates' and tier==6:
        steps[-1]+=' Quadrant II cannot occur because a negative real coordinate requires t below the smaller zero, where the imaginary coordinate is also negative. Sketch the line through the two axis crossings with labelled real and imaginary axes.'
    if path=='argand-displacement' and tier==5:
        steps[-1]+=' Geometrically, draw the sum and directed difference arrows from the origin; their vector half-sum and half-difference recover the original two arrows.'
    if path=='polar-geometry' and tier==6:
        steps[-1]+=' In Cartesian coordinates, write the endpoints as (h/2+u,y) and (h/2-u,-y). Equality of their squared distances gives 2hu=0. For nonzero h, u=0, so the vertical chord is forced; the sign choices then exhaust the endpoints.'
    old=p['rubric']; design=DESIGNS[path][tier-1]
    if len(design)!=len(old) or any(row['marks']!=1 or 'type' in row for row in old):
        raise ValueError('Unreviewed AY rubric structure')
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
