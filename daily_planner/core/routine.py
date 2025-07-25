from datetime import date, datetime
import os
from ..file_utils import read_json, write_json
from ..constants import ROUTINE_FILE, TODAY_FILE


def match_one(entries, key_func, query):
    """
    Find a single entry matching the query using a key function.

    Args:
        entries (list): List of entries to search.
        key_func (callable): Function to extract the string to match
            from each entry.
        query (str): The query string to match.

    Returns:
        tuple or None: (index, entry) if a single match is found,
            None otherwise.
    """
    matches = [(i, e) for i, e in enumerate(entries)
               if query.lower() in key_func(e).lower()]
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
    """
    Normalize a section name to its canonical form ('focus' or 'todo').
    Args:
        section (str): Section name or abbreviation.
    Returns:
        str: Canonical section name.
    Raises:
        ValueError: If the section is unknown.
    """
    section = section.lower()
    if section.startswith("f"):
        return "focus"
    elif section.startswith("t"):
        return "todo"
    else:
        raise ValueError(f"Unknown section: {section}")


def fuzzy_show_type(value):
    """
    Fuzzy match a display type string to its canonical type.
    Args:
        value (str): The type string to match.
    Returns:
        str: Canonical type ('routine', 'plan', 'goals', 'summary', 'all').
    Raises:
        ValueError: If the type is unknown.
    """
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


def init_day(target_date=None) -> None:
    """
    Initialize the planner for a specific day. Creates a new planner file
    if it doesn't exist.

    Args:
        target_date (str, optional): Date string in 'YYYY-MM-DD' format.
            Defaults to today.

    Returns:
        None
    """
    if target_date:
        try:
            d = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            print("[!] Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        d = date.today()

    if os.path.exists(TODAY_FILE):
        print(f"[!] Planner for {d} already exists.")
        return

    template = read_json(ROUTINE_FILE)
    data = {
        "tasks": template,
        "done": {s: [False] * len(items) for s, items in template.items()},
        "plan": {f"{h:02}": "" for h in range(5, 25)},
        "goals": {"focus": [], "todo": []},
        "food": {"breakfast": [], "lunch": [], "dinner": []},
        "water": 0
    }
    weekday = d.weekday()
    if weekday in (1, 4):
        data["goals"]["todo"].append({"text": "laundry", "done": False})
    write_json(TODAY_FILE, data)
    print(f"[✓] Initialized planner for {d}.")


def check_by_name(task_name, status=True):
    """
    Check or uncheck a routine task by name.
    Args:
        task_name (str): The task name to check/uncheck.
        status (bool): True to check, False to uncheck. Defaults to True.
    Returns:
        None
    """
    data = read_json(TODAY_FILE)
    matches = []
    for section, items in data["tasks"].items():
        for i, item in enumerate(items):
            if task_name.lower() in item.lower():
                matches.append((section, i, item))
    if not matches:
        print(f"[x] Task containing '{task_name}' not found.")
        return
    for section, idx, item in matches:
        already_checked = data["done"][section][idx]
        if already_checked != status:
            data["done"][section][idx] = status
            write_json(TODAY_FILE, data)
            print(f"[✓] Marked '{item}' in [{section}]" if status
                  else f"[ ] Unmarked '{item}' in [{section}]")
            return
    print(
        f"[!] All matches for '{task_name}' are already "
        f"{'checked' if status else 'unchecked'}:"
    )
    for sec, i, name in matches:
        print(f" - {name} [{sec}]")


def plan_hours(task, start_hour, end_hour=None):
    """
    Plan a task for a range of hours in the daily planner.

    Args:
        task (str): The task to plan.
        start_hour (int or str): The starting hour (24h format).
        end_hour (int or str, optional): The ending hour (24h format).
            Defaults to start_hour + 1.

    Returns:
        None
    """
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


def show_summary():
    """
    Print a summary of completed tasks and goals for the day.
    Args:
        None
    Returns:
        None
    """
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


def print_help_message() -> None:
    """
    Print usage examples and help message for the CLI.
    Args:
        None
    Returns:
        None
    """
    print("""
Usage Examples:
  planner init                         Initialize today's planner
  planner check "meditate"            Check a routine task
  planner uncheck "meditate"          Uncheck a routine task
  planner plan "Work on report" 9 11  Plan a task between 9:00 and 11:00
  planner add-goal f "Deep focus"     Add a focus goal
  planner check-goal f "focus"        Check a focus goal
  planner show goals                  Show goals
  planner show summary                Show summary of the day
  planner add-food lunch "egg"        Log 'egg' in lunch
                                      (requires food_db.json)
  planner add-food-info "egg" 5 6.3 5.3 0.6  Add 'egg' to database
  planner add-exercise workout "push-ups"    Log push-ups to workout
""")
