# Task 10 - AI reflection

Written by the student. Wording corrected by Claude Code at the student's request, to match the facts in
docs/ai-evidence.md (see the last row of the evidence log).

During this assignment, I used Claude Opus 5.5 (medium) in Claude Code, giving it one detailed prompt; it read the repository files itself, because `CLAUDE.md` (referencing `@AGENTS.md`) was created during the session and was not auto-loaded at the start. So in this session `AGENTS.md` did not steer the agent; it was produced as an output and will only guide future sessions.

A useful result came from the risk review of `load_tasks` in `tracker.py`. I had suggested that a bare `except:` might hide a corrupted file, and the agent verified it: a truncated `tasks.json` looks empty, so a subsequent `add` overwrites existing tasks. Reproducing this in a temporary directory confirmed the data loss, leaving only "Task C" instead of two tasks. The fix was one line, `except FileNotFoundError:`, and a test that failed before the fix and passed after it confirmed the change. The agent also independently found a `UnicodeEncodeError` when printing non-ASCII titles under `cp1252`.

By contrast, the initial characterization test for `export_text` used `banana`, `Apple`, and `cherry`, which sort identically with or without `.lower()`. A mutation check removing `.lower()` still passed five tests, showing the test could not catch a broken case-insensitive sort; renaming `cherry` to `Cherry` (commit `a9d9121`) caused the mutant to fail. Additionally, the first draft of the `load_tasks` test caught `except Exception` too broadly; the agent narrowed it to `ValueError` before applying the fix.

I personally reviewed the diffs, re-ran the tests, and checked that unverified areas (unrun `ruff` and `mypy`, UTF-8 terminal behavior, branch protection, and non-atomic or concurrent writes) remained marked as unconfirmed. Seeing a broken mutant pass changed how I evaluate test effectiveness. Next time, I will prepare `AGENTS.md` upfront, check test sensitivity against mutations earlier, and install linters and type checkers before starting.
