# Further Mathematics AS1 — FM-16AB preservation checkpoint

This branch is based on the Mathematics Studio development commit `868da3b7b689c16b85e8c9d8da299f37c059014d`. No Foundation or website files are modified by this checkpoint. No merge or deployment is authorised.

## Publication status

The screened upload bundle is **prepared, not yet uploaded**. The public subset contains 56 original pathway generator and exact-fact validator modules, the editorial skill map, a source-free verification script and a SHA-256 manifest (59 files total). It excludes examination PDFs, SQLite databases, offline history, examiner-report-derived notes, source-dependent audit fixtures and the legacy practice bank pending further review.

- Archive: FM16AB-public-upload.zip
- Archive SHA-256: `db025edf39584a834692931c4d7733cf9d0e6a4cb7bd9a6328f13b18d74ecebc`
- Manifest: further_maths/FM16AB-PUBLIC-SHA256.txt
- Manifest SHA-256: `843eeae187063fd0ce7a970fe7c648b03af59d32f73cc94da7ce6921edc4a11b`

Extract the archive and upload the contents of its further_maths directory into this repository's further_maths directory on this feature branch only. Do not upload the full private archive or the unscreened cumulative code candidate. After upload, verify the file hashes from repository root, then run:

    sha256sum -c further_maths/FM16AB-PUBLIC-SHA256.txt
    python -m pip install sympy
    python further_maths/verify_pathways.py

The standalone verifier passed locally against all 117 skill mappings and 2,106 structured answer checks in the screened bundle. Six levels and three variants per level are represented. This does not verify every written solution, marking rubric or educational demand; difficulty is editorial and teacher approval is pending. The comprehensive FM-16 difficulty audit, FM-17, FM-18, FM-19 and engine integration remain outstanding. The private checkpoint contains 4,332 original records in total, of which 2,226 older records are practice-only and uncalibrated.

Keep source material and private data outside Git and any web root. Do not treat this branch as a release.
