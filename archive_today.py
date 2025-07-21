# archive_today.py
import os
import shutil
import subprocess
from planner.constants import TODAY_FILENAME, DATA_DIR

def move_today_to_logs():
    if not os.path.exists(TODAY_FILENAME):
        print(f"[x] File {TODAY_FILENAME} not found in current directory.")
        return False

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    dst = os.path.join(DATA_DIR, TODAY_FILENAME)
    shutil.move(TODAY_FILENAME, dst)
    print(f"[→] Moved {TODAY_FILENAME} to {DATA_DIR}/")
    return True

def git_commit_and_push(filename):
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", f"archive: add {filename}"], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("[✓] Pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[x] Git error: {e}")

if __name__ == "__main__":
    if move_today_to_logs():
        log_path = os.path.join("logs", TODAY_FILENAME)
        git_commit_and_push(log_path)
