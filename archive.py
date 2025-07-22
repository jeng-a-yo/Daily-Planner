import os
import shutil
import subprocess
import sys
from datetime import datetime
from planner.constants import DATA_DIR

def get_today_filename(date_str=None):
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return f"{date_str}.json"
        except ValueError:
            print(f"[x] Invalid date format: {date_str}. Use YYYY-MM-DD.")
            sys.exit(1)
    return f"{datetime.today().strftime('%Y-%m-%d')}.json"

def move_today_to_logs(today_filename):
    if not os.path.exists(today_filename):
        print(f"[x] File {today_filename} not found in current directory.")
        return False

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    dst = os.path.join(DATA_DIR, today_filename)
    shutil.move(today_filename, dst)
    print(f"[→] Moved {today_filename} to {DATA_DIR}/")
    return True

def git_commit_and_push(filename):
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", f"archive: add {filename}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[✓] Pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[x] Git error: {e}")

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    today_filename = get_today_filename(date_arg)
    
    if move_today_to_logs(today_filename):
        log_path = os.path.join("logs", today_filename)
        git_commit_and_push(log_path)
