# File: planner/display.py
from .file_utils import read_json
from .constants import TODAY_FILE

def show_routine():
    data = read_json(TODAY_FILE)
    print("\n[Checklist] Daily Routine:")
    for section, items in data["tasks"].items():
        print(f"\n[{section}]")
        for i, item in enumerate(items):
            status = "[✓]" if data["done"][section][i] else "[ ]"
            print(f"{i+1:2}. {status} {item}")

def show_plan():
    data = read_json(TODAY_FILE)
    print("\n[Schedule] Daily Planning:")
    for h in range(5, 25):
        hour = f"{h:02}"
        task = data["plan"].get(hour, "")
        bar = "-->" if task else "   "
        print(f"{hour}:00 | {bar} {task}")

def show_goals():
    data = read_json(TODAY_FILE)
    print("\n[Goals] Focus:")
    for i, g in enumerate(data["goals"].get("focus", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        print(f"{i}. {icon} {g['text']}")
    print("\n[Goals] Action Items:")
    for i, g in enumerate(data["goals"].get("todo", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        print(f"{i}. {icon} {g['text']}")


def get_routine_lines(data):
    lines = ["[Checklist] Daily Routine:"]
    for section, items in data["tasks"].items():
        lines.append("")  # add spacing between sections
        lines.append(f"[{section}]")
        for i, item in enumerate(items):
            status = "[✓]" if data["done"][section][i] else "[ ]"
            lines.append(f"{i+1:2}. {status} {item}")
    return lines


def get_plan_lines(data):
    lines = ["[Schedule] Daily Planning:"]
    for h in range(5, 25):
        hour = f"{h:02}"
        task = data["plan"].get(hour, "")
        bar = "-->" if task else "   "
        lines.append(f"{hour}:00 | {bar} {task}")
    return lines

def get_goals_lines(data):
    lines = ["[Goals] Focus:"]
    for i, g in enumerate(data["goals"].get("focus", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        lines.append(f"{i}. {icon} {g['text']}")

    lines.append("")  # add spacing before action items
    lines.append("[Goals] Action Items:")
    for i, g in enumerate(data["goals"].get("todo", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        lines.append(f"{i}. {icon} {g['text']}")
    return lines


def show_all_columns():
    data = read_json(TODAY_FILE)
    col1 = get_routine_lines(data)
    col2 = get_plan_lines(data)
    col3 = get_goals_lines(data)

    # Normalize line lengths
    max_lines = max(len(col1), len(col2), len(col3))
    col1 += [''] * (max_lines - len(col1))
    col2 += [''] * (max_lines - len(col2))
    col3 += [''] * (max_lines - len(col3))

    # Define column widths
    width1 = 30
    width2 = 30
    width3 = 30

    # Print side-by-side
    for l1, l2, l3 in zip(col1, col2, col3):
        print(f"{l1:<{width1}} | {l2:<{width2}} | {l3:<{width3}}")

