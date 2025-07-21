from .constants import ROUTINE_FILE, TODAY_FILE, DATA_DIR
from .file_utils import read_json, write_json
import os
from datetime import date

def init_day():
    if os.path.exists(TODAY_FILE):
        print("[!] Today's planner already exists.")
        return

    template = read_json(ROUTINE_FILE)

    # Basic structure
    data = {
        "tasks": template,
        "done": {s: [False] * len(items) for s, items in template.items()},
        "plan": {f"{h:02}": "" for h in range(5, 25)},
        "goals": {
            "focus": [],
            "todo": []
        }
    }

    # Add "laundry" to todo if today is Tuesday (1) or Friday (4)
    weekday = date.today().weekday()
    if weekday in (1, 4):  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        data["goals"]["todo"].append({"text": "laundry", "done": False})

    write_json(TODAY_FILE, data)
    print("[✓] Initialized with routine and empty goals.")

def match_one(entries, key_func, query):
    matches = [(i, e) for i, e in enumerate(entries) if query.lower() in key_func(e).lower()]
    if not matches:
        print(f"[x] No match for '{query}'")
        return None
    if len(matches) > 1:
        print(f"[!] Multiple matches for '{query}':")
        for i, e in matches:
            print(f" - {i+1}. {key_func(e)}")
        return None
    return matches[0]

def normalize_section(section):
    section = section.lower()
    if section.startswith("f"):
        return "focus"
    elif section.startswith("t"):
        return "todo"
    else:
        raise ValueError(f"Unknown section: {section}")

def fuzzy_show_type(value):
    value = value.lower()
    if value.startswith("r"):
        return "routine"
    elif value.startswith("p"):
        return "plan"
    elif value.startswith("g"):
        return "goals"
    elif value.startswith("s"):
        return "summary"
    elif value.startswith("a") or value == "":
        return "all"
    else:
        raise ValueError(f"Unknown show type: {value}")

def check_by_name(task_name, status=True):
    data = read_json(TODAY_FILE)
    matches = []

    # Find all task matches
    for section, items in data["tasks"].items():
        for i, item in enumerate(items):
            if task_name.lower() in item.lower():
                matches.append((section, i, item))

    if not matches:
        print(f"[x] Task containing '{task_name}' not found.")
        return

    # Find the first *unmarked* match (or just pick first if unchecking)
    for section, idx, item in matches:
        already_checked = data["done"][section][idx]
        if already_checked != status:
            data["done"][section][idx] = status
            write_json(TODAY_FILE, data)
            print(f"[✓] Marked '{item}' in [{section}]" if status else f"[ ] Unmarked '{item}' in [{section}]")
            return

    # All matches already in desired state
    print(f"[!] All matches for '{task_name}' are already {'checked' if status else 'unchecked'}:")
    for sec, i, name in matches:
        print(f" - {name} [{sec}]")


def plan_hours(task, start_hour, end_hour=None):
    data = read_json(TODAY_FILE)
    try:
        start = int(start_hour)
        end = int(end_hour) if end_hour else start + 1
        if not (5 <= start < end <= 24):
            print("[!] Time must be between 5 and 24.")
            return
    except ValueError:
        print("[!] Invalid time format. Use numbers like 8 or 14.")
        return
    for h in range(start, end):
        data["plan"][f"{h:02}"] = task
    write_json(TODAY_FILE, data)
    print(f"[->] Planned '{task}' from {start}:00 to {end}:00")

def add_goal(section, text):
    section = normalize_section(section)
    data = read_json(TODAY_FILE)
    if "goals" not in data:
        data["goals"] = {}
    if section not in data["goals"]:
        data["goals"][section] = []
    data["goals"][section].append({"text": text, "done": False})
    write_json(TODAY_FILE, data)
    print(f"[+] Added to {section.title()} Goals: {text}")

def mark_goal_by_name(section, text_snippet, status=True):
    section = normalize_section(section)
    data = read_json(TODAY_FILE)
    try:
        goals = data["goals"][section]
    except KeyError:
        print(f"[x] No goals section '{section}' found.")
        return

    match = match_one(goals, lambda g: g["text"], text_snippet)
    if match is None:
        return

    idx, goal = match
    goal["done"] = status
    data["goals"][section][idx] = goal
    write_json(TODAY_FILE, data)
    print(f"[✓] Marked goal: {goal['text']} in [{section}]" if status else f"[ ] Unmarked goal: {goal['text']} in [{section}]")

def list_goals(section=None, done=None):
    data = read_json(TODAY_FILE)
    results = []
    for sec, goals in data["goals"].items():
        if section and sec != section:
            continue
        for g in goals:
            if done is None or g["done"] == done:
                results.append((sec, g))
    return results

def show_summary():
    data = read_json(TODAY_FILE)
    total = done = 0
    for section, checks in data["done"].items():
        total += len(checks)
        done += sum(checks)
    print(f"[Summary] Tasks: {done}/{total} completed")
    for category in ["focus", "todo"]:
        goals = data["goals"].get(category, [])
        g_done = sum(1 for g in goals if g["done"])
        print(f"  {category.title()}: {g_done}/{len(goals)} complete")

def print_help_message():
    print("""
Usage Examples:
  planner init                         Initialize today's planner
  planner check "meditate"             Check a routine task
  planner uncheck "meditate"          Uncheck a routine task
  planner plan "Work on report" 9 11  Plan a task between 9:00 and 11:00
  planner add-goal f "Deep focus"      Add a focus goal
  planner check-goal f "focus"         Check a focus goal
  planner show goals                   Show goals
  planner show summary                 Show summary of the day
""")