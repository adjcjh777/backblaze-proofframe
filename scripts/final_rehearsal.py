#!/usr/bin/env python3
"""Build a no-secret final-submission rehearsal checklist."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-rehearsal-checklist.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-rehearsal-checklist.md"
SCHEMA = "proofframe.final_rehearsal.v1"
EXPECTED_SECRET_MISSING_IDS = ["b2_key_id", "b2_application_key", "genblaze_api_key"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def task_statuses(root: Path) -> dict[str, str]:
    data = load_json(root / "tasks.json")
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in data.get("tasks", [])
    }


def report(root: Path, relative_path: str, expected_schema: str) -> dict[str, Any]:
    payload = load_json(root / relative_path)
    return {
        "path": relative_path,
        "present": bool(payload),
        "schema_ok": payload.get("schema") == expected_schema,
        "mode": payload.get("mode"),
        "ok": payload.get("ok"),
        "safe_to_submit": payload.get("safe_to_submit"),
        "ready_for_secret_entry": payload.get("ready_for_secret_entry"),
        "current_phase": payload.get("current_phase"),
        "next_command": payload.get("next_command"),
        "mock_form_ready": payload.get("mock_form_ready"),
        "final_form_ready": payload.get("final_form_ready"),
        "mock_recording_ready": payload.get("mock_recording_ready"),
        "final_video_ready": payload.get("final_video_ready"),
        "runtime_sha": (payload.get("observed") or {}).get("runtime_sha"),
        "failed_checks": payload.get("failed_checks", []),
        "missing_ids": payload.get("missing_ids")
        or (payload.get("credential_handoff") or {}).get("missing_ids", []),
        "blocking_items": payload.get("blocking_items", []),
    }


def current_reports(root: Path) -> dict[str, dict[str, Any]]:
    return {
        "operator_brief": report(
            root,
            "docs/assets/final-operator-brief.json",
            "proofframe.final_operator_brief.v1",
        ),
        "launch_plan": report(
            root,
            "docs/assets/final-launch-plan.json",
            "proofframe.final_launch_plan.v1",
        ),
        "final_control": report(
            root,
            "docs/assets/final-submission-control.json",
            "proofframe.final_submission_control.v1",
        ),
        "devpost_form": report(
            root,
            "docs/assets/devpost-form-kit.json",
            "proofframe.devpost_form_kit.v1",
        ),
        "public_space_sync": report(
            root,
            "docs/assets/public-space-sync-report.json",
            "proofframe.public_space_sync.v1",
        ),
        "recording_assets": report(
            root,
            "docs/assets/recording-assets.json",
            "proofframe.recording_assets.v1",
        ),
        "secret_scan": report(
            root,
            "docs/assets/secret-scan-report.json",
            "proofframe.secret_scan.v1",
        ),
        "submission_audit": report(
            root,
            "docs/assets/submission-audit-report.json",
            "proofframe.submission_audit.v1",
        ),
        "devpost_receipt": report(
            root,
            "docs/assets/devpost-submission-receipt.json",
            "proofframe.devpost_submission_receipt.v1",
        ),
    }


def public_space_ready(report_data: dict[str, Any]) -> bool:
    return bool(report_data.get("schema_ok") and report_data.get("ok") is True and not report_data.get("failed_checks"))


def build_preconditions(reports: dict[str, dict[str, Any]], statuses: dict[str, str]) -> list[dict[str, Any]]:
    missing_ids = sorted(str(item) for item in reports["operator_brief"].get("missing_ids", []))
    return [
        {
            "id": "operator_ready",
            "ok": reports["operator_brief"].get("ready_for_secret_entry") is True,
            "detail": f"Operator brief mode is {reports['operator_brief'].get('mode')}.",
            "evidence": reports["operator_brief"]["path"],
        },
        {
            "id": "only_expected_secrets_missing",
            "ok": missing_ids == sorted(EXPECTED_SECRET_MISSING_IDS),
            "detail": f"Missing ids: {', '.join(missing_ids) or 'none'}.",
            "evidence": reports["operator_brief"]["path"],
        },
        {
            "id": "launch_plan_at_credential_entry",
            "ok": reports["launch_plan"].get("mode") == "ready_for_credential_entry",
            "detail": f"Current phase is {reports['launch_plan'].get('current_phase')}.",
            "evidence": reports["launch_plan"]["path"],
        },
        {
            "id": "public_space_synced",
            "ok": public_space_ready(reports["public_space_sync"]),
            "detail": f"Runtime sha: {reports['public_space_sync'].get('runtime_sha')}.",
            "evidence": reports["public_space_sync"]["path"],
        },
        {
            "id": "mock_form_ready",
            "ok": reports["devpost_form"].get("mock_form_ready") is True,
            "detail": f"Devpost form mode is {reports['devpost_form'].get('mode')}.",
            "evidence": reports["devpost_form"]["path"],
        },
        {
            "id": "mock_recording_ready",
            "ok": reports["recording_assets"].get("mock_recording_ready") is True,
            "detail": f"Recording assets mode is {reports['recording_assets'].get('mode')}.",
            "evidence": reports["recording_assets"]["path"],
        },
        {
            "id": "secret_scan_currently_clear",
            "ok": reports["secret_scan"].get("ok") is True and reports["secret_scan"].get("mode") == "clear",
            "detail": f"Secret scan mode is {reports['secret_scan'].get('mode')}.",
            "evidence": reports["secret_scan"]["path"],
        },
        {
            "id": "final_gate_fail_closed",
            "ok": reports["final_control"].get("safe_to_submit") is False,
            "detail": f"Final control mode is {reports['final_control'].get('mode')}.",
            "evidence": reports["final_control"]["path"],
        },
        {
            "id": "live_tasks_not_overclaimed",
            "ok": statuses.get("T020") != "done" and statuses.get("T021") != "done",
            "detail": f"T020={statuses.get('T020')}; T021={statuses.get('T021')}.",
            "evidence": "tasks.json",
        },
    ]


def rehearsal_steps() -> list[dict[str, Any]]:
    return [
        {
            "id": "enter_credentials",
            "owner": "operator",
            "command": "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
            "success_signal": "docs/assets/live-credential-handoff.json reports no missing ids after live_env_handoff.py --strict.",
            "safe_to_commit": [],
        },
        {
            "id": "b2_live_proof",
            "owner": "codex",
            "command": "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
            "success_signal": "B2 evidence JSON has ok=true, storage_backend=b2, asset and manifest checksums, and sanitized object keys.",
            "safe_to_commit": ["docs/assets/b2-live-proof-evidence.json"],
            "task_update": 'python3 scripts/task.py done T020 --note "B2 live proof evidence captured in docs/assets/b2-live-proof-evidence.json."',
        },
        {
            "id": "final_live_proof",
            "owner": "codex",
            "command": (
                "python scripts/run_final_live_proof.py --env-file .env.final.local "
                "--genblaze-provider openai --genblaze-image-model gpt-image-1 "
                "--evidence-out docs/assets/final-live-proof-evidence.json"
            ),
            "success_signal": "Final evidence JSON has storage_backend=b2, generation_backend=genblaze, provider/model metadata, checksums, and no raw provider URLs.",
            "safe_to_commit": ["docs/assets/final-live-proof-evidence.json"],
            "task_update": 'python3 scripts/task.py done T021 --note "Final B2 plus Genblaze live proof evidence captured in docs/assets/final-live-proof-evidence.json."',
        },
        {
            "id": "seed_public_video_packet",
            "owner": "codex",
            "command": 'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" && python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final',
            "success_signal": "Devpost packet includes the public video URL and public-video-check reports safe_to_submit=true.",
            "safe_to_commit": [
                "docs/assets/devpost-submission-packet.json",
                "docs/assets/public-video-check.json",
            ],
        },
        {
            "id": "final_secret_scan",
            "owner": "codex",
            "command": "python scripts/secret_scan.py",
            "success_signal": "Secret scan is clear after live proof and public video URL are present.",
            "safe_to_commit": [
                "docs/assets/secret-scan-report.json",
            ],
            "task_update": 'python3 scripts/task.py done T041A --note "Final secret scan clear after live proof and public video."',
        },
        {
            "id": "final_video_reports",
            "owner": "codex",
            "command": "python scripts/devpost_form_kit.py --strict-final && python scripts/demo_storyboard.py --strict-final && python scripts/demo_readiness.py --strict-final && python scripts/recording_assets.py --verify-public --strict-final",
            "success_signal": "Devpost form kit, storyboard, demo readiness, and recording assets all report final video readiness.",
            "safe_to_commit": [
                "docs/assets/devpost-form-kit.json",
                "docs/assets/demo-storyboard.json",
                "docs/assets/demo-readiness-report.json",
                "docs/assets/recording-assets.json",
            ],
        },
        {
            "id": "devpost_submission_checklist",
            "owner": "codex",
            "command": "python scripts/devpost_submission_checklist.py --strict-final",
            "success_signal": "Devpost submission checklist is ready_to_submit_devpost.",
            "safe_to_commit": [
                "docs/assets/devpost-submission-checklist.json",
            ],
        },
        {
            "id": "devpost_submission_preview",
            "owner": "codex",
            "command": "python scripts/devpost_submission_preview.py",
            "success_signal": "Devpost submission preview is regenerated with current copy, evidence links, and remaining final blockers.",
            "safe_to_commit": [
                "docs/assets/devpost-submission-preview.json",
            ],
        },
        {
            "id": "final_submission_audit",
            "owner": "codex",
            "command": "python scripts/submission_audit.py --strict-final",
            "success_signal": "Submission audit is pre_submit_audit_ready after live proof, final video, final scan, and Devpost checklist.",
            "safe_to_commit": [
                "docs/assets/submission-audit-report.json",
            ],
            "task_update": 'python3 scripts/task.py done T041 --note "Final submission audit passed after live proof, public video, secret scan, and Devpost checklist."',
        },
        {
            "id": "devpost_receipt",
            "owner": "operator",
            "command": 'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
            "success_signal": "Devpost receipt JSON is ok=true, uses a devpost.com project URL, and contains no cookies or session data.",
            "safe_to_commit": ["docs/assets/devpost-submission-receipt.json"],
            "task_update": 'python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."',
        },
        {
            "id": "final_green_gate",
            "owner": "codex",
            "command": "python scripts/secret_scan.py && python scripts/final_submission_control.py --strict-final && python scripts/final_launch_plan.py --strict-final && python scripts/devpost_submission_preview.py --strict-final && python scripts/submission_bundle.py --strict-final",
            "success_signal": "Final scan is clear; final control, launch plan, Devpost preview, and submission bundle all report final submit readiness.",
            "safe_to_commit": [
                "docs/assets/secret-scan-report.json",
                "docs/assets/final-submission-control.json",
                "docs/assets/final-launch-plan.json",
                "docs/assets/devpost-submission-preview.json",
                "docs/assets/submission-bundle-manifest.json",
            ],
        },
    ]


def stop_rules() -> list[str]:
    return [
        "Stop immediately if a command prints or writes a value that looks like a B2 key, Genblaze provider key, browser cookie, authorization header, or signed URL.",
        "Do not mark T020 or T021 done unless the corresponding sanitized evidence JSON exists and passes the expected backend/provider checks.",
        "Do not run Devpost submission until final_submission_control.py --strict-final passes after live proof, public video, final scan, and final audit.",
        "Do not update public copy from pre-live to completed sponsor proof until both B2 and Genblaze evidence are committed after a clean secret scan.",
    ]


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    statuses = task_statuses(root)
    reports = current_reports(root)
    preconditions = build_preconditions(reports, statuses)
    ready = all(item["ok"] for item in preconditions)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "ready_for_credential_rehearsal" if ready else "needs_rehearsal_setup",
        "ok": ready,
        "safe_to_submit": False,
        "current_phase": reports["launch_plan"].get("current_phase"),
        "next_command": reports["launch_plan"].get("next_command"),
        "task_statuses": {
            task: statuses.get(task, "missing")
            for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "preconditions": preconditions,
        "required_secret_ids": EXPECTED_SECRET_MISSING_IDS,
        "steps": rehearsal_steps(),
        "stop_rules": stop_rules(),
        "reports": reports,
    }


def render_markdown(report_data: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Rehearsal Checklist",
        "",
        f"Mode: `{report_data['mode']}`",
        f"OK: `{str(report_data['ok']).lower()}`",
        f"Safe to submit: `{str(report_data['safe_to_submit']).lower()}`",
        f"Current phase: `{report_data.get('current_phase')}`",
        f"Next command: `{report_data.get('next_command')}`",
        "",
        "## Preconditions",
        "",
    ]
    for item in report_data["preconditions"]:
        marker = "OK" if item["ok"] else "TODO"
        lines.append(f"- {marker} `{item['id']}`: {item['detail']} Evidence: `{item['evidence']}`")
    lines.extend(["", "## Required Secret IDs", ""])
    lines.extend(f"- `{secret_id}`" for secret_id in report_data["required_secret_ids"])
    lines.extend(["", "## Rehearsal Steps", ""])
    for index, step in enumerate(report_data["steps"], start=1):
        lines.append(f"### {index}. {step['id']} ({step['owner']})")
        lines.extend(["```bash", step["command"], "```"])
        lines.append(f"- Success signal: {step['success_signal']}")
        if step["safe_to_commit"]:
            lines.append("- Safe to commit after a clean secret scan:")
            lines.extend(f"  - `{path}`" for path in step["safe_to_commit"])
        if step.get("task_update"):
            lines.append(f"- Task update after success: `{step['task_update']}`")
        lines.append("")
    lines.extend(["## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in report_data["stop_rules"])
    lines.append("")
    lines.append("This checklist contains secret names only, never secret values.")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report_data: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report_data), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a no-secret final submission rehearsal checklist.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-ready", action="store_true", help="Fail unless ready for credential rehearsal.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report_data = build_report(args.root)
    write_outputs(report_data, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report_data["ok"],
                "mode": report_data["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "safe_to_submit": report_data["safe_to_submit"],
                "next_command": report_data["next_command"],
            },
            indent=2,
        )
    )
    if args.strict_ready and not report_data["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
