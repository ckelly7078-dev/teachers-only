# FM-16BC — matrix transformations, composition and invariants

Reviewed 48 designs and 144 variants across eight pathways: basis-images, describe-transform, figure-images, composition-order, composition-compute, fixed-points, invariant-lines and fixed-invariant. Added explicit provisional M/A/R criteria to 46 previously untyped designs (138 variants); retained the AE composition-order T6 and AI invariant-lines T6 rubrics. Criteria address composition order, dependent basis inputs, singular line images, fixed-point kernels, onto versus pointwise invariance, reflection-axis exceptions and exhaustive parameter classification. Equivalent valid methods and consequential-error guidance retained. Prompts, answers, worked solutions, structured facts, scope and mark totals unchanged.

Representative design and worked-solution review, variant prompts and answers inspected, independent exact-fact validation and structural delimiter checks. No claim of individual written-solution or rendered mathematics certification. The frozen ledger contains 144 new records; combined ledger validates 1,101 accepted editorial records (54 individual re-reviews, 1,047 shared-design-plus-variant-oracle). Across AS1: 1,152 typed provisional rubrics, 954 untyped; 1,005 lack current ledger evidence. Matrix ledger coverage 270 of 648. Approved examination pool remains empty.

Run from repository root with SymPy:

    python further_maths/marking_design_bc.py > matrix-bc.jsonl
    python further_maths/marking_batch.py matrix-bc.jsonl
    python -m unittest discover -s further_maths
    python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite

Verification: 82 regression tests passed and 82 passed separately in a source-free copy. Full active database comparison matched all 2,106 items; 35 source hashes verified. Exactly 138 payloads changed, rubric only; 1,017 predecessor historical rows preserved, 1,155 total history records with hashes verified. All 71 other tables unchanged, schema unchanged, SQLite integrity and foreign keys passed. 117 skills, 702 designs, 384 active revised cells; scope and eligibility counts unchanged. Parent DB SHA-256 e0d0b10f4bf6587ba1719387e5d9414c5b95f4a5bd3829c3abd147ade8456596; new DB SHA-256 574a23bdb61a181b6c0b2fe2424ed17adf732679b0f92c9b0ddc8bfe6be4f599.

Next: FM-16BD — remaining determinant, area/orientation, singularity and inverse pathways; then simultaneous-equation systems. Direct specification review, rendered mathematics, empirical calibration, teacher approval and final integration remain outstanding. Separate historical suites and browser tests not rerun. Private database, migration and original sources stay offline. No merge or deployment. FM-17 remains gated.
