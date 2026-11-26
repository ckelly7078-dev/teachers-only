# FM-16AM — active AS1 difficulty resolver

One resolver now routes the original 28 banks, nine revision layers (23 revised cells, 69 active replacements) and seven editorial review modules. Missing or overlapping registry entries fail closed. All 117 skills, 702 cells and 2,106 current variants are checked. Original generators and historical verifier remain unchanged; use the active verifier for the current bank.

From repository root, with SymPy installed:

```sh
python further_maths/test_active_difficulty.py
python further_maths/active_difficulty.py
python further_maths/active_difficulty.py --database /path/to/private/as1.sqlite
```

The last command opens the private checkpoint read-only and compares all active records and scope/approval flags. It is optional; no private materials are required for the first two commands.

`Resolver().resolve(path, tier, variant, mode=...)` requires an explicit selection mode. Learning preview: 1755 items (levels 1–5); exam_candidate_preview: 1053 (levels 3–5 only); challenge_preview: 312; enrichment_preview: 39; approved_exam: 0. Learning and exam candidate pools overlap. All outputs are provisional; original-origin records, not examination-board items. This is a local Python interface, not a web access-control or deployment mechanism.

## Verification

Six distinct selection/routing tests passed, repeated successfully in the isolated source-free package. Both full active checks passed: source-free and with private SQLite comparison, 2106 items each. Two private negative checks passed: existing DB constraint rejected an unapproved flag update, and the new verifier rejected a changed stored mark in a disposable copy. All 58 original manifest entries and all 35 private source hashes matched. Database unchanged: SHA-256 cb78fd4644920c80f61ba02cace6a9543cdbf05a337a8de519353e98fbad10a8. Retained 69 historical item versions. No new question designs, no altered database records.

## Remaining gates before FM-17

- Priority progression review: polar-products T4/T5 both recover a missing factor by division; differentiate linked reasoning from independent reconstruction. Conjugate-find and cartesian-product T6 still share parameter compatibility structures; assess differentiation without forcing gratuitous complexity.
- Vector review: line-plane-angle T6 extends T5 mostly through endpoint classification; perpendicular-parameter T6, scalar-product T6 and triangle-area T6 share elementary quadratic-range reasoning. Revisit challenge level and distinguish the geometric demands.
- Matrix review: singular-condition T6 is a single quadratic discriminant threshold; compare with the revised det-two task. Resolve flagged structural overlaps in line/plane classification and distance.
- Marking gate: 66 of 2106 current items have explicit provisional M/A/R rubric types, 2040 do not. Do not automatically relabel solution steps as marks. Review method, accuracy, reasoning, alternative solutions and consequential errors, and preserve original marking provenance.
- Review existing curriculum mappings directly against specification and appropriate evidence; existing scope labels are provisional. Full solution and rendered mathematics review, empirical difficulty calibration and teacher approval are not complete.

Next: FM-16AN — targeted priority progression and marking remediation. FM-17 remains gated. No merge, deployment or live runtime integration. Separate historical suites and browser tests not rerun. Private database and evidence stay offline.
