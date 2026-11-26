# FM-16AR — evidence-backed marking pilot and batch workflow

Inspected all three level-three variants of four original pathways: root-sum-product, cartesian-product, det-two and scalar-product. All twelve stored answers and worked calculations are mathematically correct. Six records (Cartesian multiplication and scalar product) have editorial review recorded; six request changes. Root sum/product needs a substantive method criterion rather than merely identifying coefficients; determinant misconception guidance includes an unrelated squared-parameter error. Each record proposes M1/A1 with exact per-item evidence, alternative methods, consequential-error guidance and a boundary-case decision. Text and delimiters inspected, not rendered. No active rubric or question changes and no teacher approval.

`marking_pilot_ar.py` preserves the inspected arithmetic and frozen version fingerprints. `marking_batch.py` reads JSON Lines, rejects duplicate item IDs or JSON keys, unknown IDs, stale fingerprints, unsupported approval, incomplete evidence and invalid allocations. Existing typed allocations cannot change without a revise decision. Validation returns decisions without modifying the bank; it does not prove the evidence true or authenticate a reviewer.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_pilot_ar.py > pilot.jsonl
python further_maths/marking_batch.py pilot.jsonl
python further_maths/test_marking_batch.py
python further_maths/test_marking_review.py
python further_maths/test_active_difficulty.py
```

Nine batch tests, eight marking-framework tests and six resolver tests passed. A mistyped pilot fingerprint was initially rejected and corrected against the frozen inventory. The batch accepted twelve records: six editorial_review_recorded and six changes_requested. All 2,106 inventory entries were independently reconstructed from the read-only stored payloads and matched; all 35 source hashes checked; integrity and foreign keys passed. The database is unchanged (SHA-256 65aab46b6d51f8dbf89d745395f89edb1a04c8f5168b5be94d3a07b8abbf02b7). The preceding full symbolic verification still applies to the unchanged bank and resolver; it was not rerun. 102 historical versions retained, 99 typed provisional rubrics, 2,007 untyped. Pilot decisions do not alter these counts. 2,094 items have no pilot review record; six more need amendments and re-review. No browser or historical suites rerun, teacher approval, empirical calibration, direct specification review or live integration.

Next: FM-16AS — implement the pilot amendments and explicit provisional marking allocations, with version history and re-review; then extend batch marking across all four topics. Private database and source evidence stay offline. No merge or deployment. FM-17 remains gated.
