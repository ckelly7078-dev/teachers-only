# FM-16BA — multi-version history and angle-congruence marking

Complete the three pending FM-16AY angle-units T6 marking amendments. The FM-16BA overlay explicitly succeeds FM-16AD for this one design; other overlapping revisions remain disallowed. The active resolver checks exact predecessor authorisation and rejects unused succession declarations. Historical payload resolution is internal to audit, not a preview selection route. All three variants retain their prompts, answers, mathematical facts, worked solutions, four marks and enrichment-only scope. The new marking criteria explicitly assign M1, R1, A1 and R1. The independent degree-congruence oracle checks the inclusive interval and the stricter half-angle congruence. No teacher approval.

`revision_history.py` provides transactional offline schema upgrade and authorised successor application. It replaces the legacy question-ID-only primary key with `(question_id, revision)`, where `revision` identifies the revision that retired the stored payload. All six historical fields are preserved, including the original SHA-256. The migration requires foreign keys enabled, rejects unexpected schema/dependencies or damaged history hashes, checks that the stored active payload matches the exact authorised predecessor, and archives it before replacing it. The three BA replacements are applied in a single outer transaction. Existing historical records and review evidence are not overwritten.

Review validation now requires a recognised explicit `review_basis` (`individual_item_review`, `individual_item_rereview`, or `shared_design_plus_variant_oracle`). Re-reviews must identify a distinct valid predecessor fingerprint; current records still require the active fingerprint. The three frozen BA individual re-reviews link to their superseded AY review records. Historical AY records remain reproducible against their original AD payloads, but those three records cannot be accepted against the active BA items. Review-basis validation checks evidence structure, not independent human certification or the truth of every editorial judgement. Older source records without a basis remain historical, not valid new review submissions.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_ba.py > angle-ba.jsonl
python further_maths/marking_batch.py angle-ba.jsonl
python further_maths/test_revision_history.py
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 69 regression tests passed, including six targeted tests for migration, rollback, history tampering, exact predecessor authorisation, stale reviews and review basis. The separate isolated source-free run also passed all 69 tests. Full active verification matched 2,106 items. Private preservation checks confirmed all 894 preceding history rows unchanged, three new archived AD payloads, 897 historical hashes valid, exactly three active rubrics amended, 71 other tables unchanged, and all 35 source hashes checked. All 834 current ledger records validate (54 individual re-reviews and 780 shared-design reviews); zero changes requested. All 576 complex-number variants have accepted editorial decisions. Of 2,106 active items, 894 have explicit provisional marking and 1,212 remain untyped; 1,272 lack current ledger evidence. There are 21 overlay layers and 298 distinct revised designs, with 117 skills, 702 designs and selection counts unchanged. Parent private DB SHA-256 86f68052961ecd9e14bb102e15ce70e39e4e54f61dd83c993666dcf0e4a8bc8a; BA DB SHA-256 836a65fa7b895a900adef0406e5bdd13e87422104ccd346763b5356484a44c75.

Next: FM-16BB — accelerated matrix marking review, retaining existing typed rubrics where sound. Direct specification review, rendered mathematics, empirical calibration, teacher approval and integration remain outstanding. No separate historical suites or browser tests rerun. Private database, migration runner and original sources remain offline. No merge or deployment. FM-17 remains gated.
