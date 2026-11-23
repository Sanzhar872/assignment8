# Task 9 - Release decision

Agent: Claude Code, model Claude Opus 5.5, 2026-11-23. Decision prepared by the agent; it is **not valid until the student
reviews it**. Human review: PENDING - student review before submission.

## Decision: **CONDITIONAL**

(Exactly one of GO / CONDITIONAL / NO-GO.) The current `main` may be released **only after** the conditions in section 3 are
met. Until then it must not be treated as released.

## 1. Basis (only real evidence)

**Test results** (commit `0b27bb6`, Python 3.13.15, pytest 9.2.0):
```
$ python -m pytest -q
11 passed in 0.15s
```
All acceptance criteria AC1-AC4 hold (tests + temp-dir CLI runs in docs/07 and docs/06 Part B).
Not executed: ruff, mypy (not installed), no CI, no build step exists.

**Risk register after mitigations** (docs/05-risk-register.md):
- The two highest CONFIRMED risks were mitigated with failing-test-first fixes: R1 6 -> 2, R2 6 -> 3.
- No CONFIRMED risk with score >= 5 remains open.
- Open CONFIRMED risks: R4 no lint/type/CI (4), R3 argv/int crash (3), R5 duplicate ids (2), R6 empty titles (2),
  R7 unpinned dependency (2), R8 non-ASCII output crash (2). Open unverified: R9 agent rules not enforced (4).

**Readiness level:** 2 - Documented (before and after mitigations; docs/06). Not agent-ready (level 3).

## 2. Why not GO / why not NO-GO
- **Not GO:** quality gates are incomplete - lint and type checks were never executed, dependencies are unpinned, six CONFIRMED
  risks remain open (though all low/medium), readiness is only level 2, and **no human has reviewed the agent-made changes**.
- **Not NO-GO:** there is no open CONFIRMED high-impact risk (the data-loss and data-exposure risks are mitigated and verified by
  tests); all 11 tests pass; documented commands work. Remaining issues are crashes with tracebacks on invalid input (no data
  changed, verified: the crash happens before `save_tasks`) and missing tooling.

## 3. Conditions to reach GO
| # | Condition | Owner | Control / verification |
|---|---|---|---|
| G1 | Student reviews the full diff `git diff baseline..HEAD` and every doc, and records the review (name, date) in docs/SUBMISSION.md | Student | Review recorded; "PENDING" replaced |
| G2 | Lint and type checks executed: add pinned `ruff` and `mypy` (needs explicit approval for new dev dependencies), `ruff check .` and `mypy tracker.py` exit 0 | Student | Real command output added to docs |
| G3 | Pin `requirements.txt` (e.g. `pytest==9.2.0`) | Student | Fresh venv install + `pytest -q` green |
| G4 | Fix R3: validate argv length and `int()` in `main`, print usage, non-zero exit; tests with `monkeypatch`/`capsys` | Student | New tests fail first, then pass |

## 4. Remaining limitations accepted for a CONDITIONAL release
| Limitation | Risk ID | Owner | Control until fixed |
|---|---|---|---|
| Corrupted `tasks.json` -> raw traceback (file preserved) | R1 residual | Student | Documented in README; user repairs/restores the file |
| Non-atomic save may truncate the file on crash | C7 (unverified) | Student | Keep a manual backup of `tasks.json` |
| Duplicate ids if `tasks.json` is hand-edited | R5 | Student | Do not hand-edit ids; no delete command exists |
| Empty/whitespace titles accepted | R6 | Student | Cosmetic; user discipline |
| Non-ASCII titles crash output on cp1252 consoles | R8 | Student | Use `PYTHONUTF8=1` / UTF-8 terminal |
| AGENTS.md not technically enforced | R9 | Student | Human review gate before every push; check GitHub branch protection |
