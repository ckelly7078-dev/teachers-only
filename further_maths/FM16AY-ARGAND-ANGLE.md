# FM-16AY - Argand, radian and modulus/argument marking review

All six tiers and three variants of seven pathways (argand-coordinates, argand-displacement, angle-units, exact-radians, polar-geometry, modulus-constraints, argument-range): 42 designs, 126 variants. New explicit provisional M/A/R rubrics for 39 previously untyped designs (117 variants). Retain AD argument-range T6 and AH modulus-constraints T6 (six already typed variants). Review the three AD angle-units T6 variants, but retain their untyped active payload and proposed allocations as changes_requested: the existing difficulty_revision_history table has one historical row per question ID, so a second revision requires a separately reviewed multi-version history migration. Do not silently replace that row or the AD overlay.

Marking separates labelled Argand plotting and signed coordinates, directed displacement and parallelogram classification, exact angle conversions, half-open angular intervals, trigonometric phase branches, circle chord uniqueness and principal-argument quadrant restrictions. Respect expressly requested geometric and trigonometric methods. Nine worked solutions clarified: absent quadrant II in the parameterised line, geometric half-sum/half-difference construction and the Cartesian proof forcing the nonzero-midpoint chord direction. Prompts, answers, facts, totals, scope and eligibility unchanged. Diagram requirements reviewed as text, not rendered or certified.

Frozen AY evidence batch: 126 shared-design-plus-variant-oracle records (123 editorial_review_recorded, three changes_requested). Previous 510 ledger records unchanged. Combined current ledger: 636 records (633 editorial_review_recorded, three changes_requested; 51 individual re-reviews and 585 shared-design checks). Across complex numbers, 378 of 576 variants reviewed, 375 have accepted editorial review, 198 not yet reviewed. Across all topics: 699 typed provisional rubrics, 1,407 untyped, 1,470 without current ledger evidence. No teacher approval.

Run from repository root with SymPy installed:

```sh
python further_maths/marking_design_ay.py > complex-ay.jsonl
python further_maths/marking_batch.py complex-ay.jsonl
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

Verification: 56 regression tests passed, including a separate isolated source-free run of all 56 tests. Full active database verification matched all 2,106 questions. All 58 original public manifest entries matched. New tests check exact signed coordinates, parallel/perpendicular boundaries, chord endpoints, congruence parity, angular branches, all 126 variant payloads and delimiter structure, pending-review decisions, and frozen evidence rejection on changed versions. Exact 117 active payload changes, all 702 history versions and hashes, 71 other tables unchanged, all 35 source hashes verified. Parent DB SHA-256 e152250745d640d0b110b288cc44e0845cbadb0bfaa62e7287d5b144bbb5c3dc; AY DB SHA-256 1bb78a281312e42d3bdf28baf9a0a09561f0672e31933c64e7876dfe16f0fe3b. 117 skills, 702 designs, 19 overlay layers, 234 revised cells. The approved examination pool is empty.

Keep original sources, private database, migration and ledger offline. Next: remaining polar conversions, zero exception, polar arithmetic and loci (11 pathways, 198 variants) and explicit multi-version history remediation for AD angle-units T6. Direct specification review, individual written-solution and rendering certification, empirical calibration, teacher approval, historical/browser suites and integration remain open. FM-17 stays gated. No merge/deployment.
