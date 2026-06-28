#!/usr/bin/env python3
"""Build a no-secret operator checklist for the final Devpost web submission."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.devpost_submission_checklist.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-submission-checklist.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-submission-checklist.md"

FINAL_PREREQUISITE_TASKS = ["T020", "T021", "T040", "T041A"]
SUBMISSION_TASKS = ["T041", "T042"]
FIELD_ORDER = [
    "project_name",
    "tagline",
    "one_liner",
    "short_description",
    "repository_url",
    "demo_url",
    "video_url",
    "built_with",
    "tags",
    "inspiration",
    "what_it_does",
    "how_we_built_it",
    "backblaze_b2_usage",
    "genblaze_usage",
    "challenges",
    "accomplishments",
    "what_we_learned",
    "whats_next",
    "judging_note",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json")
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def form_field_map(form_kit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(field.get("id")): field
        for field in form_kit.get("fields", [])
        if field.get("id")
    }


def ordered_fields(form_kit: dict[str, Any]) -> list[dict[str, Any]]:
    fields_by_id = form_field_map(form_kit)
    ordered = [fields_by_id[field_id] for field_id in FIELD_ORDER if field_id in fields_by_id]
    known = {field.get("id") for field in ordered}
    extras = [
        field
        for field in form_kit.get("fields", [])
        if field.get("id") not in known
    ]
    return ordered + extras


def field_item(field: dict[str, Any]) -> dict[str, Any]:
    value = str(field.get("value", ""))
    return {
        "id": field.get("id"),
        "label": field.get("label"),
        "source": field.get("source"),
        "chars": field.get("chars"),
        "max_chars": field.get("max_chars"),
        "ok_for_mock": bool(field.get("ok_for_mock")),
        "ok_for_final": bool(field.get("ok_for_final")),
        "copy_value": value,
        "copy_instruction": f"Paste into Devpost field: {field.get('label')}",
        "verification": [
            "Confirm the pasted text matches this checklist exactly.",
            "Confirm Devpost does not show a length or required-field error.",
        ],
    }


def build_field_items(form_kit: dict[str, Any]) -> list[dict[str, Any]]:
    return [field_item(field) for field in ordered_fields(form_kit)]


def all_required_tasks_done(statuses: dict[str, str]) -> bool:
    return all(statuses.get(task_id) == "done" for task_id in FINAL_PREREQUISITE_TASKS)


def build_preflight(
    *,
    form_kit: dict[str, Any],
    packet: dict[str, Any],
    final_control: dict[str, Any],
    submission_audit: dict[str, Any],
    receipt: dict[str, Any],
    statuses: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "id": "final_form_ready",
            "ok": form_kit.get("final_form_ready") is True,
            "detail": f"Devpost form kit mode is {form_kit.get('mode')}.",
            "evidence": "docs/assets/devpost-form-kit.json",
        },
        {
            "id": "packet_post_live_verified",
            "ok": packet.get("mode") == "post_live_verified",
            "detail": f"Devpost packet mode is {packet.get('mode')}.",
            "evidence": "docs/assets/devpost-submission-packet.json",
        },
        {
            "id": "prerequisite_tasks_done",
            "ok": all_required_tasks_done(statuses),
            "detail": ", ".join(f"{task}={statuses.get(task, 'missing')}" for task in FINAL_PREREQUISITE_TASKS),
            "evidence": "tasks.json",
        },
        {
            "id": "submission_audit_report_present",
            "ok": submission_audit.get("schema") == "proofframe.submission_audit.v1",
            "detail": f"Submission audit mode is {submission_audit.get('mode')}.",
            "evidence": "docs/assets/submission-audit-report.json",
        },
        {
            "id": "final_control_report_present",
            "ok": final_control.get("schema") == "proofframe.final_submission_control.v1",
            "detail": f"Final control mode is {final_control.get('mode')}; safe_to_submit={final_control.get('safe_to_submit')}.",
            "evidence": "docs/assets/final-submission-control.json",
        },
        {
            "id": "receipt_not_already_done",
            "ok": receipt.get("ok") is not True and statuses.get("T042") != "done",
            "detail": f"T042={statuses.get('T042', 'missing')}; receipt mode={receipt.get('mode')}.",
            "evidence": "docs/assets/devpost-submission-receipt.json",
        },
    ]


def build_stop_rules() -> list[str]:
    return [
        "Do not paste Backblaze keys, Genblaze/GMI keys, Devpost cookies, authorization headers, or signed URLs into Devpost.",
        "Do not press Submit unless every preflight item is OK and final_submission_control.py --strict-final passes.",
        "If Devpost changes field labels or requirements, stop and update this checklist before submitting.",
        "After Devpost accepts the project, record only the public project URL and submitted timestamp; never capture cookies or private browser state.",
    ]


def build_post_submit_commands() -> list[str]:
    return [
        'python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
        'python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."',
        "PYTHONPATH=src python scripts/final_submission_control.py --strict-final",
        "PYTHONPATH=src python scripts/submission_bundle.py",
    ]


def build_checklist(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    form_kit = load_json(root / "docs" / "assets" / "devpost-form-kit.json")
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json")
    final_control = load_json(root / "docs" / "assets" / "final-submission-control.json")
    submission_audit = load_json(root / "docs" / "assets" / "submission-audit-report.json")
    receipt = load_json(root / "docs" / "assets" / "devpost-submission-receipt.json")
    statuses = task_statuses(root)
    fields = build_field_items(form_kit)
    field_gate_ok = bool(fields) and all(field["ok_for_final"] for field in fields)
    preflight = build_preflight(
        form_kit=form_kit,
        packet=packet,
        final_control=final_control,
        submission_audit=submission_audit,
        receipt=receipt,
        statuses=statuses,
    )
    ready = field_gate_ok and all(item["ok"] for item in preflight)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "ready_to_submit_devpost" if ready else "pre_submit_blocked",
        "ok": ready,
        "safe_to_submit": ready,
        "task_statuses": {
            task_id: statuses.get(task_id, "missing")
            for task_id in FINAL_PREREQUISITE_TASKS + SUBMISSION_TASKS
        },
        "preflight": preflight,
        "field_gate": {
            "ok": field_gate_ok,
            "field_count": len(fields),
            "final_pending_fields": [
                field["id"] for field in fields if not field["ok_for_final"]
            ],
        },
        "fields": fields,
        "stop_rules": build_stop_rules(),
        "post_submit_commands": build_post_submit_commands(),
    }


def render_markdown(checklist: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Devpost Submission Checklist",
        "",
        f"Mode: `{checklist['mode']}`",
        f"OK: `{str(checklist['ok']).lower()}`",
        f"Safe to submit: `{str(checklist['safe_to_submit']).lower()}`",
        "",
        "## Preflight",
        "",
    ]
    for item in checklist["preflight"]:
        marker = "OK" if item["ok"] else "BLOCKED"
        lines.append(f"- {marker} `{item['id']}`: {item['detail']} Evidence: `{item['evidence']}`")

    lines.extend(["", "## Copy Order", ""])
    for index, field in enumerate(checklist["fields"], start=1):
        final_status = "FINAL OK" if field["ok_for_final"] else "FINAL PENDING"
        lines.extend(
            [
                f"### {index}. {field['label']}",
                "",
                f"- Field id: `{field['id']}`",
                f"- Source: `{field['source']}`",
                f"- Status: `{final_status}`",
                f"- Length: `{field['chars']} / {field['max_chars']}`",
                "",
                "```text",
                field["copy_value"],
                "```",
                "",
            ]
        )

    lines.extend(["## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in checklist["stop_rules"])
    lines.extend(["", "## Post-submit Commands", "", "```bash"])
    lines.extend(checklist["post_submit_commands"])
    lines.extend(["```", ""])
    lines.append("This checklist contains Devpost copy only, never credentials or browser session data.")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(checklist: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(checklist, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(checklist), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a final Devpost web submission checklist.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless Devpost is ready to submit.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    checklist = build_checklist(args.root)
    write_outputs(checklist, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": checklist["ok"],
                "mode": checklist["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "safe_to_submit": checklist["safe_to_submit"],
                "pending_fields": checklist["field_gate"]["final_pending_fields"],
            },
            indent=2,
        )
    )
    if args.strict_final and not checklist["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
