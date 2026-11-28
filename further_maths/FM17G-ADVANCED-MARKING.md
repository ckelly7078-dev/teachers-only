# FM-17G: polynomial division, systems and three-dimensional geometry

FM-16FINAL remains the authoritative mathematical snapshot. This checkpoint adds exact structured observations for 22 Tier 3 designs, 66 original variants. Combined with FM-17D/E/F, the supported set is 65 designs and 195 variants. All other items retain the provisional marking context. No canonical question, rubric, mark, difficulty tier, scope guard or historical record changes.

## Private engine contract

Use `Engine.from_bundle(checkpoint_root)` as before. The unified private dispatcher selects the supported checker without requiring the consuming backend to know its checkpoint:

```python
from marking_dispatch_fm17g import capability, check_work, supported_designs
info = capability(engine, item_id, mode=mode, item_fingerprint=fingerprint)
if info['structured_checks_available']:
    proposal = check_work(engine, item_id, mode=mode,
                          item_fingerprint=fingerprint, work=observations)
```

Capability validates current item identity and preview eligibility. It does not disclose answers or approve a grade. Unsupported designs or tiers reject exact marking and retain their existing rubric context. `structured_math_fm17g.specifications(item)` provides private reference fields, not a learner-facing parser or answer payload. All accepted quantities are bounded rational strings; operation labels are fixed, and null denotes unsupported or unavailable evidence. The `signed_area_square`, `signed_distance_square` and `signed_root_squares` fields encode an exact real value as its sign and rational square. They must not be populated by rounding an approximate learner result. The degree field is the requested one-decimal-place angle value, not radians.

Division fields contain divisor coefficients, padded dividend coefficients, the quotient-term coefficient and the reduced dividend in descending powers. Reductions are checked separately against the submitted preceding reduction, with missing predecessor evidence remaining uncertain. The complete quotient, zero remainder and root set remain tied to the original question. The supported quadratic-method field checks signed discriminant, denominator and use of both branches; other valid methods must be represented as null. For simultaneous systems, an elimination observation contains coefficients of a linear combination of original equations and its resulting augmented row, and must actually eliminate a contributing variable. The single-variable stage must isolate exactly one variable. The inverse-three complete elimination field verifies an explicit matrix of row-combination coefficients applied to the original augmented matrix. Verification checks do not automatically certify a contradictory reported answer.

For geometry, nonzero proportional plane directions are equivalent, but a zero vector is not a direction. Cross-product reversal and permutations of scalar triple product inputs are permitted where the magnitude, rather than signed orientation, is assessed. Correct sign is required for exact distances and areas. Independent checks reconstruct polynomial roots, substitute systems, project perpendicular feet, use Gram determinants for areas, and use atan2 for the smaller angle. The source-specific CCEA marking evidence remains separate from provisional original rubrics.

## Boundaries and verification

Run `python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'`. The private audits test the actual final snapshot, independent answers, criterion-level errors/uncertainty, mode eligibility, stale fingerprints, and the unified availability contract. This is not unrestricted handwriting or free-text interpretation; an external trusted parser or reviewer must supply the observations. Unrecognized methods remain uncertain. No official mark, teacher approval, live engine integration, or empirical calibration is asserted. The existing qualification hierarchy remains unchanged; only Foundation GCSE Mathematics and AS1 A-level Further Mathematics are active. No portal, navigation, Foundation, merge or deployment changes. Keep all private database and source evidence outside Git and web roots.
