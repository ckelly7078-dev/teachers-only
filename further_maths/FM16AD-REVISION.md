# FM-16AD — targeted difficulty revisions

Preserves the original FM-16AB generators and 59-file checksum manifest unchanged. The additive `difficulty_revision_ad.py` overlay defines four revised skill/level cells (12 variants); use `revise(path,tier,variant)` for its TARGETS instead of the historical generator. Other cells still use the original generators. The separate oracle checks the new structured facts. This overlay is not yet wired into the existing application or standalone historical verifier.

- Complex division T6: classify a quotient with unknown denominator components, singular parameter values and the excluded zero denominator.
- Cartesian multiplication T4: combine Cartesian expansion with an exact ray condition, including checking direction.
- Principal argument T6: variable component signs, origin exclusion and inverse argument conditions.
- Angle units T6: explicitly label the half-angle task enrichment only.
- Three redesigned cells introduce provisional method (M), accuracy (A), reasoning (R) criteria. These are not approved CCEA marks.
- All 702 cells have proposed scope metadata: 12 known enrichment-only, 690 scope-review-pending. Four system-classification T6 cells share a family identifier as a review signal, not a completed redesign.

The private FM-16AD database migration retains original payloads and marks for all 12 revised items in revision history. Parent SHA-256: 9e444da45382dce0999c9488a532abdd782716fd9744dd4c048f61f98380c0dd. New private database SHA-256: c6ef553a2dafad6f53ef7629b6b0dfbb8488f48d192b22674d433c9246958e2c. All 14 new tests passed locally, including a recheck of all 2,106 stored pathway fixtures and structured facts, corrupted revised answers, boundary cases and preservation of other questions and all 35 source hashes. Historical tests were run in FM-16AC; not all rerun for AD. No teacher approval or empirical difficulty calibration. Private migration, source checks and database stay offline. Do not merge or deploy.

Remaining: redesign the related parameter-system tasks and composition-order challenge, continue semantic and scope review of other pathways, and extend marking guidance. FM-17 remains gated.
