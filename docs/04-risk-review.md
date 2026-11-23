# Task 4 - Read-only risk review

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Human review: DONE - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

Scope: code at commit `7a2d867` (after the Phase 3 refactoring; `load_tasks`, `save_tasks`, `add_task`, `main`
are byte-identical to `baseline`). **No tracked source or test file was modified in this phase** (see the
`git status` at the end). All dynamic checks ran on copies of `tracker.py` in directories created with
`mktemp -d` outside the repository (Git Bash, Windows, Python 3.13.15).

Classification: **CONFIRMED** = reproduced with a command whose real output is shown;
**PLAUSIBLE-UNVERIFIED** = reasonable but not demonstrated; **UNSUPPORTED** = searched for and not found.

## Summary

| ID | Category | Candidate risk | Classification |
|---|---|---|---|
| C1 | Correctness / data integrity | Bare `except:` hides a corrupted `tasks.json`; next save overwrites it | CONFIRMED |
| C2 | Correctness | `id = len(tasks) + 1` creates duplicate ids; `done` hits the wrong task | CONFIRMED |
| C3 | Correctness | Empty / whitespace-only titles accepted | CONFIRMED |
| C4 | Correctness | Non-integer priority: CLI traceback; API accepts a string and breaks sorting | CONFIRMED |
| C5 | Correctness / UX | Missing argv -> unhandled `IndexError` | CONFIRMED |
| C6 | Correctness (portability) | Non-ASCII title crashes printing on a cp1252 stdout | CONFIRMED (environment-dependent) |
| D1 | Dependency | `requirements.txt` unpinned (`pytest`) | CONFIRMED (fact); consequence PLAUSIBLE-UNVERIFIED |
| S1 | Security / privacy | No `.gitignore`: `tasks.json` (user data) and caches are stageable by `git add -A` | CONFIRMED |
| M1 | Maintainability | No lint / type checks / CI | CONFIRMED |
| A1 | Agent operations | AGENTS.md rules are advisory only; nothing enforces them (no hooks, no CI, branch protection unknown) | PLAUSIBLE-UNVERIFIED |
| C7 | Correctness | Non-atomic `save_tasks`: crash mid-write leaves a truncated file (then C1 wipes it) | PLAUSIBLE-UNVERIFIED |
| C8 | Correctness | Two concurrent processes lose updates (no locking) | PLAUSIBLE-UNVERIFIED |
| S2 | Security | Hard-coded secrets / credentials in the repo | UNSUPPORTED |
| S3 | Security | Code injection (`eval`, `exec`, `subprocess`, `os.system`, `pickle`) | UNSUPPORTED |

14 candidates across 5 categories (correctness, maintainability, security, dependency, agent operations).

## CONFIRMED

### C1 - Bare `except:` + overwrite = silent data loss
`tracker.py:8-13`
```python
def load_tasks():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []
```
`main` then calls `save_tasks(tasks)` after `add`/`done`, writing the (empty + new) list over the file.
```
$ printf '[{"id": 1, "title": "Task A", "priority": 1, "done": false}, {"id": 2, "title": "Task B"' > tasks.json
$ python tracker.py list
                                   <- nothing printed, exit=0
$ python tracker.py add "Task C" 1
Added task 1: Task C
$ cat tasks.json
[{"id": 1, "title": "Task C", "priority": 1, "done": false}]
```
Additional evidence that the bare `except:` swallows non-JSON errors too (directory named `tasks.json`):
```
$ mkdir tasks.json; python -c "import tracker; print(tracker.load_tasks())"
[]
```

### C2 - Duplicate ids from `len(tasks) + 1`
`tracker.py:21-22`: `task = {"id": len(tasks) + 1, ...}`. Any non-contiguous id list (hand-edited file, future delete feature) collides.
```
$ printf '[{"id": 2, "title": "kept", "priority": 1, "done": false}]' > tasks.json
$ python tracker.py add "new" 1
Added task 2: new
$ python tracker.py done 2
Task 2 completed
$ cat tasks.json
[{"id": 2, "title": "kept", "priority": 1, "done": true}, {"id": 2, "title": "new", "priority": 1, "done": false}]
```
The user wanted to complete "new" (id 2) but "kept" was completed. Note: the current CLI has no delete command, so the
trigger needs an externally edited file; likelihood is low today.

### C3 - Empty / whitespace titles
`tracker.py:21-24` performs no validation.
```
$ python tracker.py add "" 3
Added task 1: 
$ python tracker.py add "   " 1
Added task 2:    
$ python tracker.py list
[ ] 1.  (priority 3)
[ ] 2.     (priority 1)
```

