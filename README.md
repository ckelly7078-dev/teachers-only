# St Columb's College — Teacher portal
Standalone, independent teacher-only demo extracted from school-platform-demo on 24 November 2026. The original project is not modified. This repository is the canonical source for teacher-specific development.
## Run
Open index.html in a modern browser or serve it with a local static HTTP server. The entry screen is Choose your role, with Teacher as the only option, followed by the Mr Stephenson demo sign-in.
## Current scope
Nine navigable teacher modules:
- Teaching and learning: My classes, Learning resources, Scanned assessment marking, Assessment feedback builder.
- Lesson preparation: Practical room and equipment planner, Cover lesson handover.
- School services: Parent information publisher, Sixth-form course comparison, Exam notice update checker.
The dashboard, My classes and Learning resources now use a shared fictional dataset and browser localStorage. Create teaching groups and learners, create assignments, save completion status and manually entered percentage scores, and create reusable resources linked to class assignments. Dashboard statistics derive from these records. Save each learner row before switching views. No student study app, other role dashboards, real authentication, server backend, live AI or actual student delivery. The other seven modules remain previews. Browser data is local to the current browser and must not contain real pupil data. The teacher portrait is inherited from the original demo; obtain consent before official or public use. Recommend private repository and fictional demo data.
## Development
Read AGENTS.md. Prioritize functional end-to-end workflows, shared class and assessment data, teacher review, and secure server-side storage. The teacher portal can evolve independently of the original.

## Tests
Run `node tests/smoke.cjs` with a current Node.js release. Checks use a mocked DOM and storage, not a full browser. Manual accessibility and browser testing remain necessary.

## Foundation mathematics knowledge base

The Teacher dashboard now opens a separate Curriculum Knowledge Base for CCEA GCSE Mathematics Foundation. M1 is the initial retrieval and practice unit. M2, M5 and M6 have inventory coverage. The nine existing portal modules keep their existing behaviour.

Run the Python service and mount the saved private SQLite checkpoint to use the knowledge base. The static portal also opens independently. The teacher demo sign-in is separate from the credentials protecting the curriculum service.

Setup, ingestion, restoration, retrieval budgets, rights decisions and current verification coverage are in [foundation/README.md](foundation/README.md). Run both test suites from the project root.

```sh
node tests/smoke.cjs
python -m unittest discover -s tests -p 'test_*.py' -v
```

## AS1 Further Mathematics teacher review

The combined localhost service adds an AS1 review link to the teacher dashboard and Foundation Mathematics Studio. The AS1 workspace links back to both. Foundation and AS1 check their configured teacher accounts independently. The static portal and the Foundation-only server retain their original entry points and nine modules. Setup, review queues and integration checks are in the [FM-16BS handover](further_maths/FM16BS-INTEGRATION.md).
