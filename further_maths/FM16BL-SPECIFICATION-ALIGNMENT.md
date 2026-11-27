# FM-16BL — specification alignment and targeted demand review

Parent: FM-16BK. This checkpoint remediates the eleven BK observations: five designs gain stronger mathematical tasks and six gain clearer, separately creditable stages. Exactly 33 active numerical variants have explicit successor authorisations; prior versions and marking evidence remain intact. All original items remain teacher-pending and the selection-mode policy is unchanged.

## Source and evidence level

The supplied CCEA GCE Further Mathematics specification (from September 2018), section 3.2, printed pages 9–12 (PDF pages 11–14), was reopened directly. The local page/bullet locators are not official outcome IDs. The scope register binds each active item to its current fingerprint and the 41-concept crosswalk. The T3–6 representative prompts (468 designs) were compared with the specification; independent variant checks do not certify every individual question's wording or exam demand. T1–2 (234 designs) retain their previous prerequisite/diagnostic role; no new individual review is asserted. Source papers and schemes remain private.

The supplied 2025 paper and scheme provide examples of examination demand, including root transformations, combined transformations, locus intersections, real-polynomial factorisation, parameterised square inverses and linked line/plane geometry. They do not imply a one-to-one match between our originals and examination questions. The supplied CCEA scheme uses M/W/MW terminology; our M/A/R labels are internal provisional criteria, not official CCEA marking labels. No official material is reproduced in this public package.

The 11 candidate-preview scope watches cover prerequisite-only demand, region inequalities beyond the explicit simple-locus examples, symmetry/rank terminology and rectangular one-sided identity reasoning. They remain flagged for confirmation, not approved. All 13 enrichment designs are confined to enrichment preview (39 variants); challenge items remain outside exam-candidate preview. Exam-ready and teacher-approved counts remain zero. Scope flags do not change the existing preview counts; a future assessment selector must not treat those flags as approved.

All prior eleven difficulty observations were addressed. The adjacent inverse-three T5–T6 transition exposes a new marking-allocation watch: a general inverse plus all singular homogeneous families has only three provisional marks. It remains explicitly open for the matrix solution review, not an automatic difficulty downgrade. The cube-sums T4–T5 and symmetric-parameter T5–T6 transitions retain lower marks with a documented increase in independent inverse or inequality reasoning. All decisions are editorial, not measured difficulty.

## Verification commands

```
python further_maths/test_marking_design_bl.py
python further_maths/test_scope_review_bl.py
python further_maths/scope_review_bl.py
python further_maths/active_difficulty.py --database /private/as1.sqlite
python -m unittest discover -s further_maths -p 'test_*.py'
```

The optional `scope_review_bl.py --validate /private/register.jsonl` command checks record identity, fingerprint and exact scope/decision coverage. Neither it nor the marking verifier grants examination approval. Remaining gates: individual written solutions and rendered mathematics; scope watches and demand allocation follow-up; empirical calibration; teacher approval; final readiness assessment. No deployment or merge.
