"""Submission readiness gate for the browser demo and final audit flow."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


REQUIRED_FINAL_TASKS = ["T020", "T021", "T040", "T041", "T041A", "T042"]
REQUIRED_FINAL_REPORTS = [
    {
        "id": "secret_scan",
        "task_id": "T041A",
        "path": "docs/assets/secret-scan-report.json",
        "schema": "proofframe.secret_scan.v1",
        "action": "Run the final secret scan and capture a clean report.",
    },
    {
        "id": "submission_audit",
        "task_id": "T041",
        "path": "docs/assets/submission-audit-report.json",
        "schema": "proofframe.submission_audit.v1",
        "action": "Run the final submission audit and capture a passing report.",
    },
    {
        "id": "devpost_submission_receipt",
        "task_id": "T042",
        "path": "docs/assets/devpost-submission-receipt.json",
        "schema": "proofframe.devpost_submission_receipt.v1",
        "action": "Capture the public-safe Devpost submission receipt after submitting.",
    },
]
FINAL_EVIDENCE_FIELDS: dict[str, Any] = {
    "ok": True,
    "storage_backend": "b2",
    "generation_backend": "genblaze",
    "asset_storage_backend": "b2",
}
FINAL_ALLOWED_ASSET_PROVIDERS = {"genblaze/gmicloud-image", "genblaze/openai-image"}
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


def display_path(path: Path, root: Path | None = None) -> str:
    if root is not None:
        try:
            return str(path.resolve().relative_to(root.resolve()))
        except ValueError:
            pass
    return str(path)


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


def build_evidence_gate(evidence_path: Path, root: Path | None = None) -> dict[str, Any]:
    evidence = load_json(evidence_path)
    findings: list[dict[str, str]] = []
    if evidence is None:
        return {
            "ok": False,
            "status": "missing",
            "path": display_path(evidence_path, root),
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
    asset_provider = evidence.get("asset_provider")
    if asset_provider not in FINAL_ALLOWED_ASSET_PROVIDERS:
        findings.append(
            {
                "field": "asset_provider",
                "detail": (
                    "Expected one of "
                    f"{sorted(FINAL_ALLOWED_ASSET_PROVIDERS)!r}, got {asset_provider!r}."
                ),
            }
        )
    for key in FINAL_EVIDENCE_REQUIRED_VALUES:
        if not evidence.get(key):
            findings.append({"field": key, "detail": "Required evidence value is missing."})

    return {
        "ok": not findings,
        "status": "verified" if not findings else "incomplete",
        "path": display_path(evidence_path, root),
        "findings": findings,
    }


def build_packet_gate(root: Path) -> dict[str, Any]:
    packet_path = root / "docs" / "assets" / "devpost-submission-packet.json"
    packet = load_json(packet_path)
    if packet is None:
        return {
            "ok": False,
            "status": "missing",
            "path": display_path(packet_path, root),
            "mode": None,
        }
    mode = packet.get("mode")
    final_packet_ready = mode == "post_live_verified"
    if final_packet_ready:
        status = "post_live_packet_ready"
    elif mode == "pre_live_safe":
        status = "pre_live_packet_pending"
    else:
        status = "invalid_packet_mode"
    return {
        "ok": final_packet_ready,
        "status": status,
        "path": display_path(packet_path, root),
        "mode": mode,
        "claim_warning": packet.get("claim_warning"),
    }


def build_report_gate(root: Path) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []
    for spec in REQUIRED_FINAL_REPORTS:
        path = root / spec["path"]
        report = load_json(path)
        record: dict[str, Any] = {
            "id": spec["id"],
            "task_id": spec["task_id"],
            "path": display_path(path, root),
            "required_schema": spec["schema"],
            "schema": None,
            "schema_ok": False,
            "ok": False,
            "status": "missing",
            "mode": None,
            "findings": [],
        }
        if report is None:
            detail = "Required final report is missing or invalid JSON."
            finding = {"report": spec["id"], "field": "file", "detail": detail}
            record["findings"].append(finding)
            findings.append(finding)
            reports.append(record)
            continue

        schema = report.get("schema")
        schema_ok = schema == spec["schema"]
        ok = report.get("ok") is True
        report_findings: list[dict[str, str]] = []
        if not schema_ok:
            report_findings.append(
                {
                    "report": spec["id"],
                    "field": "schema",
                    "detail": f"Expected {spec['schema']!r}, got {schema!r}.",
                }
            )
        if not ok:
            report_findings.append(
                {
                    "report": spec["id"],
                    "field": "ok",
                    "detail": "Final report must explicitly set ok=true.",
                }
            )

        record.update(
            {
                "schema": schema,
                "schema_ok": schema_ok,
                "ok": schema_ok and ok,
                "status": "verified" if schema_ok and ok else "incomplete",
                "mode": report.get("mode"),
                "findings": report_findings,
            }
        )
        reports.append(record)
        findings.extend(report_findings)

    if all(report["ok"] for report in reports):
        status = "verified"
    elif any(report["status"] == "missing" for report in reports):
        status = "missing"
    else:
        status = "incomplete"

    return {
        "ok": not findings,
        "status": status,
        "reports": reports,
        "findings": findings,
    }


def next_actions(
    task_gates: list[dict[str, Any]],
    evidence_gate: dict[str, Any],
    packet_gate: dict[str, Any],
    report_gate: dict[str, Any],
) -> list[str]:
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
    if not packet_gate["ok"]:
        actions.append("Regenerate the Devpost packet in post-live mode with the public video URL.")
    for report in report_gate["reports"]:
        if report["ok"]:
            continue
        action = next(
            spec["action"]
            for spec in REQUIRED_FINAL_REPORTS
            if spec["id"] == report["id"]
        )
        if action not in actions:
            actions.append(action)
    return actions[:5]


def build_submission_gate(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    tasks_path = root / "tasks.json"
    final_evidence_path = root / "docs" / "assets" / "final-live-proof-evidence.json"

    tasks_data = load_json(tasks_path)
    task_gates = build_task_gates(tasks_data)
    evidence_gate = build_evidence_gate(final_evidence_path, root)
    packet_gate = build_packet_gate(root)
    report_gate = build_report_gate(root)

    required_done = sum(1 for gate in task_gates if gate["ok"])
    blocked = sum(1 for gate in task_gates if gate["status"] == "blocked")
    doing = sum(1 for gate in task_gates if gate["status"] == "doing")
    todo = sum(1 for gate in task_gates if gate["status"] == "todo")
    missing = sum(1 for gate in task_gates if gate["status"] == "missing")
    ready = (
        required_done == len(task_gates)
        and evidence_gate["ok"]
        and packet_gate["ok"]
        and report_gate["ok"]
    )

    return {
        "ok": ready,
        "mode": "final_ready" if ready else "pre_live_safe",
        "tasks_path": display_path(tasks_path, root),
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
        "report_gate": report_gate,
        "next_actions": next_actions(task_gates, evidence_gate, packet_gate, report_gate),
    }
