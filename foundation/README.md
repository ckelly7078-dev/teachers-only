# CCEA Foundation mathematics

The first deliverable covers inventory for M1, M2, M5 and M6 and question-level work for M1. The existing dashboard links to a protected web application at /foundation/web/index.html. The runtime reads SQLite on a persistent server volume. It can start with the supplied private checkpoint alone. Source PDFs are needed for ingestion and checking the underlying pages.

## Restore and run

Use Python 3.11 or newer with SQLite and scrypt support. The runtime and tests use the Python standard library. Offline ingestion and its PDF integration test also require Poppler's pdftotext and pdfinfo executables on PATH. The portal regression test uses Node.js.

1. Place the checkpoint's foundation.sqlite on a private, writable, persistent volume. Keep the mounted path outside the checkout and any static web root. Keep the original ZIP separately in the school's approved private document storage.
2. Apply foundation/.env.example to the service environment. Set KB_DB to the restored database and KB_USERS to a separate, private teacher credential file. The module reads the process environment.
3. From the repository root, initialise a teacher credential with the command below. It prompts for a password and exclusively creates the file. Its JSON array accepts individually provisioned teacher identities with salted scrypt hashes.
4. Launch the localhost development server, open http://127.0.0.1:8080, select Teacher, continue to the demo dashboard and open Curriculum Knowledge Base. Enter the separate teacher credential when prompted.

```sh
export KB_DB=/srv/teachers-private/foundation.sqlite
export KB_USERS=/srv/teachers-private/teacher-users.json
python -m foundation.server --add-user teacher
python -m foundation.server --port 8080
```

For a school-hosted deployment, supply the WSGI callable foundation.server:application to the host's production WSGI service behind an HTTPS reverse proxy with request size and authentication rate limits. Route the portal and Foundation API under the same origin. A static-only host needs that backend route before search or generation can work. Mount KB_DB on persistent local storage shared by the service and ingestion job. SQLite uses WAL and needs write access to its directory. Provision the teacher credential file read-only to the service. Use the school's encrypted volumes and encrypted backups. This milestone has no student-data endpoint. No school deployment or live model credential is included.

The school can rotate credentials in the teacher file. The identity is used in review history and to restrict practice drafts. Review and approval history follow the school's retention period for teaching resources. An administrator removing data should include database backups and follow the school's retention decision. HTTPS, access policy, retention settings and deployment monitoring belong to the hosting environment.

## Import and resume

The audit accepts the Foundation ZIP layout with 00_INVENTORY.csv and 00_MISSING_DOCUMENTS.csv. Audit each unit separately. Each command handles at most one unit. An empty database is created on the first audit. A fresh import yields candidates. The saved checkpoint preserves the initial source-checked annotations and subsequent teacher reviews.

```sh
for unit in M1 M2 M5 M6; do
  python -m foundation.ingest audit --db "$KB_DB" --archive "$PRIVATE_ZIP" --unit "$unit" || exit 1
done
python -m foundation.ingest extract --db "$KB_DB" --archive "$PRIVATE_ZIP" --unit M1
python -m foundation.report --db "$KB_DB" --out /srv/teachers-backups/foundation-snapshot
```

Copy the completed backup's SQLite file to restore it. The report tool uses the SQLite backup API to include committed WAL data and exports CSVs from that same snapshot. For a consistent audit of a changing collection, run one offline importer per archive. Use a new, empty backup folder for each retained snapshot.

The importer validates manifest membership, byte count, SHA-256 and ZIP member CRC on read. Cover evidence includes Foundation tier, component code, qualification year, sitting date, calculator status, print identifier and document role. The ambiguous Summer 2021 materials have matching print identifiers but undated covers. Their archive-assigned series remains subject to review. A November series can have a sitting date in December. Missing items are relative to the supplied catalogue. Individual official URLs and official-release authentication are unresolved where independent evidence is unavailable.

The audit checkpoints individual files. Repeating a unit on an identical archive reads its archive hash and skips PDF decoding for completed files. Repackaged archives reuse parsed covers by content hash. Identical bytes at another path have one document identity. Changed bytes at an existing path require a versioned archive path so both sources remain attributable. Parsing failures remain retryable. Pairing requires a unique paper and scheme that agree on cover evidence. A change to a pairing invalidates its search entries.

