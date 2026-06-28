#!/usr/bin/env python3
"""Fail-closed audit for ProofFrame's final Devpost submission package."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.submission_audit.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "submission-audit-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "submission-audit-report.md"
REQUIRED_PRE_SUBMIT_TASKS = ["T020", "T021", "T040", "T041A"]
OBSERVER_TASKS = ["T041", "T042"]
EXPECTED_FINAL_CONTROL_BLOCKERS = {"final_submission_audit", "devpost_submitted"}
REQUIRED_PUBLIC_FILES = [
    "README.md",
    "docs/prd.md",
    "docs/spec.md",
    "docs/devpost_draft.md",
    "docs/assets/devpost-submission-packet.json",
    "docs/assets/devpost-submission-packet.md",
    "docs/assets/devpost-form-kit.json",
    "docs/assets/devpost-form-kit.md",
    "docs/assets/devpost-submission-checklist.json",
    "docs/assets/devpost-submission-checklist.md",
    "docs/assets/judge-brief.json",
    "docs/assets/judge-brief.md",
    "docs/assets/devpost-event-snapshot.json",
    "docs/assets/devpost-event-snapshot.md",
    "docs/assets/demo-storyboard.json",
    "docs/assets/demo-storyboard.md",
    "docs/assets/demo-readiness-report.json",
    "docs/assets/demo-readiness-report.md",
    "docs/assets/recording-assets.json",
    "docs/assets/recording-assets.md",
    "docs/assets/final-submission-control.json",
    "docs/assets/final-submission-control.md",
    "docs/assets/final-operator-brief.json",
    "docs/assets/final-operator-brief.md",
    "docs/assets/final-rehearsal-checklist.json",
    "docs/assets/final-rehearsal-checklist.md",
    "docs/evidence_package.md",
    "docs/demo_script.md",
    "docs/public_claim_freeze.md",
    "docs/verification.md",
]
REQUIRED_SCREENSHOTS = [
    "docs/assets/proofframe-local-ui-smoke.png",
    "docs/assets/proofframe-review-console-smoke.png",
    "docs/assets/proofframe-hf-public-smoke.png",
]
REQUIRED_REPORT_SCHEMAS = {
    "docs/assets/devpost-form-kit.json": "proofframe.devpost_form_kit.v1",
    "docs/assets/devpost-submission-checklist.json": "proofframe.devpost_submission_checklist.v1",
    "docs/assets/judge-brief.json": "proofframe.judge_brief.v1",
    "docs/assets/devpost-event-snapshot.json": "proofframe.devpost_event_snapshot.v1",
    "docs/assets/demo-storyboard.json": "proofframe.demo_storyboard.v1",
    "docs/assets/demo-readiness-report.json": "proofframe.demo_readiness.v1",
    "docs/assets/recording-assets.json": "proofframe.recording_assets.v1",
    "docs/assets/sponsor-fit-audit.json": "proofframe.sponsor_fit_audit.v1",
    "docs/assets/award-readiness-report.json": "proofframe.award_readiness.v1",
    "docs/assets/secret-scan-report.json": "proofframe.secret_scan.v1",
    "docs/assets/final-submission-control.json": "proofframe.final_submission_control.v1",
    "docs/assets/final-operator-brief.json": "proofframe.final_operator_brief.v1",
    "docs/assets/final-rehearsal-checklist.json": "proofframe.final_rehearsal.v1",
    "docs/assets/devpost-submission-receipt.json": "proofframe.devpost_submission_receipt.v1",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def task_map(tasks_data: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not tasks_data:
        return {}
    return {str(task.get("id", "")).upper(): task for task in tasks_data.get("tasks", [])}


def task_statuses(tasks_data: dict[str, Any] | None, task_ids: list[str]) -> dict[str, str]:
    tasks = task_map(tasks_data)
    return {task_id: str(tasks.get(task_id, {}).get("status", "missing")) for task_id in task_ids}


def finding(gate: str, status: str, detail: str, evidence: str) -> dict[str, str]:
    return {"gate": gate, "status": status, "detail": detail, "evidence": evidence}


def check_tasks(tasks_data: dict[str, Any] | None) -> list[dict[str, str]]:
    tasks = task_map(tasks_data)
    findings: list[dict[str, str]] = []
    for task_id in REQUIRED_PRE_SUBMIT_TASKS:
        task = tasks.get(task_id)
        if not task:
            findings.append(finding(task_id, "missing", "Task is absent.", "tasks.json"))
        elif task.get("status") != "done":
            findings.append(
                finding(
                    task_id,
                    str(task.get("status")),
                    f"{task.get('title', task_id)} is not done.",
                    "tasks.json",
                )
            )
    return findings


def check_files(paths: list[Path], root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            findings.append(
                finding(
                    relative_path(path, root),
                    "missing",
                    "Required public submission artifact is missing.",
                    relative_path(path, root),
                )
            )
    return findings


def check_report_schemas(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for relative, expected_schema in REQUIRED_REPORT_SCHEMAS.items():
        report = load_json(root / relative)
        if report is None:
            findings.append(finding(relative, "missing", "Report is missing or invalid JSON.", relative))
            continue
        actual = report.get("schema")
        if actual != expected_schema:
            findings.append(
                finding(
                    f"{relative}.schema",
                    "mismatch",
                    f"Expected schema {expected_schema!r}, got {actual!r}.",
                    relative,
                )
            )
    return findings


def check_final_evidence(path: Path, root: Path) -> list[dict[str, str]]:
    evidence = load_json(path)
    if evidence is None:
        return [
            finding(
                "final-live-proof-evidence",
                "missing",
                f"{relative_path(path, root)} is missing or invalid JSON.",
                relative_path(path, root),
            )
        ]
    findings: list[dict[str, str]] = []
    expected = {
        "ok": True,
        "storage_backend": "b2",
        "generation_backend": "genblaze",
        "asset_storage_backend": "b2",
        "asset_provider": "genblaze/gmicloud-image",
    }
    for key, expected_value in expected.items():
        actual = evidence.get(key)
        if actual != expected_value:
            findings.append(
                finding(
                    f"evidence.{key}",
                    "mismatch",
                    f"Expected {expected_value!r}, got {actual!r}.",
                    relative_path(path, root),
                )
            )
    for key in ("asset_sha256", "manifest_sha256", "asset_storage_key", "manifest_key"):
        if not evidence.get(key):
            findings.append(
                finding(
                    f"evidence.{key}",
                    "missing",
                    "Final evidence is missing this field.",
                    relative_path(path, root),
                )
            )
    return findings


def usable_video_url(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("https://", "http://")) and not text.lower().startswith("tbd")


def check_devpost_packet(root: Path) -> list[dict[str, str]]:
    relative = "docs/assets/devpost-submission-packet.json"
    packet = load_json(root / relative)
    if packet is None:
        return [finding("devpost_packet", "missing", "Devpost packet is missing or invalid JSON.", relative)]
    findings: list[dict[str, str]] = []
    if packet.get("schema") != "proofframe.devpost_packet.v1":
        findings.append(
            finding(
                "devpost_packet.schema",
                "mismatch",
                f"Expected 'proofframe.devpost_packet.v1', got {packet.get('schema')!r}.",
                relative,
            )
        )
    if packet.get("mode") != "post_live_verified":
        findings.append(
            finding(
                "devpost_packet.mode",
                "mismatch",
                f"Expected 'post_live_verified', got {packet.get('mode')!r}.",
                relative,
            )
        )
    if not usable_video_url(packet.get("video_url")):
        findings.append(
            finding(
                "devpost_packet.video_url",
                "missing",
                "Final packet must include a public http(s) demo video URL, not a placeholder.",
                relative,
            )
        )
    checklist = {
        str(item.get("task", "")).upper(): str(item.get("status", "missing"))
        for item in packet.get("submission_checklist", [])
    }
    for task_id in REQUIRED_PRE_SUBMIT_TASKS:
        if checklist.get(task_id) != "done":
            findings.append(
                finding(
                    f"devpost_packet.{task_id}",
                    checklist.get(task_id, "missing"),
                    "Devpost packet checklist is not synchronized with required pre-submit task status.",
                    relative,
                )
            )
    return findings


def check_event_snapshot(root: Path) -> list[dict[str, str]]:
    relative = "docs/assets/devpost-event-snapshot.json"
    report = load_json(root / relative)
    if report is None:
        return [finding("devpost_event_snapshot", "missing", "Event snapshot is missing.", relative)]
    validation = report.get("validation") or {}
    findings: list[dict[str, str]] = []
    if not validation.get("ok"):
        findings.append(finding("devpost_event_snapshot.validation", "incomplete", "Snapshot validation is not ok.", relative))
    if not validation.get("submission_open"):
        findings.append(finding("devpost_event_snapshot.submission_open", "closed", "Devpost submission is not marked open.", relative))
    return findings


def check_final_reports(root: Path) -> list[dict[str, str]]:
    checks = [
        (
            "docs/assets/devpost-form-kit.json",
            "devpost_form_kit.final_form_ready",
            "final_form_ready",
            True,
            "Final Devpost form kit is not ready.",
        ),
        (
            "docs/assets/devpost-submission-checklist.json",
            "devpost_submission_checklist.safe_to_submit",
            "safe_to_submit",
            True,
            "Final Devpost submission checklist is not ready.",
        ),
        (
            "docs/assets/demo-storyboard.json",
            "demo_storyboard.public_video_ready",
            "public_video_ready",
            True,
            "Storyboard does not have a public video URL ready.",
        ),
        (
            "docs/assets/demo-readiness-report.json",
            "demo_readiness.final_recording_ready",
            "final_recording_ready",
            True,
            "Final recording readiness gate is not ready.",
        ),
        (
            "docs/assets/recording-assets.json",
            "recording_assets.final_video_ready",
            "final_video_ready",
            True,
            "Recording assets do not verify the final public video.",
        ),
        (
            "docs/assets/live-credential-handoff.json",
            "live_credential_handoff.ready_for_live_proof",
            "ready_for_live_proof",
            True,
            "Live credential handoff is not ready.",
        ),
        (
            "docs/assets/secret-scan-report.json",
            "secret_scan.ok",
            "ok",
            True,
            "Secret scan report is not clean.",
        ),
    ]
    findings: list[dict[str, str]] = []
    for relative, gate, key, expected, detail in checks:
        report = load_json(root / relative)
        if report is None:
            findings.append(finding(gate, "missing", "Report is missing or invalid JSON.", relative))
            continue
        if report.get(key) != expected:
            findings.append(finding(gate, "incomplete", detail, relative))

    award = load_json(root / "docs/assets/award-readiness-report.json")
    if award is None:
        findings.append(finding("award_readiness", "missing", "Award readiness report is missing.", "docs/assets/award-readiness-report.json"))
    elif int(award.get("score") or 0) < 75:
        findings.append(
            finding(
                "award_readiness.score",
                "low",
                f"Award readiness score is {award.get('score')}/{award.get('max_score')}.",
                "docs/assets/award-readiness-report.json",
            )
        )
    return findings


def check_final_control(root: Path) -> list[dict[str, str]]:
    relative = "docs/assets/final-submission-control.json"
    report = load_json(root / relative)
    if report is None:
        return [finding("final_submission_control", "missing", "Final control report is missing.", relative)]
    blocker_ids = {str(item.get("id", "")) for item in report.get("blocking_items", [])}
    unexpected = sorted(blocker_ids - EXPECTED_FINAL_CONTROL_BLOCKERS)
    if unexpected:
        return [
            finding(
                "final_submission_control.blocking_items",
                "blocked",
                "Unexpected blockers remain before audit sign-off: " + ", ".join(unexpected),
                relative,
            )
        ]
    return []


def build_audit_report(
    tasks_path: Path,
    final_evidence_path: Path,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    root = root.resolve()
    tasks_data = load_json(tasks_path)
    required_files = [root / path for path in REQUIRED_PUBLIC_FILES + REQUIRED_SCREENSHOTS]
    sections = {
        "tasks": check_tasks(tasks_data),
        "files": check_files(required_files, root),
        "schemas": check_report_schemas(root),
        "final_evidence": check_final_evidence(final_evidence_path, root),
        "devpost_packet": check_devpost_packet(root),
        "event_snapshot": check_event_snapshot(root),
        "final_reports": check_final_reports(root),
        "final_control": check_final_control(root),
    }
    findings = [item for values in sections.values() for item in values]
    ok = not findings
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "pre_submit_audit_ready" if ok else "pre_submit_audit_blocked",
        "ok": ok,
        "root": ".",
        "required_pre_submit_tasks": REQUIRED_PRE_SUBMIT_TASKS,
        "observer_tasks": OBSERVER_TASKS,
        "task_statuses": task_statuses(tasks_data, REQUIRED_PRE_SUBMIT_TASKS + OBSERVER_TASKS),
        "final_evidence_path": relative_path(final_evidence_path, root),
        "section_counts": {name: len(values) for name, values in sections.items()},
        "findings": findings,
        "next_commands": [
            "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
            "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
            "python scripts/demo_storyboard.py --strict-final",
            "python scripts/demo_readiness.py --strict-final",
            "python scripts/recording_assets.py --verify-public --strict-final",
            "python scripts/secret_scan.py",
            'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"',
            "python scripts/devpost_form_kit.py --strict-final",
            "python scripts/devpost_submission_checklist.py --strict-final",
            "python scripts/final_submission_control.py --strict-final",
            "python scripts/submission_audit.py --strict-final",
            'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
        ],
        "signoff_instruction": (
            "When this report is ok, mark T041 done, submit Devpost, generate the public submission receipt, then mark T042 done and rerun final_submission_control.py --strict-final."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Submission Audit",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Final evidence: `{report['final_evidence_path']}`",
        "",
        "## Task Statuses",
        "",
    ]
    for task_id, status in report["task_statuses"].items():
        lines.append(f"- {task_id}: `{status}`")
    lines.extend(["", "## Section Findings", ""])
    for section, count in report["section_counts"].items():
        status = "OK" if count == 0 else f"{count} finding(s)"
        lines.append(f"- {section}: {status}")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for item in report["findings"]:
            lines.append(
                f"- `{item['gate']}` [{item['status']}]: {item['detail']} Evidence: `{item['evidence']}`"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Next Commands", ""])
    lines.extend(f"- `{command}`" for command in report["next_commands"])
    lines.extend(["", "## Signoff", "", report["signoff_instruction"]])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit final Devpost submission readiness.")
    parser.add_argument("--tasks", type=Path, default=ROOT / "tasks.json")
    parser.add_argument(
        "--final-evidence",
        type=Path,
        default=ROOT / "docs" / "assets" / "final-live-proof-evidence.json",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Exit nonzero unless the pre-submit audit is fully ready.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = args.tasks.resolve().parents[0]
    if args.tasks.name != "tasks.json":
        root = ROOT
    report = build_audit_report(args.tasks, args.final_evidence, root=root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "findings": len(report["findings"]),
            },
            indent=2,
        )
    )
    if args.strict_final and not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
