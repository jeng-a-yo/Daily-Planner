import subprocess
from datetime import datetime
import sys


def get_today_filename(date_str=None):
    """
    Get the filename for today's planner or a specific date.
    Args:
        date_str (str, optional): Date string in 'YYYY-MM-DD' format.
    Returns:
        str: The filename for the planner JSON file.
    """
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return f"{date_str}.json"
        except ValueError:
            print(f"[x] Invalid date format: {date_str}. Use YYYY-MM-DD.")
            sys.exit(1)
    return f"{datetime.today().strftime('%Y-%m-%d')}.json"


def git_commit_and_push(filename):
    """
    Commit and push a file to the main branch using git.
    Args:
        filename (str): The file to commit and push.
    Returns:
        None
    """
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
