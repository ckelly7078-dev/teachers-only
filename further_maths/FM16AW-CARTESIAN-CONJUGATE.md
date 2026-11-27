# FM-16AW — Cartesian and conjugate marking review and remediation

Seven complex-number pathways (identify-components, standard-cartesian, cartesian-sums, cartesian-product, complex-division, conjugate-find, conjugate-product), all six tiers and three variants: 42 designs, 126 variants. Apply explicit provisional M/A/R criteria to 36 previously untyped designs (108 variants); preserve all six previously typed designs, including the three individual AS reviews. Design-specific criteria address signed components, exact Cartesian forms, nonzero denominators, both sign branches, ray conditions, singular systems and proof of completeness. Clarify the squared quotient's reduced/unreduced representation, bracket expansion notation, conjugate-product misconception and distinct signed roots. Prompts, exact answers, structured facts, mark totals and difficulty/scope classifications remain unchanged. Enrichment-only conjugate-product and standard-cartesian T6 remain enrichment-only.

The new frozen ledger covers 123 shared-design-plus-variant-oracle records; combined current ledger 384 (51 individual re-reviews and 333 shared-design checks). All 126 variants in the seven pathways have typed provisional rubrics and current ledger evidence. Across AS1: 459 typed provisional, 1647 untyped; 1722 without current ledger evidence. No teacher approval, official mark-scheme claim or individual written-solution/render certification.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_aw.py > complex-aw.jsonl
python further_maths/marking_batch.py complex-aw.jsonl
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 42 tests passed, full active database verification matched all 2106 items; 35 source hashes and 58 original public manifest entries matched. Exactly 108 stored payloads changed, 462 historical versions and their hashes retained, 71 other database tables unchanged, previous audit metadata retained. 117 skills, 702 designs, 17 overlays, 154 revised cells; preview scope and approval counts unchanged. Parent DB SHA-256 a25a31a464eee33af40517fedda2fabc23d42a5eff0fb725d9a2846f8846484b; AW DB SHA-256 3c595baf0934ac63e338278f2ff64e77d94e000e1a9f26c325aee605e39c814e.

Publication baseline: feature/further-maths-as1-kb at 1e17c312d4a199e4694c1c491c85a3d183042afc. This screened update is prepared locally, not yet committed. Do not publish the private archive, ledger, migration or exam sources. No merge/deployment. Next: continue complex polynomial roots, Argand/radians/polar and loci reviews in large related-design batches; 25 complex pathways (450 variants) remain outside the AW seven-pathway batch. Direct specification review, rendering, empirical calibration, teacher approval, browser/historical suites and integration remain outstanding. FM-17 stays gated.
