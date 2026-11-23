# Task 3 - Pattern decision (one refactoring)

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Human review: DONE - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

## 1. Maintainability problem
1. **Duplicated sort conditionals.** At `baseline`, the same three-way `if/elif` (`priority` desc, `title` case-insensitive,
   `id` asc, otherwise stored order) existed twice: `sort_tasks` (`tracker.py:35-42`) and `export_text` (`tracker.py:47-54`).
   Adding a sort key or changing one rule requires two identical edits; forgetting one makes `list` inconsistent.
   `main` (`tracker.py:83`) even calls both, so the list is sorted twice.
2. **Mixed UI and business logic in `main`** (`tracker.py:62-85`): argument parsing, `int()` conversion, persistence calls
   and `print` are all in one function, which is why the CLI has no tests and crashes with tracebacks (see docs/01-baseline.md W2).

Only **one** refactoring was allowed. Problem 1 was chosen because it is fully covered by a characterization test and is a
pure, behaviour-preserving change. Problem 2 is left as a known limitation (it touches error handling, i.e. behaviour,
and overlaps with the Phase 7 mitigations, which must stay minimal).

## 2. Options compared

| Option | Description | Pros | Cons |
|---|---|---|---|
| Strategy pattern | A `SortStrategy` class hierarchy (`PrioritySort`, `TitleSort`, `IdSort`) with a `sort(tasks)` method, selected by name. | Open/closed; each strategy can hold complex logic. | 3+ classes for 3 one-line lambdas; more code than it removes; unusual in a 90-line script. |
| Dict of key functions | `SORT_KEYS = {name: (key_fn, reverse)}`; `sort_tasks` looks up the entry; `export_text` calls `sort_tasks`. | Single source of truth; adding a key = one line; idiomatic Python (functions are first-class, effectively a lightweight strategy). | Unknown-key fallback must be kept explicit; tuple `(key, reverse)` is slightly implicit. |
| No pattern | Keep `sort_tasks`, just make `export_text` call it. | Smallest diff, removes the duplication. | The `if/elif` chain remains; adding a key still means editing control flow. |

## 3. Decision
**Dict of key functions**, plus `export_text` reusing `sort_tasks`. It removes the duplication with the smallest amount of
new structure and keeps the exact behaviour (including "unknown key -> stored order, same list object"). Strategy classes
would be over-engineering for three one-line keys.

## 4. Before / after

Before (`baseline`, `tracker.py:35-54`):
```python
def sort_tasks(tasks, by):
    if by == "priority":
        return sorted(tasks, key=lambda t: t["priority"], reverse=True)
    elif by == "title":
        return sorted(tasks, key=lambda t: t["title"].lower())
    elif by == "id":
        return sorted(tasks, key=lambda t: t["id"])
    return tasks


def export_text(tasks, by="id"):
    # same sorting logic duplicated on purpose-free of reuse
    if by == "priority":
        items = sorted(tasks, key=lambda t: t["priority"], reverse=True)
    elif by == "title":
        items = sorted(tasks, key=lambda t: t["title"].lower())
    elif by == "id":
        items = sorted(tasks, key=lambda t: t["id"])
    else:
        items = tasks
```
After (commit `6bce98b`):
```python
# sort key name -> (key function, reverse)
SORT_KEYS = {
    "priority": (lambda t: t["priority"], True),
    "title": (lambda t: t["title"].lower(), False),
    "id": (lambda t: t["id"], False),
}


def sort_tasks(tasks, by):
    if by not in SORT_KEYS:
        return tasks
    key, reverse = SORT_KEYS[by]
    return sorted(tasks, key=key, reverse=reverse)


def export_text(tasks, by="id"):
    items = sort_tasks(tasks, by)
```
`git diff --stat`: `tracker.py | 29 +++++++++++++----------------  (13 insertions, 16 deletions)`.

## 5. Test evidence

Step 1 - characterization test `test_export_text_characterization` added first (commit `a11e1f7`), run against the
unrefactored code:
```
tests/test_tracker.py::test_export_text_characterization PASSED          [100%]
============================== 5 passed in 0.04s ==============================
```
Step 2 - **agent mistake found and fixed**: after the refactor, a mutation check (title key changed from
`t["title"].lower()` to `t["title"]` in a temp copy) still gave `5 passed`. The original sample titles
(`banana`, `Apple`, `cherry`) sort the same with and without `.lower()`, so the test did not pin case-insensitivity.
`cherry` was changed to `Cherry` (commit `a9d9121`) and re-run on three temp copies:
```
=== baseline ===   (git show baseline:tracker.py)
5 passed in 0.02s
=== current ===    (refactored tracker.py)
5 passed in 0.01s
=== mutant ===     (title sort without .lower())
FAILED tests/test_tracker.py::test_export_text_characterization - AssertionEr...
1 failed, 4 passed in 0.06s
```
Step 3 - after the refactor (commit `6bce98b`):
```
$ python -m pytest -q
.....                                                                    [100%]
5 passed in 0.01s
```

## 6. Acceptance criteria after the refactoring
| ID | Result | Evidence |
|---|---|---|
| AC1 | holds | `test_add_task_appears_in_list` PASSED |
| AC2 | holds | `test_complete_task_sets_done`, `test_complete_unknown_task_returns_none` PASSED |
| AC3 | holds | `test_sort_by_priority_descending`, `test_export_text_characterization` PASSED |
| AC4 | holds | temp-dir run below |

```
$ python tracker.py add "Buy milk" 2
Added task 1: Buy milk
$ python tracker.py add "apple" 1
Added task 2: apple
$ python tracker.py list priority
[ ] 1. Buy milk (priority 2)
[ ] 2. apple (priority 1)
$ python tracker.py list title
[ ] 2. apple (priority 1)
[ ] 1. Buy milk (priority 2)
$ python tracker.py done 1
Task 1 completed
$ cat tasks.json
[{"id": 1, "title": "Buy milk", "priority": 2, "done": true}, {"id": 2, "title": "apple", "priority": 1, "done": false}]
```
Not executed: ruff, mypy (not installed). `main` still sorts twice (`sort_tasks` then `export_text`); harmless, left unchanged
to keep the refactoring to exactly one change.
