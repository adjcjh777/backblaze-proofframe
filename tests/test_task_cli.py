import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "task.py"
SPEC = importlib.util.spec_from_file_location("task_cli", SCRIPT_PATH)
task_cli = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(task_cli)


def write_tasks(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "project": "ProofFrame",
                "updated_at": "2026-06-27T00:00:00Z",
                "tasks": [
                    {
                        "id": "T001",
                        "title": "Pick contest",
                        "phase": "P0 Foundation",
                        "owner": "scout",
                        "status": "done",
                        "done_criteria": "Contest is selected.",
                        "notes": "Backblaze event selected.",
                    },
                    {
                        "id": "T002",
                        "title": "Build task ledger",
                        "phase": "P0 Foundation",
                        "owner": "executor",
                        "status": "doing",
                        "done_criteria": "Tasks can be queried.",
                        "notes": "",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_cli(args: list[str]) -> None:
    parsed = task_cli.build_parser().parse_args(args)
    parsed.func(parsed)


def test_add_task_inserts_after_existing_task(tmp_path, monkeypatch, capsys):
    tasks_path = tmp_path / "tasks.json"
    write_tasks(tasks_path)
    monkeypatch.setattr(task_cli, "TASKS_PATH", tasks_path)

    run_cli(
        [
            "add",
            "T003",
            "Prepare Devpost copy",
            "--phase",
            "P4 Submit",
            "--owner",
            "controller",
            "--status",
            "todo",
            "--done-criteria",
            "Copy is ready.",
            "--note",
            "Needs live claim check.",
            "--after",
            "T001",
        ]
    )

    output = capsys.readouterr().out
    data = json.loads(tasks_path.read_text(encoding="utf-8"))
    assert "T003 [todo]" in output
    assert [task["id"] for task in data["tasks"]] == ["T001", "T003", "T002"]
    assert data["tasks"][1]["title"] == "Prepare Devpost copy"
    assert data["updated_at"] != "2026-06-27T00:00:00Z"


def test_add_task_rejects_duplicate_id(tmp_path, monkeypatch):
    tasks_path = tmp_path / "tasks.json"
    write_tasks(tasks_path)
    monkeypatch.setattr(task_cli, "TASKS_PATH", tasks_path)

    with pytest.raises(SystemExit, match="Task already exists"):
        run_cli(
            [
                "add",
                "t001",
                "Duplicate",
                "--phase",
                "P0 Foundation",
                "--owner",
                "scout",
            ]
        )


def test_search_matches_notes_and_filters_status(tmp_path, monkeypatch, capsys):
    tasks_path = tmp_path / "tasks.json"
    write_tasks(tasks_path)
    monkeypatch.setattr(task_cli, "TASKS_PATH", tasks_path)

    run_cli(["search", "Backblaze", "--status", "done"])

    output = capsys.readouterr().out
    assert "T001 [done]" in output
    assert "T002" not in output
