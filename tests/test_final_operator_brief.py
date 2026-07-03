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
        "docs/assets/b2-key-scope-checklist.json",
        {
            "schema": "proofframe.b2_key_scope_checklist.v1",
            "pre_key_creation_confirmation": {
                "status": "required_before_key_creation",
                "required_phrase": (
                    "I confirm ProofFrame B2 key scope: standard key, bucket proofframe-demo, "
                    "prefix campaigns/, no all-bucket access, no delete/admin permissions, "
                    "and no secrets in chat/docs/git."
                ),
                "safe_to_store": True,
            },
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
        "docs/assets/public-video-check.json",
        {
            "schema": "proofframe.public_video_check.v1",
            "mode": "pending_video_url",
            "safe_to_submit": False,
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
        "docs/assets/secret-scan-report.json",
        {
            "schema": "proofframe.secret_scan.v1",
            "mode": "clear",
            "ok": True,
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
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {
            "schema": "proofframe.submission_audit.v1",
            "mode": "pre_submit_audit_blocked",
            "ok": False,
        },
    )
    write_json(
        root,
        "docs/assets/final-rehearsal-checklist.json",
        {
            "schema": "proofframe.final_rehearsal.v1",
            "mode": "ready_for_credential_rehearsal",
            "ok": True,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-checklist.json",
        {
            "schema": "proofframe.devpost_submission_checklist.v1",
            "mode": "pre_submit_blocked",
            "ok": False,
            "safe_to_submit": False,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {
            "schema": "proofframe.devpost_submission_receipt.v1",
            "mode": "pending_submission",
            "ok": False,
        },
    )
    write_json(
        root,
        "docs/assets/submission-bundle-manifest.json",
        {
            "schema": "proofframe.submission_bundle.v1",
            "mode": "pre_live_safe",
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
    assert report["b2_pre_key_confirmation"]["status"] == "required_before_key_creation"
    assert any("I confirm ProofFrame B2 key scope" in action for action in report["user_actions"])
    assert any("least-privilege Backblaze B2" in action for action in report["user_actions"])
    assert 'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"' in report[
        "codex_actions_after_credentials"
    ]
    assert report["codex_actions_after_credentials"][0] == (
        "python scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks"
    )
    assert report["codex_actions_after_credentials"][1:4] == [
        'python scripts/public_space_upload.py --execute --commit-message "Sync ProofFrame public Space after live proof"',
        "python scripts/public_space_sync.py --wait-attempts 5 --wait-seconds 30",
        "python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space",
    ]
    assert not any(
        action.startswith("python scripts/run_b2_live_proof.py")
        or action.startswith("python scripts/run_final_live_proof.py")
        for action in report["codex_actions_after_credentials"]
    )
    assert "python scripts/submission_audit.py --strict-final" in report["codex_actions_after_credentials"]
    assert "python scripts/devpost_submission_preview.py" in report["codex_actions_after_credentials"]
    assert "python scripts/devpost_submission_checklist.py --strict-final" in report[
        "codex_actions_after_credentials"
    ]
    assert "docs/assets/devpost-submission-preview.json" in report["safety_policy"]["safe_to_commit_after_scan"]
    assert any(
        action.startswith('python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL"')
        for action in report["codex_actions_after_credentials"]
    )
    actions = report["codex_actions_after_credentials"]
    receipt_index = next(index for index, action in enumerate(actions) if action.startswith("python scripts/devpost_submission_receipt.py"))
    assert actions[receipt_index + 1 :] == [
        "python scripts/secret_scan.py",
        "python scripts/final_submission_control.py --strict-final",
        "python scripts/final_launch_plan.py --strict-final",
        "python scripts/devpost_submission_preview.py --strict-final",
        "python scripts/submission_bundle.py --strict-final",
        'python scripts/public_space_upload.py --execute --commit-message "Sync ProofFrame public Space after final receipt"',
        "python scripts/public_space_sync.py --wait-attempts 5 --wait-seconds 30",
        "python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space",
    ]
    assert report["reports"]["secret_scan"]["schema_ok"] is True
    assert report["reports"]["public_video_check"]["schema_ok"] is True
    assert report["reports"]["submission_audit"]["schema_ok"] is True
    assert report["reports"]["final_rehearsal"]["schema_ok"] is True
    assert report["reports"]["devpost_submission_checklist"]["schema_ok"] is True
    assert report["reports"]["devpost_submission_receipt"]["schema_ok"] is True
    assert report["reports"]["submission_bundle"]["schema_ok"] is True


def test_final_operator_brief_is_ready_for_genblaze_live_proof(tmp_path):
    write_ready_fixtures(tmp_path)
    write_json(
        tmp_path,
        "tasks.json",
        {
            "tasks": [
                {"id": "T020", "title": "T020", "status": "done"},
                {"id": "T021", "title": "T021", "status": "blocked"},
                {"id": "T040", "title": "T040", "status": "done"},
                {"id": "T041", "title": "T041", "status": "todo"},
                {"id": "T041A", "title": "T041A", "status": "todo"},
                {"id": "T042", "title": "T042", "status": "todo"},
            ]
        },
    )
    write_json(
        tmp_path,
        "docs/assets/live-credential-handoff.json",
        {
            "schema": "proofframe.live_credential_handoff.v1",
            "mode": "live_env_ready",
            "ok": True,
            "source": ".env.final.local",
            "missing_ids": [],
            "required": [
                {"id": "storage_backend_mode", "ok": True},
                {"id": "generation_backend_mode", "ok": True},
                {"id": "b2_endpoint", "ok": True},
                {"id": "b2_bucket", "ok": True},
                {"id": "b2_key_id", "ok": True},
                {"id": "b2_application_key", "ok": True},
                {"id": "genblaze_api_key", "ok": True},
                {"id": "genblaze_image_model", "ok": True},
            ],
        },
    )

    report = final_operator_brief.build_report(tmp_path)

    assert report["mode"] == "genblaze_live_proof_ready"
    assert report["ready_for_secret_entry"] is False
    assert report["ready_for_genblaze_live_proof"] is True
    assert report["credential_handoff"]["missing_ids"] == []
    assert any("Genblaze account access or credits" in action for action in report["user_actions"])


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
    assert "I confirm ProofFrame B2 key scope" in markdown
