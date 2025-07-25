from ..file_utils import read_json, write_json
from ..constants import TODAY_FILE
import os


def add_water(amount):
    """
    Add drinking water (in milliliters) to today's log.
    Args:
        amount (int or str): Amount of water in milliliters to add.
    Returns:
        None
    """
    if not os.path.exists(TODAY_FILE):
        print("[!] No planner for today. Run 'init' first.")
        return
    data = read_json(TODAY_FILE)
    if "water" not in data:
        data["water"] = 0
    try:
        data["water"] += int(amount)
        write_json(TODAY_FILE, data)
        print(f"[✓] Added {amount}ml water. Total: {data['water']}ml.")
    except ValueError:
        print("[!] Invalid water amount. Please enter an integer.")
