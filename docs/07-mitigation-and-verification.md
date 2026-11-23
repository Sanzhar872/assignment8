# Task 7 - Mitigations and verification

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Each mitigation: pytest BEFORE -> failing test -> minimal fix ->
pytest AFTER -> acceptance criteria -> one commit. No refactoring, no new dependencies (`requirements.txt` unchanged).
All `pytest` runs use `python -m pytest` from the repo root (venv outside the repo, pytest 9.2.0, Python 3.13.15).

---

## Mitigation 1 - R1: corrupted `tasks.json` silently overwritten

- **Risk ID:** R1 (evidence C1 in docs/04-risk-review.md)
- **Commit:** `079a1fa` "Mitigation R1: stop bare except from hiding and overwriting a corrupted tasks.json"
- **Change summary:** `load_tasks` now catches only `FileNotFoundError` (first run -> empty list). Invalid JSON or OS errors
  propagate, so `main` stops before `save_tasks` and the existing file is left untouched.

### Diff summary
```
$ git show --stat 079a1fa
 tests/test_tracker.py | 22 ++++++++++++++++++++++
 tracker.py            |  2 +-
 2 files changed, 23 insertions(+), 1 deletion(-)
```
```diff
--- a/tracker.py
+++ b/tracker.py
@@ -9,7 +9,7 @@ def load_tasks():
     try:
         with open(DATA_FILE) as f:
             return json.load(f)
-    except:
+    except FileNotFoundError:
         return []
```
Tests added (`tests/test_tracker.py`):
```python
CORRUPTED = '[{"id": 1, "title": "Task A", "priority": 1, "done": false}, {"id": 2, "title": "Task B"'


def test_corrupted_tasks_file_is_not_overwritten(tmp_path, monkeypatch):
    """R1: a corrupted tasks.json must never be silently replaced."""
    data_file = tmp_path / "tasks.json"
    data_file.write_text(CORRUPTED)
    monkeypatch.setattr(tracker, "DATA_FILE", str(data_file))
    monkeypatch.setattr(sys, "argv", ["tracker.py", "add", "Task C", "1"])
    try:
        tracker.main()
    except ValueError:  # json.JSONDecodeError is a ValueError
        pass  # failing loudly is acceptable; losing data is not
    assert data_file.read_text() == CORRUPTED


def test_missing_tasks_file_still_means_empty_list(tmp_path, monkeypatch):
    """R1 guard: first run without tasks.json keeps working."""
    monkeypatch.setattr(tracker, "DATA_FILE", str(tmp_path / "tasks.json"))
    assert tracker.load_tasks() == []
```

### BEFORE
```
$ python -m pytest -q   (BEFORE R1, at f862efc)
.....                                                                    [100%]
5 passed in 0.01s
```
New test, before the fix (shows the data loss):
```
>       assert data_file.read_text() == CORRUPTED
E       assert '[{"id": 1, "...one": false}]' == '[{"id": 1, "...le": "Task B"'
E         - [{"id": 1, "title": "Task A", "priority": 1, "done": false}, {"id": 2, "title": "Task B"
E         + [{"id": 1, "title": "Task C", "priority": 1, "done": false}]
tests\test_tracker.py:89: AssertionError
---------------------------- Captured stdout call -----------------------------
Added task 1: Task C
FAILED tests/test_tracker.py::test_corrupted_tasks_file_is_not_overwritten - ...
1 failed, 6 passed in 0.09s
```
(The guard test `test_missing_tasks_file_still_means_empty_list` passed before and after - it is a regression guard,
not a failing test.)

### AFTER
```
$ python -m pytest -q   (AFTER R1 fix)
.......                                                                  [100%]
7 passed in 0.03s
```
CLI re-run of the C1 probe (temp dir):
```
$ printf '...truncated JSON...' > tasks.json
$ python tracker.py add "Task C" 1
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 89 (char 88)     (exit=1)
$ cat tasks.json
[{"id": 1, "title": "Task A", "priority": 1, "done": false}, {"id": 2, "title": "Task B"
```
Acceptance criteria: AC1, AC2, AC3 - their tests PASSED in the 7-test run; AC4 - temp-dir run:
```
Added task 1: Buy milk
[ ] 1. Buy milk (priority 2)
Task 1 completed
[{"id": 1, "title": "Buy milk", "priority": 2, "done": true}]
```

