# Task 5 - Risk register

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Human review: PENDING - student review before submission.
Evidence IDs (C1, S1, ...) refer to docs/04-risk-review.md. Scale: Likelihood 1 = rare, 2 = possible, 3 = likely;
Impact 1 = annoyance, 2 = wrong result / rework, 3 = data loss or privacy exposure. Score = L x I (max 9).
Owner of every row: the student (Sanzhar872).

## Register (state BEFORE mitigations, scores at commit `275462b`)

| ID | Category | Cause -> Event -> Consequence | Affected component | Evidence | Likelihood (1-3) | Impact (1-3) | Score (L x I) | Mitigation | Owner (student) | Verification plan | Residual risk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Correctness / data integrity | Bare `except:` in `load_tasks` -> a corrupted/partial/unreadable `tasks.json` is treated as an empty list -> next `add`/`done` overwrites the file: **silent loss of all tasks** | `tracker.py` `load_tasks` (l.8-13), `save_tasks`, `main` | C1, CONFIRMED | 2 | 3 | **6** | Catch only `FileNotFoundError`; let JSON/OS errors surface so nothing is overwritten | Student | Failing test first: corrupted file + `main add` must not change the file; full pytest; AC1-AC4 | Corruption still possible (non-atomic write, C7); user sees a traceback instead of a friendly message |
| R2 | Security / privacy | No `.gitignore` -> running the CLI in the repo creates `tasks.json` (personal tasks) -> `git add -A` + push publishes it to GitHub, where history keeps it | repo root, `tasks.json`, caches | S1, CONFIRMED | 2 | 3 | **6** | Add `.gitignore` for `tasks.json`, `.env`, `__pycache__/`, `.pytest_cache/`, `.venv/` | Student | Failing test first: `git check-ignore -q tasks.json` etc. must succeed; `git ls-files` shows no data | `git add -f` still bypasses it; does not remove data that was committed earlier (none was, `git log --all -- tasks.json` is empty) |
| R3 | Correctness / UX | No argv/int validation in `main` -> `add` without title, `done` without id, or `priority`=`high` -> unhandled `IndexError`/`ValueError` traceback, exit 1 | `tracker.py` `main` | C4, C5, CONFIRMED | 3 | 1 | 3 | Validate argv length and `int()` in `main`, print usage, non-zero exit | Student | CLI tests with `monkeypatch` on `sys.argv` + `capsys` | Low |
| R4 | Maintainability | No linter / type checker / CI -> defects like the bare `except:` are not caught automatically -> regressions reach `main` | whole repo | M1, CONFIRMED | 2 | 2 | 4 | Add ruff + mypy (pinned) and a CI workflow - **requires human approval** (new dependencies) | Student | `ruff check .` and `mypy tracker.py` exit 0 in CI | Depends on rules chosen |
| R5 | Correctness | `id = len(tasks)+1` -> non-contiguous ids (hand-edited file / future delete) -> duplicate ids -> `done N` completes the wrong task | `tracker.py` `add_task` (l.22) | C2, CONFIRMED | 1 | 2 | 2 | `max((t["id"] for t in tasks), default=0) + 1` | Student | Unit test with ids `[2]` -> new id 3 | Low |
| R6 | Correctness | No title validation -> `""`/`"   "` accepted -> blank, unidentifiable tasks | `tracker.py` `add_task` | C3, CONFIRMED | 2 | 1 | 2 | Reject `title.strip() == ""` | Student | Unit test expects `ValueError` | Low |
| R7 | Dependency | `requirements.txt` = `pytest` (unpinned) -> a future pytest release changes behaviour -> tests break or differ between machines | `requirements.txt` | D1, CONFIRMED (fact) | 2 | 1 | 2 | Pin `pytest==9.2.0` (version installed 2026-11-23) - **requires human approval** | Student | Fresh venv install + pytest | Transitive deps still unpinned |
| R8 | Correctness / portability | Non-ASCII title + cp1252 stdout -> `UnicodeEncodeError` on `print` -> `add`/`list` crash on some Windows consoles | `tracker.py` `main` print calls | C6, CONFIRMED (env-dependent) | 2 | 1 | 2 | Document `PYTHONUTF8=1` or reconfigure stdout | Student | Re-run probe with UTF-8 mode | Environment-dependent |
| R9 | Agent operations | AGENTS.md rules are advisory -> an agent ignores them (force-push, commits `tasks.json`, adds dependencies) -> damage to shared history or data leak | AGENTS.md, git remote | A1, PLAUSIBLE-UNVERIFIED | 2 | 2 | 4 | Branch protection on `main`, pre-commit hook, Claude Code permission deny-rules, human review gate | Student | Check GitHub branch-protection settings; try a denied command | Not verified at all yet |

Arithmetic check: R1 2x3=6, R2 2x3=6, R3 3x1=3, R4 2x2=4, R5 1x2=2, R6 2x1=2, R7 2x1=2, R8 2x1=2, R9 2x2=4.
9 rows, 5 categories (correctness, security/privacy, maintainability, dependency, agent operations); 8 rows CONFIRMED.

## Top two CONFIRMED risks for corrective action
1. **R1 - silent data loss (score 6).** Highest impact (3): the user's whole task list is destroyed without any warning, and
   the failure is silent (exit 0, empty list), so it would not even be noticed. Fix is small and local (one `except` clause)
   and fully testable without new dependencies.
2. **R2 - `tasks.json` can be committed and pushed (score 6).** Same score; impact is a privacy exposure on a GitHub remote
   that is hard to undo (history), and the README's own usage instructions create `tasks.json` in the repo directory. Fix is a
   one-file change with no runtime effect.

Why not the others: R4 and R9 (score 4) would need new dependencies or remote settings (requires human approval; R9 is not
even confirmed). R3 (score 3) only produces a traceback - no data is changed because the crash happens before `save_tasks`.

## After mitigations
See the "After mitigations" section appended in Phase 7 below.
