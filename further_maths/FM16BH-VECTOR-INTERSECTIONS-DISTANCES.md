# FM-16BH — final vector marking review

Parent: FM-16BG. Fourteen pathways, 84 shared mathematical designs and 252 numerical variants: point-line distance, skew lines, line-plane intersections, point-plane distance, line-line distance, triangle area, triple-product volume, line intersections, plane intersection direction, parallelogram area, common plane points, related solids, plane intersection lines and proof of skewness. Amends 78 designs (234 active payloads), retaining all six previously typed advanced designs (18 variants). Original variant-specific rubric criteria are retained verbatim and extended with provisional M/A/R types and credit guidance. All questions, answers, worked solutions, facts, mark totals and scope remain unchanged.

Independent exact-fact validators and representative mathematical review cover perpendicular feet, orthogonal decomposition, unique minima, signed and unsigned products, degeneracy, exceptional parameter branches, complete intersection families, projection consistency, and closed-interval volume extrema. Twelve new tests cover frozen evidence, preservation and symbolic boundary checks. Shared-design plus variant-oracle evidence is not individual written-solution or rendered mathematics certification.

Run from repository root:

```
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/marking_design_bh.py > bh-review.jsonl
python further_maths/marking_batch.py bh-review.jsonl
python further_maths/active_difficulty.py
# Optional private copy only:
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

The offline migration appends 234 predecessor rows, retaining 1,875 prior historical versions; current ledger increases from 1,854 to 2,106. All 117 pathways, 702 designs and 2,106 active variants now have typed provisional rubrics and current accepted editorial evidence (54 individual re-reviews, 2,052 shared-design plus variant-oracle records). No teacher approval is implied. Direct specification review, individual written-solution and rendered mathematics review, empirical difficulty calibration, teacher approval and integration remain outstanding. FM-17 remains gated. Private materials stay offline; no merge or deployment.
