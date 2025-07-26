from daily_planner.constants import TODAY_FILE, DATA_DIR
from datetime import datetime
import subprocess
import sys
import os
# Ensure project root is in sys.path for absolute imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def get_today_filepath(date_str=None):
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            filename = f"{date_str}.json"
            filepath = os.path.join(DATA_DIR, filename)
            return filepath
        except ValueError:
            print(f"[x] Invalid date format: {date_str}. Use YYYY-MM-DD.")
            sys.exit(1)
    return TODAY_FILE


def git_commit_and_push(filename):
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"archive: add {filename}"],
            check=True
        )
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[✓] Pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[x] Git error: {e}")


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    today_filename = get_today_filepath(date_arg)

    git_commit_and_push(today_filename)