### C4 - Non-integer priority
CLI (`tracker.py` `main`, `priority = int(sys.argv[3]) ...`):
```
$ python tracker.py add "X" high
ValueError: invalid literal for int() with base 10: 'high'      (exit=1, full traceback)
```
API: `add_task` stores whatever it gets; sorting then fails:
```
$ python -c "import tracker; t=[]; tracker.add_task(t,'a',1); tracker.add_task(t,'b','3'); tracker.sort_tasks(t,'priority')"
TypeError: '<' not supported between instances of 'int' and 'str'
```

### C5 - Missing arguments -> `IndexError`
`main`: `title = sys.argv[2]` and `int(sys.argv[2])` without length checks.
```
$ python tracker.py add
IndexError: list index out of range      (exit=1)
$ python tracker.py done
IndexError: list index out of range      (exit=1)
```

### C6 - Non-ASCII title crashes output on a cp1252 stdout
`print(f"Added task ...{task['title']}")` in `main`. Run with stdout piped in Git Bash on Windows:
```
$ python tracker.py add "Молоко" 2
UnicodeEncodeError: 'charmap' codec can't encode characters in position 14-19: character maps to <undefined>   (exit=1)
$ cat tasks.json
[{"id": 1, "title": "Молоко", "priority": 2, "done": false}]
$ python tracker.py list
UnicodeEncodeError: 'charmap' codec can't encode characters in position 7-12: ...
$ python -c "import sys; print(sys.stdout.encoding)"
cp1252
```
The task is saved (json escapes it), but the command reports a crash and `list` becomes unusable in this environment.
Depends on the console encoding; a UTF-8 terminal was not tested.

### D1 - Unpinned dependency
```
$ cat requirements.txt
pytest
```
Today `pip install -r requirements.txt` installed `pytest-9.2.0` (plus `colorama-0.4.6 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0`).
Fact CONFIRMED; the consequence (a future pytest release breaking the suite or changing behaviour) is PLAUSIBLE-UNVERIFIED.

### S1 - No `.gitignore`: user data and caches can be committed
```
$ git ls-files
README.md  requirements.txt  tests/test_tracker.py  tracker.py   (+ docs added by the agent; no .gitignore)
```
Throwaway repo built with `git archive HEAD | tar -x` + `git init` in a temp dir:
```
$ python tracker.py add "Doctor appointment" 1
Added task 1: Doctor appointment
$ git status --short --untracked-files=all
...
?? tasks.json
...
$ git add -A --dry-run | grep -E "tasks.json|pycache"
add 'tasks.json'
```
`.pytest_cache/` is only excluded because pytest writes its own `.gitignore` inside it.

### M1 - No lint / type checks / CI
```
$ python -m ruff --version   -> No module named ruff
$ python -m mypy --version   -> No module named mypy
$ ls .github                 -> No such file or directory
```
No `pyproject.toml`, `setup.cfg`, `tox.ini`, `Makefile` (find returned nothing). The bare `except:` (C1) is exactly the kind of
issue a linter (E722) would have flagged — that specific ruff result is not verified because ruff is not installed.

## PLAUSIBLE-UNVERIFIED
- **A1 - Agent instructions are not enforced.** `AGENTS.md` forbids force-push, committing `tasks.json`, etc., but there is no
  pre-commit hook (`.git/hooks` only contains `*.sample` files), no CI, no `.claude/settings.json` permission rules in the repo.
  GitHub branch protection for `main` was **not checked**. An agent that ignores or never loads AGENTS.md could violate it.
  Not demonstrated (doing so would mean performing a forbidden action).
- **C7 - Non-atomic save.** `save_tasks` opens the file with `"w"` (truncate) then writes; a crash/kill between the two leaves an
  empty/partial file, which C1 would then silently discard. Not simulated.
- **C8 - Lost updates under concurrency.** Two processes doing load -> modify -> save interleaved would lose one update. Not tested.

## UNSUPPORTED (searched, not found)
- **S2 - Secrets in the repo.** `git grep -n -i -E "password|secret|token|api_key|apikey"` -> no matches (exit 1).
  `git ls-files | grep -E "^\.gitignore$|\.env"` -> no matches. `git log --all --oneline -- tasks.json` -> empty (never committed).
- **S3 - Code injection.** `git grep -n -E "eval\(|exec\(|subprocess|os\.system|pickle"` -> no matches (exit 1). Input is only
  used as data in `json.dump` and f-strings.

## Read-only check
```
$ git status --short
?? docs/04-risk-review.md
```
(Run before committing this document; no tracked source/test files modified.)
