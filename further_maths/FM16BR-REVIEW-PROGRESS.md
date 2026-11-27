# FM-16BR - private readiness progress reconciliation

Continue from FM-16BQ. No question, scope guard, proof or database payload is changed. This utility consumes the private BQ runtime bundle and the optional observation ledger produced by the BQ service. It never writes either input. Reports must be kept outside Git and the web root.

Run from the repository root (choose a minimum sample size appropriate to the real pilot):

```sh
python further_maths/review_progress_br.py --bundle /private/fm16bq \
  --observations /private/as1-observations.sqlite \
  --calibration /private/aggregate-scores.jsonl --minimum-attempts 20 \
  --output /private/as1-progress.json
```

Omit `--observations` or `--calibration` when that evidence has not yet been collected. A supplied missing observation ledger is an error. An all-null calibration histogram is an unfilled template, not a score. No pupil data is required. The report reconciles the latest explicit decision per actor and check, retains conflicts between actors, excludes stale version/proof evidence, and refuses duplicate calibration inputs. A later `not_reviewed` entry does not erase a previous explicit decision. Scope watches, revision issues and recent successors are prioritised for review. Even all-pass observations and adequate sample counts are not examination approval or proof that difficulty levels are calibrated.

Run `python -m unittest discover -s further_maths -p 'test_*.py'`. No release, merge, or deployment is authorised. Real teacher decisions and observed assessment outcomes are still required; the FM-17 gate remains closed.
