# FM-17D: private knowledge engine contract

The FM-16FINAL snapshot remains the active mathematical baseline. This checkpoint connects its validated questions, provisional rubrics, six editorial demand tiers, and FM-17C source evidence in one private Python adapter. No portal/UI, Foundation database, approval flow, or deployed service is modified.

## Generation and marking handoff

Load once in a trusted backend with `further_maths` on the Python import path. The root is the extracted cumulative private checkpoint, not the predecessor database at its root.

```python
from engine_fm17d import Engine, reconcile_proposal
engine = Engine.from_bundle(checkpoint_root)
result = engine.generate([
    {'skill': 'ALG.roots-coefficients.sum-product', 'tier': 3, 'count': 2},
    {'skill': 'MAT.arithmetic.multiply', 'tier': 3, 'count': 1},
], mode='learning_preview', total_marks=7, seed=42)
row = result['questions'][0]
context = engine.marking_context(row['item_id'], mode=row['mode'], item_fingerprint=row['fingerprint'])
```

Selection is restricted to exact skill/tier/count groups (1–3 variants per group, maximum 10 questions). Optional exact total marks and prior item exclusions are hard constraints. An impossible request fails instead of relaxing difficulty, eligibility, marks, or diversity. The seed permits reproducible ordering, not new mathematical parameters. Draft rows use familiar Studio question/answer/solution/rubric fields plus typed criteria, version identity, assessment role, demand rationale and source-coverage counts. They are not persisted or student-facing. The reference pointer identifies a teacher proof containing the solution; never serve it as a student question. Fifteen original items have a reference diagram; independent question-only rendering is not provided by this adapter. Source counts distinguish note-level, component-level and parent/specification evidence. They do not convert CCEA easy/medium/hard labels into the six editorial tiers.

`reconcile_proposal(context, decisions)` accepts complete criterion observations (`criterion_id`, `status`, `evidence`); supported statuses are `met`, `not_met`, `uncertain`. It calculates a possible mark interval, retains grouped criteria intact, does not interpret evidence text, and never approves or publishes a grade. `structured_math_fm17d.check_work` provides a limited independent exact checker for Tier 3 root sum/product, signed radians-to-degrees, and rectangular matrix multiplication. It accepts structured rational observations, distinguishes demonstrated method from final accuracy, supports specified equivalent methods and leaves other methods uncertain. It is not handwriting recognition, a general symbolic solution parser, or a universal marking engine.

`source_proposal_fm17d.source_bounds` reconciles explicitly supplied observations on exactly one version-bound official source route. Each stage must be accounted for. Grouped partial marks are accepted only when a published partial-credit note exists; the caller must establish the actual condition. Explicit observed caps restrict the eligible stages and total. Follow-through and other exception notes do not automatically award credit. Alternative routes are never added together; ambiguous allocations remain unavailable. Official M/W/MW rules are never imported as original M/A/R awards.

## Verification and limitations

Run `python -m unittest discover -s further_maths -p 'test_*.py'`. The private runtime audit exercises the actual final bank, its current fingerprints, selection constraints, all detailed source routes and structured arithmetic fixtures. The new contract is ready for private application integration; the existing Foundation Studio has no AS1 consumer or generic scanned-work marking service in this checkpoint. The existing engine must explicitly call this adapter; live end-to-end integration, question-only rendering, empirical difficulty calibration and teacher approval remain outstanding. Private source evidence, databases and proof files stay outside Git/web roots. No student records, automatic award, merge or deployment.
