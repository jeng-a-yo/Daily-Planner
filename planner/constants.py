from datetime import date
import os

# Directory paths
DATA_DIR = "logs"
DEFAULTS_DIR = "defaults"

# Default template files
ROUTINE_FILE = os.path.join(DEFAULTS_DIR, "routine.json")
FOOD_DB_FILE = os.path.join(DEFAULTS_DIR, "food_db.json")
USER_PROFILE_FILE = os.path.join(DEFAULTS_DIR, "user_profile.json")

# Today’s data file path (e.g., logs/2025-07-24.json)
TODAY_FILENAME = f"{date.today()}.json"
TODAY_FILE = os.path.join(DATA_DIR, TODAY_FILENAME)
