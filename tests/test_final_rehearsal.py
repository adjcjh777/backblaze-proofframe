import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_rehearsal.py"
SPEC = importlib.util.spec_from_file_location("final_rehearsal", SCRIPT_PATH)
final_rehearsal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_rehearsal)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_ready_fixtures(root: Path) -> None:
    write_json(
        root,
        "tasks.json",
        {
            "tasks": [
                {"id": "T020", "status": "doing"},
                {"id": "T021", "status": "doing"},
                {"id": "T040", "status": "done"},
                {"id": "T041", "status": "todo"},
                {"id": "T041A", "status": "todo"},
                {"id": "T042", "status": "todo"},
            ]
        },
    )
    write_json(
        root,
        "docs/assets/final-operator-brief.json",
        {
            "schema": "proofframe.final_operator_brief.v1",
            "mode": "credential_entry_ready",
            "ready_for_secret_entry": True,
            "credential_handoff": {
                "missing_ids": ["b2_key_id", "b2_application_key", "genblaze_api_key"]
            },
        },
    )
    write_json(
        root,
        "docs/assets/final-launch-plan.json",
        {
            "schema": "proofframe.final_launch_plan.v1",
            "mode": "ready_for_credential_entry",
            "current_phase": "credential_entry",
            "next_command": "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "pre_live_control",
            "safe_to_submit": False,
            "blocking_items": ["b2_live_proof", "genblaze_live_proof"],
        },
    )
    write_json(
        root,
        "docs/assets/devpost-form-kit.json",
        {
            "schema": "proofframe.devpost_form_kit.v1",
            "mode": "pre_live_form_ready",
            "mock_form_ready": True,
            "final_form_ready": False,
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {
            "schema": "proofframe.public_space_sync.v1",
            "mode": "public_space_synced",
            "ok": True,
            "observed": {"runtime_sha": "abc123"},
            "failed_checks": [],
        },
    )
    write_json(
        root,
        "docs/assets/recording-assets.json",
        {
            "schema": "proofframe.recording_assets.v1",
            "mode": "public_mock_verified",
            "mock_recording_ready": True,
            "final_video_ready": False,
        },
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {"schema": "proofframe.secret_scan.v1", "mode": "clear", "ok": True},
    )
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {"schema": "proofframe.submission_audit.v1", "mode": "pre_submit_audit_blocked", "ok": False},
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {"schema": "proofframe.devpost_submission_receipt.v1", "mode": "pending_submission", "ok": False},
    )


def test_final_rehearsal_is_ready_for_credential_entry(tmp_path):
    write_ready_fixtures(tmp_path)

    report = final_rehearsal.build_report(tmp_path)

    assert report["schema"] == final_rehearsal.SCHEMA
    assert report["ok"] is True
    assert report["mode"] == "ready_for_credential_rehearsal"
    assert report["safe_to_submit"] is False
    assert report["required_secret_ids"] == ["b2_key_id", "b2_application_key", "genblaze_api_key"]
    assert report["next_command"].endswith("--force")
    assert any(step["id"] == "final_green_gate" for step in report["steps"])
    assert any(step["id"] == "devpost_submission_preview" for step in report["steps"])
    step_ids = [step["id"] for step in report["steps"]]
    assert step_ids[step_ids.index("devpost_receipt") + 1] == "final_green_gate"
    final_green_gate = next(step for step in report["steps"] if step["id"] == "final_green_gate")
    assert final_green_gate["command"] == (
        "python scripts/secret_scan.py && "
        "python scripts/final_submission_control.py --strict-final && "
        "python scripts/final_launch_plan.py --strict-final && "
        "python scripts/devpost_submission_preview.py --strict-final && "
        "python scripts/submission_bundle.py --strict-final"
    )
    assert "docs/assets/submission-bundle-manifest.json" in final_green_gate["safe_to_commit"]
    assert any("Stop immediately" in rule for rule in report["stop_rules"])


def test_final_rehearsal_blocks_unsafe_overclaim(tmp_path):
    write_ready_fixtures(tmp_path)
    tasks = json.loads((tmp_path / "tasks.json").read_text(encoding="utf-8"))
    tasks["tasks"][0]["status"] = "done"
    write_json(tmp_path, "tasks.json", tasks)

    report = final_rehearsal.build_report(tmp_path)

    failed = {item["id"] for item in report["preconditions"] if not item["ok"]}
    assert report["ok"] is False
    assert report["mode"] == "needs_rehearsal_setup"
    assert "live_tasks_not_overclaimed" in failed


def test_final_rehearsal_writes_outputs(tmp_path):
    write_ready_fixtures(tmp_path)
    report = final_rehearsal.build_report(tmp_path)
    json_path = tmp_path / "out" / "rehearsal.json"
    markdown_path = tmp_path / "out" / "rehearsal.md"

    final_rehearsal.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.final_rehearsal.v1"
    assert "# ProofFrame Final Rehearsal Checklist" in markdown
    assert "This checklist contains secret names only" in markdown
