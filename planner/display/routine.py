from ..file_utils import read_json


def show_routine(file_path):
    """
    Display the daily routine checklist for the given file.
    Args:
        file_path (str): Path to the planner file.
    Returns:
        None
    """
    data = read_json(file_path)
    print("\n[Checklist] Daily Routine:")
    for section, items in data["tasks"].items():
        print(f"\n[{section}]")
        for i, item in enumerate(items):
            status = "[✓]" if data["done"][section][i] else "[ ]"
            print(f"{i+1:2}. {status} {item}")


def get_routine_lines(data):
    """
    Get formatted lines for the daily routine checklist.
    Args:
        data (dict): Planner data loaded from file.
    Returns:
        list: List of formatted strings for display.
    """
    lines = ["[Checklist] Daily Routine:"]
    for section, items in data["tasks"].items():
        done_list = data["done"][section]
        count_done = sum(done_list)
        total = len(done_list)
        lines.append("")
        lines.append(f"[{section}]")
        for i, item in enumerate(items):
            status = "[✓]" if done_list[i] else "[ ]"
            lines.append(f"{i+1:2}. {status} {item}")
        lines.append("    " + "=" * 16)
        filled = int(count_done / total * 10) if total > 0 else 0
        empty = 10 - filled
        bar = "#" * filled + "-" * empty
        percent = int(count_done / total * 100) if total > 0 else 0
        progress_text_1 = f"Progress |{bar}|"
        progress_text_2 = (
            f"          {percent}% ({count_done:.1f}/{total:.1f})"
        )
        lines.append(progress_text_1)
        lines.append(progress_text_2)
    return lines