Question extraction operates on one confirmed pair at a time and commits each pair atomically. It preserves reviewed values, records parser versions and skips successful pairs on restart. Page references retain access to notation, diagrams and tables in the original private copy. Text layout can merge answer boxes, drop superscripts or reveal hidden text layers. Candidate paper/scheme page links, numeric mark sums, subpart labels and keyword-based classification suggestions need checking. A verified, independently written note records the expected reasoning and marking routes. Parent and part labels share the paper/number key. Dependencies can refer to a named preceding part. Current school review is per record.

## Runtime boundaries and cost

The static portal loads zero question records. Unit counters are precomputed when data changes. Search reads a revision number, then uses a bounded process-local LRU cache. On a cache miss, the composite postings index reads at most 96 recent candidates per token for eight tokens, with up to eight results. Typed topic labels and curated search terms support skill synonyms. Candidate caps favour recent indexed IDs for high-frequency terms. The M1 pilot uses keyword retrieval and an exact skill lookup. Other filters and an embedding index remain future work.

Source browsing uses keyset pagination. Direct source reviews require an authenticated teacher, source-page bounds, valid per-route totals and an optimistic review version. Reviews, postings and cache revision commit together. Practice uses at most three verified examples. Optional model-assisted parameter selection receives a short allowlist of metadata and an output cap of 60 tokens. Documents, teacher free text and full search hits stay out of the model request.

The local generator supports original, two-mark questions for percentages, metric conversion and finance. Each includes worked reasoning, an authored rubric, an independently evaluated inverse arithmetic check, source citations, an estimated difficulty and the specification page. The optional server-side model selects bounded integer parameters for those same validated families. Set KB_MODEL_URL to a school-approved HTTPS Chat Completions-compatible endpoint and configure KB_MODEL_KEY and KB_MODEL_NAME to enable it. A missing or failed provider is reported. Oracle tests cover all 867 combinations across the three families. The dashboard saves drafts and teacher-approved versions, with a distinct validation label after a teacher changes wording.

## Corpus and evidence

Snapshot audit, 25 November 2026. All 149 file hashes correspond to the supplied manifest. All are distinct. The three accompanying manifest/readme files are administrative material.

| Unit | Papers | Schemes | Confirmed pairs | Pairs needing date evidence | Missing files |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 15 | 15 | 14 | 1 | 0 |
| M2 | 14 | 13 | 12 | 1 | 3 |
| M5 | 24 | 22 | 20 | 2 | 6 |
| M6 | 24 | 22 | 20 | 2 | 6 |

