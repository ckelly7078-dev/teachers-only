"""AS1 source-locator and item-version scope register. Editorial, not release approval."""
import argparse,collections,json
from pathlib import Path
from active_difficulty import Resolver,MODES,require
from consolidation_audit import OUTCOMES
from marking_review import fingerprint

# Representative prompts for T3--6 were checked against the supplied specification,
# with numerical variants separately checked by the resolver. T1--2 retain their
# bridge/diagnostic status; no direct new content review of those prompts is asserted.
# These notes are paraphrases and judgments, not CCEA wording or official codes.
CONCEPT_METHOD={
 'ALG.roots-coefficients':'Signed sum/product, coefficient normalization, symmetric expressions and quadratic discriminants.',
 'ALG.related-quadratic':'Use symmetric expressions or coefficient substitution to construct related-root quadratics; retain denominator and sign restrictions.',
 'CPX.quadratic':'Real-coefficient quadratic discriminant, exact complex roots, and verification.',
 'CPX.cubic-quartic':'Use supplied roots/factors, conjugacy and polynomial division; degree and multiplicity checks.',
 'CPX.arithmetic':'Component arithmetic, coupled real/imaginary equations, nonzero division denominator.',
 'CPX.parts':'Read or recover real/imaginary components of Cartesian expressions.',
 'CPX.conjugate':'Conjugation, real component equations and modulus-square identities.',
 'CPX.conjugate-roots':'Conjugate roots of real polynomials and their corresponding factors.',
 'CPX.argand':'Cartesian coordinates, reflections, midpoint and displacement geometry on Argand diagrams.',
 'CPX.radians':'Radian measure, angle conversions and exact trigonometric values as prerequisite techniques.',
 'CPX.polar':'Modulus and principal argument; quadrant, nonzero and exact trigonometric constraints.',
 'CPX.conversion':'Convert between Cartesian and modulus-argument forms, including undefined zero argument.',
 'CPX.polar-arithmetic':'Modulus products/quotients, angle sums/differences and principal range.',
 'CPX.loci':'Circles, perpendicular bisectors and argument rays; solve simultaneous simple loci, check boundaries.',
 'MAT.arithmetic':'Conformability, entrywise sums and ordered row-column multiplication.',
 'MAT.scalar':'Entrywise scalar multiplication, linear combinations and area scaling consequences.',
 'MAT.identity':'Conformable zero and identity operations; explain zero products without assuming scalar cancellation.',
 'MAT.transformation':'2D linear transformations, basis images, coordinate mapping and reconstruction.',
 'MAT.composition':'Composition in the stated order and recovery of unknown transformations.',
 'MAT.invariants':'Solve coordinate equations for invariant points and setwise or pointwise invariant lines.',
 'MAT.determinant':'2x2 and 3x3 determinant calculations and parameter-dependent singularity.',
 'MAT.area-scale':'Absolute determinant as area factor; signed determinant and orientation.',
 'MAT.zero-transformation':'Zero determinant, collapsed images and preimages via coordinate equations.',
 'MAT.singular':'Zero/nonzero determinant and implications for products and invertibility.',
 'MAT.inverse-properties':'Inverse identities and ordered product rules for square matrices.',
 'MAT.inverse':'2x2 and 3x3 inverses, matrix equations and inverse-based reconstruction.',
 'MAT.systems':'Two- or three-variable linear equations, unique and nonunique solution sets.',
 'MAT.zero-system':'Singularity and compatibility, solve by elimination and distinguish free parameters.',
 'MAT.geometry-system':'Common point, line, plane or empty intersection; distinguish pairwise from common intersections.',
 'VEC.3d':'Three-dimensional components, displacement, magnitude and unit directions.',
 'VEC.line':'Vector and Cartesian line equations, zero components and parameter recovery.',
 'VEC.plane':'Vector and Cartesian plane forms, independent directions and normals.',
 'VEC.scalar-product':'Dot product, normal-plane equations and smaller-angle conventions.',
 'VEC.perpendicular':'Dot-product orthogonality, nonzero restrictions and parameter equations.',
 'VEC.intersections':'Solve shared-coordinate constraints for line-line and line-plane intersections.',
 'VEC.skew':'Check all coordinates and nonparallel directions; distinguish skew, parallel and intersecting lines.',
 'VEC.distance':'Perpendicular feet, shortest distances and exact distance constraints.',
 'VEC.plane-intersection':'Find a common point and nonzero line direction using both plane equations.',
 'VEC.vector-product':'Ordered two-vector cross product and normals; no vector triple product required.',
 'VEC.vector-properties':'Anticommutativity, distributivity, zero cross products and parallel vectors.',
 'VEC.area-volume':'Cross-product area and scalar triple-product volume, including simple solid ratios.',
}
# These preview designs need explicit teacher judgment or clearer demand wording.
# Do not silently promote an existing preview or call it exam-ready.
WATCH={
 ('factor-connection',3):'Expanding supplied factors alone is prerequisite work, rather than independently demonstrating root-coefficient relationships.',
 ('exact-radians',3):'Pure exact-trigonometric evaluation is mainly assumed prerequisite knowledge, not direct Further Mathematics content.',
 ('exact-radians',5):'Periodic trigonometric equation with inequality is assumed-knowledge demand; direct AS1 Further Mathematics linkage needs confirmation.',
 ('zero-exception',4):'Real rational expression and its excluded value primarily assess prerequisite algebra; the zero-argument part provides a limited link.',
 ('complex-regions',3):'Half-plane inequalities extend the listed simple-locus examples; confirm intended exam scope.',
 ('complex-regions',4):'Region area with strict inequalities extends construction/interpretation of simple loci; confirm intended exam scope.',
 ('complex-regions',5):'Circle and bisector are explicit; strict inequality side-selection is a linked extension, not explicitly specified.',
 ('matrix-add-subtract',5):'Symmetric-matrix terminology and diagonal-sum constraint are not explicitly named in the arithmetic outcomes; define terminology or confirm scope.',
 ('matrix-products',5):'Rectangular ordered products are covered, but one-sided identity behaviour is an extension of ordinary multiplication, not square-matrix inverse content.',
 ('det-three',5):'Rank exactly two is not explicit in the determinant outcomes; allow elementary independent-row reasoning and confirm terminology.',
 ('matrix-equation',5):'Symmetric-matrix terminology is not explicitly named; confirm wording/assumed knowledge while retaining the inverse-equation skill.',
}
ENRICHMENT={
 'angle-units':'Coupled angular congruences and interval periodicity exceed a basic radian conversion.',
 'complex-regions':'Global strict-region extrema and attainment go beyond simple-locus construction.',
 'conjugate-product':'Global rational modulus classification and endpoint analysis extend basic conjugate use.',
 'cross-linearity':'Coupled vector-pair reconstruction with nonlinear equality is extended cross-product demand.',
 'cube-sums':'Implicit cubic range/uniqueness proof (calculus-based solution) exceeds quadratic-root identities.',
 'describe-transform':'Full two-parameter reflection/enlargement classification extends routine 2D transformations.',
 'exact-radians':'Global inverse-trigonometric parameter classification extends basic radian use.',
 'matrix-add-subtract':'Symmetric/skew-symmetric decomposition and uniqueness exceed elementary matrix arithmetic.',
 'matrix-products':'All rectangular right inverses and idempotence are not the specified square-matrix inverse tasks.',
 'polar-quotients':'Global reciprocal complex quotient classification exceeds direct polar multiplication/division.',
 'reciprocal':'General multiset-preserving rational transformation, including repeated and complex roots, exceeds related quadratic construction.',
 'standard-cartesian':'Global rational-map range and inverse classification extend Cartesian arithmetic.',
 'vector-combinations':'Convex combination and full triangle membership classification are extended 3D vector geometry.',
}

