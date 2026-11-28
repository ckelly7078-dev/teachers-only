# FM-17H: complete Tier 3 structured marking profiles

Preserve the FM16FINAL active mathematical baseline and the FM-17D-G marking contract. This checkpoint adds private prompt-derived, fingerprint-bound mathematical profiles for the 52 remaining Tier 3 designs (156 variants). All 117 Tier 3 designs and 351 variants have a supported bounded structured observation route through one adapter. The other five tiers retain provisional marking contexts; no question payload, difficulty tier, database, rubric or eligibility rule is changed.

## Private backend contract

Load the cumulative private checkpoint in the existing trusted backend, with `further_maths` on the import path:

```python
from engine_fm17d import Engine
from profile_marking_fm17h import ProfileMarking
engine = Engine.from_bundle(checkpoint_root)
marking = ProfileMarking.from_bundle(engine, checkpoint_root)
capability = marking.capability(item_id, mode=mode, item_fingerprint=fingerprint)
proposal = marking.check_work(item_id, mode=mode, item_fingerprint=fingerprint, work=observations)
```

The FM17H profile register is private. The loader checks the register hash, exact active question fingerprints, revisions, criterion order, types and marks, unique fields and complete coverage of the remaining Tier 3 items. Existing FM-17D-G checkers are delegated unchanged. No learner-facing reference values are returned by capability. The profile register and manifest must be trusted offline artifacts, not accepted from a learner or exposed by a web endpoint.

For a new profile, the observation object has exactly the fields described by its private criteria. Each value is a bounded rational string, fixed label, structured array, or a tagged exact radical sum. A radical sum is represented by `{'radical_terms': [['coefficient', 'positive_integer_radicand'], ...]}` with at most eight terms, each rational coefficient bounded as in FM-17D and radicand at most 10000. Square factors are removed and like radicals combined; an empty sum represents zero. Angles in pi units are rational coefficients, not floating-point degrees. The private profile determines the required units, representation and task restrictions. Comparators recognise equivalent nonzero proportional equations and directions, unordered complete sets, equivalent line representations, and scaled plane equations with consistent substitution evidence. Diagram profiles require explicit observed features; they do not inspect images. Other valid methods and representations not covered by a profile must remain null (uncertain), not be forced into an incorrect observation.

## Verification and limitations

The private reproduction script derives observations from the trusted current prompts and compares the calculated mathematical facts to the canonical answer facts and rubric. This is a bounded editorial interpretation; it is not an independent assessment of unrestricted learner work or a universal proof checker. A method observation must describe actual working extracted by a trusted parser/reviewer; do not invent it from an answer. Consequential-error rules for earlier batches remain available, while new profile methods compare the specified observations and do not infer arbitrary follow-through. An unsupported but valid method must be marked uncertain. No automatic award, learner score, examination approval or release is produced.

Run `python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'`. The private audit checks all active contexts, supported variant dispatch, profile positive/negative/uncertain observations and stale or ineligible requests. The final bank, source evidence, scope guards and all historical payloads remain unchanged. Keep private evidence, sources, databases and credentials outside Git and web roots. No portal, Foundation, qualification navigation, merge or deployment changes. Live integration, empirical difficulty calibration, remaining source gaps, and handwriting interpretation are separate outstanding work.

## Roadmap

FM-17I: extend reusable mathematical observation coverage to the other five difficulty levels, recording partial capability rather than inventing unsupported marking. FM-17J: strengthen method alternatives, explicit partial-credit and consequential-error rules. FM-17K: connect to the existing Mathematics Studio engine using distinct qualification pathways. FM-17L: final validation and consolidation. These are development targets, not proof of full empirical or live readiness.
