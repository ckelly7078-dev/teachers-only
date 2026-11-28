# FM-17E: structured marking across AS1 topics

This is mathematical knowledge development, not a new review interface. Preserve FM16FINAL as the active bank and FM17D as the private generation/marking adapter. No question, rubric, difficulty tier, guard, database, website or approval change.

## Mathematics Studio qualification architecture (user requirement)

The eventual first-level pathways after entering Mathematics Studio are separate qualifications:

- GCSE Mathematics: Foundation and Higher tiers. Only Foundation is active for now.
- GCSE Further Mathematics: its own standalone GCSE, not a GCSE Mathematics tier. Not active yet.
- A-level Mathematics: a separate A level. Not active yet.
- A-level Further Mathematics: four parts, of which only AS1 is active for now. AS1 must not be placed under A-level Mathematics.

For the present implementation, expose only GCSE Mathematics > Foundation and A-level Further Mathematics > AS1 when navigation is developed. Do not introduce placeholder active courses, conflate qualification/tier/unit IDs, or modify navigation as part of this knowledge-base checkpoint. The AS1 engine remains isolated from the Foundation mathematics data and contract. This note preserves the user's architecture for later Studio integration.

## Private marking contract

Use the existing `Engine.from_bundle(root)` and `marking_context` as in FM-17D. The new `structured_math_fm17e.check_work(engine, item_id, mode=..., item_fingerprint=..., work=...)` supports 16 additional Tier 3 designs (48 variants); the FM17D checker for three designs (nine variants) remains unchanged. The `specifications` function derives field definitions and expected values from the trusted current original prompt, checks the canonical facts, and checks the typed rubric. It is private, not a learner-facing expected-answer API. Use the appropriate checker only for the supported item design and tier. No raw expression evaluation of learner input. Rational observations are strings of at most 12 digits per numerator/denominator; complex pairs are [real, imaginary], polynomial coefficients descend in degree, matrices are row lists, vectors are component lists. A null field means unavailable/unrecognized; it does not mean wrong. Exact field sets and shapes are required. Fields describe observations of working actually present, not information the parser should invent from the question. In particular formula labels assert that the corresponding mathematical operation was observed. An unsupported alternative must be represented as null, not forced into a supported method's incorrect operand shape.

| Design | Observation fields (in rubric order) |
|---|---|
| root-squares | identity_work: [signed sum/product ratio pairs, S_squared_minus_2P]; answer |
| cube-sums | coefficient_ratios: [signed ratio pairs, reported S/P]; identity_work: [S_cubed_minus_3SP, S, P]; answer |
| quadratic-from-roots | identity_work: [x_squared_minus_Sx_plus_P, S, P]; coefficients |
| complex-discriminant | discriminant_work: [b_squared_minus_4ac, a, b, c]; answer: [D, two_distinct_nonreal_conjugates] |
| cartesian-product | expansion: [first complex pair, second complex pair, i_squared_minus_one]; answer pair |
| cartesian-sums | sum pair; difference pair |
| complex-division | rationalisation: [numerator pair, denominator pair, conjugate multiplier pair]; answer pair |
| argument-normalization | full_turn_work: [original pi multiple, signed integer number of full turns added]; answer_pi_multiple |
| det-two | diagonal_products: [main diagonal factors, off-diagonal factors]; answer |
| inverse-two | inverse_work: [diagonal factor pairs, adjugate, reported determinant, divisor used]; answer matrix; verification: [left matrix, right matrix, reported product] |
| composition-order | ordered_factors: [matrix applied second, matrix applied first]; answer matrix |
| matrix-add-subtract | signed_operation: [A, B, -2]; answer matrix |
| scalar-product | component_products: three factor pairs; answer |
| cross-product | component_1; component_2; component_3 |
| vector-combinations | scaled_vectors: [2, u, -3, v]; answer vector |
| zero-cross | cross_product vector; parallel_work: [parallel, signed multiplier, first vector, second vector] |

The checker accepts equivalent monic ratios, swapped scalar factors and term order where commutative, reversed complex multiplication operands, and both orders of inverse verification. Matrix composition is not commutative. For cube sums a correctly observed identity using earlier reported S/P can retain method credit after a wrong ratio calculation. For inverses a correct adjugate and nonzero consistently used determinant can retain method credit after a determinant slip. Correct final accuracy still requires the exact original answer. Conflicting inverse verification and reported inverse remain uncertain. These are limited structured representations, not a general symbolic proof checker or an OCR/handwriting model. No follow-through or partial credit is inferred beyond supported criteria. The result is a proposed mark interval, not a grade, and all approval/release flags remain false.

Run `python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. The private runtime audit covers actual variants, independently recomputes their answers via symbolic/linear algebra, and checks eligible modes, stale fingerprints, correct/wrong/unavailable observations. Preserve all private source records outside Git and web roots. No live engine hookup, deployment, merge, empirical calibration, or teacher approval is claimed.
