# File: planner/cli.py
import argparse
import sys
import os
from .core import (
    init_day, check_by_name, plan_hours, add_goal,
    mark_goal_by_name, show_summary, fuzzy_show_type,
    print_help_message, add_food, add_food_info, add_water
)
from .core.archive import get_today_filename, git_commit_and_push
from .core.food import sort_key
import json
from .display import (
    show_routine, show_plan, show_goals, show_food, show_all_columns
)
from .constants import TODAY_FILE, DATA_DIR

# Explicit aliases take precedence
alias_map = {
    "p": "plan",
    "c": "check",
    "cg": "check-goal",
    "ug": "uncheck-goal",
    "ch": "check",
    "tick": "check",
    "u": "uncheck",
    "unch": "uncheck",
    "untick": "uncheck",
    "ag": "add-goal",
    "addgoal": "add-goal",
    "newgoal": "add-goal",
    "s": "show",
    "sh": "show",
    "display": "show",
    "v": "show",
    "init": "init",
    "i": "init",
    "initialize": "init",
    "h": "help",
    "helpme": "help",
    "?": "help",
    "af": "add-food",
    "afi": "add-food-info",
    "ae": "add-exercise",
    "aw": "add-water",
    "water": "add-water",
}

# Canonical full commands (used for prefix matching)
canonical_cmds = [
    "interactive", "init", "show", "check", "uncheck",
    "check-goal", "uncheck-goal", "add-goal", "plan", "help",
    "add-food", "add-food-info", "add-exercise"
]


def resolve_cmd(cmd):
    # First: check exact aliases
    if cmd in alias_map:
        return alias_map[cmd]

    # Second: attempt prefix match against canonical list
    matches = [full for full in canonical_cmds if full.startswith(cmd)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise ValueError(f"Ambiguous command '{cmd}' matches: {matches}")
    else:
        return cmd  # no match found


# Example usage
if len(sys.argv) > 1:
    try:
        sys.argv[1] = resolve_cmd(sys.argv[1])
    except ValueError as e:
        print(e)
        sys.exit(1)


def interactive_mode():
    print("[🧠 Interactive Mode] Type 'exit', 'quit' or 'q' to leave.")
    while True:
        try:
            cmd = input("planner> ").strip()
            if cmd in ("exit", "quit", "q"):
                break
            if cmd:
                import subprocess
                subprocess.run([sys.executable, "main.py"] + cmd.split())
        except KeyboardInterrupt:
            print("[!] Interrupted by keyboard. Type 'exit' to quit.")


def handle_archive(args):
    """
    CLI handler to archive today's planner file (git commit and push).
    Args:
        args: argparse.Namespace with optional date argument.
    Returns:
        None
    """
    date_arg = args.date if hasattr(args, 'date') else None
    today_filename = get_today_filename(date_arg)
    git_commit_and_push(today_filename)


def handle_sort_food_db(args):
    """
    CLI handler to sort the food database by nutrient or name.
    Args:
        args: argparse.Namespace with optional mode argument.
    Returns:
        None
    """
    mode = args.mode[0].lower() if args.mode else 'n'
    from .constants import FOOD_DB_FILE
    with open(FOOD_DB_FILE, "r", encoding="utf-8") as f:
        food_db = json.load(f)
    reverse = mode in {"p", "f", "c"}
    sorted_items = sorted(
        food_db.items(),
        key=lambda x: sort_key(x, mode),
        reverse=reverse
    )
    sorted_db = {k: v for k, v in sorted_items}
    with open(FOOD_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_db, f, ensure_ascii=False, indent=2)
    print(
        f"[✓] Sorted by '{mode}' "
        f"({'desc' if reverse else 'asc'}) "
        f"and saved to {FOOD_DB_FILE}"
    )


def main():
    parser = argparse.ArgumentParser(description="Daily Planner")
    subparsers = parser.add_subparsers(dest="cmd")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("date", nargs="?", default=None)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("task_name")

    uncheck_parser = subparsers.add_parser("uncheck")
    uncheck_parser.add_argument("task_name")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("date", nargs="?", default=None)
    show_parser.add_argument("type", type=fuzzy_show_type, nargs="?",
                             default="all")

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("task")
    plan_parser.add_argument("start")
    plan_parser.add_argument("end", nargs='?', default=None)

    add_goal_parser = subparsers.add_parser("add-goal")
    add_goal_parser.add_argument("section")
    add_goal_parser.add_argument("text")

    goal_check_parser = subparsers.add_parser("check-goal")
    goal_check_parser.add_argument("section")
    goal_check_parser.add_argument("text")

    goal_uncheck_parser = subparsers.add_parser("uncheck-goal")
    goal_uncheck_parser.add_argument("section")
    goal_uncheck_parser.add_argument("text")

    food_parser = subparsers.add_parser("add-food")
    food_parser.add_argument("meal")
    food_parser.add_argument("name")
    food_parser.add_argument("weight", type=float)

    food_info_parser = subparsers.add_parser("add-food-info")
    food_info_parser.add_argument("name")
    food_info_parser.add_argument("protein", type=float)
    food_info_parser.add_argument("fat", type=float)
    food_info_parser.add_argument("carbon", type=float)

    water_parser = subparsers.add_parser("add-water")
    water_parser.add_argument("ml")

    archive_parser = subparsers.add_parser("archive")
    archive_parser.add_argument("date", nargs="?", default=None)
    archive_parser.set_defaults(func=handle_archive)

    sort_parser = subparsers.add_parser("sort-food-db")
    sort_parser.add_argument("mode", nargs="?", default="n")
    sort_parser.set_defaults(func=handle_sort_food_db)

    subparsers.add_parser("interactive")

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
        return
    if args.cmd == "init":
        init_day(args.date)
    elif args.cmd == "check":
        check_by_name(args.task_name, status=True)
    elif args.cmd == "uncheck":
        check_by_name(args.task_name, status=False)
    elif args.cmd == "show":
        file_path = (
            TODAY_FILE if args.date is None
            else os.path.join(DATA_DIR, f"{args.date}.json")
        )
        if args.type == "all":
            show_all_columns(file_path)
        elif args.type == "routine":
            show_routine(file_path)
        elif args.type == "plan":
            show_plan(file_path)
        elif args.type == "goals":
            show_goals(file_path)
        elif args.type == "food":
            show_food(file_path)
        elif args.type == "summary":
            show_summary()
    elif args.cmd == "plan":
        plan_hours(args.task, args.start, args.end)
    elif args.cmd == "add-goal":
        add_goal(args.section, args.text)
    elif args.cmd == "check-goal":
        mark_goal_by_name(args.section, args.text, status=True)
    elif args.cmd == "uncheck-goal":
        mark_goal_by_name(args.section, args.text, status=False)
    elif args.cmd == "add-food":
        add_food(args.meal, args.name, args.weight)
    elif args.cmd == "add-food-info":
        add_food_info(args.name, args.protein, args.fat, args.carbon)
    elif args.cmd == "add-water":
        if args:
            add_water(args.ml)
        else:
            print("[!] Please provide the amount of water in ml.")
    elif args.cmd == "help":
        print_help_message()
    elif args.cmd == "interactive":
        interactive_mode()
    else:
        parser.print_help()
