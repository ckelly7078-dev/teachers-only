# FM-16AX - complex polynomial marking review and remediation

All six tiers and three variants of seven pathways (complex-discriminant, complex-quadratic, conjugate-deduction, conjugate-factor, solve-cubic, solve-quartic and verify-roots): 42 designs and 126 variants. Add explicit provisional M/A/R criteria to 41 previously untyped designs (123 variants). Preserve the three AH conjugate-factor T6 variants and their typed criteria. Separate method credit in polynomial division, exact roots and coefficients, conjugate-root hypotheses, multiplicity, common-factor collision, discriminant boundaries and completeness. Respect the explicitly required methods while accepting equivalent valid forms and independent method/reasoning credit after arithmetic errors. Clarify worked solutions in 15 variants across five designs: discriminant calculation, quadratic formula, shifted-quadratic invariant verification, exact conjugate multiplicity proof and signed numerical substitution. Prompts, final answers, structured facts, total marks, scope and eligibility remain unchanged.

Frozen AX batch: 126 shared-design-plus-variant-oracle records. The 384 preceding AW ledger records remain unchanged. Current ledger: 510 records (51 individual re-reviews, 459 shared-design checks); 582 typed provisional rubrics, 1,524 untyped, 1,596 items without current marking evidence. Across complex numbers, 252 of 576 variants have current review evidence. This is provisional editorial review, not individual written-solution certification, rendered mathematics certification, official CCEA marking or teacher approval.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_ax.py > complex-ax.jsonl
python further_maths/marking_batch.py complex-ax.jsonl
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 49 focused/regression tests passed; full active verification matched all 2,106 items. Additional boundary checks independently computed root multiplicities for all three variants of cubic, quartic and retained AH conjugate-factor challenges. Exactly 123 active payloads changed, all 585 historical versions and their hashes preserved, all 71 other tables unchanged, audit metadata retained, all 35 source hashes and 58 original public manifest entries matched. 117 skills, 702 designs, 18 overlays, 195 revised cells. Approved examination pool remains empty. Parent DB SHA-256 3c595baf0934ac63e338278f2ff64e77d94e000e1a9f26c325aee605e39c814e; AX DB SHA-256 e152250745d640d0b110b288cc44e0845cbadb0bfaa62e7287d5b144bbb5c3dc.

Publication: the cumulative public package includes AW and AX changes against FM-16AV (1e17c312d4a199e4694c1c491c85a3d183042afc). FM16AW-PUBLIC-SHA256.txt is a historical manifest for the AW snapshot, not a checksum assertion for the later AX resolver and resolver test. Check the cumulative AX manifest for current publication. Private databases, migrations, original exam sources and private ledgers remain offline. No merge/deployment. Next: review Argand diagrams, radians, modulus/argument and the remaining complex pathways in large related-design batches. Eighteen complex pathways (324 variants) remain. Direct specification review, rendering, empirical calibration, teacher approval, historical/browser suites and integration remain open. FM-17 stays gated.
