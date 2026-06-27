import json
from pathlib import Path

from proofframe.submission_gate import REQUIRED_FINAL_TASKS, build_submission_gate


def write_tasks(root: Path, status: str = "done") -> None:
    (root / "tasks.json").write_text(
        json.dumps(
            {
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
                    for task_id in REQUIRED_FINAL_TASKS
                ],
            }
        ),
        encoding="utf-8",
    )


def write_packet(root: Path, mode: str = "pre_live_safe") -> None:
    packet_path = root / "docs" / "assets" / "devpost-submission-packet.json"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps({"mode": mode, "claim_warning": "safe"}), encoding="utf-8")


def write_live_evidence(root: Path) -> None:
    evidence_path = root / "docs" / "assets" / "final-live-proof-evidence.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
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


def test_submission_gate_fails_closed_without_live_evidence(tmp_path):
    write_tasks(tmp_path, status="done")
    write_packet(tmp_path)

    gate = build_submission_gate(tmp_path)

    assert gate["ok"] is False
    assert gate["mode"] == "pre_live_safe"
    assert gate["summary"]["done"] == len(REQUIRED_FINAL_TASKS)
    assert gate["evidence_gate"]["status"] == "missing"
    assert "Capture final live proof evidence JSON." in gate["next_actions"]


def test_submission_gate_passes_with_done_tasks_packet_and_live_evidence(tmp_path):
    write_tasks(tmp_path, status="done")
    write_packet(tmp_path, mode="post_live_verified")
    write_live_evidence(tmp_path)

    gate = build_submission_gate(tmp_path)

    assert gate["ok"] is True
    assert gate["mode"] == "final_ready"
    assert gate["summary"]["done"] == len(REQUIRED_FINAL_TASKS)
    assert gate["evidence_gate"]["ok"] is True
    assert gate["packet_gate"]["mode"] == "post_live_verified"
    assert gate["next_actions"] == []
