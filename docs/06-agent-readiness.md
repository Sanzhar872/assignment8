# Task 6 - Agent readiness audit

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Human review: DONE - reviewed by the student (Sanzhar872) on 2026-11-23; see docs/SUBMISSION.md.

Levels used:
- **1 Baseline** - code runs and has some tests, but nothing tells an agent how to work safely; setup/hygiene gaps.
- **2 Documented** - accurate README + agent instructions (AGENTS.md) with setup, safe commands, prohibited actions and
  review gates; tests run green from the documented commands.
- **3 Agent-ready** - level 2 **plus** reproducible pinned setup, automated quality gates (lint/type/tests in CI), repo
  safeguards that actually enforce the rules (.gitignore, hooks/permissions/branch protection), and no open high-score
  CONFIRMED risks.

## Part A - State BEFORE mitigations (commit `ec6ac21`)

### README commands, actually run
Fresh virtualenv (outside the repo), PATH pointing at it, repo root:
```
$ pip install -r requirements.txt
Successfully installed colorama-0.4.6 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.2.0
$ pytest
tests\test_tracker.py .....                                              [100%]
============================== 5 passed in 0.05s ==============================
exit=0
```
Usage commands, in a `mktemp -d` copy (so no `tasks.json` lands in the repo):
```
$ python tracker.py add "Buy milk" 2
Added task 1: Buy milk
$ python tracker.py list priority
[ ] 1. Buy milk (priority 2)
$ python tracker.py done 1
Task 1 completed
$ python tracker.py list
[x] 1. Buy milk (priority 2)
$ python tracker.py
Usage: python tracker.py add|done|list ...
```

### Evaluation

| Area | Finding | Evidence | Status |
|---|---|---|---|
| Structure | One module + one test module, clear function split (persistence / domain / presentation / CLI); `main` mixes UI and logic | `tracker.py`, docs/03-pattern-decision.md | OK (small) |
| README accuracy | All documented commands work as written. Gaps: no Python version, no venv advice, sort keys `title`/`id` and the location of `tasks.json` (current directory) not documented, no link to docs/ | run above | Partly |
| Reproducible setup | `pip install -r requirements.txt` worked twice (2 venvs) and gave identical versions today, but nothing pins them | `requirements.txt` = `pytest` | Weak |
| Pinned dependencies | No | R7 / D1 | Missing |
| Tests | 5 unit tests, green; no CLI, persistence or error-path tests | `pytest` output above | Partial |
| Lint / type checks | ruff, mypy not installed, no config | M1 | Missing |
| Build | No build step exists (plain script) - nothing to build or verify | `find` for pyproject/setup.py/Makefile: none | N/A |
| Logging | None (`git grep logging` -> no match); errors are either swallowed (`except:`) or raw tracebacks | R1, R3 | Missing |
| Security safeguards | No `.gitignore`; `tasks.json` stageable by `git add -A`; no secrets found in repo | S1 (CONFIRMED), S2 (UNSUPPORTED) | Missing |
| AGENTS.md | Present (Phase 2): purpose, real architecture, setup, safe commands, prohibited actions, review gates, test expectations; `CLAUDE.md` imports it | `AGENTS.md`, `CLAUDE.md` | Present |
| Enforcement of AGENTS.md | None: no hooks (only `*.sample`), no `.claude/settings.json`, no CI; branch protection not checked | A1 / R9 | Missing |
| Open CONFIRMED high risks | R1 (score 6), R2 (score 6) | docs/05-risk-register.md | Open |

### Level BEFORE mitigations: **2 - Documented**
Justification: README commands are accurate and were executed successfully; AGENTS.md/CLAUDE.md give an agent the purpose,
real architecture, safe commands, forbidden actions and review gates; tests are green from the documented command.
It is **not level 3** because evidence for the level-3 criteria is missing:
- no pinned dependencies (unpinned `pytest`);
- no lint/type checks and no CI (nothing runs automatically);
- no `.gitignore`, no hooks/permission rules/branch protection - AGENTS.md is advisory only;
- two open CONFIRMED score-6 risks (R1 data loss, R2 data exposure).

Note: at the untouched `baseline` tag (no AGENTS.md, no acceptance criteria) the repository would only have been
**level 1 - Baseline**; the jump to 2 comes entirely from documentation added in Phase 2.

## Part B - After mitigations (re-evaluated at commit `0b27bb6`)

Commands re-run:
```
$ python -m pytest -q
11 passed in 0.15s
$ python -m ruff --version   -> No module named ruff
$ python -m mypy --version   -> No module named mypy
$ cat requirements.txt
pytest
$ git ls-files | grep -E "gitignore|tasks.json"
.gitignore
```
Temp-dir CLI run: `add "Buy milk" 2` -> `Added task 1: Buy milk`; `list priority` -> `[ ] 1. Buy milk (priority 2)`;
`done 1` -> `Task 1 completed`; `add` (no title) -> still `IndexError: list index out of range` (R3 open).

| Area | Before | After | Evidence |
|---|---|---|---|
| Tests | 5 unit tests | 11 tests incl. persistence error path and git-ignore checks | `11 passed` |
| Security safeguards | no `.gitignore` | `.gitignore` covers `tasks.json`, `.env*`, caches, venvs | R2 mitigation, docs/07 |
| Data integrity | silent overwrite of corrupted file | fails loudly, file preserved | R1 mitigation, docs/07 |
| Pinned dependencies | missing | **still missing** | `requirements.txt` = `pytest` |
| Lint / type checks / CI | missing | **still missing** (not installed, not executed) | above |
| Logging / friendly errors | missing | **still missing** (raw tracebacks for R1 corrupt file and R3) | CLI run above |
| AGENTS.md enforcement | none | **still none** (no hooks, no permission rules, branch protection not checked) | R9 |
| README | accurate, gaps | updated in the final phase (docs links, venv, sort keys) | README.md |
| Human review of agent changes | - | **Done** by the student on 2026-11-23 (after this audit was written) | docs/SUBMISSION.md |

### Level AFTER mitigations: **2 - Documented** (unchanged)
The two score-6 CONFIRMED risks are mitigated and safeguards improved, but the level-3 evidence is still missing:
no pinned dependencies, no automated lint/type/CI gate, no technical enforcement of AGENTS.md, and the human review gate
has not been passed. Raising the level would require at least: pinned `requirements.txt`, ruff + mypy configured and passing in
CI, branch protection or permission deny-rules, and a recorded human review.
