"""Editorial decomposition of AS1 outcomes, not additional CCEA outcome IDs.
This map is a first teaching decomposition, to be reviewed before authoring the bank.
"""
DETAIL='''ALG.roots-coefficients|factor-connection:Expand quadratic factors and compare coefficients;sum-product:Calculate root sum and product;sum-squares:Evaluate sum of squares;sum-cubes:Evaluate sum of cubes;reciprocal-sum:Evaluate reciprocal sum with nonzero roots;shifted-product:Evaluate shifted products;parameter:Determine a parameter from symmetric conditions
ALG.related-quadratic|form-equation:Construct an equation from sum and product;shift:Form an equation with shifted roots;scale:Form an equation with scaled roots;reciprocal:Form an equation with reciprocal roots;square:Form an equation with squared roots;ratio:Form an equation with root ratios;combined:Form an equation with combined transformations and restrictions
CPX.parts|identify:Identify real and imaginary components;standard-form:Write numbers in Cartesian form
CPX.arithmetic|add-subtract:Add and subtract complex numbers;multiply:Multiply and reduce powers of i;divide:Divide by a nonzero complex number
CPX.conjugate|find:Find the conjugate;norm-product:Use the conjugate product to simplify expressions
CPX.quadratic|discriminant:Identify real, repeated or non-real roots;solve:Solve a real-coefficient quadratic over the complex numbers
CPX.conjugate-roots|deduce:Deduce conjugate roots of real polynomials;factor:Construct real quadratic factors from conjugate roots
CPX.cubic-quartic|cubic:Solve a cubic with sufficient root information;quartic:Solve a quartic with sufficient root or quadratic-factor information;verify:Verify all roots including multiplicity
CPX.argand|plot:Plot and interpret Cartesian points;sum-difference:Represent complex addition and subtraction geometrically
CPX.radians|convert:Convert between radians and degrees;exact:Use exact radian angles and trig values
CPX.polar|modulus:Calculate the modulus;argument:Determine an argument in the required range;interpret:Interpret modulus and argument geometrically
CPX.conversion|to-polar:Convert Cartesian to modulus-argument form;to-cartesian:Convert modulus-argument to Cartesian form;zero:Handle zero modulus and undefined argument
CPX.polar-arithmetic|product:Multiply moduli and add arguments;quotient:Divide moduli and subtract arguments;normalize:Express argument in the required range
CPX.loci|circle:Construct and interpret a distance circle;bisector:Construct and interpret an equidistant locus;ray:Construct and interpret an argument locus;region:Interpret strict or inclusive simple regions;intersection:Find intersections or common regions of simple loci
MAT.arithmetic|dimensions:Check matrix conformability;add-subtract:Add and subtract matrices;multiply:Multiply matrices in the specified order
MAT.scalar|scale:Multiply every entry by a scalar
MAT.identity|zero:Use the zero matrix;identity:Use the identity matrix of the correct order
MAT.transformation|basis:Find the image of basis vectors;describe:Identify and describe 2D linear transformations;map:Calculate images of points and figures
MAT.composition|order:Determine the order of successive transformations;compute:Calculate their composition
MAT.invariants|fixed-points:Find points fixed under a transformation;invariant-lines:Find lines mapped onto themselves;distinguish:Distinguish pointwise fixed lines from setwise invariant lines
MAT.determinant|two:Compute 2 by 2 determinants;three:Compute 3 by 3 determinants
MAT.area-scale|area:Use the absolute determinant as an area multiplier;orientation:Interpret the sign of a nonzero determinant
MAT.zero-transformation|collapse:Identify collapse onto a line or a point;parameter:Determine a parameter producing zero determinant
MAT.singular|classify:Classify square matrices using determinants;condition:Determine conditions for singularity
MAT.inverse|two:Find and verify a 2 by 2 inverse;three:Find and verify a 3 by 3 inverse;apply:Use an inverse in a matrix equation
MAT.inverse-properties|identity:Use inverse identity properties;product:Reverse the order for the inverse of a product
MAT.systems|two:Solve two-variable linear systems;three:Solve three-variable systems;inverse:Solve unique systems using an inverse;nonunique:Express a non-unique solution set
MAT.zero-system|classify:Distinguish no solution from infinitely many;parameter:Determine system consistency under parameter conditions
MAT.geometry-system|unique:Interpret three planes meeting at one point;nonunique:Interpret common lines or planes;inconsistent:Interpret no common intersection
VEC.3d|components:Use component and unit-vector notation;operations:Add, subtract and scale 3D vectors;unit:Calculate magnitudes and unit vectors
VEC.line|vector:Form vector equations of lines;cartesian:Convert to and from Cartesian form;zero-direction-component:Handle zero direction components correctly
VEC.plane|vector:Form a plane using a point and independent directions;cartesian:Form and interpret a Cartesian plane equation;normal:Identify a nonzero normal
VEC.scalar-product|calculate:Calculate scalar products;plane:Use a normal and scalar product to express a plane;line-line:Find the angle between lines;plane-plane:Find the angle between planes;line-plane:Find the angle between a line and a plane
VEC.perpendicular|test:Test perpendicularity using a scalar product;parameter:Solve an unknown using perpendicularity
VEC.intersections|line-line:Find or rule out line intersections;line-plane:Find or classify line-plane intersections
VEC.skew|classify:Distinguish skew, parallel, intersecting and coincident lines;justify:Justify skewness using equations
VEC.distance|point-line:Find perpendicular distance from point to line;point-plane:Find perpendicular distance from point to plane;line-line:Find distance between parallel or skew lines, including intersecting cases
VEC.plane-intersection|direction:Find a direction for the common line;point:Find a common point;equation:Form and check the line of intersection
VEC.vector-product|calculate:Calculate a cross product via components or determinant;normal:Use a nonzero cross product to find a normal
VEC.vector-properties|order:Use anti-commutativity;linearity:Use scalar multiplication and distributivity;zero:Recognise the zero cross product and parallelism
VEC.area-volume|parallelogram:Calculate parallelogram area;triangle:Calculate triangle area;parallelepiped:Calculate unsigned volume using scalar triple product;related-solids:Calculate related prism and tetrahedron volumes with the appropriate geometric factor'''

# Association means the question practises the child skill; does not certify
# mastery or six-tier coverage of every child skill. Some questions are prerequisite tasks.
PILOT_LINKS={
'ALG.roots-coefficients':[['factor-connection'],['sum-product'],['sum-product'],['sum-product','sum-squares'],['sum-product','sum-cubes'],['sum-product','sum-squares','parameter']],
'ALG.related-quadratic':[['form-equation'],['form-equation','shift'],['form-equation','reciprocal'],['form-equation','square'],['form-equation','ratio'],['form-equation','combined']]}

def detail_map():
 out={}
 for line in DETAIL.splitlines():
  concept,items=line.split('|');out[concept]=[tuple(item.split(':',1)) for item in items.split(';')]
 return out
