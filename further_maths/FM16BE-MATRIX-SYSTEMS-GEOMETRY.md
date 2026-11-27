# FM-16BE: simultaneous equations and geometry marking

Parent checkpoint FM-16BD. Review all six tiers of nine remaining matrix pathways (54 designs, 162 variants): system-consistency, system-classification, nonunique-set, three-plane-unique, two-variable-system, inverse-systems, three-system, inconsistent-geometry and nonunique-geometry. Add provisional design-specific M/A/R marking to 50 previously untyped designs (150 variants). Preserve the four typed advanced designs from AE and AJ. All prompts, answers, solutions, facts, scope and marks are unchanged. All items remain original previews, not approved examinations.

Review distinguishes coefficient and augmented rank, compatibility at singular values, complete parameter families, nonnegative boundary cases, inverse existence and independent solution vectors, unique points versus lines and planes, and pairwise versus common plane intersections. Equivalent valid methods are accepted subject to explicit task constraints; independently demonstrated method credit survives arithmetic slips without awarding incorrect accuracy results.

The frozen batch manifest binds 162 active item fingerprints to the shared-design review. Each variant runs the existing independent fact oracle. New independent tests check homogeneous rank and span, feasible intervals including singleton endpoints, admissibility at negative and singular coefficients, inverse-system independence and distinct compatibility constants, two singular values of a three-variable system, pairwise plane intersections and dimensions of nonunique intersections. This does not constitute individual written-solution or rendered-mathematics certification.

## Verification commands (source-free)

From repository root, with SymPy installed:

```
sha256sum -c further_maths/FM16BE-PUBLIC-SHA256.txt
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/marking_design_be.py > matrix-be.jsonl
python further_maths/marking_batch.py matrix-be.jsonl
python further_maths/active_difficulty.py
```

Expected active counts: 117 skills, 702 designs, 2106 items, 503 distinct revised cells, 1509 typed provisional rubrics, 1479 accepted current editorial reviews, 1512 historical rows (1362 predecessors preserved plus 150 newly archived). All 648 matrix variants now have editorial review. Teacher-approved examination items: zero. Private migration and evidence remain offline. Separate historical suites, browser tests, direct specification review, rendered mathematics, empirical calibration, teacher approval and integration remain outstanding. Next: accelerated vector marking (627 variants without current editorial evidence). No merge or deployment.
