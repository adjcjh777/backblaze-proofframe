"""Submission readiness gate for the browser demo and final audit flow."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


REQUIRED_FINAL_TASKS = ["T020", "T021", "T040", "T041", "T041A", "T042"]
FINAL_EVIDENCE_FIELDS: dict[str, Any] = {
    "ok": True,
    "storage_backend": "b2",
    "generation_backend": "genblaze",
    "asset_storage_backend": "b2",
    "asset_provider": "genblaze/gmicloud-image",
}
FINAL_EVIDENCE_REQUIRED_VALUES = [
    "asset_sha256",
    "manifest_sha256",
    "asset_storage_key",
    "manifest_key",
]


def project_root() -> Path:
    explicit_root = os.environ.get("PROOFFRAME_PROJECT_ROOT", "").strip()
    candidates = []
    if explicit_root:
        candidates.append(Path(explicit_root).expanduser())
    candidates.extend([Path.cwd(), Path(__file__).resolve().parents[2]])
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "tasks.json").exists() or (resolved / "apps" / "web").exists():
            return resolved
    return Path.cwd().resolve()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def task_lookup(tasks_data: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not tasks_data:
        return {}
    return {
        str(task.get("id", "")).upper(): task
        for task in tasks_data.get("tasks", [])
        if task.get("id")
    }


def build_task_gates(tasks_data: dict[str, Any] | None) -> list[dict[str, Any]]:
    tasks = task_lookup(tasks_data)
    gates: list[dict[str, Any]] = []
    for task_id in REQUIRED_FINAL_TASKS:
        task = tasks.get(task_id)
        status = str(task.get("status", "missing") if task else "missing")
        gates.append(
            {
                "id": task_id,
                "title": str(task.get("title", task_id) if task else task_id),
                "status": status,
                "ok": status == "done",
                "notes": str(task.get("notes", "") if task else ""),
            }
        )
    return gates


def build_evidence_gate(evidence_path: Path) -> dict[str, Any]:
    evidence = load_json(evidence_path)
    findings: list[dict[str, str]] = []
    if evidence is None:
        return {
            "ok": False,
            "status": "missing",
            "path": str(evidence_path),
            "findings": [
                {
                    "field": "final-live-proof-evidence",
                    "detail": "Final B2 and Genblaze evidence file is missing or invalid JSON.",
                }
            ],
        }

    for key, expected in FINAL_EVIDENCE_FIELDS.items():
        actual = evidence.get(key)
        if actual != expected:
            findings.append({"field": key, "detail": f"Expected {expected!r}, got {actual!r}."})
    for key in FINAL_EVIDENCE_REQUIRED_VALUES:
        if not evidence.get(key):
            findings.append({"field": key, "detail": "Required evidence value is missing."})

    return {
        "ok": not findings,
        "status": "verified" if not findings else "incomplete",
        "path": str(evidence_path),
        "findings": findings,
    }


def build_packet_gate(root: Path) -> dict[str, Any]:
    packet_path = root / "docs" / "assets" / "devpost-submission-packet.json"
    packet = load_json(packet_path)
    if packet is None:
        return {
            "ok": False,
            "status": "missing",
            "path": str(packet_path),
            "mode": None,
        }
    return {
        "ok": True,
        "status": "ready",
        "path": str(packet_path),
        "mode": packet.get("mode"),
        "claim_warning": packet.get("claim_warning"),
    }


def next_actions(task_gates: list[dict[str, Any]], evidence_gate: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    for gate in task_gates:
        if gate["ok"]:
            continue
        if gate["id"] == "T020":
            actions.append("Run a live Backblaze B2 asset and manifest proof.")
        elif gate["id"] == "T021":
            actions.append("Run a live Genblaze generation proof and capture provider metadata.")
        elif gate["id"] == "T040":
            actions.append("Complete Devpost registration after user-confirmed account details.")
        elif gate["id"] == "T041A":
            actions.append("Run the final secret scan before recording or submitting.")
        elif gate["id"] == "T041":
            actions.append("Run the final submission audit after live proofs are captured.")
        elif gate["id"] == "T042":
            actions.append("Submit the Devpost project after every preceding gate is done.")
    if not evidence_gate["ok"] and "Capture final live proof evidence JSON." not in actions:
        actions.append("Capture final live proof evidence JSON.")
    return actions[:5]


def build_submission_gate(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    tasks_path = root / "tasks.json"
    final_evidence_path = root / "docs" / "assets" / "final-live-proof-evidence.json"

    tasks_data = load_json(tasks_path)
    task_gates = build_task_gates(tasks_data)
    evidence_gate = build_evidence_gate(final_evidence_path)
    packet_gate = build_packet_gate(root)

    required_done = sum(1 for gate in task_gates if gate["ok"])
    blocked = sum(1 for gate in task_gates if gate["status"] == "blocked")
    doing = sum(1 for gate in task_gates if gate["status"] == "doing")
    todo = sum(1 for gate in task_gates if gate["status"] == "todo")
    missing = sum(1 for gate in task_gates if gate["status"] == "missing")
    ready = required_done == len(task_gates) and evidence_gate["ok"] and packet_gate["ok"]

    return {
        "ok": ready,
        "mode": "final_ready" if ready else "pre_live_safe",
        "tasks_path": str(tasks_path),
        "summary": {
            "required": len(task_gates),
            "done": required_done,
            "blocked": blocked,
            "doing": doing,
            "todo": todo,
            "missing": missing,
        },
        "task_gates": task_gates,
        "evidence_gate": evidence_gate,
        "packet_gate": packet_gate,
        "next_actions": next_actions(task_gates, evidence_gate),
    }