def bind(r,path,tier,variant):
    item=r._resolve(path,tier,variant);skill=item['payload']['focus_skill'];concept=skill.rsplit('.',1)[0];page,bullet=OUTCOMES[concept];scope=item['scope']
    if scope=='enrichment_only':
        require(path in ENRICHMENT and tier==6,'Unexpected enrichment');decision='enrichment_isolated';note=ENRICHMENT[path]
    elif tier<=2:decision='bridge_or_diagnostic_only';note='Existing editorial learning role retained; direct individual scope review not asserted.'
    elif (path,tier) in WATCH:decision='scope_confirmation_required';note=WATCH[path,tier]
    elif tier==6:decision='challenge_only';note='Linked advanced task; challenge role retained, not examination selection.'
    else:decision='representative_linked_candidate';note=CONCEPT_METHOD[concept]
    modes=[m for m in MODES if r.eligible(path,tier,m)]
    require('approved_exam' not in modes and item['teacher_approved'] is False,'Unexpected examination approval')
    if scope=='enrichment_only':require(modes==['enrichment_preview'],'Enrichment leakage')
    return {'id':item['id'],'fingerprint':fingerprint(item),'revision':item['revision'],'skill':skill,'scope':scope,'printed_page':page,'page_bullet':bullet,'basis':'prior_learning_role' if tier<=2 else 'representative_prompt_plus_variant_oracle','decision':decision,'note':note,'eligible_preview_modes':modes,'teacher_approved':False,'empirical_calibration':False,'individual_scope_certified':False,'exam_ready':False}

def records(r=None):
    r=Resolver() if r is None else r
    require(set(CONCEPT_METHOD)==set(OUTCOMES),'Outcome coverage mismatch')
    require({p for p in r.bases if r.scope(p,6)=='enrichment_only'}==set(ENRICHMENT),'Enrichment coverage mismatch')
    require(all(r.scope(p,t)=='syllabus_linked_candidate' for p,t in WATCH),'Watch scope mismatch')
    for path in sorted(r.bases):
        for t in range(1,7):
            for v in (1,2,3):yield bind(r,path,t,v)

def validate(rows,r=None):
    r=Resolver() if r is None else r;seen=set();counts=collections.Counter()
    for row in rows:
        _,p,t,v=row['id'].split('.');require(row['id'] not in seen,'Duplicate scope record');seen.add(row['id'])
        require(row==bind(r,p,int(t[1:]),int(v[1:])),'Stale or altered scope record');counts[row['decision']]+=1
    require(len(seen)==2106,'Incomplete scope register')
    return {'items':len(seen),'decisions':dict(counts),'teacher_approved':0,'individual_scope_certified':0,'exam_ready':0}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--validate',type=Path);args=parser.parse_args()
    if args.validate:print(json.dumps(validate([json.loads(x) for x in args.validate.read_text().splitlines() if x.strip()]),indent=2))
    else:
        for row in records():print(json.dumps(row,sort_keys=True))
