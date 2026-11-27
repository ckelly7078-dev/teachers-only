# FM-16BP - guarded preview boundary (development only)

FM-16BO remains the canonical content baseline. The private FM-16BP assessment and draft notation revisions are not active question payloads and are not included in Git. All scope-watch restrictions remain in force. No teacher approval, empirical calibration, individual visual certification, production renderer certification or FM-17 readiness is asserted.

`preview_bp.PreviewCatalogue` is a source-free integration boundary for a future authenticated teacher service. Both `list_ids(mode=...)` and `get(item_id, mode=...)` use the FM-16BO conservative policy. Retrieval returns explicit `release_allowed=False` and `exam_ready=False`. Approved-exam retrieval is always denied. Do not expose the legacy resolver directly through the application, and do not use a preview as an approved examination item.

The existing Foundation service and static teacher portal have no AS1 selection route; this change does not connect or deploy an AS1 web service. Authentication, authorization and production rendering must be designed and verified before exposing this boundary to users.

Run `python -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. Keep private databases, source materials and item-level teaching evidence outside Git and the web root.
