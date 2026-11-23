"""Simple console task tracker."""
import json
import sys

DATA_FILE = "tasks.json"


def load_tasks():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)


def add_task(tasks, title, priority=1):
    task = {"id": len(tasks) + 1, "title": title, "priority": priority, "done": False}
    tasks.append(task)
    return task


def complete_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            return t
    return None


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
    lines = []
    for t in items:
        mark = "x" if t["done"] else " "
        lines.append(f"[{mark}] {t['id']}. {t['title']} (priority {t['priority']})")
    return "\n".join(lines)


def main():
    tasks = load_tasks()
    if len(sys.argv) < 2:
        print("Usage: python tracker.py add|done|list ...")
        return
    cmd = sys.argv[1]
    if cmd == "add":
        title = sys.argv[2]
        priority = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        task = add_task(tasks, title, priority)
        save_tasks(tasks)
        print(f"Added task {task['id']}: {task['title']}")
    elif cmd == "done":
        task = complete_task(tasks, int(sys.argv[2]))
        if task is None:
            print("Task not found")
        else:
            save_tasks(tasks)
            print(f"Task {task['id']} completed")
    elif cmd == "list":
        by = sys.argv[2] if len(sys.argv) > 2 else "id"
        print(export_text(sort_tasks(tasks, by), by))
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
