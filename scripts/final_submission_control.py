#!/usr/bin/env python3
"""Build a single operator-facing control report for final Devpost submission."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-submission-control.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-submission-control.md"

EVENT_SNAPSHOT = {
    "name": "Backblaze Generative Media Hackathon",
    "devpost_url": "https://backblaze-generative-media.devpost.com/",
    "rules_url": "https://backblaze-generative-media.devpost.com/rules",
    "deadline_et": "2026-08-03 17:00 EDT",
    "deadline_beijing": "2026-08-04 05:00 Asia/Shanghai",
    "prize_total_usd": 10000,
    "participant_count_observed": None,
    "participant_count_checked_at": None,
    "participant_count_note": "Dynamic Devpost count; use docs/assets/devpost-event-snapshot.json before final public claims.",
}
EVENT_SNAPSHOT_SCHEMA = "proofframe.devpost_event_snapshot.v1"

OPERATOR_COMMANDS = [
    "python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local",
    "python scripts/final_env_wizard.py --output .env.final.local",
    "python scripts/live_env_handoff.py --env-file .env.final.local",
    "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
    "python scripts/devpost_packet.py --post-live --video-url <public video URL>",
    "python scripts/agent_handoff_check.py",
    "python scripts/public_space_sync.py",
    "python scripts/secret_scan.py",
    "python scripts/devpost_form_kit.py --strict-final",
    "python scripts/demo_storyboard.py --strict-final",
    "python scripts/demo_readiness.py --strict-final",
    "python scripts/recording_assets.py --verify-public --strict-final",
    "python scripts/submission_audit.py --strict-final",
    "python scripts/devpost_submission_receipt.py --project-url <public Devpost project URL> --submitted-at <ISO timestamp> --confirmation-note \"Devpost accepted/submitted the ProofFrame project.\"",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def report_summary(path: Path, expected_schema: str | None = None, root: Path = ROOT) -> dict[str, Any]:
    report = load_json(path)
    if report is None:
        return {"present": False, "path": display_path(path, root)}
    schema_ok = expected_schema is None or report.get("schema") == expected_schema
    return {
        "present": True,
        "path": display_path(path, root),
        "schema_ok": schema_ok,
        "schema": report.get("schema"),
        "mode": report.get("mode"),
        "ok": report.get("ok"),
        "score": report.get("score"),
        "max_score": report.get("max_score"),
        "final_form_ready": report.get("final_form_ready"),
        "final_video_ready": report.get("final_video_ready"),
        "final_recording_ready": report.get("final_recording_ready"),
        "mock_recording_ready": report.get("mock_recording_ready"),
        "public_mock_verified": report.get("public_mock_verified"),
        "public_video_ready": report.get("public_video_ready"),
    }


def evidence_summary(root: Path, relative_path: str, expected: dict[str, Any]) -> dict[str, Any]:
    path = root / relative_path
    evidence = load_json(path)
    if evidence is None:
        return {
            "ok": False,
            "status": "missing",
            "path": relative_path,
            "findings": [{"field": relative_path, "detail": "Evidence file is missing or invalid JSON."}],
        }
    findings: list[dict[str, str]] = []
    for key, expected_value in expected.items():
        actual = evidence.get(key)
        if actual != expected_value:
            findings.append({"field": key, "detail": f"Expected {expected_value!r}, got {actual!r}."})
    for key in ("asset_sha256", "manifest_sha256", "asset_storage_key", "manifest_key"):
        if not evidence.get(key):
            findings.append({"field": key, "detail": "Required evidence value is missing."})
    return {
        "ok": not findings,
        "status": "verified" if not findings else "incomplete",
        "path": relative_path,
        "findings": findings,
    }


def credential_summary(root: Path) -> dict[str, Any]:
    report = load_json(root / "docs" / "assets" / "live-credential-handoff.json") or {}
    missing = [item.get("id") for item in report.get("required", []) if not item.get("ok")]
    return {
        "present": bool(report),
        "mode": report.get("mode"),
        "ready": bool(report.get("ready_for_live_proof")),
        "missing_ids": [item for item in missing if item],
        "secret_policy": "Report records only variable names and presence; credential values are never printed.",
    }


def event_snapshot_summary(root: Path) -> dict[str, Any]:
    path = root / "docs" / "assets" / "devpost-event-snapshot.json"
    report = load_json(path)
    if report is None:
        return {
            "present": False,
            "path": display_path(path, root),
            "schema_ok": False,
            "schema": None,
            "validation_ok": False,
            "event": EVENT_SNAPSHOT,
        }
    validation = report.get("validation", {})
    return {
        "present": True,
        "path": display_path(path, root),
        "schema_ok": report.get("schema") == EVENT_SNAPSHOT_SCHEMA,
        "schema": report.get("schema"),
        "mode": report.get("mode"),
        "validation_ok": bool(validation.get("ok")),
        "submission_open": bool(validation.get("submission_open")),
        "checked_at": report.get("checked_at"),
        "age_days": validation.get("age_days"),
        "event": {**EVENT_SNAPSHOT, **(report.get("event") or {})},
    }


def requirement(
    requirement_id: str,
    label: str,
    ok: bool,
    detail: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "label": label,
        "ok": ok,
        "detail": detail,
        "evidence": evidence,
    }


def build_requirements(
    *,
    gate: dict[str, Any],
    b2_evidence: dict[str, Any],
    statuses: dict[str, str],
    form: dict[str, Any],
    event_snapshot: dict[str, Any],
    agent_handoff: dict[str, Any],
    public_space_sync: dict[str, Any],
    storyboard: dict[str, Any],
    demo: dict[str, Any],
    recording: dict[str, Any],
    award: dict[str, Any],
    credentials: dict[str, Any],
    secret_scan: dict[str, Any],
    submission_audit: dict[str, Any],
    devpost_receipt: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries = {
        "Devpost form": form,
        "Devpost event snapshot": event_snapshot,
        "Agent handoff": agent_handoff,
        "Public Space sync": public_space_sync,
        "Demo storyboard": storyboard,
        "Demo readiness": demo,
        "Recording assets": recording,
        "Award readiness": award,
        "Secret scan": secret_scan,
        "Submission audit": submission_audit,
        "Devpost submission receipt": devpost_receipt,
    }
    bad_schemas = [
        f"{name}: {summary.get('schema') or 'missing'}"
        for name, summary in summaries.items()
        if not summary.get("present") or not summary.get("schema_ok")
    ]
    schemas_ok = not bad_schemas
    b2_proof_ok = b2_evidence["ok"] or gate["evidence_gate"]["ok"]
    return [
        requirement(
            "devpost_registration",
            "Devpost registration complete",
            statuses.get("T040") == "done",
            f"T040 is {statuses.get('T040', 'missing')}.",
            "tasks.json",
        ),
        requirement(
            "public_mock_demo",
            "Credential-free public demo is ready",
            bool(form.get("present"))
            and bool(form.get("schema_ok"))
            and form.get("mode") in {"pre_live_form_ready", "final_form_ready"},
            f"Devpost form kit mode is {form.get('mode')}.",
            "docs/assets/devpost-form-kit.json",
        ),
        requirement(
            "official_event_snapshot",
            "Official Devpost event snapshot is fresh",
            bool(event_snapshot.get("present"))
            and bool(event_snapshot.get("schema_ok"))
            and bool(event_snapshot.get("validation_ok"))
            and bool(event_snapshot.get("submission_open")),
            (
                f"Snapshot checked at {event_snapshot.get('checked_at')}; "
                f"submission open is {event_snapshot.get('submission_open')}; "
                f"age days is {event_snapshot.get('age_days')}."
            ),
            "docs/assets/devpost-event-snapshot.json",
        ),
        requirement(
            "agent_handoff",
            "Agent handoff metadata points at the current repo",
            bool(agent_handoff.get("present"))
            and bool(agent_handoff.get("schema_ok"))
            and bool(agent_handoff.get("ok")),
            f"Agent handoff mode is {agent_handoff.get('mode')}; ok is {agent_handoff.get('ok')}.",
            "docs/assets/agent-handoff-report.json",
        ),
        requirement(
            "public_space_sync",
            "Public Space is synced to the current judge-facing demo",
            bool(public_space_sync.get("present"))
            and bool(public_space_sync.get("schema_ok"))
            and bool(public_space_sync.get("ok")),
            f"Public Space sync mode is {public_space_sync.get('mode')}; ok is {public_space_sync.get('ok')}.",
            "docs/assets/public-space-sync-report.json",
        ),
        requirement(
            "recording_assets",
            "Recording assets are ready",
            bool(recording.get("present"))
            and bool(recording.get("schema_ok"))
            and bool(recording.get("mock_recording_ready")),
            (
                f"Recording assets mode is {recording.get('mode')}; "
                f"public mock verified is {recording.get('public_mock_verified')}."
            ),
            "docs/assets/recording-assets.json",
        ),
        requirement(
            "source_report_schemas",
            "Control input reports match expected schemas",
            schemas_ok,
            "All input report schemas are current." if schemas_ok else "; ".join(bad_schemas),
            "docs/assets/*.json readiness reports",
        ),
        requirement(
            "b2_live_proof",
            "Backblaze B2 live proof captured",
            statuses.get("T020") == "done" and b2_proof_ok,
            (
                f"T020 is {statuses.get('T020', 'missing')}; "
                f"B2 evidence status is {b2_evidence['status']}; "
                f"final evidence status is {gate['evidence_gate']['status']}."
            ),
            "tasks.json, docs/assets/b2-live-proof-evidence.json, and docs/assets/final-live-proof-evidence.json",
        ),
        requirement(
            "genblaze_live_proof",
            "Genblaze live proof captured",
            statuses.get("T021") == "done" and gate["evidence_gate"]["ok"],
            f"T021 is {statuses.get('T021', 'missing')}; final evidence status is {gate['evidence_gate']['status']}.",
            "tasks.json and docs/assets/final-live-proof-evidence.json",
        ),
        requirement(
            "credential_handoff",
            "Live credential handoff is ready",
            credentials["ready"],
            f"Credential handoff mode is {credentials.get('mode')}; missing ids: {', '.join(credentials['missing_ids']) or 'none'}.",
            "docs/assets/live-credential-handoff.json",
        ),
        requirement(
            "public_video",
            "Final public demo video URL is ready",
            bool(storyboard.get("present"))
            and bool(storyboard.get("schema_ok"))
            and bool(storyboard.get("public_video_ready")),
            f"Storyboard mode is {storyboard.get('mode')}; public video ready is {storyboard.get('public_video_ready')}.",
            "docs/assets/demo-storyboard.json",
        ),
        requirement(
            "final_recording",
            "Final recording gate is ready",
            bool(demo.get("present"))
            and bool(demo.get("schema_ok"))
            and bool(demo.get("final_recording_ready")),
            f"Demo readiness mode is {demo.get('mode')}; final recording ready is {demo.get('final_recording_ready')}.",
            "docs/assets/demo-readiness-report.json",
        ),
        requirement(
            "award_readiness",
            "Award readiness score remains competitive",
            bool(award.get("present"))
            and bool(award.get("schema_ok"))
            and int(award.get("score") or 0) >= 75,
            f"Award readiness score is {award.get('score')}/{award.get('max_score')}.",
            "docs/assets/award-readiness-report.json",
        ),
        requirement(
            "final_secret_scan",
            "Final secret scan is complete",
            statuses.get("T041A") == "done"
            and bool(secret_scan.get("present"))
            and bool(secret_scan.get("schema_ok"))
            and bool(secret_scan.get("ok")),
            (
                f"T041A is {statuses.get('T041A', 'missing')}; "
                f"secret scan mode is {secret_scan.get('mode')}; "
                f"secret scan ok is {secret_scan.get('ok')}."
            ),
            "tasks.json and docs/assets/secret-scan-report.json",
        ),
        requirement(
            "final_submission_audit",
            "Final submission audit is complete",
            statuses.get("T041") == "done"
            and bool(submission_audit.get("present"))
            and bool(submission_audit.get("schema_ok"))
            and bool(submission_audit.get("ok")),
            (
                f"T041 is {statuses.get('T041', 'missing')}; "
                f"audit mode is {submission_audit.get('mode')}; "
                f"audit ok is {submission_audit.get('ok')}."
            ),
            "tasks.json and docs/assets/submission-audit-report.json",
        ),
        requirement(
            "devpost_submitted",
            "Devpost project submitted",
            statuses.get("T042") == "done"
            and bool(devpost_receipt.get("present"))
            and bool(devpost_receipt.get("schema_ok"))
            and bool(devpost_receipt.get("ok")),
            (
                f"T042 is {statuses.get('T042', 'missing')}; "
                f"receipt mode is {devpost_receipt.get('mode')}; "
                f"receipt ok is {devpost_receipt.get('ok')}."
            ),
            "tasks.json and docs/assets/devpost-submission-receipt.json",
        ),
    ]


def next_actions(requirements: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    missing = {item["id"] for item in requirements if not item["ok"]}
    if "source_report_schemas" in missing:
        actions.append("Regenerate readiness reports so every control input has the expected schema.")
    if "credential_handoff" in missing:
        actions.append("Complete .env.final.local with B2_KEY_ID, B2_APPLICATION_KEY, and Genblaze/GMI API key values.")
    if "official_event_snapshot" in missing:
        actions.append("Refresh the official Devpost event snapshot before recording or submitting.")
    if "agent_handoff" in missing:
        actions.append("Run the Agent handoff check so future Codex and Agent Bus sessions use the current repo path.")
    if "public_space_sync" in missing:
        actions.append("Run the public Space sync verifier and refresh the HF Space if the runtime/artifacts drift.")
    if "b2_live_proof" in missing:
        actions.append("Run the B2 live proof runner and save sanitized B2 evidence.")
    if "genblaze_live_proof" in missing:
        actions.append("Run the final B2 plus Genblaze proof runner and save sanitized final evidence.")
    if "public_video" in missing or "final_recording" in missing:
        actions.append("Record and upload the public demo video after live proof is captured.")
    if "recording_assets" in missing:
        actions.append("Regenerate recording assets and run the public GET-only verifier.")
    if "final_secret_scan" in missing:
        actions.append("Run and mark the final secret scan after live evidence/video assets are ready.")
    if "final_submission_audit" in missing:
        actions.append("Run final submission audit after proof, video, and secret scan pass.")
    if "devpost_submitted" in missing:
        actions.append("Submit Devpost after every preceding control item is green, then generate the public submission receipt.")
    return actions[:8]


def build_control_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    gate = build_submission_gate(root)
    statuses = task_statuses(root)
    form = report_summary(root / "docs" / "assets" / "devpost-form-kit.json", "proofframe.devpost_form_kit.v1", root)
    event_snapshot = event_snapshot_summary(root)
    agent_handoff = report_summary(
        root / "docs" / "assets" / "agent-handoff-report.json",
        "proofframe.agent_handoff.v1",
        root,
    )
    public_space_sync = report_summary(
        root / "docs" / "assets" / "public-space-sync-report.json",
        "proofframe.public_space_sync.v1",
        root,
    )
    storyboard = report_summary(root / "docs" / "assets" / "demo-storyboard.json", "proofframe.demo_storyboard.v1", root)
    demo = report_summary(root / "docs" / "assets" / "demo-readiness-report.json", "proofframe.demo_readiness.v1", root)
    recording = report_summary(root / "docs" / "assets" / "recording-assets.json", "proofframe.recording_assets.v1", root)
    award = report_summary(root / "docs" / "assets" / "award-readiness-report.json", "proofframe.award_readiness.v1", root)
    secret_scan = report_summary(
        root / "docs" / "assets" / "secret-scan-report.json",
        "proofframe.secret_scan.v1",
        root,
    )
    submission_audit = report_summary(
        root / "docs" / "assets" / "submission-audit-report.json",
        "proofframe.submission_audit.v1",
        root,
    )
    devpost_receipt = report_summary(
        root / "docs" / "assets" / "devpost-submission-receipt.json",
        "proofframe.devpost_submission_receipt.v1",
        root,
    )
    b2_evidence = evidence_summary(
        root,
        "docs/assets/b2-live-proof-evidence.json",
        {"ok": True, "storage_backend": "b2", "asset_storage_backend": "b2"},
    )
    credentials = credential_summary(root)
    requirements = build_requirements(
        gate=gate,
        b2_evidence=b2_evidence,
        statuses=statuses,
        form=form,
        event_snapshot=event_snapshot,
        agent_handoff=agent_handoff,
        public_space_sync=public_space_sync,
        storyboard=storyboard,
        demo=demo,
        recording=recording,
        award=award,
        credentials=credentials,
        secret_scan=secret_scan,
        submission_audit=submission_audit,
        devpost_receipt=devpost_receipt,
    )
    ready = all(item["ok"] for item in requirements)
    return {
        "schema": "proofframe.final_submission_control.v1",
        "created_at": utc_now(),
        "mode": "final_submit_ready" if ready else "pre_live_control",
        "safe_to_submit": ready,
        "event": event_snapshot["event"],
        "public_demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
        "submission_gate": {
            "ok": gate["ok"],
            "mode": gate["mode"],
            "summary": gate["summary"],
            "evidence_status": gate["evidence_gate"]["status"],
            "b2_evidence_status": b2_evidence["status"],
            "packet_status": gate["packet_gate"]["status"],
        },
        "task_statuses": {task: statuses.get(task, "missing") for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]},
        "report_inputs": {
            "devpost_form": form,
            "devpost_event_snapshot": event_snapshot,
            "agent_handoff": agent_handoff,
            "public_space_sync": public_space_sync,
            "demo_storyboard": storyboard,
            "demo_readiness": demo,
            "recording_assets": recording,
            "award_readiness": award,
            "secret_scan": secret_scan,
            "b2_live_evidence": b2_evidence,
            "credential_handoff": credentials,
            "submission_audit": submission_audit,
            "devpost_submission_receipt": devpost_receipt,
        },
        "requirements": requirements,
        "blocking_items": [item for item in requirements if not item["ok"]],
        "next_actions": next_actions(requirements),
        "operator_commands": OPERATOR_COMMANDS,
        "claim_boundary": "Public demo remains local/mock and pre_live_safe until final live B2 plus Genblaze proof is captured.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Submission Control",
        "",
        f"Mode: `{report['mode']}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Public demo: {report['public_demo_url']}",
        f"Repository: {report['repository_url']}",
        "",
        "## Event Snapshot",
        "",
        f"- Event: {report['event']['name']}",
        f"- Deadline: {report['event']['deadline_et']} / {report['event']['deadline_beijing']}",
        f"- Prize total: `${report['event']['prize_total_usd']}`",
        f"- Observed participants: `{report['event']['participant_count_observed']}` checked `{report['event']['participant_count_checked_at']}`",
        f"- Source: {report['event']['devpost_url']}",
        f"- Note: {report['event']['participant_count_note']}",
        "",
        "## Submission Gate",
        "",
        f"- Mode: `{report['submission_gate']['mode']}`",
        f"- Tasks: `{report['submission_gate']['summary']['done']} / {report['submission_gate']['summary']['required']}` done",
        f"- B2 evidence: `{report['submission_gate']['b2_evidence_status']}`",
        f"- Live evidence: `{report['submission_gate']['evidence_status']}`",
        f"- Devpost packet: `{report['submission_gate']['packet_status']}`",
        "",
        "## Requirements",
        "",
        "| Status | Requirement | Detail | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["requirements"]:
        status = "OK" if item["ok"] else "PENDING"
        lines.append(f"| {status} | {item['label']} | {item['detail']} | `{item['evidence']}` |")
    lines.extend(["", "## Next Actions", ""])
    if report["next_actions"]:
        lines.extend(f"- {action}" for action in report["next_actions"])
    else:
        lines.append("- Ready for final Devpost submit.")
    lines.extend(["", "## Operator Commands", ""])
    lines.append("```bash")
    lines.extend(report["operator_commands"])
    lines.append("```")
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ProofFrame final submission control report.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless final submission is ready.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_control_report(ROOT)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["safe_to_submit"] if args.strict_final else True,
                "mode": report["mode"],
                "safe_to_submit": report["safe_to_submit"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "blocking_items": [item["id"] for item in report["blocking_items"]],
            },
            indent=2,
        )
    )
    if args.strict_final and not report["safe_to_submit"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
