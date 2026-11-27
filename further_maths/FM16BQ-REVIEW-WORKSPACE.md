# FM-16BQ - private successor and guarded review workspace

This is a development-only extension of FM-16BP. The BO resolver and all earlier files remain intact. The optional `SuccessorResolver` accepts private, exact-predecessor-bound presentation edits and narrowly scoped vocabulary definitions. It preserves mathematical facts, rubrics and marks and rejects changed mathematical tokens, including a starred polynomial incorrectly converted into multiplication. The existing BO scope guard is still authoritative for preview eligibility. The source-free repository contains no private edit manifest, SQLite database, proof PDF, source material or item-level review evidence.

## Local review service

Python 3.11+, SymPy and PyMuPDF are required. Restore the separately supplied private BQ snapshot to a directory outside the checkout and any web root. Keep the original BO and BP archives as predecessor evidence. The runtime validates the private manifest, exact generated database contents, all page identities, current fingerprints and guarded selection modes before serving previews. A failed validation stops startup. Do not serve the private directory as static files.

Create a private credential file with an exclusive-create command (prompted password; never commit credentials):

```sh
python further_maths/review_service_bq.py --users /private/as1-users.json --add-user teacher
python further_maths/review_service_bq.py --users /private/as1-users.json --bundle /private/fm16bq --review-db /private/as1-observations.sqlite --port 8081
```

Open `http://127.0.0.1:8081/`. The service is bound to localhost. All assets, list, item, page and observation routes require teacher credentials; every item and page request is checked against the same conservative eligibility. An approved examination list is empty and approved-exam retrieval is denied. Pages are rendered from the hash-verified precompiled proof; no user-supplied TeX runs at request time. Review observations bind to the item fingerprint and proof SHA-256, record authenticated actor and timestamp, and are separate from the canonical database. Observations are not release approval. Do not enter pupil data in notes.

For an optional local same-origin mount on the existing Foundation application, configure its normal `KB_DB` and `KB_USERS` variables, and add `--with-foundation --port 8080` to the second command. The AS1 workspace is at `/as1/`; all non-AS1 requests pass unchanged to Foundation. This is an optional route, not a dashboard redesign. The existing root role, sign-in and nine modules are untouched. The Foundation database is not needed for the standalone AS1 service.

## Real calibration and teacher decisions

`calibration_bq.summarize` accepts a version-bound anonymous score histogram with one count per integer score from zero to available marks, rejects missing or stale observations, and computes observed facility, zero/full-credit rates and a standard error. Minimum sample size is an explicit teacher choice. It neither assigns a difficulty level nor grants approval. Real cohort evidence and teacher decisions are required; fictional test fixtures are not calibration. Preserve review and calibration records in private approved storage.

Run `python -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. No merge or deployment is authorised. Local rendering, automated pixel checks and individual layout sampling do not constitute individual visual certification or live production certification. Before hosting, require the school's HTTPS/access policy, secure private volumes and backups, rate limits, retention, accessibility testing, complete Foundation/portal integration and actual teacher sign-off. FM-17 remains gated.
