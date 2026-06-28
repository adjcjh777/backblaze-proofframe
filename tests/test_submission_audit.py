import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "submission_audit.py"
SPEC = importlib.util.spec_from_file_location("submission_audit", SCRIPT_PATH)
submission_audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(submission_audit)


def tasks_payload(statuses: dict[str, str]) -> dict:
    return {
        "project": "ProofFrame",
        "updated_at": "2026-06-27T00:00:00Z",
        "tasks": [
            {
                "id": task_id,
                "title": f"{task_id} gate",
                "phase": "P4 Submit",
                "owner": "tester",
                "status": status,
                "done_criteria": "Gate passes.",
                "notes": "",
            }
            for task_id, status in statuses.items()
        ],
    }


def write_text(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_text(root, relative_path, json.dumps(payload))


def write_complete_audit_fixture(root: Path) -> tuple[Path, Path]:
    tasks_path = root / "tasks.json"
    evidence_path = root / "docs/assets/final-live-proof-evidence.json"
    write_json(
        root,
        "tasks.json",
        tasks_payload(
            {
                "T020": "done",
                "T021": "done",
                "T040": "done",
                "T041": "todo",
                "T041A": "done",
                "T042": "todo",
            }
        ),
    )
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
    for relative_path in submission_audit.REQUIRED_PUBLIC_FILES:
        if relative_path.endswith(".json"):
            write_json(root, relative_path, {"schema": "fixture"})
        else:
            write_text(root, relative_path, "# ProofFrame\n")
    for relative_path in submission_audit.REQUIRED_SCREENSHOTS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")

    for relative_path, schema in submission_audit.REQUIRED_REPORT_SCHEMAS.items():
        write_json(root, relative_path, {"schema": schema})
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "schema": "proofframe.devpost_packet.v1",
            "mode": "post_live_verified",
            "video_url": "https://youtu.be/proofframe-demo",
            "submission_checklist": [
                {"task": task_id, "status": "done"}
                for task_id in submission_audit.REQUIRED_PRE_SUBMIT_TASKS
            ],
        },
    )
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {
            "schema": "proofframe.devpost_event_snapshot.v1",
            "validation": {"ok": True, "submission_open": True},
        },
    )
    write_json(
        root,
        "docs/assets/devpost-form-kit.json",
        {"schema": "proofframe.devpost_form_kit.v1", "final_form_ready": True},
    )
    write_json(
        root,
        "docs/assets/devpost-submission-checklist.json",
        {"schema": "proofframe.devpost_submission_checklist.v1", "safe_to_submit": True},
    )
    write_json(
        root,
        "docs/assets/demo-storyboard.json",
        {"schema": "proofframe.demo_storyboard.v1", "public_video_ready": True},
    )
    write_json(
        root,
        "docs/assets/public-video-check.json",
        {"schema": "proofframe.public_video_check.v1", "safe_to_submit": True},
    )
    write_json(
        root,
        "docs/assets/demo-readiness-report.json",
        {"schema": "proofframe.demo_readiness.v1", "final_recording_ready": True},
    )
    write_json(
        root,
        "docs/assets/recording-assets.json",
        {"schema": "proofframe.recording_assets.v1", "final_video_ready": True},
    )
    write_json(
        root,
        "docs/assets/live-credential-handoff.json",
        {"ready_for_live_proof": True},
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {"schema": "proofframe.award_readiness.v1", "score": 100, "max_score": 115},
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {"schema": "proofframe.secret_scan.v1", "mode": "clear", "ok": True},
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "blocking_items": [
                {"id": "final_submission_audit"},
                {"id": "devpost_submitted"},
            ],
        },
    )
    write_json(
        root,
        "docs/assets/final-operator-brief.json",
        {"schema": "proofframe.final_operator_brief.v1"},
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
    return tasks_path, evidence_path


def test_check_tasks_fails_when_required_pre_submit_gates_are_not_done():
    report = submission_audit.check_tasks(
        tasks_payload(
            {
                "T020": "doing",
                "T021": "done",
                "T040": "blocked",
                "T041": "todo",
                "T041A": "todo",
                "T042": "todo",
            }
        )
    )

    gates = {finding["gate"] for finding in report}
    assert {"T020", "T040", "T041A"} <= gates
    assert "T041" not in gates
    assert "T042" not in gates


def test_check_final_evidence_requires_live_b2_and_genblaze(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "ok": True,
                "storage_backend": "local",
                "generation_backend": "mock",
                "asset_storage_backend": "local",
                "asset_provider": "mock",
            }
        ),
        encoding="utf-8",
    )

    findings = submission_audit.check_final_evidence(evidence_path, tmp_path)

    gates = {finding["gate"] for finding in findings}
    assert "evidence.storage_backend" in gates
    assert "evidence.generation_backend" in gates
    assert "evidence.asset_sha256" in gates


def test_devpost_packet_requires_post_live_public_video_url(tmp_path):
    write_json(
        tmp_path,
        "docs/assets/devpost-submission-packet.json",
        {
            "schema": "proofframe.devpost_packet.v1",
            "mode": "pre_live_safe",
            "video_url": "TBD after final proof.",
            "submission_checklist": [],
        },
    )

    findings = submission_audit.check_devpost_packet(tmp_path)

    gates = {finding["gate"] for finding in findings}
    assert "devpost_packet.mode" in gates
    assert "devpost_packet.video_url" in gates


def test_final_control_allows_only_audit_and_submit_blockers(tmp_path):
    write_json(
        tmp_path,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "blocking_items": [
                {"id": "final_submission_audit"},
                {"id": "devpost_submitted"},
                {"id": "public_video"},
            ],
        },
    )

    findings = submission_audit.check_final_control(tmp_path)

    assert findings[0]["gate"] == "final_submission_control.blocking_items"
    assert "public_video" in findings[0]["detail"]


def test_build_audit_report_passes_before_t041_and_t042_are_done(tmp_path):
    tasks_path, evidence_path = write_complete_audit_fixture(tmp_path)

    report = submission_audit.build_audit_report(tasks_path, evidence_path, root=tmp_path)

    assert report["schema"] == "proofframe.submission_audit.v1"
    assert report["ok"] is True
    assert report["mode"] == "pre_submit_audit_ready"
    assert report["root"] == "."
    assert report["task_statuses"]["T041"] == "todo"
    assert report["task_statuses"]["T042"] == "todo"
    assert report["findings"] == []


def test_write_outputs_creates_json_and_markdown(tmp_path):
    tasks_path, evidence_path = write_complete_audit_fixture(tmp_path)
    report = submission_audit.build_audit_report(tasks_path, evidence_path, root=tmp_path)
    json_path = tmp_path / "out/audit.json"
    markdown_path = tmp_path / "out/audit.md"

    submission_audit.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.submission_audit.v1"
    assert "# ProofFrame Submission Audit" in markdown
    assert "generate the public submission receipt" in markdown
