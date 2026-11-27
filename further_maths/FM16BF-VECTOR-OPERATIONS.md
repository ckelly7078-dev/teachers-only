# FM-16BF — foundational vector operations and products

Parent: FM-16BE. Covers 10 pathways, 60 shared mathematical designs and 180 numerical variants: component notation, combinations, unit vectors, scalar product, perpendicularity tests and parameters, cross product, order, linearity and zero cross products. Amends 56 designs (168 active payloads), retaining 12 existing typed variants from AS, AO and AK. Three AS individual reviews remain current; 177 new shared-design-plus-variant-oracle records extend the ledger to 1,656. Every affected rubric preserves criterion count and total marks; no prompt, answer, solution, facts or scope changes.

Representative design reviews and independent exact-fact oracles support provisional M/A/R allocations. Boundary checks include fixed-coordinate distance intersections, convex combinations on edges and vertices, unit-sphere tangency, zero-vector exclusions, cross-product compatibility, minimum length and equal-length solution families. Existing advanced rubrics remain unchanged. The frozen batch fingerprint prevents automatic acceptance of subsequent changes. Equivalent methods and consequential errors are treated explicitly.

Run from the repository root:

```
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/marking_design_bf.py > bf-review.jsonl
python further_maths/marking_batch.py bf-review.jsonl
python further_maths/active_difficulty.py
# Optional private copy only:
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Historical audit: 168 predecessor payloads appended, preserving all 1,512 existing rows. Private database, source material, current ledger and migration evidence remain offline. The active bank remains 117 skills, 702 designs, 2,106 variants and zero teacher approvals. Remaining vector pathways: equations and geometry of lines and planes, angles, intersections, skewness, distances, normals and areas/volumes (25 pathways, 450 variants). Shared-design review is not individual written-solution or rendered-mathematics certification. Direct specification review, empirical calibration, teacher approval and FM-17 integration remain gated; no merge or deployment.
