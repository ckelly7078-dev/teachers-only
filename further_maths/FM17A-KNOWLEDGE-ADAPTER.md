# FM-17A: source-linked marking and difficulty adapter

FM-16BT is the unchanged question-bank baseline. The FM-17A development work is a private Python knowledge adapter, not a second teacher workspace, a student grader, or a release of examination material.

## Runtime contract

From the existing service's private backend, with `further_maths` on the import path:

```python
from knowledge_fm17 import KnowledgeBank
from marking_batch import read_batch
from source_evidence_fm17 import bind_subskills, enriched_evidence

bank = KnowledgeBank.from_bundle(private_bundle_root)
links = bind_subskills(bank, read_batch(private_mapping_path))
context = enriched_evidence(bank, links, skill_id)
questions = bank.select(skill_id, tier, mode='exam_candidate_preview')
```

`private_bundle_root` must contain the existing BQ-era database, successor-edit register and current marking-review ledger. `private_mapping_path` is the separately supplied FM17A-subskill-mappings.jsonl. The constructor verifies all active payloads and marking-review fingerprints; load it once in the private backend, not per HTTP request. `context` is private evidence, not content to send to a student or publish. `questions` contains original-only candidates with provisional rubrics and demand profiles. The existing eligibility guard applies; exam-candidate preview is not exam approval. No UI or HTTP route is added.

The archived CCEA schemes use M (method), W (working), MW (combined method and working). The original bank uses provisional M/A/R criteria. Preserve both conventions separately. The policy notes summarize general positive marking, follow-through, alternative valid solutions and simpler misreads, but cannot replace a part-specific marking route. The two disputed printed records are excluded from usable source parts. Source notes and report observations are not student grading rules.

The fine-grained crosswalk is an editorial interpretation of previously source-checked part notes, bound to the exact note, allocation and source hashes. Parent concept links remain separate. A missing subskill link means insufficient direct note evidence, not that the skill is absent from the specification. Do not treat the entire part's marks as belonging to each linked skill. The mapping register is private, not in Git.

Demand profiles preserve the existing tier, rationale and role. Marks, criterion types, solution-step counts and prompt wording are descriptive features, not measured learner difficulty. The transition screen flags overlapping mark ranges and identical wording signals for further substantive comparison. Neither source easy/medium/hard classifications nor bank tiers are empirically calibrated; no automatic tier reassignment occurs.

## Verification and boundaries

Run `python -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. Private all-bank verification and mapping results are supplied separately. No teacher approvals, scope promotions, database edits, student scores, portal changes, deployment or merge are introduced. The prior BS private supplement remains missing; do not silently replace it. The integration adapter is ready for private engine testing, not certified live integration or examination release. Preserve existing guard and release boundaries.
