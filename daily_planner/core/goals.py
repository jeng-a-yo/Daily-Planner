from ..file_utils import read_json, write_json
from ..constants import TODAY_FILE
from .routine import match_one, normalize_section


def add_goal(section, text):
    """
    Add a new goal to the specified section (focus or todo).
    Args:
        section (str): Section name or abbreviation.
        text (str): The goal text to add.
    Returns:
        None
    """
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
    """
    Mark or unmark a goal as done by searching for a text snippet.
    Args:
        section (str): Section name or abbreviation.
        text_snippet (str): Substring to match in goal text.
        status (bool): True to mark as done, False to unmark. Defaults to True.
    Returns:
        None
    """
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
    print(
        f"[✓] Marked goal: {goal['text']} in [{section}]" if status else
        f"[✗] Unmarked goal: {goal['text']} in [{section}]"
    )


def list_goals(section=None, done=None):
    """
    List all goals, optionally filtered by section and done status.
    Args:
        section (str, optional): Section to filter ('focus' or 'todo').
        done (bool, optional): Filter by done status.
    Returns:
        list: List of (section, goal) tuples.
    """
    data = read_json(TODAY_FILE)
    results = []
    for sec, goals in data["goals"].items():
        if section and sec != section:
            continue
        for g in goals:
            if done is None or g["done"] == done:
                results.append((sec, g))
    return results
