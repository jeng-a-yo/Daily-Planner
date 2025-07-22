# File: planner/display.py
from .file_utils import read_json
from .constants import TODAY_FILE, USER_PROFILE_FILE
from wcwidth import wcswidth
from tqdm import tqdm

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

def show_food():
    data = read_json(TODAY_FILE)
    print("\n[Food] Meals:")
    for line in get_food_lines(data)[1:]:
        print(line)

def show_exercise():
    data = read_json(TODAY_FILE)
    print("\n[Exercise] Activity:")
    for line in get_exercise_lines(data)[1:]:
        print(line)

def make_bar(current, total, width=10, label=""):
    ratio = min(current / total, 1.0) if total > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = "#" * filled + "-" * empty
    percent = int(ratio * 100)

    line1 = f"{label:<8} |{bar}|"
    line2 = f"         {percent:>3}% ({current:.1f}/{total:.1f}g)"
    return [line1, line2]



def get_routine_lines(data):
    lines = ["[Checklist] Daily Routine:"]
    for section, items in data["tasks"].items():
        done_list = data["done"][section]
        count_done = sum(done_list)
        total = len(done_list)

        lines.append("")  # spacing between sections
        lines.append(f"[{section}]")
        for i, item in enumerate(items):
            status = "[✓]" if done_list[i] else "[ ]"
            lines.append(f"{i+1:2}. {status} {item}")
        
        # Add separator before progress bar
        lines.append("    " + "=" * 16)

        # Use same bar format as food section
        filled = int(count_done / total * 10) if total > 0 else 0
        empty = 10 - filled
        bar = "#" * filled + "-" * empty
        percent = int(count_done / total * 100) if total > 0 else 0
        progress_text_1 = f"Progress |{bar}|"
        progress_text_2 = f"          {percent}% ({count_done:.1f}/{total:.1f})"
        lines.append(progress_text_1)
        lines.append(progress_text_2)
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


def get_food_lines(data):
    lines = ["[Food] Meals:"]
    profile = read_json(USER_PROFILE_FILE)
    weight = profile.get("weight", 0)
    target_p = profile.get("protein_factor", 0) * weight
    target_f = profile.get("fat_factor", 0) * weight
    target_c = profile.get("carbon_factor", 0) * weight

    total_protein = 0.0
    total_fat = 0.0
    total_carbon = 0.0

    for meal in ["breakfast", "lunch", "dinner"]:
        items = data.get("food", {}).get(meal, [])
        lines.append(f"  {meal.capitalize()}:")

        meal_protein = 0.0
        meal_fat = 0.0
        meal_carbon = 0.0

        if items:
            for i, food in enumerate(items, 1):
                name = food.get("name", str(food))
                lines.append(f"    {i}. {name}")
                meal_protein += food.get("protein", 0.0)
                meal_fat += food.get("fat", 0.0)
                meal_carbon += food.get("carbon", 0.0)
        else:
            lines.append("    (none)")

        total_protein += meal_protein
        total_fat += meal_fat
        total_carbon += meal_carbon

    # Add total
    lines.append("")
    lines.append("  Total:")
    lines.append(f"    Protein: {total_protein:.1f}g")
    lines.append(f"    Fat: {total_fat:.1f}g")
    lines.append(f"    Carbon: {total_carbon:.1f}g")

    # Add separator before progress bar
    lines.append(" " * ((35//2) - 12) + "=" * 24 + (" " * ((35//2) - 12)))

    # Add progress bars
    lines.append("")
    lines.append("  Progress:")
    for label, val, target in [
        ("Protein", total_protein, target_p),
        ("Fat", total_fat, target_f),
        ("Carbon", total_carbon, target_c)
    ]:
        bar_lines = make_bar(val, target, label=label)
        lines.extend([f"    {line}" for line in bar_lines])

    return lines



def get_exercise_lines(data):
    lines = ["[Exercise] Activity:"]
    for typ in ["exercising", "workout"]:
        items = data.get("exercise", {}).get(typ, [])
        lines.append(f"  {typ.capitalize()}:")
        if items:
            for i, act in enumerate(items, 1):
                if isinstance(act, dict):
                    name = act.get("name") or str(act)
                    lines.append(f"    {i}. {name}")
                else:
                    lines.append(f"    {i}. {act}")
        else:
            # Pad with space so column rendering remains intact
            lines.append("    (none)")
    return lines

def pad_display(s, width):
    display_len = wcswidth(s)
    padding = max(0, width - display_len)
    return s + ' ' * padding



def show_all_columns():
    data = read_json(TODAY_FILE)
    col1 = get_routine_lines(data)
    col2 = get_plan_lines(data)
    col3 = get_goals_lines(data)
    col4 = get_food_lines(data)
    col5 = get_exercise_lines(data)

    # Normalize line lengths
    max_lines = max(len(col1), len(col2), len(col3), len(col4), len(col5))
    col1 += [' '] * (max_lines - len(col1))
    col2 += [' '] * (max_lines - len(col2))
    col3 += [' '] * (max_lines - len(col3))
    col4 += [' '] * (max_lines - len(col4))
    col5 += [' '] * (max_lines - len(col5))

    # Define column widths
    widths = [30, 30, 30, 35, 30]

    # Print side-by-side with properly padded lines
    for l1, l2, l3, l4, l5 in zip(col1, col2, col3, col4, col5):
        print(f"{pad_display(l1, widths[0])} | {pad_display(l2, widths[1])} | {pad_display(l3, widths[2])} | {pad_display(l4, widths[3])} | {pad_display(l5, widths[4])}")



