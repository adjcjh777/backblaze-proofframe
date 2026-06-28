import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_launch_plan.py"
SPEC = importlib.util.spec_from_file_location("final_launch_plan", SCRIPT_PATH)
final_launch_plan = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_launch_plan)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_tasks(root: Path, **overrides: str) -> None:
    statuses = {
        "T020": "doing",
        "T021": "doing",
        "T040": "done",
        "T041": "todo",
        "T041A": "todo",
        "T042": "todo",
    }
    statuses.update(overrides)
    write_json(
        root,
        "tasks.json",
        {
            "tasks": [
                {"id": task_id, "title": task_id, "status": status}
                for task_id, status in statuses.items()
            ]
        },
    )


def write_base_reports(root: Path) -> None:
    write_tasks(root)
    write_json(
        root,
        "docs/assets/live-credential-handoff.json",
        {
            "schema": "proofframe.live_credential_handoff.v1",
            "ok": False,
            "mode": "missing_live_env",
            "missing_ids": ["b2_key_id", "b2_application_key", "genblaze_api_key"],
        },
    )
    write_json(
        root,
        "docs/assets/final-operator-brief.json",
        {
            "schema": "proofframe.final_operator_brief.v1",
            "ready_for_secret_entry": True,
            "mode": "credential_entry_ready",
            "safe_to_submit": False,
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "pre_live_control",
            "safe_to_submit": False,
            "blocking_items": [
                {"id": "b2_live_proof"},
                {"id": "genblaze_live_proof"},
                {"id": "credential_handoff"},
                {"id": "public_video"},
                {"id": "final_recording"},
                {"id": "final_secret_scan"},
                {"id": "final_submission_audit"},
                {"id": "devpost_submitted"},
            ],
        },
    )
    write_json(
        root,
        "docs/assets/recording-assets.json",
        {"schema": "proofframe.recording_assets.v1", "final_video_ready": False},
    )
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {"schema": "proofframe.submission_audit.v1", "ok": False},
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {"schema": "proofframe.devpost_submission_receipt.v1", "ok": False},
    )


def test_launch_plan_is_ready_for_credential_entry(tmp_path):
    write_base_reports(tmp_path)

    plan = final_launch_plan.build_report(tmp_path)

    assert plan["ok"] is False
    assert plan["mode"] == "ready_for_credential_entry"
    assert plan["current_phase"] == "credential_entry"
    assert plan["summary"] == {"total": 6, "done": 0, "ready": 1, "blocked": 5}
    assert "final_env_wizard.py" in plan["next_command"]
    assert plan["safety_policy"]["source_env_files"] is False
    assert "source .env.final.local" not in json.dumps(plan)


def test_launch_plan_blocks_unexpected_credential_setup_gap(tmp_path):
    write_base_reports(tmp_path)
    handoff = json.loads((tmp_path / "docs/assets/live-credential-handoff.json").read_text())
    handoff["missing_ids"] = ["b2_endpoint", "b2_key_id"]
    write_json(tmp_path, "docs/assets/live-credential-handoff.json", handoff)

    plan = final_launch_plan.build_report(tmp_path)

    assert plan["mode"] == "blocked_at_credential_entry"
    assert plan["phases"][0]["status"] == "blocked"
    assert "unexpected setup values" in plan["phases"][0]["detail"]


def test_launch_plan_marks_devpost_ready_when_only_submission_remains(tmp_path):
    write_base_reports(tmp_path)
    write_tasks(tmp_path, T020="done", T021="done", T041="done", T041A="done")
    write_json(
        tmp_path,
        "docs/assets/live-credential-handoff.json",
        {"schema": "proofframe.live_credential_handoff.v1", "ok": True, "missing_ids": []},
    )
    write_json(
        tmp_path,
        "docs/assets/b2-live-proof-evidence.json",
        {"ok": True, "mode": "b2_live_verified"},
    )
    write_json(
        tmp_path,
        "docs/assets/final-live-proof-evidence.json",
        {"ok": True, "mode": "final_live_verified"},
    )
    write_json(
        tmp_path,
        "docs/assets/recording-assets.json",
        {"schema": "proofframe.recording_assets.v1", "final_video_ready": True},
    )
    write_json(
        tmp_path,
        "docs/assets/submission-audit-report.json",
        {"schema": "proofframe.submission_audit.v1", "ok": True},
    )
    write_json(
        tmp_path,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "pre_live_control",
            "safe_to_submit": False,
            "blocking_items": [{"id": "devpost_submitted"}],
        },
    )

    plan = final_launch_plan.build_report(tmp_path)

    assert plan["mode"] == "ready_for_devpost_submit"
    assert plan["current_phase"] == "devpost_submit"
    assert plan["summary"] == {"total": 6, "done": 5, "ready": 1, "blocked": 0}
    assert plan["phases"][-1]["status"] == "ready"
    assert "devpost_submission_receipt.py" in plan["next_command"]


def test_launch_plan_writes_outputs(tmp_path):
    write_base_reports(tmp_path)
    plan = final_launch_plan.build_report(tmp_path)
    json_path = tmp_path / "out" / "launch.json"
    markdown_path = tmp_path / "out" / "launch.md"

    final_launch_plan.write_outputs(plan, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == final_launch_plan.SCHEMA
    assert "# ProofFrame Final Launch Plan" in markdown
    assert "Do not source `.env.final.local`" in markdown
