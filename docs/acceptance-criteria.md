# Acceptance criteria

Based on the real code in `tracker.py` and the tests in `tests/test_tracker.py` at tag `baseline`.
Every criterion must hold after every change (refactoring or mitigation). Run all tests with
`python -m pytest -q` from the repository root.

Human review: PENDING - student review before submission.

| ID | Criterion | Checked by |
|---|---|---|
| AC1 | Adding a task appends exactly one task with the given title, the given priority, `done == False` and a positive integer `id`. | `tests/test_tracker.py::test_add_task_appears_in_list` |
| AC2 | Completing an existing task id sets `done` to `True` and returns that task; completing an unknown id returns `None` and changes nothing. | `tests/test_tracker.py::test_complete_task_sets_done`, `tests/test_tracker.py::test_complete_unknown_task_returns_none` |
| AC3 | Sorting: `priority` sorts highest priority first; `title` sorts case-insensitively; `id` sorts ascending; any other key returns the tasks in their stored order. | `tests/test_tracker.py::test_sort_by_priority_descending` (baseline). Title/id/unknown key and the `export_text` text format are covered by the characterization test added in Phase 3 (`test_export_text_characterization`). |
| AC4 | The command-line usage documented in README.md works: `add "<title>" <priority>`, `list <key>`, `done <id>` print `Added task N: <title>`, the `[ ] N. <title> (priority P)` lines, and `Task N completed`, and the state persists in `tasks.json`. | Manual command run in a temporary directory (never in the repo): `python tracker.py add "Buy milk" 2`, `python tracker.py list priority`, `python tracker.py done 1`, `cat tasks.json`. Output recorded in docs/06-agent-readiness.md. |

Notes
- AC4 is a manual check because there is no CLI test at baseline. It is run in a `mktemp -d` copy so no `tasks.json` is created in the repository.
- Criteria describe *existing* behaviour. Mitigations in Phase 7 may add new criteria; they must not break these four.
