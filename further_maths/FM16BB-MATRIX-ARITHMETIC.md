# FM-16BB — matrix arithmetic and two-by-two determinants

Reviewed 42 designs and 126 variants across seven pathways: matrix-conformability, matrix-add-subtract, matrix-products, scalar-matrix, identity-operations, zero-matrix and det-two. Added explicit provisional M/A/R criteria to 40 previously untyped designs (120 variants). Existing AS det-two T3 individual evidence and AI det-two T6 rubric retained. Criteria cover conformability, ordered integer factor pairs, symmetric/skew decomposition, one-sided inverses, idempotence, zero and singular cases, signed determinants and proof of exhaustion. Equivalent valid methods and consequential-error guidance retained. Prompts, answers, worked solutions, structured facts, scope labels and mark totals unchanged.

Representative design and worked-solution review, every variant prompt/answer inspected, independent exact-fact validation and structural delimiter checks. No claim of individual written-solution or rendered mathematics certification. The new frozen ledger contains 123 records; the combined ledger validates 957 unique accepted editorial records (54 individual re-reviews, 903 shared-design-plus-variant-oracle). All 126 selected matrix variants have current editorial evidence including the three existing AS items. Across AS1: 1,014 typed provisional rubrics, 1,092 untyped; 1,149 lack current ledger evidence. Approved examination pool remains empty.

Run from repository root with SymPy:

    python further_maths/marking_design_bb.py > matrix-bb.jsonl
    python further_maths/marking_batch.py matrix-bb.jsonl
    python -m unittest discover -s further_maths
    python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite

Verification: 75 regression tests passed and 75 passed separately in a source-free copy. Full active database comparison matched all 2,106 items; all 35 source hashes verified. Exactly 120 active payloads changed, rubric only; 897 predecessor historical rows preserved, 1,017 total history records with hashes verified. All 71 other tables unchanged, schema unchanged, SQLite integrity and foreign keys passed. 117 skills, 702 designs, 338 active revised cells; scope and eligibility counts unchanged. Parent DB SHA-256 836a65fa7b895a900adef0406e5bdd13e87422104ccd346763b5356484a44c75; new DB SHA-256 e0d0b10f4bf6587ba1719387e5d9414c5b95f4a5bd3829c3abd147ade8456596.

Next: FM-16BC — matrix transformations, composition and invariants; then remaining determinant, inverse and systems work. Direct specification review, rendered mathematics, empirical calibration, teacher approval and final integration remain outstanding. Separate historical suites and browser tests not rerun. Private database, migration and original sources stay offline. No merge or deployment. FM-17 remains gated.
