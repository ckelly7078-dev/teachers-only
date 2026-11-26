# FM-16AS — pilot marking amendments and re-review

Apply the twelve FM-16AR pilot allocations as provisional M1/A1 criteria, with explicit equivalent methods, method credit after arithmetic slips and exact-answer accuracy. Root sum/product now rewards both signed coefficient ratios rather than merely identifying coefficients. The determinant misconception removes the irrelevant squared-parameter warning. The twelve prompts, facts, worked solutions, final answers and mark totals are unchanged.

All twelve revised items have fresh, frozen fingerprints in marking_rereview_as.py. The six previously requested amendments are closed editorially; all twelve records validate as editorial_review_recorded. Historical AR evidence is retained and rejected as stale for active versions. No teacher approval is granted. Re-review checks text, not rendered mathematics.

Verification: five re-review tests, six resolver tests, eight marking-framework tests and nine batch tests passed. Full active database verification passed for all 2,106 questions; 35 source hashes verified. Twelve active payloads changed, all other payloads and non-audit tables preserved, and 114 historical versions retained. Scope and preview eligibility unchanged. The resolver has 14 overlay layers and 38 revised cells, including four marking-only cells. Of 2,106 items, 111 have typed provisional rubrics, 1,995 still need type review, and 2,094 lack item-specific editorial marking-review records. Approved exam pool remains empty. Parent database SHA-256 65aab46b6d51f8dbf89d745395f89edb1a04c8f5168b5be94d3a07b8abbf02b7; new database SHA-256 c2fca1046e895b7a9e8a3a7097a900b128feaaf0e261c528b145ee00d8872364.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_rereview_as.py > rereviews.jsonl
python further_maths/marking_batch.py rereviews.jsonl
python further_maths/test_marking_rereview_as.py
python further_maths/test_active_difficulty.py
python further_maths/active_difficulty.py
```

Private database, original sources and migration remain offline. Historical suites and browser tests not rerun; comprehensive marking and direct specification review, rendering, empirical calibration and teacher approval remain open. No merge, deployment or website integration. Next: FM-16AT — expand evidence-backed marking review in larger topic batches, preserving per-item decisions. FM-17 remains gated.
