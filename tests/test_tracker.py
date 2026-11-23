import os
import sys

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
