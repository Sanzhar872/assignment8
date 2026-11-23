# Task 8 - Background-agent safeguards (hypothetical task: "add CSV export")

**No background agent was run.** This is a documentation-only plan describing how a background/asynchronous coding agent
*would* be allowed to implement a hypothetical feature, "add CSV export", in this repository.
Author: Claude Code, model Claude Opus 5.5, 2026-11-23. Human review: PENDING - student review before submission.

## 1. Task definition
Add `export_csv(tasks, by="id") -> str` to `tracker.py` (columns `id,title,priority,done`, same sort keys as `sort_tasks`,
using the standard-library `csv` module) and a CLI command `python tracker.py csv [key]` that prints it.
Done = new tests pass, all existing tests pass, AC1-AC4 still hold, README documents the command.

## 2. Isolation
- Runs on a dedicated branch in a separate worktree, never on `main`:
  ```
  git worktree add ../task-tracker-csv -b agent/csv-export main   # branch from the current, reviewed main
  ```
- The agent's working directory is the worktree only; it has no access to the user's real `tasks.json` (tests use `tmp_path`).
- No network access: nothing to download, no package installs (stdlib `csv` only).
- Remote: the agent may **not** push. A human pushes the branch after review, or the agent pushes only `agent/csv-export` if the
  human explicitly allows it - never `main`.

## 3. Allowed files
| File | Allowed change |
|---|---|
| `tracker.py` | add `export_csv` and the `csv` branch in `main`; no other edits |
| `tests/test_tracker.py` | add tests only; existing tests must not be modified or deleted |
| `README.md` | document the `csv` command |
| `docs/agent-runs/csv-export.md` | the run report (new file) |
Everything else (`requirements.txt`, `.gitignore`, `AGENTS.md`, `CLAUDE.md`, other docs, `.git/` config, hooks) is read-only.

## 4. Allowed commands
- `python -m pytest -q`, `python -m pytest -v`
- `git status`, `git diff`, `git add <allowed files>`, `git commit` (on `agent/csv-export` only), `git log`, `git show`
- `python tracker.py ...` **only inside a `mktemp -d` copy**
- read-only `cat`, `ls`, `grep`

## 5. Forbidden operations
- Any `pip install`, editing `requirements.txt`, adding/upgrading dependencies.
- `git push` (any), `git push --force`, `git reset --hard`, `git rebase` of shared branches, deleting branches/tags (esp. `baseline`),
  `git checkout main`, merging.
- Reading or writing `.env`, credentials, tokens, SSH keys, or the user's real `tasks.json`.
- Network access, deployment, publishing, opening PRs without a human.
- Deleting or weakening existing tests or acceptance criteria; `pytest -k`/`--deselect` to hide failures.
- `rm -rf` or any deletion outside the worktree.

Enforcement (not just instructions): Claude Code permission rules in the worktree's `.claude/settings.json`
(allow-list for the commands above, deny `Bash(git push:*)`, `Bash(pip:*)`, `Read(.env*)`, `Bash(rm:*)`), branch protection
on `main` (required review), and a pre-commit check that `requirements.txt` is unchanged. These are recommendations; none of
them is configured in this repository today (see R9).

## 6. Limits
- Wall-clock time: max **30 minutes**.
- Tool calls: max **60**; max **3** consecutive failing test runs - then stop and report.
- Diff size: max ~150 changed lines across the allowed files; larger -> stop and ask.
- On hitting any limit the agent stops, commits nothing further and writes the report with status "INCOMPLETE".

## 7. Required artefacts (in `docs/agent-runs/csv-export.md` + the branch)
1. Change summary (what and why, 5-10 lines).
2. Full diff: `git diff main...agent/csv-export` and `git show --stat` per commit.
3. Test logs: real `python -m pytest -v` output **before** and **after**, plus the failing-test-first run.
4. Build result: "no build step exists" (state it explicitly, do not invent one).
5. Acceptance criteria AC1-AC4 + new criterion "AC5: csv export" with pass/fail evidence.
6. Risk notes: new risks introduced (e.g. CSV/formula injection when titles start with `=`, `+`, `-`, `@` and the file is opened in
   a spreadsheet; commas/quotes/newlines in titles; encoding of non-ASCII titles - cf. R8), and checks not executed (ruff/mypy).
7. List of every command run (tool-call log).

## 8. Mandatory human review before merge or deploy
Nothing is merged into `main` and nothing is released until a human has completed this checklist:

- [ ] Diff touches only the allowed files; no change to `requirements.txt`, `.gitignore`, `AGENTS.md`.
- [ ] No existing test was modified or deleted (`git diff -- tests/` shows only additions).
- [ ] Re-ran `python -m pytest -q` myself on the branch - result matches the report.
- [ ] Ran the CLI in a temp dir: `add`, `list`, `done`, `csv`, `csv priority`.
- [ ] Titles containing `,`, `"`, newlines and a leading `=` were tested; CSV injection decision recorded.
- [ ] No secrets, `.env`, `tasks.json` or personal data in the diff (`git diff --name-only`, `git grep -i password`).
- [ ] Report claims match evidence (no invented outputs; "not executed" where applicable).
- [ ] Risk register updated if a new risk was introduced.
- [ ] Reviewer name + date recorded; then merge with a merge commit (no squash-rewrite of evidence).

## 9. Failure and rollback handling
- **Agent fails / exceeds limits / report incomplete:** discard the work:
  ```
  git worktree remove ../task-tracker-csv
  git branch -D agent/csv-export        # local only, never pushed
  ```
  (performed by the human, not by the agent).
- **Problem found after merge:** do not rewrite history; create a revert commit:
  ```
  git revert <merge-commit> -m 1
  ```
- **Repository badly damaged:** restore the known-good state from the `baseline` tag on a new branch and cherry-pick verified
  commits, e.g. `git switch -c recovery baseline` (the tag `baseline` = `efbc9e4` is never moved or deleted).
- **Data:** the user's `tasks.json` is outside the agent's reach and git-ignored; if it was touched, restore it from the user's own
  backup - git cannot restore it because it is (correctly) not versioned.
- Every incident is logged in `docs/ai-evidence.md` with what happened and how it was rolled back.
