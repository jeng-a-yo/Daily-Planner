from ..file_utils import read_json


def show_plan(file_path):
    """
    Display the daily planning schedule for the given file.
    Args:
        file_path (str): Path to the planner file.
    Returns:
        None
    """
    data = read_json(file_path)
    print("\n[Schedule] Daily Planning:")
    for h in range(5, 25):
        hour = f"{h:02}"
        task = data["plan"].get(hour, "")
        bar = "-->" if task else "   "
        print(f"{hour}:00 | {bar} {task}")


def get_plan_lines(data):
    """
    Get formatted lines for the daily planning schedule.
    Args:
        data (dict): Planner data loaded from file.
    Returns:
        list: List of formatted strings for display.
    """
    lines = ["[Schedule] Daily Planning:"]
    for h in range(5, 25):
        hour = f"{h:02}"
        task = data["plan"].get(hour, "")
        bar = "-->" if task else "   "
        lines.append(f"{hour}:00 | {bar} {task}")
    return lines