The archive includes no examiner reports or specification PDF. The M1 taxonomy groups the published outcomes into 28 local skill groups under the three official strands. The groups, keywords and individual mappings are editorial classifications. References give the printed pages of section 3.1. The specification identifies M1 on pages 8–13, M5 from page 14, M2 from page 17 and M6 from page 20. [CCEA GCSE Mathematics, version 2, 8 June 2017](https://ccea.org.uk/downloads/docs/Specifications/GCSE/GCSE%20Mathematics%20%282017%29/GCSE%20Mathematics%20%282017%29-specification-Standard.pdf)

The first M1 checkpoint contains 405 question numbers and 980 question or part anchors. Twelve records across eight skill groups were checked against rendered paper and scheme pages in development. A further 183 have provisional classifications and 968 anchors await source review. The 14 processed papers each reconcile to their 100-mark cover total after correction of a hidden duplicate mark label in Summer 2019 Q9. A matching total alone does not establish correct part boundaries, diagram interpretation or marking. Review verified examples in the portal through the 2018 Summer and 2019 Summer papers. The private companion archive contains the database, full per-file inventory, pairing decisions, missing list and per-paper mark reconciliation.

CCEA's published past-paper notice permits educational download/print and restricts electronic redistribution and storage of content in retrieval systems. The initial importer retains identifiers, hashes, factual marks, independently authored notes and page references. The PDF stream and page text are transient. Keep scans and verbatim paper/scheme text out of the service. No permission specific to this platform has been established. [CCEA past-paper copyright notice](https://ccea.org.uk/key-stage-4/gcse/subjects/gcse-gaeilge-2017/archived-past-papers-mark-schemes) · [CCEA past-paper catalogue](https://apps.ccea.org.uk/pastpapers/)

## Validation and outstanding work

Run both test commands in the project README. The Foundation suite uses fictional PDFs and exercises parsing, duplicates, pairing, incremental restarts, classification, reference search, access control, cache invalidation, alternative marking routes, restore, generation and teacher approval. A local single-process benchmark used 35 uncached searches per size and an indexed high-frequency term. Median lookup took 0.58 ms with 10,000 added synthetic records and 0.58 ms with 100,000. These are local retrieval timings, excluding authentication, HTTP and provider latency. Production latency and costs have not been measured.

Full mock papers, free-form AI question writing, diagram generation and licensed visual retrieval, examiner observations, scanned marking, class feedback integration and teacher-scored evaluation are later milestones. School deployment, live provider testing and full browser acceptance are outstanding. The existing portal's 26 mocked-DOM checks cover the shared teacher workspace. The all-unit candidate expansion below is staged for review; retrieval remains restricted to source-checked records.

## All-unit candidate expansion (25 November 2026)

The new private checkpoint `CCEA-Foundation-all-units-checkpoint.zip` extends the M1 pilot while preserving all previous reviewed records, reviews, postings and pair decisions. It contains 2,981 candidate or verified question/part anchors: M1 980, M2 711, M5 691 and M6 599. The 12 previously source-checked M1 records remain the only searchable records. M2/M5/M6 taxonomy and source-level review are not yet implemented.

Run the new metadata-only structural audit on an existing restored database, one unit at a time:
```sh
python -m foundation.expand --db "$KB_DB" --archive "$PRIVATE_ZIP" --unit M1 --out /private/structural-M1.csv
# Repeat for M2, M5 and M6
python -m unittest discover -s tests -p test_expand.py
```
The audit checks cover question count, layout and raw-text mark totals, scheme question count and exact marked-part anchors. It stages only missing non-M1 candidates, never overwrites existing records and never promotes them to verified. Both text views can share PDF extraction errors; structural agreement is not visual, mathematical or rubric verification. Results: 41/66 confirmed pairs show structural agreement; 25 need review, including missed question headings, hidden or duplicated mark labels and unmatched part labels. Six date-unresolved 2021 pairs remain excluded. Missing files remain 15 against the supplied inventory. The repeated audit preserved row counts and the snapshot passed SQLite integrity and foreign-key checks. The three new focused parser tests passed locally. Full prior integration and browser suites were not rerun in this session.

The candidate staging uses extraction version 4. Do not rerun the version-3 extractor against these units until parser reconciliation is implemented. Keep the database, reports and source PDFs outside public Git. Next: improve layout-aware extraction, add unit-specific curriculum classification and reviewed marking routes, then test retrieval across all Foundation units. The all-unit checkpoint contains no new verbatim examination content.

## Foundation taxonomy and cross-unit source-check pilot

Restore the private CCEA-Foundation-classified-checkpoint.zip instead of the earlier all-units snapshot. All 2,981 anchors remain intact; 1,050 now have a skill label (mostly provisional), compared with 195 before this pass. Taxonomy groups are editorial summaries of specification printed pages 8–21. M2 and M5 inherit M1; M6 inherits M1/M2/M5. There are 203 unit-specific skill entries including prerequisite copies (28/49/44/82 by unit). A copy retains its original specification page; IDs encode origin. These are not 203 distinct learning outcomes. 

```sh
python -m foundation.taxonomy --db "$KB_DB" --archive "$PRIVATE_ZIP" --out /private/taxonomy-audit
```

The classifier matches phrases against transient paper text, preserves prior labels and source checks, requires matching paper page and a scheme anchor, and leaves ties unassigned. It assigned 852 new provisional labels. Three more classifications were added by source review. It does not validate classification accuracy or promote records. Results are reproducible: repeat assigned zero new labels. Broad phrases, incomplete anchors and diagram questions may produce incorrect or missing suggestions; teacher review remains necessary.

Twelve additional records were source-checked against rendered paper/scheme pages and independently calculated (M2 four, M5 three, M6 five). They carry a separate AI-assisted development reviewer identity, not teacher approval. The original twelve M1 records remain unchanged. Private checkpoint contains these annotations, answers, rubrics and audit events. Indexed search now has 24 records across all Foundation units. SQLite integrity, foreign keys, original verified row preservation, repeatability, exclusion of unverified records from postings, and four direct index retrieval probes passed. Full server/API and UI tests were not rerun. Existing three M1 practice families are unchanged; wider question generation and live API are outstanding. The 25 structural exceptions, six unresolved date pairs and 15 missing files remain. No official licensing or teacher approval is implied.

## Coordinate reconciliation and source-review continuation

Latest private checkpoint: `CCEA-Foundation-reconciled-checkpoint.zip`. All 72 available paper/scheme pairs reconcile at the whole-question level (1,477 numbered questions), including 66 cover-confirmed pairs and six undated Summer 2021 assessment pairs. The six undated pairs remain explicitly archive-attributed and excluded from verified runtime retrieval. The 2021 CCEA alternative arrangements guidance distinguishes assessment resources from normal scheduled exams. Source: https://ccea.org.uk/downloads/docs/Support/General/2021/Summer%202021%20Alternative%20Arrangements%3A%20GCSE%20Mathematics%20Subject%20Guidance.pdf

Install PyMuPDF in an isolated offline ingestion environment; the existing runtime does not require it. Run:
```sh
python -m foundation.reconcile --db "$KB_DB" --archive "$PRIVATE_ZIP" --out /private/coordinate-audit
python -m unittest discover -s tests -p test_reconcile.py
```
The new audit uses bold left-column headings, position-aware mark labels, and the scheme's available-marks column. Eight pinned, visually checked source corrections address hidden marks and a missing scheme total in extracted text; an additional tick-glyph correction repairs a spurious candidate mark. Four broken candidate papers were rebuilt without overwriting reviewed records. New structure_pairs and structure_questions tables hold factual source-linked metadata, not raw source text. All existing candidate whole-question totals now agree with the 66 confirmed pairs. Repeating the audit preserved question IDs, classification, review history, postings and structural records. Three focused tests passed; full application integration/browser tests were not rerun.

The database contains 3,055 anchors, of which 2,485 carry marks; 35 are source-checked and indexed (24 prior records preserved, 11 newly checked by independent arithmetic and rendered source review). There are 2,450 mark-bearing records requiring further review, and 570 other structural or parent anchors. 1,049 have a skill label, mostly provisional. The private review queue records question IDs, source paths and hashes, page references and remaining actions. Do not interpret structural reconciliation as answer or rubric verification or teacher approval. Do not overwrite these repaired candidates with the earlier extraction pipeline.

The 15 absent PDFs and examiner reports remain missing. Official download attempts for two missing documents failed in this environment. No Phase 2 development was undertaken in this pass; prioritize semantic review, missing-source ingestion and evidence-based classifications. Do not deploy until source permissions, security, teacher review and retrieval evaluation are addressed.

## Examiner report ingestion

Latest private checkpoint: CCEA-Foundation-examiner-checkpoint.zip. Five supplied CCEA reports (Summer 2018, January 2019, Summer 2019, January 2020, November 2021) link to 22 Foundation components and 450 whole-question anchors (M1 136, M2 131, M5 90, M6 93). The additive examiner_reports, examiner_sections, examiner_anchors and examiner_notes tables preserve source hashes and physical page ranges; all section question-number sets match the reconciled paper records. Twenty-six independently worded, AI-assisted teaching notes are included in the private snapshot, not official marking rules or teacher approvals. Original report text/PDFs are not stored in Git or the database. Retain originals privately. Reimport with `python -m foundation.examiner --db "$KB_DB" --out /private/report-audit /private/reports/*.pdf` (PyMuPDF offline). The parser is tailored to the supplied reports and requires additional validation for newer formats. Repeated ingestion produced no duplicates; prior question, skill, review and posting records are unchanged; SQLite integrity and foreign keys passed. Runtime report retrieval/UI and later examiner reports remain outstanding. Phase 2 remains on hold.

## Examiner evidence retrieval and expanded source-checked bank

Latest private checkpoint: CCEA-Foundation-evidence-checkpoint.zip. The 3,055 question/part anchors and the 72 structurally reconciled paper/scheme pairs are unchanged. 82 source-checked question records are indexed (M1 33, M2 18, M5 11, M6 20); 47 additional one-mark questions were checked against rendered paper and mark-scheme pages and independently calculated using exact arithmetic. These are AI-assisted development reviews, not teacher approval. Existing 35 source-checked records and prior review history are preserved. 1,077 records have skill labels, mostly provisional. 2,403 mark-bearing records remain pending review; 570 non-mark-bearing structural/parent anchors remain. Six date-unverified pairs remain excluded and 15 PDFs remain missing.

Five supplied examiner reports now supply 450 linked question references, 83 independently worded source-linked teaching notes and 455 provisional whole-question topic links across 307 report questions. The latter are phrase-matched evidence, not verified part-level classifications; broad topics and overlapping skills require review. No verbatim report text is retained. The authenticated GET /api/foundation/examiner endpoint and Examiner Insights section support unit/topic searches and show PDF page references, notes and provisional labels; individual source-record inspection also displays related whole-question evidence. Summary counts now reflect examiner tables. Evidence is separate from official marking criteria and not automatically fed into the generator. A bounded result count and confirmed paper-pair gate apply. Older checkpoints without examiner tables return no evidence.

Offline re-tagging (Poppler required) after examiner metadata ingestion:
```sh
python -m foundation.report_topics --db "$KB_DB" --out /private/examiner_skill_evidence.csv /private/reports/*.pdf
python -m unittest discover -s tests -p test_evidence.py
``
Ten focused tests passed locally; database integrity, prior review preservation, source hash checks, four unit-specific evidence searches and repeat source-review import checks passed. Full server integration/browser acceptance and teacher review remain outstanding. No Phase 2 expansion or live API calls. Continue source review of multi-mark, diagram and contextual questions, improve classification, and collect missing papers/reports. Keep original source documents and private reviewed data outside public Git; seek appropriate CCEA permissions before deployment.

## Phase 2.1 — Foundation Question Studio (local mathematical engine)

User authorised moving onto Phase 2 while preserving the incomplete Phase 1 checkpoint. The latest private database remains CCEA-Foundation-evidence-checkpoint.zip; no database migration or source-review changes are needed. New foundation/studio.py defines 13 original question families: percentage of an amount, fraction of an amount, linear equations, rounding, rectangle area, HCF, LCM, midpoint, ratio sharing, arithmetic sequences, binary conversion, linear nth terms and algebraic index laws. Unit availability is restricted to exact native or inherited skill IDs present in the checkpoint, not assumed from a broad topic name. Difficulty is an uncalibrated parameter-range estimate; marks and rubrics are original proposals for teacher approval. Related-skill evidence means source-checked examples of the same skill/unit, not exact template alignment. Where no source-checked examples exist, label as specification-only. No CCEA question wording or examiner report text is copied.

Authenticated GET /api/foundation/studio-catalog?unit=M1 returns enabled families and evidence metadata. POST /api/foundation/studio accepts unit, family, difficulty (easy, standard, challenge), count (integer 1–10); it generates distinct drafts with independent numeric checks, then persists them atomically under the authenticated owner. Existing draft history and approval are reused. Studio question wording is read-only and server-side edits are rejected until a revalidation workflow is built. Existing M1 pilot is unchanged. No model API call or key is needed for this milestone; model wording/context integration remains a future stage.

Run `python -m unittest discover -s tests -p test_studio.py -v`. Three focused tests passed locally, exercising all 63,869 parameter combinations (13 x 17^3) with correct and deliberately incorrect answers; the latest real private checkpoint also produced 990 distinct-within-batch draft outputs across 99 unit/family/difficulty combinations. The checkpoint hash, 82 verified records, foreign keys and SQLite integrity were unchanged. Unit family counts: M1 5 (3 with related verified evidence), M2 8 (5), M5 7 (3), M6 13 (4). New draft persistence/ownership regression test added to test_foundation.py; the full server/integration/browser suite has not yet been rerun. No public deployment or merge. Next priorities: extend multi-mark and contextual questions, geometry diagrams and stronger rubric/wording validation; then securely configure model API and test the model in a server-only environment. Continue Phase 1 enrichment when new material arrives.

## Phase 2.2 — Contextual multi-part questions and schematic geometry

The studio now has 20 families, with 51 unit-family mappings (M1 7, M2 13, M5 11, M6 20). Seven new families cover discount budgets, composite floor area and cost, trapezium area and cost, Pythagoras and length cost, map-scale return journeys, expected frequencies, and gradient/intercept. Each has two parts, 3–4 proposed marks, worked solutions, independent checks of both answers and explicit follow-through where appropriate. Difficulty still reflects parameter ranges rather than calibrated grades. The probability family uses equally likely draws with replacement. Geometry diagrams are fixed schematics, labelled from the same parameters as their questions, explicitly not drawn to scale. The authenticated asset diagrams.js renders bounded numeric primitives and text using DOM APIs rather than raw SVG markup. Diagrams are shown in batch cards and the saved-draft review view; existing drafts without diagram data still work.

Validation: five focused Python studio/contextual tests passed; 98,260 family/parameter combinations (20 × 17³), of which 34,391 are new contextual combinations checked against deliberately wrong answers to both parts. On the actual private checkpoint, 1,530 test drafts across 153 unit-family-difficulty combinations passed, without changing the database hash, 82 verified records, or integrity/foreign-key checks. Isolated Chromium smoke test passed six mobile schematic cases and two malformed/injection input checks. Reproduce using python -m unittest discover -s tests -p 'test_studio.py' and python -m unittest discover -s tests -p 'test_contextual.py'; optional python tests/browser_diagrams.py (requires Playwright and Chromium). Full authenticated browser/server suite remains outstanding. No API key needed for this milestone. Next implement model adapter and constrained contextual variation, then run live API tests using securely configured credentials. Proposed mark schemes need teacher review; do not imply CCEA approval or calibrated difficulty. No deployment or merge.

## Phase 2.4 — Constrained OpenAI adapter

The optional Studio model mode uses the OpenAI Responses endpoint with strict JSON selection of distinct locally validated candidates and curated wording variants. No free-form model question, answer, rubric or SVG is accepted. Only original candidate wording, public curriculum skill metadata and reference mark counts are sent; no source PDF text, pupil data, teacher notes or keys in the request body. Server configuration uses OPENAI_API_KEY and KB_STUDIO_MODEL. Local mode is independent of the API; failed model requests save no drafts and the teacher can explicitly choose local mode. Model configuration does not imply a successful live connection. Run python -m unittest discover -s tests -p test_studio_ai.py for mock-based tests. To authorise one potentially billable test on a network-enabled local backend with the private checkpoint restored, run python -m foundation.live_studio_check --db /private/foundation.sqlite --live. The command prompts for a hidden key if not already configured and does not persist drafts. The default model is gpt-4.1-mini; choose another compatible model with --model if necessary. Never paste keys into chat or commit them. No live API verification or full application release validation has been performed. Keep the draft PR unmerged.

## Phase 2.4 — Optional AI-assisted selection adapter

The Question Studio now has separate Local and AI-assisted modes. Local remains default, requires no API key, and does not call a model. To enable AI-assisted selection, set the server process's OPENAI_API_KEY and KB_STUDIO_MODEL (a Responses API model supporting Structured Outputs; start with gpt-6-luna if available in the project). The older M1 pilot uses separate KB_MODEL_* variables and is unchanged. The UI reports configuration, not a verified live connection. Obtain a dedicated project key from https://platform.openai.com/api-keys and configure it in the server's secret manager/environment. Never paste the key into chat, a browser form, the repository, or an uploaded file. Use project usage/rate limits, billing controls and monitoring; this is not a hard application spending cap.

For local Windows testing from the repository root after setting KB_DB and KB_USERS per Restore and run, start the server with a hidden key prompt:

```powershell
$env:KB_STUDIO_MODEL = "gpt-6-luna"
python -c "import os,getpass; os.environ['OPENAI_API_KEY']=getpass.getpass('OpenAI project key: '); from foundation.server import main; main()"
```

Open http://127.0.0.1:8080/foundation/web/index.html, authenticate, select AI-assisted selection and generate one M1 percentage draft. This is a live billable request. Local mode can be used again without the key. Do not enable public deployment until access policy, usage controls and live tests are complete.

The adapter sends only original validated candidate wording variants, curriculum labels/page, reference mark counts, and evidence-level metadata. It does not send source PDFs, examiner notes, student data, teacher identities, answers, rubrics or API credentials in the JSON body. The key is passed only as authorization to the fixed OpenAI HTTPS endpoint. One request per batch (1–10 selections; up to 20 candidates); bounded input and output, 20-second socket timeout, no automatic retries/redirects, store=false (not a guarantee of zero service retention). The model can select distinct candidate IDs and pre-authored lexical/context variants only. It cannot write unrestricted questions or modify parameters, answers, diagrams, rubrics or source links. Invalid, duplicate, incomplete or refused output produces a 503 and saves no drafts; local mode remains available. Generated questions still require teacher review; marks and difficulty are not official/calibrated.

Eleven focused tests passed locally, including the actual WSGI handler with simulated model responses, authentication, no-key local operation, failed batch atomicity, draft ownership, approval and malformed/oversize response rejection. On a private copy of CCEA-Foundation-evidence-checkpoint.zip, 153 simulated model calls generated 1,530 drafts across every enabled unit-family-difficulty mapping; all 82 source-checked records, database hash and integrity/foreign keys were unchanged. No live OpenAI requests were made. Full browser and historical integration suite, live model connection, evaluation of selection quality, and broader model-authored question wording remain outstanding. No merge or deployment.

## Prompt-driven question design and examination preview

The authenticated POST /api/foundation/studio-prompt accepts a selected Foundation unit and a 1–500-character teacher request. The model returns a strict structured plan for 1–10 questions within the available unit-specific families, and may decline unsupported requests. Python constructs the wording, solutions, marks and diagrams from bounded parameters and independently validates the answers; unsupported family, out-of-domain parameters, repeated questions, inconsistent declared mark requests or malformed plans are rejected before any drafts are saved. Free-form model-authored text, arbitrary contexts and unsupported diagrams are not accepted. Teachers should verify that the returned questions actually meet the request: semantic interpretation is model-dependent. The selected unit, original template examples, public curriculum skill labels and teacher request are sent to the API; use fictional data only. The existing manual/local generator remains available. No change to database schema or credentials.

New shopping-discount family: three parts (2 + 1 + 1 marks), exact integer-pence arithmetic, reduction, sale price and remaining budget. Available in M1/M2/M5/M6 when the personal-finance skill exists. The exam preview displays subpart marks derived from the proposed rubric, space for working, and any existing schematic. Separate worked answers and proposed marking schemes remain behind teacher review. No automatic assignment or official CCEA approval.

Offline checks: 4,913 shopping parameter combinations with each of three answers deliberately corrupted; focused simulated model plan acceptance/rejection tests and original base-family tests passed in a local harness (not the full final server suite). Real checkpoint: 120 local and 12 mock-AI shopping drafts across all four units; hash unchanged, 82 source-checked records, SQLite integrity OK. JS syntax and part-mark splitting checks passed. Live model prompt mode, full browser and integrated server tests still need local verification. No API call made during these offline tests.

## Reasoning-based difficulty (structured Studio)

The structured mixed-topic generator uses three designed demand levels: Easy (guided direct calculation), Medium (independent application), Hard (linked reasoning, inverse problems, missing information or a practical decision). All 21 supported question families have distinct tasks across these levels. These are designed estimates, not empirically calibrated attainment levels or official CCEA grades. The legacy direct-family and free-prompt endpoints retain their prior behaviour.

Composite floor plans now include guided two-rectangle decomposition, missing-length L shapes, and harder three-strip U-shaped, raised-middle and stepped profiles. Named wall endpoints, dimension ticks and witnesses, label bounds and non-overlap, and polygon area are validated. Independent integer-cell counting checks area, exposed edge counting checks perimeter, and exact integer arithmetic checks whole-pack purchasing. AI only selects bounded parameters; diagram identity and diversity checks remain local. The original CCEA skill evidence and teacher review requirements remain unchanged.

Offline validation: 23 focused tests (including simulated model/transport and hybrid routing), 45,885 structured parameter combinations across all families, 495 locally generated questions against a real private curriculum checkpoint, and 12 representative composite diagrams visually inspected. No live API call was made during these checks. Existing database hash unchanged. Live AI and full integrated browser testing remain required.
