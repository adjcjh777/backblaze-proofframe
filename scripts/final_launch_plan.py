#!/usr/bin/env python3
"""Build a no-secret launch plan for the final ProofFrame submission pass."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-launch-plan.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-launch-plan.md"
SCHEMA = "proofframe.final_launch_plan.v1"
EXPECTED_SECRET_MISSING_IDS = {"b2_key_id", "b2_application_key", "genblaze_api_key"}


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


def report(root: Path, relative_path: str) -> dict[str, Any]:
    data = load_json(root / relative_path)
    data["_path"] = relative_path
    data["_present"] = bool(data)
    return data


def evidence_status(root: Path, relative_path: str) -> dict[str, Any]:
    data = load_json(root / relative_path)
    ok = bool(data.get("ok") or data.get("safe_to_commit") or data.get("evidence_ok"))
    return {
        "path": relative_path,
        "present": bool(data),
        "ok": ok,
        "mode": data.get("mode") or data.get("status"),
    }


def blocking_ids(final_control: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for item in final_control.get("blocking_items", []):
        if isinstance(item, dict):
            item_id = item.get("id")
        else:
            item_id = item
        if item_id:
            ids.add(str(item_id))
    return ids


def make_phase(
    *,
    phase_id: str,
    title: str,
    status: str,
    detail: str,
    command: str | None,
    expected_artifacts: list[str],
    safe_to_commit_after_scan: list[str] | None = None,
    task_updates_after_success: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": phase_id,
        "title": title,
        "status": status,
        "detail": detail,
        "command": command,
        "expected_artifacts": expected_artifacts,
        "safe_to_commit_after_scan": safe_to_commit_after_scan or [],
        "task_updates_after_success": task_updates_after_success or [],
    }


def build_phases(root: Path, reports: dict[str, dict[str, Any]], statuses: dict[str, str]) -> list[dict[str, Any]]:
    handoff = reports["credential_handoff"]
    operator = reports["operator_brief"]
    final_control = reports["final_control"]
    recording = reports["recording_assets"]
    submission_audit = reports["submission_audit"]
    receipt = reports["devpost_receipt"]
    b2_evidence = reports["b2_evidence"]
    final_evidence = reports["final_evidence"]
    b2_checklist = reports["b2_key_scope_checklist"]
    b2_confirmation = b2_checklist.get("pre_key_creation_confirmation") or {}
    b2_confirmation_phrase = b2_confirmation.get("required_phrase")
    missing_ids = {str(item) for item in handoff.get("missing_ids", [])}
    blocks = blocking_ids(final_control)

    credential_done = bool(handoff.get("ok"))
    credential_ready = bool(
        operator.get("ready_for_secret_entry")
        and missing_ids == EXPECTED_SECRET_MISSING_IDS
        and not credential_done
    )
    if credential_done:
        credential_status = "done"
        credential_detail = "Live credential handoff is complete; no missing ids remain."
    elif credential_ready:
        credential_status = "ready"
        credential_detail = "Only expected secret ids are missing; operator can enter them locally."
    else:
        credential_status = "blocked"
        credential_detail = "Credential handoff is missing unexpected setup values; regenerate .env.final.local prefill."

    b2_done = statuses.get("T020") == "done" and b2_evidence.get("ok")
    b2_status = "done" if b2_done else ("ready" if credential_done else "blocked")
    b2_detail = (
        "Sanitized B2 evidence is present and T020 is done."
        if b2_done
        else "Run after live credential handoff is complete."
        if credential_done
        else "Waiting on credential entry."
    )

    genblaze_done = statuses.get("T021") == "done" and final_evidence.get("ok")
    genblaze_status = "done" if genblaze_done else ("ready" if b2_done else "blocked")
    genblaze_detail = (
        "Sanitized final B2 plus Genblaze evidence is present and T021 is done."
        if genblaze_done
        else "Run after the B2-only proof passes so final evidence has storage and generation proof."
        if b2_done
        else "Waiting on the B2-only proof."
    )

    video_done = bool(recording.get("final_video_ready"))
    video_status = "done" if video_done else ("ready" if genblaze_done else "blocked")
    video_detail = (
        "Final public video is verified by recording assets."
        if video_done
        else "Record and upload the public demo after live proof evidence exists."
        if genblaze_done
        else "Waiting on live B2 plus Genblaze evidence."
    )

    safety_done = statuses.get("T041A") == "done" and statuses.get("T041") == "done" and bool(
        submission_audit.get("ok")
    )
    safety_status = "done" if safety_done else ("ready" if video_done else "blocked")
    safety_detail = (
        "Final secret scan and submission audit are signed off."
        if safety_done
        else "Run final scan and strict submission audit after the public video is ready."
        if video_done
        else "Waiting on final public video."
    )

    devpost_done = statuses.get("T042") == "done" and bool(receipt.get("ok"))
    devpost_ready = safety_done and blocks <= {"devpost_submitted"}
    devpost_status = "done" if devpost_done else ("ready" if devpost_ready else "blocked")
    devpost_detail = (
        "Devpost receipt is present and T042 is done."
        if devpost_done
        else "Submit Devpost and generate the public receipt."
        if devpost_ready
        else "Waiting on all pre-submit gates."
    )

    return [
        make_phase(
            phase_id="credential_entry",
            title="Enter final credentials locally",
            status=credential_status,
            detail=credential_detail,
            command="python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
            expected_artifacts=[
                "docs/assets/b2-key-scope-checklist.md reviewed before key creation",
                (
                    f"B2 pre-key confirmation phrase recorded without secrets: {b2_confirmation_phrase}"
                    if b2_confirmation_phrase
                    else "B2 pre-key confirmation phrase recorded without secrets"
                ),
                ".env.final.local (git-ignored, never committed)",
            ],
        ),
        make_phase(
            phase_id="b2_live_proof",
            title="Capture Backblaze B2 live proof",
            status=b2_status,
            detail=b2_detail,
            command="python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
            expected_artifacts=["docs/assets/b2-live-proof-evidence.json"],
            safe_to_commit_after_scan=["docs/assets/b2-live-proof-evidence.json"],
            task_updates_after_success=[
                'python3 scripts/task.py done T020 --note "B2 live proof evidence captured in docs/assets/b2-live-proof-evidence.json."'
            ],
        ),
        make_phase(
            phase_id="genblaze_live_proof",
            title="Capture final B2 plus Genblaze proof",
            status=genblaze_status,
            detail=genblaze_detail,
            command=(
                "python scripts/run_final_live_proof.py --env-file .env.final.local "
                "--genblaze-provider local --genblaze-image-model local-svg-v1 "
                "--evidence-out docs/assets/final-live-proof-evidence.json"
            ),
            expected_artifacts=["docs/assets/final-live-proof-evidence.json"],
            safe_to_commit_after_scan=["docs/assets/final-live-proof-evidence.json"],
            task_updates_after_success=[
                'python3 scripts/task.py done T021 --note "Final B2 plus Genblaze live proof evidence captured in docs/assets/final-live-proof-evidence.json."'
            ],
        ),
        make_phase(
            phase_id="public_video",
            title="Record and verify public demo video",
            status=video_status,
            detail=video_detail,
            command='python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"',
            expected_artifacts=[
                "public demo video URL",
                "docs/assets/devpost-submission-packet.json",
                "docs/assets/devpost-form-kit.json",
                "docs/assets/demo-storyboard.json",
                "docs/assets/recording-assets.json",
            ],
            safe_to_commit_after_scan=[
                "docs/assets/devpost-submission-packet.json",
                "docs/assets/devpost-form-kit.json",
                "docs/assets/demo-storyboard.json",
                "docs/assets/recording-assets.json",
            ],
        ),
        make_phase(
            phase_id="final_safety_audit",
            title="Run final secret scan and submission audit",
            status=safety_status,
            detail=safety_detail,
            command="python scripts/secret_scan.py && python scripts/submission_audit.py --strict-final",
            expected_artifacts=[
                "docs/assets/secret-scan-report.json",
                "docs/assets/submission-audit-report.json",
            ],
            safe_to_commit_after_scan=[
                "docs/assets/secret-scan-report.json",
                "docs/assets/submission-audit-report.json",
            ],
            task_updates_after_success=[
                'python3 scripts/task.py done T041A --note "Final secret scan clear after live proof and public video."',
                'python3 scripts/task.py done T041 --note "Final submission audit passed after live proof and public video."',
            ],
        ),
        make_phase(
            phase_id="devpost_submit",
            title="Submit Devpost and capture receipt",
            status=devpost_status,
            detail=devpost_detail,
            command='python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
            expected_artifacts=["docs/assets/devpost-submission-receipt.json"],
            safe_to_commit_after_scan=["docs/assets/devpost-submission-receipt.json"],
            task_updates_after_success=[
                'python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."'
            ],
        ),
    ]


def first_open_phase(phases: list[dict[str, Any]]) -> dict[str, Any] | None:
    for phase in phases:
        if phase["status"] != "done":
            return phase
    return None


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    statuses = task_statuses(root)
    reports = {
        "credential_handoff": report(root, "docs/assets/live-credential-handoff.json"),
        "operator_brief": report(root, "docs/assets/final-operator-brief.json"),
        "b2_key_scope_checklist": report(root, "docs/assets/b2-key-scope-checklist.json"),
        "final_control": report(root, "docs/assets/final-submission-control.json"),
        "recording_assets": report(root, "docs/assets/recording-assets.json"),
        "submission_audit": report(root, "docs/assets/submission-audit-report.json"),
        "devpost_receipt": report(root, "docs/assets/devpost-submission-receipt.json"),
        "b2_evidence": evidence_status(root, "docs/assets/b2-live-proof-evidence.json"),
        "final_evidence": evidence_status(root, "docs/assets/final-live-proof-evidence.json"),
    }
    phases = build_phases(root, reports, statuses)
    open_phase = first_open_phase(phases)
    done_count = sum(1 for phase in phases if phase["status"] == "done")
    ready_count = sum(1 for phase in phases if phase["status"] == "ready")
    blocked_count = sum(1 for phase in phases if phase["status"] == "blocked")
    ok = open_phase is None
    if ok:
        mode = "submitted"
    elif open_phase["status"] == "ready":
        mode = f"ready_for_{open_phase['id']}"
    else:
        mode = f"blocked_at_{open_phase['id']}"
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": mode,
        "repo_root": str(root),
        "current_phase": open_phase["id"] if open_phase else "complete",
        "summary": {
            "total": len(phases),
            "done": done_count,
            "ready": ready_count,
            "blocked": blocked_count,
        },
        "task_statuses": {
            task: statuses.get(task, "missing")
            for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "phases": phases,
        "next_command": open_phase.get("command") if open_phase else None,
        "next_detail": open_phase.get("detail") if open_phase else "Final launch is complete.",
        "safety_policy": {
            "no_secret_values_in_report": True,
            "never_commit": [
                ".env.final.local",
                "Backblaze key IDs or application keys",
                "Genblaze provider API keys",
                "Devpost cookies or browser session files",
                "raw signed URLs or provider temporary URLs",
            ],
            "source_env_files": False,
        },
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Launch Plan",
        "",
        f"Mode: `{plan['mode']}`",
        f"Current phase: `{plan['current_phase']}`",
        f"Complete: `{str(plan['ok']).lower()}`",
        (
            f"Progress: `{plan['summary']['done']} / {plan['summary']['total']}` done; "
            f"`{plan['summary']['ready']}` ready, `{plan['summary']['blocked']}` blocked."
        ),
        "",
        "## Next Command",
        "",
    ]
    if plan.get("next_command"):
        lines.extend(["```bash", plan["next_command"], "```"])
        lines.append(plan["next_detail"])
    else:
        lines.append("- Final launch is complete.")
    lines.extend(["", "## Phases", ""])
    for phase in plan["phases"]:
        lines.append(f"### {phase['id']} - {phase['title']}")
        lines.append(f"- Status: `{phase['status']}`")
        lines.append(f"- Detail: {phase['detail']}")
        if phase.get("command"):
            lines.extend(["- Command:", "```bash", phase["command"], "```"])
        lines.append("- Expected artifacts:")
        lines.extend(f"  - `{artifact}`" for artifact in phase["expected_artifacts"])
        if phase["safe_to_commit_after_scan"]:
            lines.append("- Safe to commit after scan:")
            lines.extend(f"  - `{artifact}`" for artifact in phase["safe_to_commit_after_scan"])
        if phase["task_updates_after_success"]:
            lines.append("- Task ledger updates after success:")
            lines.extend(f"  - `{command}`" for command in phase["task_updates_after_success"])
        lines.append("")
    lines.extend(["## Safety Policy", ""])
    lines.append("- This report contains command strings and artifact paths only; no secret values.")
    lines.append("- Do not commit:")
    lines.extend(f"  - {item}" for item in plan["safety_policy"]["never_commit"])
    lines.append("- Do not source `.env.final.local`; use the parser-based `--env-file` commands.")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(plan: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(plan), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a no-secret final launch plan.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless every launch phase is done.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan = build_report(args.root)
    write_outputs(plan, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": plan["ok"],
                "mode": plan["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "current_phase": plan["current_phase"],
                "next_command": plan["next_command"],
            },
            indent=2,
        )
    )
    if args.strict_final and not plan["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
