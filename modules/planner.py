"""
VISION AI Assistant - Planner Module
To-do lists, study schedules, and planning tools.
"""
import json
from datetime import datetime
import config


def _load_plans() -> dict:
    """Load plans from file."""
    if config.PLANS_FILE.exists():
        try:
            with open(config.PLANS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_plans(plans: dict):
    """Save plans to file."""
    with open(config.PLANS_FILE, 'w') as f:
        json.dump(plans, f, indent=2, ensure_ascii=False)


def manage_plan(action: str, plan_name: str = None, task: str = None, task_index: int = None) -> str:
    """Manage plans and to-do lists."""
    plans = _load_plans()

    if action == "create":
        if not plan_name:
            return "Please provide a name for the plan."
        plans[plan_name] = {
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tasks": []
        }
        _save_plans(plans)
        return f"[PLAN] Plan created: '{plan_name}'"

    elif action == "view":
        if plan_name:
            plan_lower = plan_name.lower()
            for name, data in plans.items():
                if plan_lower in name.lower():
                    tasks = data.get("tasks", [])
                    if not tasks:
                        return f"[PLAN] {name} -- No tasks yet."
                    lines = [f"[PLAN] {name}:"]
                    for i, t in enumerate(tasks):
                        status = "[x]" if t.get("done") else "[ ]"
                        lines.append(f"  {status} {i+1}. {t['text']}")
                    done = sum(1 for t in tasks if t.get("done"))
                    lines.append(f"\n  Progress: {done}/{len(tasks)} completed")
                    return "\n".join(lines)
            return f"Plan '{plan_name}' not found."
        return "Please specify which plan to view."

    elif action == "add_task":
        if not plan_name:
            return "Please specify which plan to add the task to."
        if not task:
            return "Please provide a task description."

        plan_lower = plan_name.lower()
        for name in plans:
            if plan_lower in name.lower():
                plans[name]["tasks"].append({
                    "text": task,
                    "done": False,
                    "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                _save_plans(plans)
                return f"[+] Task added to '{name}': {task}"
        return f"Plan '{plan_name}' not found. Create it first."

    elif action == "complete_task":
        if not plan_name:
            return "Please specify which plan."
        if task_index is None:
            return "Please specify the task number to complete."

        plan_lower = plan_name.lower()
        for name in plans:
            if plan_lower in name.lower():
                tasks = plans[name]["tasks"]
                idx = task_index - 1  # Convert to 0-indexed
                if 0 <= idx < len(tasks):
                    tasks[idx]["done"] = True
                    _save_plans(plans)
                    return f"[DONE] Completed: {tasks[idx]['text']}"
                return f"Invalid task number. Plan has {len(tasks)} tasks."
        return f"Plan '{plan_name}' not found."

    elif action == "list":
        if not plans:
            return "No plans created yet."
        lines = ["[PLANS] Your plans:"]
        for name, data in plans.items():
            task_count = len(data.get("tasks", []))
            done_count = sum(1 for t in data.get("tasks", []) if t.get("done"))
            lines.append(f"  > {name} -- {done_count}/{task_count} tasks done")
        return "\n".join(lines)

    return "Invalid plan action. Use: create, view, add_task, complete_task, list."
