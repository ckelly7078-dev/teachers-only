# FM-16BT - resumable teacher-specific observation queue

This source-only continuation starts from FM-16BS. It does not change the canonical question bank, marks, proof, historical versions, scope watch or approved-exam gate. The BS private editorial register and proposed corrections must be retained separately; they were not available to this continuation. Do not treat the BR private bundle as a replacement for them.

In the existing private AS1 review workspace, choose a preview mode and select **Refresh my progress**. The authenticated `/api/progress?mode=...` endpoint returns only eligible item IDs and the current teacher's five latest explicit check decisions. Revision requests rank first, then outstanding reviews, then items whose five checks were observed as pass. Within a state, scope watches and BQ successors take priority. The next-review control selects a pending item; it does not submit a decision. Previous observations are displayed separately from the blank review form. A successful save refreshes a loaded progress view. Refresh after changing modes or returning to the workspace.

A later `not_reviewed` entry does not erase a previous explicit decision. Stale fingerprints, revisions and proof hashes are excluded. The authenticated actor is not a query parameter. No other teacher's identity, notes or observations are returned. The read-only queue does not create a missing ledger; if recording is unconfigured it reports that status. A wrong or invalid existing ledger is an error rather than a blank review history.

This is a convenience aid for individual teacher review, not a replacement for the BR/BS cross-teacher reconciliation reports or editorial review register. All-pass observations are not certification or approval. No genuine teacher decision or empirical score was generated during testing. The examination gate remains closed.

## Verification

From the repository root:

```sh
python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'
node --check further_maths/review_bq.js
```

Run the BS combined-service checks when a complete checkout and the relevant private Foundation data are available. Local AS1 HTTP tests and offline Chromium fixtures do not establish live production certification. Keep all private test evidence, source material and databases outside Git and any web root.
