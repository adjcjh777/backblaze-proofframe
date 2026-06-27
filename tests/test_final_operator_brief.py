import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_operator_brief.py"
SPEC = importlib.util.spec_from_file_location("final_operator_brief", SCRIPT_PATH)
final_operator_brief = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_operator_brief)


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_file(root, relative_path, json.dumps(payload))


def write_tasks(root: Path) -> None:
    statuses = {
        "T020": "doing",
        "T021": "doing",
        "T040": "done",
        "T041": "todo",
        "T041A": "todo",
        "T042": "todo",
    }
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


def write_ready_fixtures(root: Path) -> None:
    write_tasks(root)
    write_file(root, ".gitignore", ".env.*\n!.env.final.example\n.env.final.local\n")
    write_json(
        root,
        "docs/assets/b2-live-setup.json",
        {
            "status": "bucket_created_key_pending",
            "bucket_name": "proofframe-demo",
            "endpoint": "s3.us-west-004.backblazeb2.com",
            "bucket_type": "private",
            "prepared_application_key_name": "proofframe-demo-live-proof",
            "application_key_status": "form_prepared_not_created",
        },
    )
    write_json(
        root,
        "docs/assets/live-credential-handoff.json",
        {
            "schema": "proofframe.live_credential_handoff.v1",
            "mode": "missing_live_env",
            "ok": False,
            "source": ".env.final.local",
            "missing_ids": ["b2_key_id", "b2_application_key", "genblaze_api_key"],
            "required": [
                {"id": "storage_backend_mode", "ok": True},
                {"id": "generation_backend_mode", "ok": True},
                {"id": "b2_endpoint", "ok": True},
                {"id": "b2_bucket", "ok": True},
                {"id": "b2_key_id", "ok": False},
                {"id": "b2_application_key", "ok": False},
                {"id": "genblaze_api_key", "ok": False},
                {"id": "genblaze_image_model", "ok": True},
            ],
        },
    )
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {"schema": "proofframe.devpost_event_snapshot.v1", "validation": {"ok": True}},
    )
    write_json(
        root,
        "docs/assets/recording-assets.json",
        {
            "schema": "proofframe.recording_assets.v1",
            "mock_recording_ready": True,
            "public_mock_verified": True,
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {
            "schema": "proofframe.award_readiness.v1",
            "mode": "pre_live_competitive",
            "score": 97,
            "max_score": 115,
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "pre_live_control",
            "safe_to_submit": False,
        },
    )


def test_final_operator_brief_is_ready_for_secret_entry(tmp_path):
    write_ready_fixtures(tmp_path)

    report = final_operator_brief.build_report(tmp_path)

    assert report["mode"] == "credential_entry_ready"
    assert report["ready_for_secret_entry"] is True
    assert report["safe_to_submit"] is False
    assert report["credential_handoff"]["missing_ids"] == [
        "b2_key_id",
        "b2_application_key",
        "genblaze_api_key",
    ]
    assert report["safety_policy"]["env_final_local_ignored"] is True
    assert any("least-privilege Backblaze B2" in action for action in report["user_actions"])


def test_final_operator_brief_blocks_unexpected_missing_values(tmp_path):
    write_ready_fixtures(tmp_path)
    handoff = json.loads((tmp_path / "docs/assets/live-credential-handoff.json").read_text())
    handoff["missing_ids"] = ["b2_endpoint", "b2_key_id"]
    write_json(tmp_path, "docs/assets/live-credential-handoff.json", handoff)

    report = final_operator_brief.build_report(tmp_path)

    assert report["ready_for_secret_entry"] is False
    assert report["mode"] == "needs_operator_setup"


def test_final_operator_brief_writes_outputs(tmp_path):
    write_ready_fixtures(tmp_path)
    report = final_operator_brief.build_report(tmp_path)
    json_path = tmp_path / "out" / "brief.json"
    markdown_path = tmp_path / "out" / "brief.md"

    final_operator_brief.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == final_operator_brief.SCHEMA
    assert "# ProofFrame Final Operator Brief" in markdown
    assert "## User Actions" in markdown
