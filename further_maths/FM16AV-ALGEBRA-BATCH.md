# FM-16AV — complete further-algebra design-level marking review

Complete all 14 further-algebra pathways at tiers 5–6 (28 designs, 84 variants), combining review and remediation. Explicit M/A/R requirements added to 26 previously untyped designs (78 variants); the two AF tier-six designs (reciprocal and root-squares, six variants) are retained. The marking criteria distinguish method, accuracy, reasoning, signs, real-root feasibility, zero denominators, repeated roots and exhaustive branch counts. Equivalent valid methods are accepted. The inverse-and-translate solution now supplies both invariants; shifted-root solution guidance and punctuation in the symmetric-parameter solutions are clarified. All prompts, exact answers, structured facts, scope classifications and total marks remain unchanged. Cube-sums and reciprocal T6 remain enrichment-only.

Every advanced algebra variant passed the independent existing structured mathematical validator and structural presentation checks. The frozen AV evidence batch contains 84 shared-design-plus-variant-oracle reviews; the combined current ledger validates 261 unique editorial_review_recorded entries (51 individual re-reviews and 210 shared-design-plus-variant checks). All 252 algebra variants now have typed provisional criteria and ledger evidence, plus three individually reviewed variants in each of complex numbers, matrices and vectors. Across all AS1 topics: 351 typed provisional active rubrics, 1,755 untyped; 1,845 items lack current ledger evidence. No teacher approval or certification of every written solution or rendered question.

Run with SymPy installed from repository root:

```sh
python further_maths/marking_design_av.py > algebra-av.jsonl
python further_maths/marking_batch.py algebra-av.jsonl
python further_maths/test_marking_design_av.py
python further_maths/test_active_difficulty.py
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 36 focused and regression tests passed, including a separate run of all 36 in the source-free package. Full active database verification matched all 2,106 questions, all 35 original source hashes checked, 78 changed payloads, 354 historical item versions retained. Other active payloads, non-audit tables, mark totals, 117 skills, 702 designs, scope and eligibility counts unchanged. 16 overlay layers, 118 revised cells. Approved examination pool remains empty. Parent private DB SHA-256 f6a2838b100aaf30d5e3e51479844750da9880e36f10938a81e0bf236ec54a9d; AV DB SHA-256 a25a31a464eee33af40517fedda2fabc23d42a5eff0fb725d9a2846f8846484b.

Next: FM-16AW — complex-number marking review/remediation, in large shared-design batches with independent variant validation. Direct specification review, rendering, empirical calibration, teacher approval and final integration remain outstanding. Separate historical suites and browser tests not rerun. Private database, migration and original source evidence remain offline. No merge or deployment. FM-17 remains gated.
