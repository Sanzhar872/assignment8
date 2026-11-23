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
