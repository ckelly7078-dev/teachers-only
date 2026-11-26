"""Representative vector difficulty notes; provisional scope."""
NOTES={
'cartesian-line':('Rearrange parameter.','Reject division by zero.','Convert vector to Cartesian form.','Convert and intersect coordinate plane.','Reconstruct from two points and intersect.','Classify zero-component forms and plane intersections.'),
'cross-linearity':('Scale vector.','Correct quadratic scaling.','Distribute cross product.','Recover independent coefficients.','Reconstruct full vector family.','Prescribed cross product and sum with equal norms; enrichment.'),
'cross-normal':('Test orthogonality.','Reject zero normal.','Compute and verify normal.','Construct plane through three points.','Recover parameter and verify independence.','Classify oriented unit normal and degenerate span.'),
'cross-order':('Signed arithmetic.','Correct order reversal.','Use antisymmetry.','Compare cyclic triangle orientations.','Recover vector from reversed product and component.','Classify fixed-length cross-product solutions.'),
'cross-product':('Recall determinant prerequisite.','Diagnose sign error.','Compute standard product.','Connect cross product and geometry.','Invert magnitude condition.','Revised: combine two cross-product constraints and prove compatibility.'),
'justify-skew':('Recognise proportional directions.','Reject nonparallel implies skew.','Prove skew using all coordinates.','Convert endpoints and check intersection.','Recover intersection parameter.','Classify two-parameter intersection and skew; overlap with line-intersection monitored.'),
'line-intersection':('Solve linear equations.','Check third coordinate.','Solve and verify intersection.','Determine intersection from point data.','Recover prescribed intersection parameter.','Classify parallel, intersecting, skew and coincident cases.'),
'line-line-angle':('Calculate magnitude.','Distinguish directed and smaller angles.','Use direction vectors.','Recover directions from points.','Invert acute-angle constraint.','Classify quadratic and degree-change cases.'),
'line-line-distance':('Calculate displacement length.','Distinguish shortest and arbitrary distance.','Apply skew distance formula.','Find closest points via orthogonality.','Invert parallel distance.','Classify distance and all closest pairs; overlaps with line classification noted.'),
'line-plane-angle':('Recall scalar product.','Distinguish normal and plane angle.','Compute angle.','Use reconstructed direction/normal.','Invert angle constraint.','Classify endpoints and both signs; modest progression, queued for follow-up.'),
'line-plane-intersection':('Recall substitution.','Distinguish parallel and contained.','Find intersection.','Link plane and line forms.','Classify parameter intersection.','Revised: compare two planes with distinct exceptional parameters and coincidence.'),
'normal-dot-plane':('Compute scalar product.','Use displacement from plane point.','Construct plane.','Recover constant and test points.','Recover normal component.','Classify unit normals accounting for sign-equivalent planes.'),
'parallelogram-area':('Recall rectangle area.','Distinguish oriented product and unsigned area.','Compute cross-product magnitude.','Recover vertex and area.','Invert area and check both signs.','Prove minimum and classify prescribed areas.'),
'perpendicular-parameter':('Solve linear equation.','Exclude zero direction.','Solve dot-product condition.','Use point displacement.','Solve two orthogonality constraints.','Classify quadratic inverse condition; modest progression, queued.'),
'perpendicular-test':('Compute scalar product.','Exclude undefined angle.','Test candidate vectors.','Check all triangle vertices.','Recover perpendicular vector with fixed component.','Classify parameter pairs excluding zero vectors and forbidden division.'),
'plane-cartesian':('Compute scalar product.','Scale entire equation.','Construct plane from normal.','Derive plane from points.','Recover coefficient and axis intersection.','Classify planes containing line and extra point.'),
'plane-common-point':('Check point membership.','Check both planes.','Find point with fixed coordinate.','Construct intersection line from two points.','Impose additional plane.','Minimise distance on parameterised common line.'),
'plane-intersection-direction':('Test normal orthogonality.','Distinguish normal and direction.','Cross two normals.','Recover normals from spanning vectors.','Recover coefficient from direction.','Classify coincident and parallel planes or common line; overlap queued.'),
}
def scope(path,tier):
    if path not in NOTES or tier not in range(1,7): raise ValueError('Not reviewed in FM-16AK')
    if path=='cross-linearity' and tier==6:return 'enrichment_only'
    return {1:'prerequisite_bridge_reviewed',2:'conceptual_diagnostic_reviewed',3:'syllabus_linked_candidate',4:'syllabus_linked_candidate',5:'syllabus_linked_candidate',6:'challenge_candidate'}[tier]
