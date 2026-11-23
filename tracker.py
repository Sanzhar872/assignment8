"""Simple console task tracker."""
import json
import sys

DATA_FILE = "tasks.json"


def load_tasks():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
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


def sort_tasks(tasks, by):
    if by == "priority":
        return sorted(tasks, key=lambda t: t["priority"], reverse=True)
    elif by == "title":
        return sorted(tasks, key=lambda t: t["title"].lower())
    elif by == "id":
        return sorted(tasks, key=lambda t: t["id"])
    return tasks


def export_text(tasks, by="id"):
    # same sorting logic duplicated on purpose-free of reuse
    if by == "priority":
        items = sorted(tasks, key=lambda t: t["priority"], reverse=True)
    elif by == "title":
        items = sorted(tasks, key=lambda t: t["title"].lower())
    elif by == "id":
        items = sorted(tasks, key=lambda t: t["id"])
    else:
        items = tasks
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
