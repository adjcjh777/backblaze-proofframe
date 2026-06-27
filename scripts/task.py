#!/usr/bin/env python3
"""Small task ledger helper for ProofFrame."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "tasks.json"
VALID_STATUSES = {"todo", "doing", "blocked", "done"}


def load_data() -> dict[str, Any]:
    with TASKS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    tmp_path = TASKS_PATH.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp_path.replace(TASKS_PATH)


def find_task(data: dict[str, Any], task_id: str) -> dict[str, Any]:
    task_id = task_id.upper()
    for task in data["tasks"]:
        if task["id"].upper() == task_id:
            return task
    raise SystemExit(f"Task not found: {task_id}")


def print_task(task: dict[str, Any]) -> None:
    note = f" | {task.get('notes', '')}" if task.get("notes") else ""
    print(f"{task['id']} [{task['status']}] {task['phase']} / {task['owner']} - {task['title']}{note}")


def cmd_list(args: argparse.Namespace) -> None:
    data = load_data()
    tasks = data["tasks"]
    if args.status:
        tasks = [task for task in tasks if task["status"] == args.status]
    if args.owner:
        tasks = [task for task in tasks if task["owner"] == args.owner]
    for task in tasks:
        print_task(task)


def cmd_show(args: argparse.Namespace) -> None:
    data = load_data()
    task = find_task(data, args.task_id)
    print(json.dumps(task, indent=2, ensure_ascii=False))


def update_status(args: argparse.Namespace, status: str) -> None:
    data = load_data()
    task = find_task(data, args.task_id)
    task["status"] = status
    if args.note:
        task["notes"] = args.note
    save_data(data)
    print_task(task)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query and update ProofFrame tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument("--status", choices=sorted(VALID_STATUSES))
    list_parser.add_argument("--owner")
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Show one task as JSON.")
    show_parser.add_argument("task_id")
    show_parser.set_defaults(func=cmd_show)

    for status in sorted(VALID_STATUSES):
        status_parser = subparsers.add_parser(status, help=f"Mark a task as {status}.")
        status_parser.add_argument("task_id")
        status_parser.add_argument("--note", default="")
        status_parser.set_defaults(func=lambda args, status=status: update_status(args, status))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
