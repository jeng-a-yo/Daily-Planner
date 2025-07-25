from ..file_utils import read_json
from ..constants import USER_PROFILE_FILE


def show_food(file_path):
    """
    Display the food log for the given file.
    Args:
        file_path (str): Path to the planner file.
    Returns:
        None
    """
    data = read_json(file_path)
    print("\n[Food] Meals:")
    for line in get_food_lines(data)[1:]:
        print(line)


def get_food_lines(data):
    """
    Get formatted lines for the food log, including nutrients and water.
    Args:
        data (dict): Planner data loaded from file.
    Returns:
        list: List of formatted strings for display.
    """
    lines = ["[Food] Meals:"]
    profile = read_json(USER_PROFILE_FILE)
    weight = profile.get("weight", 0)
    tall = profile.get("tall", 0)
    target_p = profile.get("protein_factor", 0) * weight
    target_f = profile.get("fat_factor", 0) * weight
    target_c = profile.get("carbon_factor", 0) * weight
    target_w = profile.get("water_factor", 0) * (tall + weight)
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
    lines.append("")
    lines.append("  Total:")
    lines.append(f"    Protein: {total_protein:.1f}g")
    lines.append(f"    Fat: {total_fat:.1f}g")
    lines.append(f"    Carbon: {total_carbon:.1f}g")
    total_water = data.get("water", 0)
    lines.append(f"    Water: {total_water} ml")
    lines.append(" " * ((35//2) - 12) + "=" * 24 + (" " * ((35//2) - 12)))
    lines.append("")
    lines.append("  Progress:")
    for label, val, target in [
        ("Protein", total_protein, target_p),
        ("Fat", total_fat, target_f),
        ("Carbon", total_carbon, target_c),
        ("Water", total_water, target_w)
    ]:
        bar_lines = make_bar(val, target, label=label)
        lines.extend([f"    {line}" for line in bar_lines])
    return lines


def make_bar(current, total, width=10, label=""):
    """
    Create a progress bar string for a nutrient or water goal.
    Args:
        current (float): Current value.
        total (float): Target value.
        width (int): Width of the bar. Defaults to 10.
        label (str): Label for the bar.
    Returns:
        list: List of two formatted strings representing the bar
            and its percentage.

    """
    ratio = min(current / total, 1.0) if total > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = "#" * filled + "-" * empty
    percent = int(ratio * 100)
    line1 = f"{label:<8} |{bar}|"
    line2 = f"         {percent:>3}% ({current:.1f}/{total:.1f}g)"
    return [line1, line2]
