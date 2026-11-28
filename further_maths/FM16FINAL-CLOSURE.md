# FM-16FINAL: editorial knowledge-base closure

The three invariant-line Tier 5 variants supersede FM-16BC with complete affine-line classification, an arbitrary-intercept family, vertical exclusion, and pointwise fixation. Five provisional marks replace three. The new independent exact normal-vector oracle verifies the complete facts; the private migration also checks direct coefficient comparison. All other active variants, historical payloads, source evidence, and scope roles are preserved.

The private final snapshot is an explicit successor under `FM16FINAL/` in the cumulative archive. The original root BQ snapshot, FM-17C evidence and prior manifests remain intact. Do not silently load the old root as the new bank. Existing BQ and FM-17A APIs remain compatible. Use the final knowledge adapter from the existing Teachers Only private backend:

```python
from final_fm16 import load_final_bank
from marking_batch import read_batch
from source_evidence_fm17 import bind_subskills
from source_coverage_fm17c import SourceCoverage

bank = load_final_bank(checkpoint_root / 'FM16FINAL')
links = bind_subskills(bank, read_batch(checkpoint_root / 'FM17A-subskill-mappings.jsonl'))
coverage = SourceCoverage(bank, read_batch(checkpoint_root / 'FM17C-source-mark-routes.jsonl'),
    read_batch(checkpoint_root / 'FM17C-ambiguous-allocations.jsonl'),
    read_batch(checkpoint_root / 'FM17C-route-component-links.jsonl'),
    read_batch(checkpoint_root / 'FM17C-source-conditions.jsonl'))
```

All 33 previously watched variants have an explicit conservative learning-only editorial disposition. The underlying historical scope labels are retained for reproducibility; the existing conservative preview guard implements the actual selection restriction. No claim of official CCEA exclusion or confirmation is made. All approved-exam modes stay empty. The final marking and written evidence for three replacements is regenerated rather than reusing predecessor certification. The reference proof preserves 2,103 prior pages and substitutes three freshly compiled pages; private QA records the comparisons.

This closes the identified mathematical remediation under the revised knowledge-base-development scope. It does not assert that every editorial difficulty transition is empirically calibrated, every visual page is individually certified, or every archived marking ambiguity is resolved. The original BS private supplement remains unavailable. Individual teacher certification, actual marks, empirical learner evidence, existing-engine live integration and examination release are separate requirements. The source-only adapter does not change portal or review UI, and does not grant approval or deploy anything. Further FM-17 work can consume this final snapshot without pretending the remaining empirical or source-evidence gaps are resolved.

Run `python -W always::ResourceWarning -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. Keep the private source PDFs, database, evidence and credentials outside Git and web roots.
