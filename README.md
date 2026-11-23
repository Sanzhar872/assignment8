# Task Tracker

Small console task tracker written in Python (standard library only). Tasks are stored in `tasks.json`
in the **current working directory** (the file is git-ignored - never commit it).

## Setup
Requires Python 3 (recorded runs used Python 3.13.15). A virtual environment is recommended:
```
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell/cmd); on Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
```
On Linux/macOS activate with `source .venv/bin/activate`.

## Usage
```
python tracker.py add "Buy milk" 2      # -> Added task 1: Buy milk   (priority defaults to 1)
python tracker.py list priority         # sort keys: id (default), priority, title
python tracker.py done 1                # -> Task 1 completed
```
Known limitations (see [docs/05-risk-register.md](docs/05-risk-register.md)):
- Missing or non-numeric arguments (e.g. `python tracker.py add`) stop with a Python traceback (R3).
- If `tasks.json` is corrupted, every command stops with a `JSONDecodeError` and the file is left unchanged (R1 residual);
  repair or restore the file manually.
- Non-ASCII titles can fail to print on a cp1252 Windows console; set `PYTHONUTF8=1` (R8).

## Tests
```
python -m pytest -q
```
(`pytest` also works when the virtual environment's `Scripts`/`bin` directory is on `PATH`.)
Lint/type checks (ruff, mypy) are not configured in this repository.

## Documentation
- Agent instructions: [AGENTS.md](AGENTS.md) (imported by [CLAUDE.md](CLAUDE.md))
- [Baseline analysis](docs/01-baseline.md) · [Acceptance criteria](docs/acceptance-criteria.md)
- [Pattern decision](docs/03-pattern-decision.md) · [Risk review](docs/04-risk-review.md) · [Risk register](docs/05-risk-register.md)
- [Agent readiness](docs/06-agent-readiness.md) · [Mitigations](docs/07-mitigation-and-verification.md)
- [Background-agent safeguards](docs/08-background-agent-safeguards.md) · [Release decision](docs/09-release-decision.md)
- [AI reflection](docs/10-ai-reflection.md) (student) · [AI evidence log](docs/ai-evidence.md) · [Submission checklist](docs/SUBMISSION.md)
- [Progress checkpoints](docs/PROGRESS.md)
