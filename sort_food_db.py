import json
import sys
from planner.constants import FOOD_DB_FILE


def sort_key(entry, mode):
    name, data = entry
    if mode == "p":
        return data.get("protein", 0)
    elif mode == "f":
        return data.get("fat", 0)
    elif mode == "c":
        return data.get("carbon", 0)
    else:
        return name  # default to name sorting

def main():
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "n"
    mode = arg[0]  # 'p', 'f', 'c', or default 'n'

    with open(FOOD_DB_FILE, "r", encoding="utf-8") as f:
        food_db = json.load(f)

    reverse = mode in {"p", "f", "c"}
    sorted_items = sorted(food_db.items(), key=lambda x: sort_key(x, mode), reverse=reverse)

    sorted_db = {k: v for k, v in sorted_items}

    with open(FOOD_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_db, f, ensure_ascii=False, indent=2)

    print(f"[✓] Sorted by '{mode}' ({'desc' if reverse else 'asc'}) and saved to {FOOD_DB_FILE}")

if __name__ == "__main__":
    main()
