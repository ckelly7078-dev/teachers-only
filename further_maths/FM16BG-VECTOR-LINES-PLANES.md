# FM-16BG — vector lines, planes, normals and angles

Parent: FM-16BF. Eleven pathways, 66 shared mathematical designs and 198 numerical variants: vector line equations, Cartesian line equations, zero direction components, vector planes, Cartesian planes, plane normals, cross-product normals, scalar-product plane equations, and line-line, plane-plane and line-plane angles. Amends 65 designs (195 active payloads); retains the three FM-16AO advanced line-plane-angle variants. All 198 receive new shared-design-plus-variant-oracle records. The original ordered, variant-specific criterion text is retained verbatim and extended with a provisional M/A/R type and appropriate credit guidance. No changes to prompts, answers, solutions, facts, total marks, scope or difficulty classification.

Review checks include coincident-point perpendicular line families, constant coordinate restrictions and zero direction, degenerate plane spans, normal-component restrictions, orientation reversal across cross-product degeneracy, unit-normal plane counting with opposite normals identified, degree changes and discriminant endpoints in line-angle equations, absolute cosine branches for plane angles and strict feasibility of simultaneous line-plane angle constraints. Eleven new tests cover structural preservation, frozen evidence, invalid targets and independent symbolic boundary checks. Equivalent methods and consequential errors are handled without automatic accuracy credit for incorrect results.

Run from repository root:

```
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/marking_design_bg.py > bg-review.jsonl
python further_maths/marking_batch.py bg-review.jsonl
python further_maths/active_difficulty.py
# Optional private copy only:
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Private migration appends 195 predecessor rows, preserves 1,680 earlier historical records and extends the current ledger from 1,656 to 1,854 records. The bank remains 117 skills, 702 designs, 2,106 variants and zero teacher approvals. Remaining vector pathways: intersections, skewness, distances, common plane intersection lines, areas and volumes (14 pathways, 252 variants). Shared-design review is not individual written-solution or rendered mathematics certification. Direct specification review, empirical calibration, teacher approval and FM-17 integration remain gated. Private database, source materials and review ledger remain offline. No merge or deployment.
