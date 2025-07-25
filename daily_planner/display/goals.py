from ..file_utils import read_json


def show_goals(file_path):
    """
    Display the goals (focus and todo) for the given file.
    Args:
        file_path (str): Path to the planner file.
    Returns:
        None
    """
    data = read_json(file_path)
    print("\n[Goals] Focus:")
    for i, g in enumerate(data["goals"].get("focus", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        print(f"{i}. {icon} {g['text']}")
    print("\n[Goals] ToDo:")
    for i, g in enumerate(data["goals"].get("todo", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        print(f"{i}. {icon} {g['text']}")


def get_goals_lines(data):
    """
    Get formatted lines for the goals (focus and todo).
    Args:
        data (dict): Planner data loaded from file.
    Returns:
        list: List of formatted strings for display.
    """
    lines = ["[Goals] Focus:"]
    for i, g in enumerate(data["goals"].get("focus", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        lines.append(f"{i}. {icon} {g['text']}")
    lines.append("")
    lines.append("[Goals] ToDo:")
    for i, g in enumerate(data["goals"].get("todo", []), 1):
        icon = "[✓]" if g["done"] else "[ ]"
        lines.append(f"{i}. {icon} {g['text']}")
    return lines
