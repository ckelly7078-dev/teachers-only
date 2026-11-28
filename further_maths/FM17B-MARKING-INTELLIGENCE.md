# FM-17B: source-specific marking routes and difficulty follow-up

Continue FM-17A knowledge-adapter development, not a separate teacher-review UI. The private FM-17A note-to-subskill mapping was independently reconstructed from the available BT/BR baseline, not recovered from the missing earlier private FM-17A supplement. Preserve that supplement if available. The BS private correction candidates are also still unavailable. No canonical payload, mark, difficulty tier, scope guard or historical version changes in this checkpoint.

## Private engine contract

With `further_maths` on the Python import path, load `KnowledgeBank.from_bundle(root)` as in FM-17A. Load private mapping and marking-route records from the separately retained archive:

```python
from marking_batch import read_batch
from source_evidence_fm17 import bind_subskills, enriched_evidence
from mark_routes_fm17b import bind_routes, part_routes, original_marking_context

links = bind_subskills(bank, read_batch(root / 'FM17A-subskill-mappings.jsonl'))
routes = bind_routes(bank, read_batch(root / 'FM17B-source-mark-routes.jsonl'))
context = enriched_evidence(bank, links, skill_id)
source_route = part_routes(bank, routes, source_part_key)
original = original_marking_context(bank, original_item_id, mode='learning_preview')
```

The source-route index is intentionally partial. Every primary allocation must match the source-checked printed code sequence and total. Each alternative has its own complete allocation; alternatives are not added to the primary marks. Stage dependencies describe the use of earlier mathematical results, not automatic award prerequisites. Explicit exception records distinguish acceptance, follow-through, restrictions and caps; a cap names its eligible stages. Partial-credit notes are recorded only where read from the breakdown. Missing route data returns `printed_allocation_only`, never guessed rules. The code validates structure and identity, not the correctness of editorial text. The private register includes its exact source PDF hash and breakdown page; source material and records stay offline.

The original-item context retains provisional M/A/R criteria, the worked solution and the fingerprint-bound per-item review of alternative methods, consequential errors, allocation and boundaries. No official M/W/MW allocation is automatically translated to M/A/R. The context respects conservative eligibility and is not an automatic student grade or a release decision. Use it only in the existing private marking engine.

## Difficulty

The private transition register compares representative prompts and rubrics for every strict decrease in mark totals between adjacent tiers, bound to all six active variant fingerprints. It distinguishes diagnostic/procedure roles from increased independent reasoning and compressed mark allocations. A candidate design revision for the invariant-line pathway is supplied privately with two independent mathematical checks; it is not active. No difficulty tier is empirically calibrated or automatically reassigned. The existing generator can continue private integration work without waiting for blanket manual certification, but examination release and actual teacher-approved marks remain separately governed.

Run `python -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. No portal, UI, Foundation, deployment or merge changes. Keep all source PDFs, private mapping records, database and item-specific evidence out of Git.
