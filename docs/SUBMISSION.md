# Submission checklist - Assignment #05

Prepared by Claude Code (model Claude Opus 5.5) on 2026-11-23.
**Human review: DONE** - see "Student review" below.

- Repository: https://github.com/Sanzhar872/assignment8
- Baseline tag: `baseline` -> `efbc9e4104f56ee6ec7b13161b98fbdab8ed35c2`
- Final commit: the commit that adds this file (see `git log --oneline -1` on `main`; the last content commit before it is `4a4c6e1`).

| # | Deliverable | Status | File |
|---|---|---|---|
| 1 | Repo link + baseline tag + final commit | Done (push recorded in the final evidence-log row) | this file |
| 2 | README with accurate commands | Done - every command run in a fresh copy (evidence log, Final row) | `README.md` |
| 3 | AGENTS.md (+ CLAUDE.md importing it) | Done | `AGENTS.md`, `CLAUDE.md` |
| 4 | Acceptance criteria | Done (AC1-AC4) | `docs/acceptance-criteria.md` |
| 5 | Real test output | Done (below; also in docs/01, 03, 07) | this file |
| 6 | Baseline analysis | Done | `docs/01-baseline.md` |
| 7 | Pattern decision (one refactoring) | Done | `docs/03-pattern-decision.md` |
| 8 | Risk review (verified, classified) | Done - 14 candidates, 9 CONFIRMED | `docs/04-risk-review.md` |
| 9 | Risk register, 5+ findings across 3+ categories | Done - 9 rows, 5 categories | `docs/05-risk-register.md` |
| 10 | Readiness audit (before + after) | Done - level 2 before and after | `docs/06-agent-readiness.md` |
| 11 | Two mitigation records | Done - R1 (`079a1fa`), R2 (`8280c88`) | `docs/07-mitigation-and-verification.md` |
| 12 | Background-agent safeguards | Done (hypothetical; no agent run) | `docs/08-background-agent-safeguards.md` |
| 13 | Release decision | Done - **CONDITIONAL** | `docs/09-release-decision.md` |
| 14 | 200-300 word reflection | Done (291 words) - written by the student, wording corrected by the agent on request; **student must confirm the claims** | `docs/10-ai-reflection.md` |
| 15 | AI evidence appendix | Done | `docs/ai-evidence.md` |
| 16 | No credentials or fabricated results | Checked by the agent (below); covered by the student review of 2026-11-23 | - |
| 17 | Human review of all AI changes | Done - 2026-11-23, see "Student review" | this file |

## Final test output (real)
```
$ python -m pytest -q
...........                                                              [100%]
11 passed in 0.16s
```
ruff / mypy: not installed, not executed. Build: no build step exists.

## `git diff baseline..HEAD --stat` (real, at `4a4c6e1`, before this file was added)
```
 .gitignore                             |  13 +++
 AGENTS.md                              |  57 +++++++++
 CLAUDE.md                              |   1 +
 README.md                              |  31 ++++-
 docs/01-baseline.md                    | 134 +++++++++++++++++++++
 docs/03-pattern-decision.md            | 130 +++++++++++++++++++++
 docs/04-risk-review.md                 | 179 ++++++++++++++++++++++++++++
 docs/05-risk-register.md               |  51 ++++++++
 docs/06-agent-readiness.md             | 100 ++++++++++++++++
 docs/07-mitigation-and-verification.md | 206 +++++++++++++++++++++++++++++++++
 docs/08-background-agent-safeguards.md |  95 +++++++++++++++
 docs/09-release-decision.md            |  52 +++++++++
 docs/10-ai-reflection.md               |  38 ++++++
 docs/PROGRESS.md                       |  25 ++++
 docs/acceptance-criteria.md            |  18 +++
 docs/ai-evidence.md                    |  20 ++++
 tests/test_tracker.py                  |  80 +++++++++++++
 tracker.py                             |  31 +++--
 18 files changed, 1239 insertions(+), 22 deletions(-)
```

## No secrets / no user data committed
```
$ git ls-files | grep -i -E "tasks\.json|\.env|secret|key|token"
                     (no output, exit=1)
$ git grep -n -i -E "password|secret_|api_key|apikey|BEGIN (RSA|OPENSSH)|ghp_|sk-"
```
The second command matched only documentation text (every hit was the substring `sk-` inside `risk-` or `task-`, or the words
`password`/`secret` inside descriptions of the checks themselves) - no credentials. `tasks.json` is git-ignored and was never
committed (`git log --all --oneline -- tasks.json` is empty). The local machine path in the pasted pytest output (`rootdir:` line in
docs/01-baseline.md) was redacted to `<local path to task-tracker, redacted>`; nothing else in that output was changed.

## Student review
- Reviewer: Sanzhar872 (student), 2026-11-23.
- Diffs `baseline..HEAD` and documents: reviewed (stated by the student).
- Tests re-run by the student in their own `.venv` (Windows PowerShell), `python -m pytest -v`:
```
tests/test_tracker.py::test_add_task_appears_in_list PASSED
tests/test_tracker.py::test_complete_task_sets_done PASSED
tests/test_tracker.py::test_complete_unknown_task_returns_none PASSED
tests/test_tracker.py::test_sort_by_priority_descending PASSED
tests/test_tracker.py::test_export_text_characterization PASSED
tests/test_tracker.py::test_corrupted_tasks_file_is_not_overwritten PASSED
tests/test_tracker.py::test_missing_tasks_file_still_means_empty_list PASSED
tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[tasks.json] PASSED
tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[.env] PASSED
tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[__pycache__/tracker.cpython-313.pyc] PASSED
tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[.venv/pyvenv.cfg] PASSED
11 passed in 0.19s
```
  (transcribed from the student's terminal screenshot; percentage column omitted)

## Still open
- Release conditions G2-G4 in docs/09-release-decision.md (lint/type checks, pinned dependencies, R3 fix).
- (The "(medium)" effort setting in the reflection was confirmed by the student on 2026-11-23.)
