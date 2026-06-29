import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_closeout_status.py"
SPEC = importlib.util.spec_from_file_location("final_closeout_status", SCRIPT_PATH)
final_closeout_status = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_closeout_status)

LIVE_ENV_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "live_env_handoff.py"
LIVE_ENV_SPEC = importlib.util.spec_from_file_location("live_env_handoff", LIVE_ENV_SCRIPT_PATH)
live_env_handoff = importlib.util.module_from_spec(LIVE_ENV_SPEC)
assert LIVE_ENV_SPEC.loader is not None
LIVE_ENV_SPEC.loader.exec_module(live_env_handoff)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_tasks(root: Path, *, final_ready: bool = False) -> None:
    statuses = {
        "T020": "done" if final_ready else "doing",
        "T021": "done" if final_ready else "doing",
        "T041": "done" if final_ready else "todo",
        "T041A": "done" if final_ready else "todo",
        "T042": "done" if final_ready else "todo",
    }
    write_json(
        root,
        "tasks.json",
        {"tasks": [{"id": task_id, "status": status} for task_id, status in statuses.items()]},
    )


def write_common_reports(root: Path, *, final_ready: bool = False) -> None:
    write_tasks(root, final_ready=final_ready)
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "ok": True,
            "control_health_ok": True,
            "mode": "final_submit_ready" if final_ready else "pre_live_control",
            "safe_to_submit": final_ready,
        },
    )
    env_file = root / ".env.test"
    env_file.write_text(
        "\n".join(
            [
                "PROOFFRAME_STORAGE_BACKEND=b2" if final_ready else "PROOFFRAME_STORAGE_BACKEND=local",
                "PROOFFRAME_GENERATION_BACKEND=genblaze" if final_ready else "PROOFFRAME_GENERATION_BACKEND=mock",
                "B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com" if final_ready else "",
                "B2_BUCKET=proofframe-test" if final_ready else "",
                "B2_KEY_ID=fixture" if final_ready else "",
                "B2_APPLICATION_KEY=fixture" if final_ready else "",
                "GENBLAZE_API_KEY=fixture" if final_ready else "",
                "GENBLAZE_IMAGE_MODEL=test-image-model" if final_ready else "",
            ]
        ),
        encoding="utf-8",
    )
    write_json(
        root,
        "docs/assets/live-credential-handoff.json",
        live_env_handoff.build_report(env_file),
    )
    write_json(
        root,
        "docs/assets/public-video-check.json",
        {
            "schema": "proofframe.public_video_check.v1",
            "mode": "public_video_verified" if final_ready else "pending_video_url",
            "ok": final_ready,
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/final-video-publish-kit.json",
        {
            "schema": "proofframe.final_video_publish_kit.v1",
            "ok": True,
            "mode": "public_video_ready" if final_ready else "ready_for_final_upload",
            "safe_to_submit": final_ready,
            "final_video_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-checklist.json",
        {
            "schema": "proofframe.devpost_submission_checklist.v1",
            "ok": final_ready,
            "mode": "ready_to_submit_devpost" if final_ready else "pre_submit_blocked",
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-preview.json",
        {
            "schema": "proofframe.devpost_submission_preview.v1",
            "ok": True,
            "mode": "final_preview_ready" if final_ready else "pre_live_preview_ready",
            "safe_to_share": True,
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {
            "schema": "proofframe.devpost_submission_receipt.v1",
            "ok": final_ready,
            "mode": "submitted" if final_ready else "pending_submission",
            "project_url": "https://devpost.com/software/proofframe" if final_ready else None,
        },
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {"schema": "proofframe.secret_scan.v1", "ok": True, "mode": "clear"},
    )
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {
            "schema": "proofframe.submission_audit.v1",
            "ok": final_ready,
            "mode": "final_audit_ready" if final_ready else "pre_submit_audit_blocked",
        },
    )
    write_json(
        root,
        "docs/assets/submission-bundle-manifest.json",
        {
            "schema": "proofframe.submission_bundle.v1",
            "safe_to_share": True,
            "safe_to_submit": False,
            "submission_gate": {"ok": final_ready, "mode": "final_ready" if final_ready else "pre_live_safe"},
            "missing_artifacts": [],
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {"schema": "proofframe.public_space_sync.v1", "ok": True, "mode": "public_space_synced"},
    )
    if final_ready:
        write_json(
            root,
            "docs/assets/b2-live-proof-evidence.json",
            {"schema": "proofframe.b2_live_proof.v1", "ok": True, "mode": "b2_live_proof_ready"},
        )
        write_json(
            root,
            "docs/assets/final-live-proof-evidence.json",
            {"schema": "proofframe.final_live_proof.v1", "ok": True, "mode": "final_live_proof_ready"},
        )


def test_closeout_status_waits_for_credentials_in_pre_live_state(tmp_path):
    write_common_reports(tmp_path, final_ready=False)

    report = final_closeout_status.build_report(root=tmp_path)

    assert report["schema"] == "proofframe.final_closeout_status.v1"
    assert report["ok"] is True
    assert report["closeout_health_ok"] is True
    assert report["safe_to_submit"] is False
    assert report["mode"] == "waiting_for_credentials"
    assert report["phase"] == "credential_entry"
    assert ".env.final.local" in report["next_command"]


def test_closeout_status_can_be_final_ready(tmp_path):
    write_common_reports(tmp_path, final_ready=True)

    report = final_closeout_status.build_report(root=tmp_path)

    assert report["ok"] is True
    assert report["safe_to_submit"] is True
    assert report["mode"] == "final_closeout_ready"
    assert all(gate["ok"] for gate in report["gates"])
    credential_report = report["reports"]["credential_handoff"]
    raw_credential_report = json.loads(
        (tmp_path / "docs/assets/live-credential-handoff.json").read_text(encoding="utf-8")
    )
    assert credential_report["mode"] == "live_env_ready"
    assert credential_report["ready_for_live_proof"] is None
    assert "ready_for_live_proof" not in raw_credential_report


def test_closeout_status_requires_live_tasks_done_even_when_evidence_exists(tmp_path):
    write_common_reports(tmp_path, final_ready=True)
    write_tasks(tmp_path, final_ready=False)

    report = final_closeout_status.build_report(root=tmp_path)

    assert report["safe_to_submit"] is False
    gates = {gate["id"]: gate for gate in report["gates"]}
    assert gates["b2_live_proof"]["ok"] is False
    assert gates["genblaze_live_proof"]["ok"] is False
    assert "T020 is doing" in gates["b2_live_proof"]["detail"]
    assert "T021 is doing" in gates["genblaze_live_proof"]["detail"]


def test_closeout_status_uses_bundle_inputs_not_bundle_safe_to_submit(tmp_path):
    write_common_reports(tmp_path, final_ready=True)

    report = final_closeout_status.build_report(root=tmp_path)

    gates = {gate["id"]: gate for gate in report["gates"]}
    assert gates["final_bundle"]["ok"] is True
    assert report["safe_to_submit"] is True


def test_closeout_status_reports_missing_control_reports(tmp_path):
    write_common_reports(tmp_path, final_ready=False)
    (tmp_path / "docs/assets/public-space-sync-report.json").unlink()

    report = final_closeout_status.build_report(root=tmp_path)

    assert report["ok"] is False
    assert report["mode"] == "closeout_needs_repair"
    assert report["unexpected_findings"]
    assert "public_space_sync" in report["unexpected_findings"][0]["detail"]
