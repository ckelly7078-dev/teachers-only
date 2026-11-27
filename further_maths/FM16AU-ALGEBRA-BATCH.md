# FM-16AU — accelerated marking review and remediation

Review related mathematical designs together, independently check each numerical variant, apply reviewed marking improvements immediately, and preserve every changed payload. Do not count shared-design review as individual written-solution certification.

Completed all 14 algebra pathways at tiers 1–4 (56 designs, 168 variants). The AS root-sum-product T3 cell and AF scaled-roots T4 cell remain unchanged. The AU revision layer applies explicitly authored M/A/R requirements to 54 previously untyped cells (162 variants); all 39 AT allocations are now active, with the 12 requested amendments closed editorially. Worked-solution derivations and misconception guidance were also improved where appropriate. Mathematical prompts, exact answers, structured facts, difficulty/scope labels and total marks are unchanged. The per-variant original independent mathematical validators are retained. No teacher approval is granted.

The AU frozen evidence batch covers 165 variants (39 individual AT re-reviews and 126 shared-design-plus-variant-oracle records, including three unchanged AF variants). Together with 12 existing AS individual re-reviews, the current ledger has 177 records: 51 individual re-reviews and 126 shared-design-plus-variant checks; all validate as editorial_review_recorded. This status is provisional and does not imply every variant's prose or rendering was individually certified. The frozen batch digest prevents silently generating review evidence for changed item versions. Preserve historical review records separately. The private inventory has 273 typed provisional active rubrics and 1,833 awaiting explicit types; 1,929 items lack current ledger evidence. Approval and empirical calibration remain separate gates.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_au.py > algebra-au.jsonl
python further_maths/marking_batch.py algebra-au.jsonl
python further_maths/test_marking_design_au.py
python further_maths/test_active_difficulty.py
python further_maths/active_difficulty.py
```

Verification: 32 focused and existing regression tests passed; full active database verification matched 2,106 items; all 35 source hashes checked. Exactly 162 active payloads changed, 276 historical versions retained, and non-audit tables and all other active records preserved. Original 117 skills, 702 difficulty cells and selection counts unchanged; 15 active overlay layers and 92 revised cells. Parent database SHA-256 c2fca1046e895b7a9e8a3a7097a900b128feaaf0e261c528b145ee00d8872364; AU database SHA-256 f6a2838b100aaf30d5e3e51479844750da9880e36f10938a81e0bf236ec54a9d.

Remaining: algebra tiers 5–6 (28 designs, 84 variants), then complex numbers, matrices and vectors in larger topic batches. Allow a design to remain changes_requested if its mathematics, allocation or evidence is unresolved; do not equate automated checking with teacher approval. Direct specification review, rendered mathematics checks, empirical calibration and final integration remain outstanding. Separate historical suites and browser tests not rerun. Private database, migration and examination-source evidence stay offline. No merge or deployment. FM-17 remains gated.
