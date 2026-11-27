# FM-16BI — AS1 consolidation and readiness screen

Parent: FM-16BH. The question bank, database, marking ledger, history, and selection modes are unchanged. This checkpoint adds a read-only audit and specification concept crosswalk. The crosswalk was checked directly against the supplied CCEA GCE Further Mathematics (from September 2018), section 3.2, printed pages 9–12 (PDF pages 11–14). The printed page/bullet pairs are local reference locators, not official outcome codes or certification of individual items. All 41 concept links and 117 skill pathways are represented. The specification states a 90-minute AS1 examination of 6–10 questions and 100 raw marks; that is not a licence to use original candidates as approved exam questions.

The audit screens all 702 shared designs and 585 adjacent-tier transitions, using all three numerical variants in each design. All 2,106 active items are typed; no variant mark-total differences within a design were found. There are 324 strictly higher, 233 touching, and 28 lower/overlapping mark-range transitions. These are mark-range observations only, not empirical difficulty or proof of demand progression. A representative-prompt review of the 28 flagged transitions identifies 12 diagnostic-to-procedure contrasts, five plausible linked-demand increases with lower marks, and 11 priority transitions for closer review. Private item-level notes stay offline. Equal mark totals can mask different demands and remain in the review queue.

Source-free commands:

```
python further_maths/consolidation_audit.py
python further_maths/test_consolidation_audit.py
python -m unittest discover -s further_maths -p 'test_*.py'
```

Optional private ledger: `python further_maths/consolidation_audit.py --ledger /path/to/current.jsonl`. The output does not grant approval. A separate private `active_difficulty.py --database` run verifies the database against the resolver. Private source provenance, ledger and archive must not be published.

Next gates: inspect the 11 priority transitions and the remaining equal/higher-mark transitions for demand; review item-level specification scope and original examination-demand evidence (including enrichment isolation); individually review written solutions and rendered mathematics; empirically calibrate difficulty; obtain teacher approval; then reassess FM-17. No merge or deployment. All approved-exam selection remains empty.
