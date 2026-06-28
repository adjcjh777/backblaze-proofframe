import importlib.util
import json
import shlex
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_submission_control.py"
SPEC = importlib.util.spec_from_file_location("final_submission_control", SCRIPT_PATH)
final_submission_control = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_submission_control)


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_file(root, relative_path, json.dumps(payload))


def write_tasks(root: Path, *, final_done: bool = False) -> None:
    statuses = {
        "T020": "done" if final_done else "doing",
        "T021": "done" if final_done else "doing",
        "T040": "done",
        "T041": "done" if final_done else "todo",
        "T041A": "done" if final_done else "todo",
        "T042": "done" if final_done else "todo",
    }
    write_json(
        root,
        "tasks.json",
        {
            "project": "ProofFrame",
            "tasks": [
                {"id": task_id, "title": task_id, "status": status}
                for task_id, status in statuses.items()
            ],
        },
    )


def write_common_reports(root: Path, *, final_done: bool = False) -> None:
    write_tasks(root, final_done=final_done)
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "mode": "post_live_verified" if final_done else "pre_live_safe",
            "claim_warning": "safe",
        },
    )
    write_json(
        root,
        "docs/assets/devpost-form-kit.json",
        {
            "schema": "proofframe.devpost_form_kit.v1",
            "mode": "final_form_ready" if final_done else "pre_live_form_ready",
            "final_form_ready": final_done,
            "public_video_ready": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-checklist.json",
        {
            "schema": "proofframe.devpost_submission_checklist.v1",
            "mode": "ready_to_submit_devpost" if final_done else "pre_submit_blocked",
            "ok": final_done,
            "safe_to_submit": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {
            "schema": "proofframe.devpost_event_snapshot.v1",
            "mode": "live_official_snapshot",
            "checked_at": "2026-06-27T16:00:00Z",
            "validation": {
                "ok": True,
                "age_days": 0,
                "submission_open": True,
            },
            "event": {
                "name": "Backblaze Generative Media Hackathon",
                "devpost_url": "https://backblaze-generative-media.devpost.com/",
                "rules_url": "https://backblaze-generative-media.devpost.com/rules",
                "deadline_et": "Aug 3, 2026 @ 5:00pm EDT",
                "deadline_beijing": "2026-08-04 05:00 Asia/Shanghai",
                "prize_total_usd": 10000,
                "participant_count_observed": 343,
                "participant_count_checked_at": "2026-06-28 Asia/Shanghai",
                "participant_count_note": "Dynamic Devpost count; recheck before final public claims.",
            },
        },
    )
    write_json(
        root,
        "docs/assets/demo-storyboard.json",
        {
            "schema": "proofframe.demo_storyboard.v1",
            "mode": "final_video_ready" if final_done else "mock_storyboard_ready",
            "final_video_ready": final_done,
            "public_video_ready": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/public-video-check.json",
        {
            "schema": "proofframe.public_video_check.v1",
            "mode": "public_video_verified" if final_done else "pending_video_url",
            "safe_to_submit": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/agent-handoff-report.json",
        {
            "schema": "proofframe.agent_handoff.v1",
            "mode": "handoff_ready",
            "ok": True,
            "bus": {
                "status": "stale",
                "active_role_cwd_ok": True,
            },
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {
            "schema": "proofframe.public_space_sync.v1",
            "mode": "public_space_synced",
            "ok": True,
        },
    )
    write_json(
        root,
        "docs/assets/final-launch-plan.json",
        {
            "schema": "proofframe.final_launch_plan.v1",
            "ok": final_done,
            "mode": "submitted" if final_done else "ready_for_credential_entry",
            "current_phase": "complete" if final_done else "credential_entry",
            "next_command": None
            if final_done
            else "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
            "next_detail": "Final launch is complete."
            if final_done
            else "Only expected secret ids are missing; operator can enter them locally.",
        },
    )
    write_json(
        root,
        "docs/assets/demo-readiness-report.json",
        {
            "schema": "proofframe.demo_readiness.v1",
            "mode": "final_ready" if final_done else "pre_live_mock_ready",
            "final_recording_ready": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/recording-assets.json",
        {
            "schema": "proofframe.recording_assets.v1",
            "mode": "final_video_ready" if final_done else "public_mock_verified",
            "mock_recording_ready": True,
            "public_mock_verified": True,
            "final_video_ready": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {
            "schema": "proofframe.award_readiness.v1",
            "mode": "final_award_ready" if final_done else "pre_live_competitive",
            "score": 82,
            "max_score": 111,
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
        "docs/assets/submission-audit-report.json",
        {
            "schema": "proofframe.submission_audit.v1",
            "mode": "pre_submit_audit_ready" if final_done else "pre_submit_audit_blocked",
            "ok": final_done,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {
            "schema": "proofframe.devpost_submission_receipt.v1",
            "mode": "submitted" if final_done else "pending_submission",
            "ok": final_done,
            "project_url": "https://devpost.com/software/proofframe" if final_done else None,
        },
    )
    required = [
        {"id": "b2_key_id", "ok": final_done},
        {"id": "b2_application_key", "ok": final_done},
        {"id": "genblaze_api_key", "ok": final_done},
    ]
    write_json(
        root,
        "docs/assets/live-credential-handoff.json",
        {
            "schema": "proofframe.live_credential_handoff.v1",
            "mode": "ready" if final_done else "missing_live_env",
            "ready_for_live_proof": final_done,
            "required": required,
        },
    )
    if final_done:
        write_json(
            root,
            "docs/assets/final-live-proof-evidence.json",
            {
                "ok": True,
                "storage_backend": "b2",
                "generation_backend": "genblaze",
                "asset_storage_backend": "b2",
                "asset_provider": "genblaze/gmicloud-image",
                "asset_sha256": "a" * 64,
                "manifest_sha256": "b" * 64,
                "asset_storage_key": "campaigns/cmp/media/asset.png",
                "manifest_key": "campaigns/cmp/manifests/manifest.json",
            },
        )


def test_control_report_blocks_pre_live_submission(tmp_path):
    write_common_reports(tmp_path)

    report = final_submission_control.build_control_report(tmp_path)

    assert report["mode"] == "pre_live_control"
    assert report["safe_to_submit"] is False
    assert "b2_live_proof" in {item["id"] for item in report["blocking_items"]}
    assert "source_report_schemas" not in {item["id"] for item in report["blocking_items"]}
    assert report["event"]["participant_count_observed"] == 343
    assert "B2_KEY_ID" in report["next_actions"][0]
    assert report["report_inputs"]["devpost_form"]["path"] == "docs/assets/devpost-form-kit.json"
    assert report["report_inputs"]["devpost_submission_checklist"]["path"] == "docs/assets/devpost-submission-checklist.json"
    assert report["report_inputs"]["agent_handoff"]["mode"] == "handoff_ready"
    assert report["report_inputs"]["agent_handoff"]["bus_status"] == "stale"
    assert report["report_inputs"]["agent_handoff"]["active_role_cwd_ok"] is True
    assert report["warnings"][0]["id"] == "agent_handoff_bus_stale"
    handoff_requirement = next(item for item in report["requirements"] if item["id"] == "agent_handoff")
    assert "bus status is stale" in handoff_requirement["detail"]
    assert "active role cwd ok is True" in handoff_requirement["detail"]
    assert report["report_inputs"]["public_space_sync"]["mode"] == "public_space_synced"
    assert report["report_inputs"]["final_launch_plan"]["current_phase"] == "credential_entry"
    assert report["report_inputs"]["public_video_check"]["path"] == "docs/assets/public-video-check.json"
    launch_requirement = next(item for item in report["requirements"] if item["id"] == "final_launch_plan")
    assert launch_requirement["ok"] is True
    assert "current phase is credential_entry" in launch_requirement["detail"]
    assert str(tmp_path) not in json.dumps(report)


def test_control_report_turns_final_ready_when_all_gates_are_done(tmp_path):
    write_common_reports(tmp_path, final_done=True)

    report = final_submission_control.build_control_report(tmp_path)

    assert report["mode"] == "final_submit_ready"
    assert report["safe_to_submit"] is True
    assert report["blocking_items"] == []
    assert report["submission_gate"]["b2_evidence_status"] == "missing"


def test_control_report_requires_devpost_receipt_when_t042_is_done(tmp_path):
    write_common_reports(tmp_path, final_done=True)
    write_json(
        tmp_path,
        "docs/assets/devpost-submission-receipt.json",
        {
            "schema": "proofframe.devpost_submission_receipt.v1",
            "mode": "pending_submission",
            "ok": False,
        },
    )

    report = final_submission_control.build_control_report(tmp_path)

    blocking = {item["id"] for item in report["blocking_items"]}
    assert "devpost_submitted" in blocking
    assert report["safe_to_submit"] is False


def test_control_report_blocks_bad_input_schema(tmp_path):
    write_common_reports(tmp_path, final_done=True)
    write_json(
        tmp_path,
        "docs/assets/demo-readiness-report.json",
        {
            "schema": "wrong.schema",
            "mode": "final_ready",
            "final_recording_ready": True,
        },
    )

    report = final_submission_control.build_control_report(tmp_path)

    blocking = {item["id"] for item in report["blocking_items"]}
    assert "source_report_schemas" in blocking
    assert "final_recording" in blocking
    assert report["safe_to_submit"] is False


def test_control_report_writes_json_and_markdown(tmp_path):
    write_common_reports(tmp_path)
    report = final_submission_control.build_control_report(tmp_path)
    json_path = tmp_path / "out" / "control.json"
    markdown_path = tmp_path / "out" / "control.md"

    final_submission_control.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.final_submission_control.v1"
    assert "# ProofFrame Final Submission Control" in markdown
    assert "Safe to submit: `false`" in markdown
    assert "## Launch Plan" in markdown
    assert "Current phase: `credential_entry`" in markdown
    assert "final_env_wizard.py" in markdown
    assert "## Warnings" in markdown
    assert "agent_handoff_bus_stale" in markdown
    assert 'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"' in markdown
    assert "python scripts/devpost_submission_checklist.py --strict-final" in markdown
    assert "python scripts/submission_audit.py --strict-final" in markdown
    assert 'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL"' in markdown
    assert "python scripts/devpost_submission_preview.py --strict-final" in markdown
    assert "python scripts/submission_bundle.py --strict-final" in markdown


def test_operator_commands_are_shell_safe_and_parseable():
    root = Path(__file__).resolve().parents[1]

    for index, command in enumerate(final_submission_control.OPERATOR_COMMANDS, start=1):
        assert "<" not in command and ">" not in command, f"command {index} is not shell-safe: {command}"
        parts = shlex.split(command)
        assert parts[:1] == ["python"]
        script = root / parts[1]
        assert script.exists(), f"command {index} references missing script: {parts[1]}"

        spec = importlib.util.spec_from_file_location(f"operator_command_{index}_{script.stem}", script)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.build_parser().parse_args(parts[2:])


def test_operator_commands_close_out_submission_bundle_after_receipt():
    commands = final_submission_control.OPERATOR_COMMANDS
    receipt_index = next(
        index for index, command in enumerate(commands) if command.startswith("python scripts/devpost_submission_receipt.py")
    )

    assert commands[receipt_index + 1 :] == [
        "python scripts/secret_scan.py",
        "python scripts/final_submission_control.py --strict-final",
        "python scripts/final_launch_plan.py --strict-final",
        "python scripts/devpost_submission_preview.py --strict-final",
        "python scripts/submission_bundle.py --strict-final",
    ]
