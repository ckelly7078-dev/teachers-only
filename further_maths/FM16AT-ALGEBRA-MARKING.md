# FM-16AT — algebra level-three marking review

Inspected all three variants of the 13 remaining further-algebra level-three pathways (39 original items), completing initial item-level marking review for all 42 algebra T3 items including the three root-sum-product items amended in AS. All 39 answers and worked numerical calculations agree with the reviewed prompts. This is an AI editorial review, not teacher approval or an official mark scheme.

The frozen review module records 27 editorial_review_recorded decisions and 12 changes_requested decisions. Factor-connection: remove irrelevant monic-root-formula misconception guidance. Reciprocal: require actual reciprocal transformation method and explain nonzero denominators. Root-squares: require the square-sum identity for method credit and remove unrelated negative-root-sum warning. Shifted-roots: show both transformed invariants and require a substantive method criterion. Each record includes individual arithmetic, proposed allocation, alternate methods, consequential-error guidance and domain checks. Text inspected, not rendered. No active question or rubric changed.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_algebra_at.py > algebra-at.jsonl
python further_maths/marking_batch.py algebra-at.jsonl
```

Validation: 39 new records accepted; combined current ledger with AS re-reviews accepted 51 unique records (39 editorial_review_recorded, 12 changes_requested). Nine batch, eight framework, five AS re-review and six resolver tests passed. All 2,106 stored inventory fingerprints and metadata matched, SQLite integrity and foreign keys passed, and 35 source hashes verified. Database SHA-256 unchanged: c2fca1046e895b7a9e8a3a7097a900b128feaaf0e261c528b145ee00d8872364. Prior full symbolic verification applies to the unchanged bank and resolver; not rerun. 114 historical versions retained; 111 typed provisional active rubrics, 1,995 untyped, 2,055 items without current item-specific review; zero teacher approvals. Proposed allocations are not active rubric changes. Private ledger and database stay offline. No merge, deployment or website integration. Remaining gates include comprehensive marking, written-solution rendering, direct specification review and empirical calibration. Next: FM-16AU — apply the 39 algebra T3 allocations, remedy the 12 flagged items, preserve versions and re-review before extending to other tiers. FM-17 remains gated.
