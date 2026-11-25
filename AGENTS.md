# Instructions for coding agents
- Work in ckelly7078-dev/teachers-only. Do not modify school-platform-demo unless separately requested.
- Keep Choose your role as the initial screen, Teacher as its only option, and the teacher sign-in and dashboard. Do not add student or other staff roles. Teacher workflows may coordinate with other staff later through explicit integrations.
- Retain navy, blue and gold St Columb's-inspired branding and the nine existing module routes. Respect accessibility, mobile layout and keyboard navigation.
- My classes and Learning resources have functional local demo workflows; seven remaining modules are prototypes, not live operations. Do not invent real records or pretend AI is connected. For future scanned marking, require rubric-based evidence, teacher approval and uncertainty flags; never silently assign grades. Assessment feedback should derive from approved marks.
- Use fictional sample records, no real pupil data or API keys in Git. No live uploads or publishing until secure authentication, authorization, storage, retention and consent are designed.
- Prefer small reviewable commits; test role selection, sign-in, all nine routes, and changed functionality. Update README and document decisions. For substantial features use feature branches and review before merging.
- Current baseline smoke test: role screen one button, sign-in, dashboard nine tiles, all nine module routes render with back navigation, invalid student route rejected. This is a mocked DOM test, not a full browser test.

- Preserve local storage key `scc-teacher-workspace-v1` and shared class, pupil, resource and assignment ID relationships. Scores are manually recorded percentages, not AI grades. Run `node tests/smoke.cjs` and browser tests before releases.

## Foundation curriculum work

The Foundation scope is M1, M2, M5 and M6. M1 is the reference implementation. Consult foundation/README.md and the private checkpoint before another ingestion run. Store originals and SQLite volumes outside the checkout and web root. Keep the existing static demo usable. The dedicated teacher service supplies verified records at runtime. Run the existing smoke suite and the Python integration suite when changing this path. Treat source-checked annotations, machine-suggested classifications and teacher approval as distinct states. Continue verification in M1 before rolling out question extraction in another unit.