- **Checks not executed:** ruff, mypy (not installed); no UTF-8-console run; non-atomic write (C7) not simulated.
- **Updated score:** L 2 -> 1, I 3 -> 2, score **6 -> 2** (the silent overwrite no longer happens; what remains is a crash with a
  raw traceback when the file is corrupt).
- **Residual risk:** user sees a Python traceback instead of a friendly message; a crash during `save_tasks` can still corrupt
  the file (C7); unreadable file now stops every command until a human repairs it (intended - fail loudly).
- **Human review: DONE** - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

---

## Mitigation 2 - R2: `tasks.json` / secrets can be committed (no `.gitignore`)

- **Risk ID:** R2 (evidence S1 in docs/04-risk-review.md)
- **Commit:** `8280c88` "Mitigation R2: add .gitignore for tasks.json, .env and Python artefacts"
- **Change summary:** new `.gitignore` ignoring `tasks.json`, `.env`, `.env.*`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`,
  `.venv/`, `venv/`. Code unchanged.

### Diff summary
```
$ git show --stat 8280c88
 .gitignore            | 13 +++++++++++++
 tests/test_tracker.py | 18 ++++++++++++++++++
 2 files changed, 31 insertions(+)
```
```diff
+++ b/.gitignore
+# User data - never commit (see AGENTS.md)
+tasks.json
+
+# Secrets
+.env
+.env.*
+
+# Python / tooling artefacts
+__pycache__/
+*.py[cod]
+.pytest_cache/
+.venv/
+venv/
```
Test added (plus imports `shutil`, `subprocess`, `pytest`):
```python
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize(
    "path", ["tasks.json", ".env", "__pycache__/tracker.cpython-313.pyc", ".venv/pyvenv.cfg"]
)
def test_user_data_and_local_files_are_git_ignored(path):
    """R2: user data, secrets and local artefacts must not be stageable by `git add -A`."""
    if shutil.which("git") is None or not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
        pytest.skip("not a git checkout")
    result = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO_ROOT)
    assert result.returncode == 0, f"{path} is not ignored by .gitignore"
```

### BEFORE
```
$ python -m pytest -q   (BEFORE R2, at 079a1fa)
7 passed in 0.03s
```
New test, before the `.gitignore` existed:
```
tests\test_tracker.py:113: AssertionError
FAILED tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[tasks.json]
FAILED tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[.env]
FAILED tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[__pycache__/tracker.cpython-313.pyc]
FAILED tests/test_tracker.py::test_user_data_and_local_files_are_git_ignored[.venv/pyvenv.cfg]
4 failed, 7 passed in 0.22s
```

### AFTER
```
$ python -m pytest -q   (AFTER R2 fix)
11 passed in 0.20s
```
S1 probe re-run (fresh repo from `git archive HEAD` + `git init`, temp dir) - also covers AC4:
```
$ python tracker.py add "Doctor appointment" 1
Added task 1: Doctor appointment
$ python tracker.py list
[ ] 1. Doctor appointment (priority 1)
$ python tracker.py done 1
Task 1 completed
$ git add -A --dry-run | grep -E "tasks.json|pycache"
                                   (no output, grep exit=1)
$ git status --short --ignored
!! tasks.json
```
Acceptance criteria: AC1-AC3 tests PASSED in the 11-test run; AC4 shown above; `tracker.py` not changed by this commit.

- **Checks not executed:** ruff, mypy (not installed). The test is skipped (not failed) outside a git checkout, e.g. in a source zip.
- **Updated score:** L 2 -> 1, I 3 (unchanged: if it still happens, it is still a privacy leak), score **6 -> 3**.
- **Residual risk:** `git add -f tasks.json` bypasses it; a `tasks.json` stored outside the repo root under another name is not
  covered; `.gitignore` does not enforce anything on the remote (no pre-commit hook / CI secret scan).
- **Human review: DONE** - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

---

## Final test totals
```
$ python -m pytest -q
...........                                                              [100%]
11 passed in 0.35s
```
(run at commit `8280c88`.) Test count history: 4 (baseline) -> 5 (characterization)
-> 7 (R1) -> 11 (R2, 4 parametrized cases).
