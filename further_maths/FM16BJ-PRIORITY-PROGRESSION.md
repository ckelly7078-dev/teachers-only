# FM-16BJ — priority difficulty remediation and equal-mark review

Parent: FM-16BI. Ten shared designs (30 numerical variants) have new original successor payloads, with explicit predecessor and mark-total authorisations. All question IDs, focus skills, tiers, original provenance, eligibility scopes and teacher-pending status are retained. The eleventh priority transition (solve-cubic T3 to T4) is retained for the distinction between supplied linear-factor division and forced conjugate-factor deduction.

| Path | Tier | Previous marks | New marks |
|---|---:|---:|---:|
| angle-units | 5 | 2 | 3 |
| argument-range | 5 | 2 | 5 |
| cartesian-to-polar | 5 | 3 | 5 |
| complex-division | 5 | 2 | 6 |
| conjugate-product | 4 | 2 | 5 |
| inverse-systems | 5 | 3 | 6 |
| related-solids | 5 | 2 | 6 |
| solve-cubic | 5 | 3 | 6 |
| solve-quartic | 5 | 3 | 7 |
| vector-plane | 5 | 3 | 6 |

Seven designs have stronger tasks, two polynomial designs have strengthened solutions and allocations, and one mixed-unit enumeration design has a separate allocation for each required stage. The new exact-fact oracle independently checks all successor variants. Historical evidence remains available using the explicit BH historical resolver, which cannot select questions. Earlier frozen review generators and tests for the affected batches use that view. The authorised migration archives each exact predecessor before updating both payload and marks atomically. The previous ledger entries are retained privately and new evidence is bound to the new fingerprints.

All 233 original equal-mark transitions were compared using representative prompts: 96 assessment-role contrasts, 112 plausible linked-demand progressions, 14 demand-review flags, and 11 allocation-review flags. The ten next-tier transitions affected by the successors were separately compared; seven need further allocation or demand review, while three retain plausible progression. Evidence is editorial, not empirical. The 25 new equal-mark flags and seven neighbour flags enter the next remediation queue. No assumption is made that more marks necessarily mean more difficulty. The earlier private review notes and updated screen stay offline.

Source-free commands:

```
python further_maths/test_marking_design_bj.py
python further_maths/test_progression_review_bj.py
python -m unittest discover -s further_maths -p 'test_*.py'
python further_maths/active_difficulty.py
python further_maths/consolidation_audit.py
```

The private demand review ledger can be checked using `python further_maths/progression_review_bj.py /path/to/demand-review-ledger.jsonl`. Do not publish the private SQLite database, sources or evidence ledgers. Individual solution/render review, item-level specification alignment, empirical calibration and teacher approval remain outstanding. FM-17 remains gated. No merge or deployment.
