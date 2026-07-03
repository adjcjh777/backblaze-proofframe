#!/usr/bin/env python3
"""Build one no-secret status report for the final Devpost closeout."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.final_closeout_status.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-closeout-status.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-closeout-status.md"

REPORTS = {
    "final_control": ("docs/assets/final-submission-control.json", "proofframe.final_submission_control.v1"),
    "credential_handoff": ("docs/assets/live-credential-handoff.json", "proofframe.live_credential_handoff.v1"),
    "b2_evidence": ("docs/assets/b2-live-proof-evidence.json", "proofframe.b2_live_proof.v1"),
    "final_evidence": ("docs/assets/final-live-proof-evidence.json", "proofframe.final_live_proof.v1"),
    "public_video": ("docs/assets/public-video-check.json", "proofframe.public_video_check.v1"),
    "video_publish_kit": ("docs/assets/final-video-publish-kit.json", "proofframe.final_video_publish_kit.v1"),
    "devpost_checklist": ("docs/assets/devpost-submission-checklist.json", "proofframe.devpost_submission_checklist.v1"),
    "devpost_preview": ("docs/assets/devpost-submission-preview.json", "proofframe.devpost_submission_preview.v1"),
    "devpost_receipt": ("docs/assets/devpost-submission-receipt.json", "proofframe.devpost_submission_receipt.v1"),
    "secret_scan": ("docs/assets/secret-scan-report.json", "proofframe.secret_scan.v1"),
    "submission_audit": ("docs/assets/submission-audit-report.json", "proofframe.submission_audit.v1"),
    "submission_bundle": ("docs/assets/submission-bundle-manifest.json", "proofframe.submission_bundle.v1"),
    "public_space_sync": ("docs/assets/public-space-sync-report.json", "proofframe.public_space_sync.v1"),
}

REQUIRED_TASKS = ("T020", "T021", "T041", "T041A", "T042")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def report_status(root: Path, report_id: str, relative_path: str, schema: str) -> dict[str, Any]:
    path = root / relative_path
    report = load_json(path)
    if report is None:
        return {
            "id": report_id,
            "present": False,
            "schema_ok": False,
            "path": relative_path,
            "schema": None,
            "ok": None,
            "mode": None,
            "safe_to_submit": None,
        }
    return {
        "id": report_id,
        "present": True,
        "schema_ok": report.get("schema") == schema,
        "path": relative(path, root),
        "schema": report.get("schema"),
        "ok": report.get("ok"),
        "mode": report.get("mode"),
        "storage_backend": report.get("storage_backend"),
        "generation_backend": report.get("generation_backend"),
        "asset_storage_backend": report.get("asset_storage_backend"),
        "manifest_storage_backend": report.get("manifest_storage_backend"),
        "asset_storage_key": report.get("asset_storage_key"),
        "manifest_key": report.get("manifest_key"),
        "asset_sha256": report.get("asset_sha256"),
        "manifest_sha256": report.get("manifest_sha256"),
        "safe_to_submit": report.get("safe_to_submit"),
        "safe_to_share": report.get("safe_to_share"),
        "control_health_ok": report.get("control_health_ok"),
        "submission_gate_ok": (report.get("submission_gate") or {}).get("ok"),
        "submission_gate_mode": (report.get("submission_gate") or {}).get("mode"),
        "closeout_gate_status": (report.get("closeout_gate") or {}).get("status"),
        "ready_for_live_proof": report.get("ready_for_live_proof"),
        "final_video_ready": report.get("final_video_ready"),
        "final_form_ready": report.get("final_form_ready"),
        "public_video_ready": report.get("public_video_ready"),
        "project_url": report.get("project_url"),
        "missing_artifacts": report.get("missing_artifacts"),
        "missing_ids": report.get("missing_ids"),
        "findings_count": len(report.get("findings") or []),
    }


def gate_item(gate_id: str, label: str, ok: bool, detail: str, evidence: str) -> dict[str, Any]:
    return {"id": gate_id, "label": label, "ok": ok, "detail": detail, "evidence": evidence}


def evidence_ok(report: dict[str, Any], *, expected_mode: str | None = None) -> bool:
    if not (report["present"] and report["schema_ok"] and report["ok"] is True):
        return False
    if expected_mode is not None and report.get("mode") != expected_mode:
        return False
    return True


def b2_live_evidence_ok(report: dict[str, Any]) -> bool:
    if evidence_ok(report):
        return True
    return bool(
        report["present"]
        and report.get("ok") is True
        and report.get("storage_backend") == "b2"
        and report.get("generation_backend") == "mock"
        and report.get("asset_storage_backend") == "b2"
        and report.get("manifest_storage_backend") == "b2"
        and report.get("asset_storage_key")
        and report.get("manifest_key")
        and report.get("asset_sha256")
        and report.get("manifest_sha256")
    )


def credential_handoff_ready(report: dict[str, Any]) -> bool:
    if not (report["present"] and report["schema_ok"]):
        return False
    if report.get("ready_for_live_proof") is True:
        return True
    return bool(report.get("ok") is True and report.get("mode") == "live_env_ready")


def credential_handoff_detail(report: dict[str, Any]) -> str:
    missing = [str(item) for item in report.get("missing_ids", []) if item]
    suffix = f"; missing ids: {', '.join(missing)}" if missing else ""
    return f"Credential handoff mode is {report.get('mode')}{suffix}."


def submission_bundle_inputs_ready(report: dict[str, Any]) -> bool:
    return bool(
        report["present"]
        and report["schema_ok"]
        and report.get("safe_to_share") is True
        and report.get("missing_artifacts") == []
        and report.get("submission_gate_ok") is True
    )


def first_failed(gates: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((gate for gate in gates if not gate["ok"]), None)


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    statuses = task_statuses(root)
    reports = {
        report_id: report_status(root, report_id, relative_path, schema)
        for report_id, (relative_path, schema) in REPORTS.items()
    }

    final_control = reports["final_control"]
    credential_handoff = reports["credential_handoff"]
    b2_evidence = reports["b2_evidence"]
    final_evidence = reports["final_evidence"]
    public_video = reports["public_video"]
    video_publish_kit = reports["video_publish_kit"]
    devpost_checklist = reports["devpost_checklist"]
    devpost_receipt = reports["devpost_receipt"]
    secret_scan = reports["secret_scan"]
    submission_audit = reports["submission_audit"]
    submission_bundle = reports["submission_bundle"]
    public_space_sync = reports["public_space_sync"]

    report_inventory_ok = all(
        report["present"] and report["schema_ok"]
        for report_id, report in reports.items()
        if report_id not in {"b2_evidence", "final_evidence"}
    )
    expected_pre_live_missing_evidence = not b2_evidence["present"] and not final_evidence["present"]

    gates = [
        gate_item(
            "report_inventory",
            "Required closeout reports are present and schema-valid",
            report_inventory_ok,
            "All standing control reports are present; live evidence files may be absent before credentials."
            if report_inventory_ok
            else "One or more standing reports are missing or schema-invalid.",
            "docs/assets/*.json",
        ),
        gate_item(
            "ci_and_public_demo",
            "Public demo evidence is synced",
            bool(public_space_sync["present"] and public_space_sync["schema_ok"] and public_space_sync["ok"] is True),
            f"Public Space sync mode is {public_space_sync.get('mode')}; ok is {public_space_sync.get('ok')}.",
            public_space_sync["path"],
        ),
        gate_item(
            "credential_handoff",
            "Live credential handoff is ready",
            credential_handoff_ready(credential_handoff),
            credential_handoff_detail(credential_handoff),
            credential_handoff["path"],
        ),
        gate_item(
            "b2_live_proof",
            "Backblaze B2 live proof is captured",
            bool(b2_live_evidence_ok(b2_evidence) and statuses.get("T020") == "done"),
            f"T020 is {statuses.get('T020', 'missing')}; evidence present is {b2_evidence['present']}.",
            b2_evidence["path"],
        ),
        gate_item(
            "genblaze_live_proof",
            "Genblaze live proof is captured",
            bool(evidence_ok(final_evidence) and statuses.get("T021") == "done"),
            f"T021 is {statuses.get('T021', 'missing')}; final evidence present is {final_evidence['present']}.",
            final_evidence["path"],
        ),
        gate_item(
            "public_video",
            "Final public video URL is verified",
            bool(public_video.get("safe_to_submit") is True and video_publish_kit.get("final_video_ready") is True),
            (
                f"Public video mode is {public_video.get('mode')}; "
                f"video kit final_video_ready is {video_publish_kit.get('final_video_ready')}."
            ),
            public_video["path"],
        ),
        gate_item(
            "devpost_ready",
            "Devpost checklist is final-ready",
            bool(devpost_checklist.get("safe_to_submit") is True),
            f"Devpost checklist mode is {devpost_checklist.get('mode')}.",
            devpost_checklist["path"],
        ),
        gate_item(
            "final_secret_scan",
            "Final secret scan is clear after live artifacts",
            bool(secret_scan.get("ok") is True and secret_scan.get("mode") == "clear" and statuses.get("T041A") == "done"),
            f"T041A is {statuses.get('T041A', 'missing')}; secret scan mode is {secret_scan.get('mode')}.",
            secret_scan["path"],
        ),
        gate_item(
            "final_submission_audit",
            "Final submission audit is complete",
            bool(submission_audit.get("ok") is True and statuses.get("T041") == "done"),
            f"T041 is {statuses.get('T041', 'missing')}; audit mode is {submission_audit.get('mode')}.",
            submission_audit["path"],
        ),
        gate_item(
            "devpost_receipt",
            "Devpost submitted receipt is captured",
            bool(devpost_receipt.get("ok") is True and statuses.get("T042") == "done"),
            f"T042 is {statuses.get('T042', 'missing')}; receipt mode is {devpost_receipt.get('mode')}.",
            devpost_receipt["path"],
        ),
        gate_item(
            "final_bundle",
            "Final submission bundle inputs are ready",
            submission_bundle_inputs_ready(submission_bundle),
            (
                f"Bundle safe_to_share is {submission_bundle.get('safe_to_share')}; "
                f"submission_gate_ok is {submission_bundle.get('submission_gate_ok')}; "
                f"missing_artifacts is {submission_bundle.get('missing_artifacts')}."
            ),
            submission_bundle["path"],
        ),
        gate_item(
            "final_control",
            "Final control gate is green",
            bool(final_control.get("safe_to_submit") is True),
            f"Final control mode is {final_control.get('mode')}; safe_to_submit is {final_control.get('safe_to_submit')}.",
            final_control["path"],
        ),
    ]

    missing_required_tasks = [task_id for task_id in REQUIRED_TASKS if task_id not in statuses]
    unexpected_findings: list[dict[str, str]] = []
    if missing_required_tasks:
        unexpected_findings.append(
            {
                "id": "missing_required_tasks",
                "detail": "Missing task ids: " + ", ".join(missing_required_tasks),
            }
        )
    if not report_inventory_ok:
        missing_reports = [
            report_id
            for report_id, report in reports.items()
            if report_id not in {"b2_evidence", "final_evidence"} and not (report["present"] and report["schema_ok"])
        ]
        unexpected_findings.append(
            {
                "id": "report_inventory",
                "detail": "Missing or schema-invalid reports: " + ", ".join(missing_reports),
            }
        )

    blocker = first_failed(gates)
    safe_to_submit = all(gate["ok"] for gate in gates)
    if safe_to_submit:
        mode = "final_closeout_ready"
        phase = "submit_receipt_captured"
        next_command = "python scripts/submission_bundle.py --strict-final"
        next_detail = "All closeout gates are green; build the strict final bundle and preserve the Devpost receipt."
    elif unexpected_findings:
        mode = "closeout_needs_repair"
        phase = "repair_reports"
        next_command = "python scripts/final_submission_control.py"
        next_detail = "Repair missing or schema-invalid control reports before continuing."
    elif expected_pre_live_missing_evidence and blocker and blocker["id"] == "credential_handoff":
        mode = "waiting_for_credentials"
        phase = "credential_entry"
        next_command = "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force"
        next_detail = "Enter live credentials locally; do not paste secrets into chat, docs, screenshots, or git."
    elif blocker:
        mode = "closeout_blocked"
        phase = blocker["id"]
        next_command = next_command_for(blocker["id"])
        next_detail = blocker["detail"]
    else:
        mode = "closeout_blocked"
        phase = "unknown"
        next_command = "python scripts/final_submission_control.py"
        next_detail = "Closeout state could not be classified."

    closeout_health_ok = report_inventory_ok and not unexpected_findings
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": closeout_health_ok,
        "mode": mode,
        "phase": phase,
        "safe_to_submit": safe_to_submit,
        "closeout_health_ok": closeout_health_ok,
        "task_statuses": {task_id: statuses.get(task_id, "missing") for task_id in REQUIRED_TASKS},
        "reports": reports,
        "gates": gates,
        "unexpected_findings": unexpected_findings,
        "next_command": next_command,
        "next_detail": next_detail,
        "secret_policy": (
            "This closeout report stores only task statuses, report metadata, public URLs, and artifact paths; "
            "it never stores Backblaze keys, Genblaze provider keys, Devpost cookies, browser sessions, or signed URLs."
        ),
    }


def next_command_for(gate_id: str) -> str:
    commands = {
        "report_inventory": "python scripts/final_submission_control.py",
        "ci_and_public_demo": "python scripts/public_space_sync.py",
        "credential_handoff": "python scripts/live_env_handoff.py --env-file .env.final.local --strict",
        "b2_live_proof": "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
        "genblaze_live_proof": (
            "python scripts/run_final_live_proof.py --env-file .env.final.local "
            "--genblaze-provider openai --genblaze-image-model gpt-image-1 "
            "--evidence-out docs/assets/final-live-proof-evidence.json"
        ),
        "public_video": 'python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final',
        "devpost_ready": "python scripts/devpost_submission_checklist.py --strict-final",
        "final_secret_scan": "python scripts/secret_scan.py",
        "final_submission_audit": "python scripts/submission_audit.py --strict-final",
        "devpost_receipt": 'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
        "final_bundle": "python scripts/submission_bundle.py --strict-final",
        "final_control": "python scripts/final_submission_control.py --strict-final",
    }
    return commands.get(gate_id, "python scripts/final_submission_control.py")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Closeout Status",
        "",
        f"Mode: `{report['mode']}`",
        f"Phase: `{report['phase']}`",
        f"Closeout health OK: `{str(report['closeout_health_ok']).lower()}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        f"Next command: `{report['next_command']}`",
        "",
        report["secret_policy"],
        "",
        "## Gates",
        "",
        "| Status | Gate | Detail | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for gate in report["gates"]:
        status = "OK" if gate["ok"] else "BLOCKED"
        lines.append(f"| {status} | `{gate['id']}` | {gate['detail']} | `{gate['evidence']}` |")

    lines.extend(["", "## Task Statuses", ""])
    for task_id, status in report["task_statuses"].items():
        lines.append(f"- `{task_id}`: `{status}`")

    lines.extend(["", "## Unexpected Findings", ""])
    if report["unexpected_findings"]:
        lines.extend(f"- `{item['id']}`: {item['detail']}" for item in report["unexpected_findings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Next Detail", "", report["next_detail"], ""])
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ProofFrame final closeout status report.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Exit nonzero unless safe_to_submit is true.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(root=args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "phase": report["phase"],
                "safe_to_submit": report["safe_to_submit"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_command": report["next_command"],
                "unexpected_findings": len(report["unexpected_findings"]),
            },
            indent=2,
        )
    )
    if args.strict_final and not report["safe_to_submit"]:
        raise SystemExit(2)
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
