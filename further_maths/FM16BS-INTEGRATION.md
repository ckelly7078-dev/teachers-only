# FM-16BS · integrated private teacher review

Start from the FM-16BR feature branch. Use the existing Foundation database and its teacher file with the BQ combined launcher. The authenticated AS1 catalogue verifies the separately supplied private snapshot before the combined service starts.

From the repository root, set `KB_DB` and `KB_USERS` for Foundation as documented in `foundation/README.md`. Supply a separate AS1 teacher file provisioned with the BQ add-user command. Use a separate writable observation ledger.

```sh
python further_maths/review_service_bq.py --with-foundation --port 8080 \
  --bundle /private/as1 --users /private/as1-users.json \
  --review-db /private/as1-observations.sqlite
```

Open http://127.0.0.1:8080/. Select Teacher, continue to the dashboard, then choose **AS1 Further Mathematics review**. Foundation Mathematics Studio has the same link in its navigation. The AS1 header area provides return links. The dashboard demo sign-in opens the local portal. Opening a protected workspace requires credentials accepted by that service.

Changing the selected variant closes the previous proof and observation form. A list filter that retains the selected variant preserves the open review. Observation records bind the authenticated actor, item version and proof. The observation writer and read-only database checks now close their SQLite handles on success and exception, with the write transaction completed before closure.

## Editorial queue and pilot

The optional private BS supplement binds each AI inspection and scope disposition to the active item and reference proof. The reconciliation report keeps teacher decisions independent. All 33 guarded variants continue to be excluded from examination-candidate previews. The private handover contains the scope decisions, exact checks, proposed corrections and a three-form pilot roster with blank score histograms. No pilot has run.

```sh
python further_maths/review_progress_br.py --bundle /private/as1 \
  --editorial-bundle /private/as1 --calibration /private/as1/FM16BQ-calibration-input-template.jsonl \
  --minimum-attempts 20 --output /private/new-progress.json
```

The number 20 reproduces the historical diagnostic report. The pilot lead determines the real threshold and sampling conditions. Add `--observations` only for a real private ledger. The command creates a new report file. Corrections in the separate BS candidate proof await adoption into a successor snapshot.

## Verification

```sh
python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'
python -m unittest discover -s tests -p 'test_*.py'
node tests/smoke.cjs
node tests/as1-selection.cjs
python tests/check_as1_mount.py --bundle /private/as1
python tests/check_as1_mount.py --bundle /private/as1 --browser --chromium /path/to/chromium
```

The HTTP test uses the real private AS1 catalogue, the existing Foundation service, a disposable four-unit Foundation database and transient credentials. The optional Playwright run exercises the portal routes, item selection, proof zoom and observations at three widths. A browser runtime with permission for loopback navigation is required. The QA report records which commands ran and any environment limitations. Historical Foundation data acceptance, school hosting, actual teacher certification and learner calibration are separate outstanding gates. FM-17 remains closed.
