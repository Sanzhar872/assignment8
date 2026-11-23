# Task 1 - Baseline analysis

Analysed state: tag `baseline` = commit `efbc9e4` ("baseline: initial task tracker").
Source code was **not modified** in this phase. Agent: Claude Code, model Claude Opus 5.5, 2026-11-23.
Human review: DONE - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

## 1. Repository map

| Item | Path | Notes |
|---|---|---|
| Entry point | `tracker.py` -> `main()` (`tracker.py:62`), run via `if __name__ == "__main__"` (`tracker.py:88`) | CLI: `python tracker.py add|done|list ...` |
| Module (only one) | `tracker.py` (89 lines) | Persistence: `load_tasks` (l.8), `save_tasks` (l.16). Domain: `add_task` (l.21), `complete_task` (l.27), `sort_tasks` (l.35). Presentation: `export_text` (l.45). CLI parsing + dispatch: `main` (l.62). |
| Data file | `tasks.json` (constant `DATA_FILE`, `tracker.py:5`) | Relative to the current working directory; not in the repository (`git ls-files` does not list it). |
| Dependencies | `requirements.txt` | One line: `pytest` (unpinned). Runtime uses only the standard library (`json`, `sys`). |
| Tests | `tests/test_tracker.py` | 4 unit tests; add, complete, complete unknown, sort by priority. No tests for `export_text`, `load_tasks`, `save_tasks`, `main`. |
| Build scripts | none | No `setup.py`, `pyproject.toml`, `Makefile`, `setup.cfg`, `tox.ini`, CI config (`.github/` does not exist). |
| Docs | `README.md` | Setup, usage, tests. |
| Repo hygiene | no `.gitignore` | `git ls-files` lists only the 4 files above. |

## 2. Commands run and actual output

Python: `Python 3.13.15`. pytest was not in the global interpreter (`No module named pytest`), so the README
setup command `pip install -r requirements.txt` was run in an isolated virtualenv outside the repo
(installed `pytest-9.2.0`). All `pytest` runs below use that venv's interpreter (`python -m pytest`).

```
$ python -m pytest
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\SANJAR\Desktop\uni\se\as8\task-tracker
collected 4 items

tests\test_tracker.py ....                                               [100%]

============================== 4 passed in 0.04s ==============================
```

```
$ python -m ruff --version
...python.exe: No module named ruff
$ python -m mypy --version
...python.exe: No module named mypy
```
ruff and mypy: **not installed / not executed** (also `ruff: command not found`, `mypy: command not found`).

Build step: **none exists** (pure script, no packaging config). Nothing to execute.

```
$ git log --oneline
efbc9e4 baseline: initial task tracker
$ git tag
baseline
```

## 3. Concrete weaknesses (with evidence)

All CLI probes were run on a copy of `tracker.py` in a temporary directory created with `mktemp -d`
(outside the repo) so that no `tasks.json` was written in the repository.

**W1 - Bare `except:` silently hides a corrupted `tasks.json`, which is then overwritten (data loss).**
`tracker.py:9-13`:
```python
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []
```
```
$ cat tasks.json (truncated)
[{"id": 1, "title": "Task A", "priority": 1, "done": false}, {"id": 2, "title": "Task B"
$ python tracker.py list
                          <- empty output, exit=0, no warning
$ python tracker.py add "Task C" 1
Added task 1: Task C
$ cat tasks.json
[{"id": 1, "title": "Task C", "priority": 1, "done": false}]
```

**W2 - Missing argument crashes with an unhandled traceback** (`tracker.py:69`, `title = sys.argv[2]`):
```
$ python tracker.py add
    title = sys.argv[2]
            ~~~~~~~~^^^
IndexError: list index out of range        (exit=1)
```
Same class of problem for non-integer numbers (`tracker.py:70`, `tracker.py:75`):
```
$ python tracker.py add "X" high
ValueError: invalid literal for int() with base 10: 'high'
$ python tracker.py done abc
ValueError: invalid literal for int() with base 10: 'abc'
```

**W3 - No input validation for titles.** `add_task` (`tracker.py:21-24`) accepts anything:
```
$ python tracker.py add "" 3
Added task 2: 
$ python tracker.py add "   " 1
Added task 3:    
```

**W4 - Duplicated sorting logic.** The same three-branch `if/elif` appears in `sort_tasks` (`tracker.py:35-42`) and in
`export_text` (`tracker.py:47-54`); `main` (`tracker.py:83`) calls both, so the list is sorted twice.

**W5 - ID generation is `len(tasks) + 1`** (`tracker.py:22`), which produces duplicates if ids are not contiguous:
```
$ python -c "import tracker; t=[{'id':2,'title':'b','priority':1,'done':False}]; n=tracker.add_task(t,'new'); print([x['id'] for x in t])"
[2, 2]
```

**W6 - Tooling/hygiene gaps.** `requirements.txt` is the single unpinned line `pytest`; no `.gitignore`
(`git status --short --ignored` after a test run shows `!! .pytest_cache/` — ignored only because pytest writes its own
`.gitignore` inside the cache dir); no lint/type checker; no CI.

## 4. OBSERVED FACTS
- 1 source module, 1 test module, 4 tests, all passing with pytest 9.2.0 on Python 3.13.15 (Windows).
- One commit, one tag (`baseline`), remote `origin` = `https://github.com/Sanzhar872/assignment8.git`.
- README usage commands work as documented (see `docs/06-agent-readiness.md`).
- W1-W6 above were reproduced with the exact commands shown.
- `git grep` for `password|secret|token|api_key` and for `eval(|exec(|subprocess|os.system|pickle` returned no matches.

## 5. ASSUMPTIONS
- The intended usage is a single local user running the CLI from the project directory (because `DATA_FILE` is relative to the CWD).
- `tasks.json` is meant to be user data and should never be committed (inferred; not stated anywhere in the repo).
- Priority is meant to be a small integer where higher = more important (inferred from `reverse=True` in the priority sort and the test name `test_sort_by_priority_descending`).
- The Windows/Python 3.13 environment is representative; no other platforms were tried.

## 6. UNVERIFIED AI SUGGESTIONS
(Ideas from the agent that were *not* tested at this stage.)
- Non-ASCII titles may be written with platform-default encoding because `open()` has no `encoding=` argument — not tested.
- A concurrent second process could lose writes (no locking) — not tested.
- ruff would likely flag the bare `except:` (E722) — ruff is not installed, so this is not verified.
- mypy would find nothing useful because there are no type hints — not verified.
