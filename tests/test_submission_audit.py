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


def test_check_tasks_fails_when_required_gates_are_not_done():
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
    assert {"T020", "T040", "T041", "T041A", "T042"} <= gates


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

    findings = submission_audit.check_final_evidence(evidence_path)

    gates = {finding["gate"] for finding in findings}
    assert "evidence.storage_backend" in gates
    assert "evidence.generation_backend" in gates
    assert "evidence.asset_sha256" in gates


def test_build_audit_report_passes_with_complete_inputs(tmp_path, monkeypatch):
    tasks_path = tmp_path / "tasks.json"
    evidence_path = tmp_path / "final-live-proof-evidence.json"
    tasks_path.write_text(
        json.dumps(
            tasks_payload({task_id: "done" for task_id in submission_audit.REQUIRED_DONE_TASKS})
        ),
        encoding="utf-8",
    )
    evidence_path.write_text(
        json.dumps(
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
            }
        ),
        encoding="utf-8",
    )
    for relative_path in submission_audit.REQUIRED_PUBLIC_FILES + submission_audit.REQUIRED_SCREENSHOTS:
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")
    monkeypatch.setattr(submission_audit, "ROOT", tmp_path)

    report = submission_audit.build_audit_report(tasks_path, evidence_path)

    assert report["ok"] is True
    assert report["findings"] == []
