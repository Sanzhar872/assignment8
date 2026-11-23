# AGENTS.md - instructions for AI coding agents

## Purpose
A small console task tracker in Python. Tasks (id, title, priority, done) are stored in a local
`tasks.json` file. This repository is a university assignment about AI-assisted development,
risk governance and agent readiness, so **evidence and honesty matter more than features**.

## Architecture (real files only)
- `tracker.py` - the whole application:
  - persistence: `load_tasks()`, `save_tasks()` (file `DATA_FILE = "tasks.json"`, relative to the current directory)
  - domain: `add_task()`, `complete_task()`, `sort_tasks()`
  - presentation: `export_text()`
  - CLI: `main()` (parses `sys.argv`: `add`, `done`, `list`)
- `tests/test_tracker.py` - pytest unit tests (imports `tracker` by adding the repo root to `sys.path`).
- `requirements.txt` - test dependency (`pytest`).
- `README.md` - user documentation. `docs/` - assignment deliverables and the AI evidence log.

## Setup
```
python -m venv .venv          # optional; keep the venv out of git
pip install -r requirements.txt
```
Python 3.13 was used for the recorded runs. Only the standard library is used at runtime.

## Safe commands (may be run without asking)
- `python -m pytest -q` / `python -m pytest`
- `git status`, `git diff`, `git log --oneline`, `git show`, `git ls-files`, `git grep`
- Running `python tracker.py ...` **only inside a temporary directory** containing a copy of `tracker.py` (e.g. `mktemp -d`), never in the repo root, so no `tasks.json` is created here.
- Read-only inspection: `cat`, `ls`, `grep`.

## Coding conventions
- Python standard library only; keep functions small and pure where possible (business logic must not print or read `sys.argv`).
- PEP 8 style, 4-space indentation, snake_case names, f-strings for formatting.
- Catch specific exceptions, never a bare `except:`.
- One logical change per commit with a descriptive message. No drive-by refactoring inside a bug fix.

## Test expectations
- `python -m pytest -q` must pass before and after every change; paste the real output into the docs.
- Bug fixes are test-first: add a failing test, show it fails, then fix.
- Every acceptance criterion in `docs/acceptance-criteria.md` must still hold after a change.
- Never claim a check passed if it was not run. ruff/mypy are not installed: say "not executed".

## FORBIDDEN actions
- Reading, creating or committing secrets, credentials, tokens or `.env` files.
- Any deployment or publishing step.
- Destructive commands: `git push --force`, `git reset --hard` on shared history, `rm -rf`, deleting branches or tags, rewriting history.
- Adding new dependencies or upgrading existing ones without asking the human first.
- Pushing to `main` without explicit human approval.
- Putting real personal data into `tasks.json`, or committing `tasks.json` at all.
- Modifying tests to make them pass instead of fixing the code.

## Review gates
1. Tests: `python -m pytest -q` green, output recorded.
2. Acceptance criteria AC1-AC4 re-checked and recorded.
3. Diff reviewed by a human (`git diff baseline..HEAD`); human review status is recorded as PENDING until the student signs off.
4. Risk register (`docs/05-risk-register.md`) updated if the change affects a risk.
5. Only after 1-4: a human merges/pushes to `main`.
