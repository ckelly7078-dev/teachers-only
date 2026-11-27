# FM-16AZ — polar conversion, arithmetic and complex locus marking

Review all 11 remaining complex-number pathways at tiers 1–6 (66 designs, 198 variants). The AZ overlay adds explicit provisional M/A/R requirements to 64 previously untyped designs (192 variants). The existing FM-16AG cartesian-to-polar T4 and FM-16AN polar-products T5 cells (six variants) remain unchanged. Criteria address positive moduli, quadrant correction, exact angle congruences, nonzero denominators, excluded zero arguments and ray endpoints, tangencies, strict region inequalities, degeneracy and completeness. Alternative valid methods and appropriate method/reasoning credit after arithmetic slips are supported. No teacher approval.

Eighteen worked solutions are strengthened, including polar conversions, normalization, numerator uniqueness, labelled half-plane sketch instructions and bisector classification. Six final-answer texts are extended without changing earlier results: complex-regions T4 now states arc/diameter boundary membership; polar-quotients T6 includes the repeated-root polar data and explicit exterior root moduli and arguments. All question prompts, structured facts, mark totals and scope classifications are preserved.

The frozen AZ batch contains 198 shared-design-plus-variant-oracle records. All 576 complex-number variants now have current ledger decisions (573 accepted editorially and three FM-16AY angle-units T6 changes requested). Of the total 2,106 items, 891 have explicit provisional marking, 1,215 remain untyped, 834 have current ledger evidence (51 individual re-reviews, 783 shared-design reviews; 831 editorial_review_recorded, three changes_requested), and 1,272 lack current ledger evidence. Shared-design review plus exact-fact validation does not certify every individual written solution or rendered diagram. Approved exam pool remains empty.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_az.py > polar-loci-az.jsonl
python further_maths/marking_batch.py polar-loci-az.jsonl
python further_maths/test_marking_design_az.py
python further_maths/test_active_difficulty.py
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 63 regression tests passed in the working source-free tree and separately in an isolated copy. Initial test-code errors involving negative integer exponent parity and SymPy Boolean counting were corrected. Full active verification matched all 2,106 questions. Private migration and preservation comparison confirmed exactly 192 changed payloads, 894 historical item versions and their hashes, 71 other tables unchanged, all 35 source hashes checked, and 834 current review fingerprints and decisions validated. 20 overlay layers and 298 revised cells; 117 skills, 702 designs and selection counts unchanged. Parent private DB SHA-256 1bb78a281312e42d3bdf28baf9a0a09561f0672e31933c64e7876dfe16f0fe3b; AZ DB SHA-256 86f68052961ecd9e14bb102e15ce70e39e4e54f61dd83c993666dcf0e4a8bc8a.

Next: FM-16BA — safely design and test multi-version history and explicit overlay succession to resolve the three outstanding AD angle-units T6 marking allocations without losing earlier payloads or evidence; then accelerate matrix marking. Review-basis validation should distinguish individual and shared-design evidence. Direct specification review, rendered mathematics, empirical calibration, teacher approval and final integration remain outstanding. No separate historical suites or browser tests rerun. Private database, migration and original sources remain offline. No merge or deployment. FM-17 remains gated.
