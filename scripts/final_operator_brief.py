#!/usr/bin/env python3
"""Build a no-secret operator brief for the final ProofFrame submission pass."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-operator-brief.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-operator-brief.md"
SCHEMA = "proofframe.final_operator_brief.v1"
EXPECTED_SECRET_MISSING_IDS = {"b2_key_id", "b2_application_key", "genblaze_api_key"}


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def gitignore_mentions(root: Path, pattern: str) -> bool:
    return pattern in read_text(root / ".gitignore").splitlines()


def b2_setup_summary(root: Path) -> dict[str, Any]:
    setup = load_json(root / "docs" / "assets" / "b2-live-setup.json") or {}
    return {
        "present": bool(setup),
        "status": setup.get("status"),
        "bucket_name": setup.get("bucket_name") or setup.get("bucket"),
        "endpoint": setup.get("endpoint"),
        "bucket_type": setup.get("bucket_type"),
        "prepared_application_key_name": setup.get("prepared_application_key_name")
        or setup.get("application_key_name"),
        "application_key_status": setup.get("application_key_status"),
    }


def handoff_summary(root: Path) -> dict[str, Any]:
    handoff = load_json(root / "docs" / "assets" / "live-credential-handoff.json") or {}
    missing = [str(item) for item in handoff.get("missing_ids", [])]
    required = {
        item.get("id"): bool(item.get("ok"))
        for item in handoff.get("required", [])
        if item.get("id")
    }
    return {
        "present": bool(handoff),
        "mode": handoff.get("mode"),
        "ready": bool(handoff.get("ok")),
        "source": handoff.get("source"),
        "missing_ids": missing,
        "missing_only_expected_secrets": set(missing) == EXPECTED_SECRET_MISSING_IDS,
        "required_presence": required,
    }


def report_status(root: Path, relative_path: str, expected_schema: str) -> dict[str, Any]:
    report = load_json(root / relative_path) or {}
    return {
        "present": bool(report),
        "path": relative_path,
        "schema_ok": report.get("schema") == expected_schema,
        "mode": report.get("mode"),
        "ok": report.get("ok"),
        "score": report.get("score"),
        "max_score": report.get("max_score"),
        "safe_to_submit": report.get("safe_to_submit"),
        "validation_ok": (report.get("validation") or {}).get("ok"),
        "mock_recording_ready": report.get("mock_recording_ready"),
        "public_mock_verified": report.get("public_mock_verified"),
    }


def task_summary(statuses: dict[str, str]) -> dict[str, str]:
    return {task: statuses.get(task, "missing") for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]}


def build_user_actions(b2_setup: dict[str, Any], handoff: dict[str, Any]) -> list[str]:
    key_name = b2_setup.get("prepared_application_key_name") or "proofframe-demo-live-proof"
    bucket = b2_setup.get("bucket_name") or "the dedicated ProofFrame bucket"
    missing = set(handoff.get("missing_ids", []))
    actions: list[str] = []
    if {"b2_key_id", "b2_application_key"} & missing:
        actions.append(
            "Create a least-privilege Backblaze B2 application key named "
            f"`{key_name}` scoped to `{bucket}`, then enter only the key id and application key "
            "into `.env.final.local` via `python scripts/final_env_wizard.py --output .env.final.local --force`."
        )
    if "genblaze_api_key" in missing:
        actions.append(
            "Enter a Genblaze/GMI API key into `.env.final.local` with the same wizard; do not paste it into chat, docs, screenshots, or git."
        )
    actions.extend(
        [
            "Run `python scripts/live_env_handoff.py --env-file .env.final.local --strict` and confirm it reports no missing ids.",
            "Run the B2-only proof first, then the final B2 plus Genblaze proof, and commit only sanitized evidence JSON.",
            "Record and upload the public demo video only after live proof evidence exists.",
            "Run final secret scan and final submission audit, submit Devpost, then generate the public Devpost submission receipt.",
        ]
    )
    return actions


def build_codex_actions() -> list[str]:
    return [
        "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
        "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
        'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"',
        "python scripts/devpost_form_kit.py --strict-final",
        "python scripts/demo_storyboard.py --strict-final",
        "python scripts/demo_readiness.py --strict-final",
        "python scripts/recording_assets.py --verify-public --strict-final",
        "python scripts/secret_scan.py",
        "python scripts/submission_audit.py --strict-final",
        'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
        "python scripts/final_submission_control.py --strict-final",
    ]


def build_safety_policy(root: Path) -> dict[str, Any]:
    return {
        "env_final_local_ignored": gitignore_mentions(root, ".env.final.local"),
        "never_commit": [
            ".env.final.local",
            "Backblaze key IDs or application keys",
            "Genblaze/GMI provider keys",
            "Devpost cookies or browser session files",
            "raw signed URLs or provider temporary URLs",
            "screen recordings that visibly expose secrets",
        ],
        "safe_to_commit_after_scan": [
            "docs/assets/b2-live-proof-evidence.json",
            "docs/assets/final-live-proof-evidence.json",
            "docs/assets/devpost-submission-packet.json",
            "docs/assets/devpost-form-kit.json",
        ],
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    statuses = task_statuses(root)
    b2_setup = b2_setup_summary(root)
    handoff = handoff_summary(root)
    reports = {
        "event_snapshot": report_status(
            root,
            "docs/assets/devpost-event-snapshot.json",
            "proofframe.devpost_event_snapshot.v1",
        ),
        "recording_assets": report_status(
            root,
            "docs/assets/recording-assets.json",
            "proofframe.recording_assets.v1",
        ),
        "award_readiness": report_status(
            root,
            "docs/assets/award-readiness-report.json",
            "proofframe.award_readiness.v1",
        ),
        "secret_scan": report_status(
            root,
            "docs/assets/secret-scan-report.json",
            "proofframe.secret_scan.v1",
        ),
        "final_control": report_status(
            root,
            "docs/assets/final-submission-control.json",
            "proofframe.final_submission_control.v1",
        ),
        "submission_audit": report_status(
            root,
            "docs/assets/submission-audit-report.json",
            "proofframe.submission_audit.v1",
        ),
        "devpost_submission_receipt": report_status(
            root,
            "docs/assets/devpost-submission-receipt.json",
            "proofframe.devpost_submission_receipt.v1",
        ),
    }
    ready_for_secret_entry = bool(
        b2_setup.get("bucket_name")
        and b2_setup.get("bucket_type") == "private"
        and handoff.get("present")
        and handoff.get("missing_only_expected_secrets")
        and reports["event_snapshot"].get("validation_ok")
        and reports["recording_assets"].get("mock_recording_ready")
        and reports["award_readiness"].get("score", 0) >= 90
    )
    return {
        "schema": SCHEMA,
        "mode": "credential_entry_ready" if ready_for_secret_entry else "needs_operator_setup",
        "ready_for_secret_entry": ready_for_secret_entry,
        "safe_to_submit": bool(reports["final_control"].get("safe_to_submit")),
        "task_statuses": task_summary(statuses),
        "b2_setup": b2_setup,
        "credential_handoff": handoff,
        "reports": reports,
        "user_actions": build_user_actions(b2_setup, handoff),
        "codex_actions_after_credentials": build_codex_actions(),
        "safety_policy": build_safety_policy(root),
        "claim_boundary": "Do not claim completed B2 or Genblaze proof until sanitized live evidence is generated and final gates pass.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Operator Brief",
        "",
        f"Mode: `{report['mode']}`",
        f"Ready for secret entry: `{str(report['ready_for_secret_entry']).lower()}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        "",
        "## Current Blockers",
        "",
    ]
    for task, status in report["task_statuses"].items():
        lines.append(f"- {task}: `{status}`")
    lines.extend(["", "## Credential Handoff", ""])
    handoff = report["credential_handoff"]
    lines.extend(
        [
            f"- Source: `{handoff.get('source')}`",
            f"- Mode: `{handoff.get('mode')}`",
            f"- Missing ids: `{', '.join(handoff.get('missing_ids', [])) or 'none'}`",
            f"- Missing only expected secrets: `{str(handoff.get('missing_only_expected_secrets')).lower()}`",
        ]
    )
    lines.extend(["", "## B2 Setup", ""])
    b2_setup = report["b2_setup"]
    for key in ["status", "bucket_name", "endpoint", "bucket_type", "prepared_application_key_name", "application_key_status"]:
        lines.append(f"- {key}: `{b2_setup.get(key)}`")
    lines.extend(["", "## User Actions", ""])
    lines.extend(f"- {action}" for action in report["user_actions"])
    lines.extend(["", "## Codex Actions After Credentials", "", "```bash"])
    lines.extend(report["codex_actions_after_credentials"])
    lines.append("```")
    lines.extend(["", "## Safety Policy", ""])
    lines.append(f"- `.env.final.local` ignored: `{str(report['safety_policy']['env_final_local_ignored']).lower()}`")
    lines.append("- Never commit:")
    lines.extend(f"  - {item}" for item in report["safety_policy"]["never_commit"])
    lines.append("- Safe to commit only after scan:")
    lines.extend(f"  - `{item}`" for item in report["safety_policy"]["safe_to_commit_after_scan"])
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a no-secret final operator brief.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-ready", action="store_true", help="Fail unless ready for credential entry.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ready_for_secret_entry"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "missing_ids": report["credential_handoff"]["missing_ids"],
                "safe_to_submit": report["safe_to_submit"],
            },
            indent=2,
        )
    )
    if args.strict_ready and not report["ready_for_secret_entry"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
