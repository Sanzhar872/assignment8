# AI evidence log

- Tool: Claude Code (desktop app, Code tab), running autonomously from a single long prompt written by the student.
- Model: Claude Opus 5.5 (`claude-opus-5-5`).
- Date: 2026-11-23.
- Human review of every row: PENDING - student review before submission. The student has not reviewed the diffs or re-run the commands.

| Step | Date | Prompt summary | Output used | Problems found | Changes made | Verification |
|---|---|---|---|---|---|---|
| 0 - Locate project / baseline | 2026-11-23 | Find tracker.py, tests, requirements, README; move to repo root if in a subfolder; tag `baseline`. | Found that the git repository itself is `task-tracker/` (the outer `as8/` folder is not a repo), so the project is already at the repo root. No `git mv` needed. `git tag -f baseline` re-pointed the tag to the same commit `efbc9e4`. | pytest was **not installed** in the global Python (`No module named pytest`); ruff and mypy are not installed either. The prompt said not to install ruff/mypy; it did not cover pytest. Agent decision (not student-approved): create a throwaway venv in the agent's temp scratchpad (outside the repo) and run the README setup `pip install -r requirements.txt` there (installed pytest 9.2.0). The global Python and the repo dependencies were not changed. | docs/PROGRESS.md, docs/ai-evidence.md created. No source changes. | `git rev-parse baseline HEAD` both print `efbc9e4104f56ee6ec7b13161b98fbdab8ed35c2`; `pytest` -> `4 passed`. |
| 1 - Baseline analysis | 2026-11-23 | Map repo, run pytest/ruff/mypy, git log/tag, list >=3 weaknesses with evidence; separate facts/assumptions/unverified. | Repo map, 6 weaknesses (W1-W6) each backed by a real command run on a copy of tracker.py in a `mktemp -d` directory. | ruff/mypy not installed -> recorded as not executed. Agent noticed that running the CLI in the repo would create an untracked `tasks.json`, so all CLI probes were run in temp dirs instead. Suggestions about file encoding, concurrency and what ruff would report were **not** verified and are listed separately as UNVERIFIED. | docs/01-baseline.md | `git status` clean except new doc; outputs pasted verbatim. |
