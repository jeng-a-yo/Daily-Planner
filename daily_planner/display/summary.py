from ..file_utils import read_json
from .routine import get_routine_lines
from .plan import get_plan_lines
from .goals import get_goals_lines
from .food import get_food_lines
from wcwidth import wcswidth


def pad_display(s, width):
    """
    Pad a string to a given display width, accounting for wide characters.
    Args:
        s (str): The string to pad.
        width (int): The target display width.
    Returns:
        str: The padded string.
    """
    display_len = wcswidth(s)
    padding = max(0, width - display_len)
    return s + ' ' * padding


def show_all_columns(file_path):
    """
    Display all planner columns side by side:
    routine, plan, goals, food, and exercise.

    Args:
        file_path (str): Path to the planner file.

    Returns:
        None
    """
    data = read_json(file_path)
    col1 = get_routine_lines(data)
    col2 = get_plan_lines(data)
    col3 = get_goals_lines(data)
    col4 = get_food_lines(data)
    max_lines = max(len(col1), len(col2), len(col3), len(col4))
    col1 += [' '] * (max_lines - len(col1))
    col2 += [' '] * (max_lines - len(col2))
    col3 += [' '] * (max_lines - len(col3))
    col4 += [' '] * (max_lines - len(col4))
    widths = [30, 30, 30, 35]
    for l1, l2, l3, l4 in zip(col1, col2, col3, col4):
        print(
            f"{pad_display(l1, widths[0])} | "
            f"{pad_display(l2, widths[1])} | "
            f"{pad_display(l3, widths[2])} | "
            f"{pad_display(l4, widths[3])}"
        )
