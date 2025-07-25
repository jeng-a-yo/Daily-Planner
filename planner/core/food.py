from ..file_utils import read_json, write_json
from ..constants import TODAY_FILE, FOOD_DB_FILE
import os


def sort_key(entry, mode):
    """
    Key function for sorting food database entries by nutrient or name.
    Args:
        entry (tuple): (name, data) tuple from food_db.items().
        mode (str): 'p' for protein, 'f' for fat, 'c' for carbon, else by name.
    Returns:
        value: The value to sort by.
    """
    name, data = entry
    if mode == "p":
        return data.get("protein", 0)
    elif mode == "f":
        return data.get("fat", 0)
    elif mode == "c":
        return data.get("carbon", 0)
    else:
        return name  # default to name sorting


def search_food_matches(food_db, query):
    """
    Search for food names in the food database that match the query substring.
    Args:
        food_db (dict): The food database.
        query (str): The query string to match.
    Returns:
        list: List of (index, name) tuples for matching foods.
    """
    query = query.lower()
    return [(i+1, name) for i, name in enumerate(food_db) if query in name]


def normalize_meal(meal):
    """
    Normalize a meal name to its canonical form
    ('breakfast', 'lunch', or 'dinner').    Args:
        meal (str): Meal name or abbreviation.
    Returns:
        str: Canonical meal name.
    Raises:
        ValueError: If the meal is invalid.
    """
    meal = meal.lower()
    if meal.startswith("b"):
        return "breakfast"
    elif meal.startswith("l"):
        return "lunch"
    elif meal.startswith("d"):
        return "dinner"
    else:
        raise ValueError(f"Invalid meal: {meal}")


def add_food(meal, food_name, weight):
    """
    Add a food entry to a meal in today's planner, with nutrient calculation.
    Args:
        meal (str): Meal name or abbreviation.
        food_name (str): Name of the food to add.
        weight (float or str): Weight in grams.
    Returns:
        None
    """
    try:
        meal = normalize_meal(meal)
    except ValueError as e:
        print(f"[x] {e}")
        return
    try:
        weight = float(weight)
        if weight <= 0:
            raise ValueError
    except ValueError:
        print(f"[x] Invalid weight: {weight}. Use a positive number.")
        return
    data = read_json(TODAY_FILE)
    food_db = read_json(FOOD_DB_FILE) if os.path.exists(FOOD_DB_FILE) else {}
    food_key = food_name.lower()
    if food_key not in food_db:
        matches = search_food_matches(food_db, food_key)
        if not matches:
            print(f"[!] '{food_name}' not found in food_db.json.")
            return
        if len(matches) == 1:
            food_key = matches[0][1]
            print(f"[✓] Auto-selected match: {food_key}")
        else:
            print(f"[?] Multiple matches found for '{food_name}'. Select one:")
            matched_food = list(dict(matches).values())
            matches = [
                (i + 1, matched_food[i])
                for i in range(len(matched_food))]
            for i, name in matches:
                print(f"  {i}. {name}")
            try:
                selected = int(input("Enter number: "))
                food_key = dict(matches).get(selected)
                if not food_key:
                    print("[x] Invalid selection.")
                    return
            except ValueError:
                print("[x] Invalid input.")
                return
    entry = food_db[food_key]
    factor = weight / 100.0
    record = {
        "name": food_key,
        "weight": weight,
        "protein": round(entry.get("protein", 0.0) * factor, 2),
        "fat": round(entry.get("fat", 0.0) * factor, 2),
        "carbon": round(entry.get("carbon", 0.0) * factor, 2)
    }
    data["food"][meal].append(record)
    write_json(TODAY_FILE, data)
    print(f"[+] Logged {weight:.1f}g of '{food_key}' in {meal}")


def add_food_info(name, protein, fat, carbon):
    """
    Add a new food entry to the food database with nutrient information.
    Args:
        name (str): Name of the food.
        protein (float or str): Protein per 100g.
        fat (float or str): Fat per 100g.
        carbon (float or str): Carbohydrates per 100g.
    Returns:
        None
    """
    food_db = read_json(FOOD_DB_FILE) if os.path.exists(FOOD_DB_FILE) else {}
    key = name.lower()
    if key in food_db:
        print(f"[!] '{name}' already exists in database.")
        return
    food_db[key] = {
        "protein": float(protein),
        "fat": float(fat),
        "carbon": float(carbon)
    }
    write_json(FOOD_DB_FILE, food_db)
    print(f"[✓] Added food '{name}' to database.")
