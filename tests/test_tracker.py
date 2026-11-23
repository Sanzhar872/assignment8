import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tracker


def test_add_task_appears_in_list():
    tasks = []
    tracker.add_task(tasks, "Buy milk", 2)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"
    assert tasks[0]["done"] is False


def test_complete_task_sets_done():
    tasks = []
    tracker.add_task(tasks, "Write report")
    result = tracker.complete_task(tasks, 1)
    assert result["done"] is True


def test_complete_unknown_task_returns_none():
    assert tracker.complete_task([], 99) is None


def test_sort_by_priority_descending():
    tasks = []
    tracker.add_task(tasks, "low", 1)
    tracker.add_task(tasks, "high", 3)
    result = tracker.sort_tasks(tasks, "priority")
    assert result[0]["title"] == "high"


def _sample_tasks():
    tasks = []
    tracker.add_task(tasks, "banana", 1)
    tracker.add_task(tasks, "Apple", 3)
    tracker.add_task(tasks, "Cherry", 2)
    tracker.complete_task(tasks, 2)
    return tasks


def test_export_text_characterization():
    """Pins the current output of export_text/sort_tasks before refactoring."""
    tasks = _sample_tasks()
    assert tracker.export_text(tasks) == (
        "[ ] 1. banana (priority 1)\n"
        "[x] 2. Apple (priority 3)\n"
        "[ ] 3. Cherry (priority 2)"
    )
    assert tracker.export_text(tasks, "priority") == (
        "[x] 2. Apple (priority 3)\n"
        "[ ] 3. Cherry (priority 2)\n"
        "[ ] 1. banana (priority 1)"
    )
    assert tracker.export_text(tasks, "title") == (
        "[x] 2. Apple (priority 3)\n"
        "[ ] 1. banana (priority 1)\n"
        "[ ] 3. Cherry (priority 2)"
    )
    reversed_tasks = list(reversed(tasks))
    assert [t["id"] for t in tracker.sort_tasks(reversed_tasks, "id")] == [1, 2, 3]
    assert [t["id"] for t in tracker.sort_tasks(reversed_tasks, "title")] == [2, 1, 3]
    # unknown key keeps stored order
    assert tracker.sort_tasks(reversed_tasks, "nope") == reversed_tasks
    assert tracker.export_text(reversed_tasks, "nope") == (
        "[ ] 3. Cherry (priority 2)\n"
        "[x] 2. Apple (priority 3)\n"
        "[ ] 1. banana (priority 1)"
    )
    assert tracker.export_text([]) == ""


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
