# File: planner/cli.py
import argparse
import sys
from .core import (
    init_day, check_by_name, plan_hours, add_goal,
    mark_goal_by_name, show_summary, fuzzy_show_type,
    print_help_message
)
from .display import show_routine, show_plan, show_goals, show_all_columns

# Explicit aliases take precedence
alias_map = {
    "p":"plan",
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
    "?": "help"
}

# Canonical full commands (used for prefix matching)
canonical_cmds = [
    "interactive", "init", "show", "check", "uncheck",
    "check-goal", "uncheck-goal", "add-goal", "plan", "help"
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


def main():
    parser = argparse.ArgumentParser(description="Daily Planner")
    subparsers = parser.add_subparsers(dest="cmd")

    subparsers.add_parser("init")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("task_name")

    uncheck_parser = subparsers.add_parser("uncheck")
    uncheck_parser.add_argument("task_name")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("type", type=fuzzy_show_type, nargs="?", default="all")

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

    help_parser = subparsers.add_parser("help")
    subparsers.add_parser("interactive")

    args = parser.parse_args()
    if args.cmd == "init":
        init_day()
    elif args.cmd == "check":
        check_by_name(args.task_name, status=True)
    elif args.cmd == "uncheck":
        check_by_name(args.task_name, status=False)
    elif args.cmd == "show":
        if args.type == "all":
            show_all_columns()
        elif args.type == "routine":
            show_routine()
        elif args.type == "plan":
            show_plan()
        elif args.type == "goals":
            show_goals()
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
    elif args.cmd == "help":
        print_help_message()
    elif args.cmd == "interactive":
        interactive_mode()
    else:
        parser.print_help()
