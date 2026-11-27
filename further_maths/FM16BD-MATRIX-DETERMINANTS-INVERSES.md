# FM-16BD: determinant, area, collapse and inverse marking

Parent checkpoint FM-16BC. Review all six levels of 12 pathways (72 designs, 216 variants): det-area, orientation, collapse, collapse-parameter, det-three, inverse-two, inverse-three, inverse-product, inverse-identities, singular-condition, det-classification and matrix-equation. Add design-specific provisional M/A/R rubrics to 69 previously untyped designs (207 variants). Preserve the three typed advanced designs from AI, AJ and AP. No changes to prompts, answers, worked solutions, facts, scope or marks. All items remain original previews, not approved examinations.

Review focuses on determinant signs versus unsigned area, composition order, exact boundary counts, rank-one versus zero maps, image and kernel completeness, cofactor signs, determinant-preserving row operations, inverse order and existence, singular homogeneous solutions, commutation and exhaustive parameter classifications. Equivalent valid methods are accepted subject to explicit question constraints; independent method/reasoning credit is retained after arithmetic slips without awarding incorrect accuracy results.

The frozen batch manifest binds the 216 current item fingerprints to the shared design review. Each variant runs its original independent fact oracle. New tests independently check absolute-determinant thresholds, repeated-root collapse and nullspace, rank of three-by-three matrices, singular triangular inverse cases, commutation and zero-product distinctions. Review is not individual written-solution/rendered-mathematics certification or teacher approval.

## Verification commands (source-free)

From repository root, after installing SymPy:

```
sha256sum -c further_maths/FM16BD-PUBLIC-SHA256.txt
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/marking_design_bd.py > matrix-bd.jsonl
python further_maths/marking_batch.py matrix-bd.jsonl
python further_maths/active_difficulty.py
```

Private database migration and evidence remain offline. Expected active counts: 117 skills, 702 designs, 2106 items, 453 distinct revised cells, 1359 typed provisional rubrics, 1317 accepted current editorial reviews, 1362 historical rows (1155 predecessors preserved plus 207 newly archived). Teacher-approved examination items: zero. No merge or deployment. Separate historical suites, browser tests, direct specification review, rendered mathematics, empirical calibration and teacher approval remain outstanding. Next: nine remaining matrix system/geometry pathways (162 variants), then vector marking.
