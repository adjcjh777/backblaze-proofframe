#!/usr/bin/env python3
"""Build a one-page, claim-safe Devpost preview for judges and final review."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-submission-preview.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-submission-preview.md"
SCHEMA = "proofframe.devpost_submission_preview.v1"

SOURCE_SPECS = {
    "packet": ("docs/assets/devpost-submission-packet.json", "proofframe.devpost_packet.v1"),
    "form_kit": ("docs/assets/devpost-form-kit.json", "proofframe.devpost_form_kit.v1"),
    "judge_brief": ("docs/assets/judge-brief.json", "proofframe.judge_brief.v1"),
    "judge_crosswalk": ("docs/assets/judge-crosswalk.json", "proofframe.judge_crosswalk.v1"),
    "public_screenshot": (
        "docs/assets/public-demo-screenshot-report.json",
        "proofframe.public_demo_screenshot.v1",
    ),
    "public_space_sync": (
        "docs/assets/public-space-sync-report.json",
        "proofframe.public_space_sync.v1",
    ),
    "final_control": (
        "docs/assets/final-submission-control.json",
        "proofframe.final_submission_control.v1",
    ),
    "submit_checklist": (
        "docs/assets/devpost-submission-checklist.json",
        "proofframe.devpost_submission_checklist.v1",
    ),
    "submission_audit": (
        "docs/assets/submission-audit-report.json",
        "proofframe.submission_audit.v1",
    ),
    "secret_scan": ("docs/assets/secret-scan-report.json", "proofframe.secret_scan.v1"),
}

FINAL_BLOCKER_LABELS = {
    "b2_live_proof": "live Backblaze B2 proof",
    "genblaze_live_proof": "live Genblaze proof",
    "public_video": "final public video",
    "public_video_check": "public video URL check",
    "final_secret_scan": "final secret scan task completion",
    "final_submission_audit": "strict final submission audit",
    "devpost_submitted": "Devpost submission receipt",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def dict_field(value: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not value:
        return {}
    field = value.get(key)
    return field if isinstance(field, dict) else {}


def list_field(value: dict[str, Any] | None, key: str) -> list[Any]:
    if not value:
        return []
    field = value.get(key)
    return field if isinstance(field, list) else []


def source_record(root: Path, source_id: str, relative_path: str, expected_schema: str) -> dict[str, Any]:
    data = load_json(root / relative_path)
    return {
        "id": source_id,
        "path": relative_path,
        "present": data is not None,
        "schema": data.get("schema") if data else None,
        "schema_ok": bool(data and data.get("schema") == expected_schema),
        "mode": data.get("mode") if data else None,
        "ok": data.get("ok") if data else None,
    }


def source_status(root: Path) -> dict[str, dict[str, Any]]:
    return {
        source_id: source_record(root, source_id, relative_path, expected_schema)
        for source_id, (relative_path, expected_schema) in SOURCE_SPECS.items()
    }


def text_list(items: list[Any]) -> list[str]:
    return [str(item).strip() for item in items if str(item).strip()]


def screenshot_ready(report: dict[str, Any] | None) -> bool:
    markers = dict_field(report, "markers")
    screenshot = dict_field(report, "screenshot")
    return bool(
        report
        and report.get("schema") == "proofframe.public_demo_screenshot.v1"
        and report.get("ok") is True
        and report.get("safe_to_commit") is True
        and markers.get("visible_ok") is True
        and markers.get("html_ok") is True
        and screenshot.get("path") == "docs/assets/proofframe-hf-public-smoke.png"
        and (screenshot.get("bytes") or 0) >= 100_000
        and (screenshot.get("width") or 0) >= 1200
        and (screenshot.get("height") or 0) >= 900
    )


def public_space_ready(report: dict[str, Any] | None) -> bool:
    observed = dict_field(report, "observed")
    screenshot = dict_field(observed, "public_demo_screenshot")
    return bool(
        report
        and report.get("schema") == "proofframe.public_space_sync.v1"
        and report.get("ok") is True
        and report.get("mode") == "public_space_synced"
        and screenshot.get("ok") is True
        and screenshot.get("visible_ok") is True
        and screenshot.get("html_ok") is True
    )


def final_blockers(control: dict[str, Any] | None) -> list[dict[str, Any]]:
    blockers = []
    for item in list_field(control, "blocking_items"):
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("id") or "")
        blockers.append(
            {
                "id": blocker_id,
                "label": FINAL_BLOCKER_LABELS.get(blocker_id, str(item.get("label") or blocker_id)),
                "detail": str(item.get("detail") or ""),
                "evidence": str(item.get("evidence") or ""),
            }
        )
    return blockers


def field_rollup(form_kit: dict[str, Any] | None) -> dict[str, Any]:
    fields = [field for field in list_field(form_kit, "fields") if isinstance(field, dict)]
    final_pending = [
        {"id": field.get("id"), "label": field.get("label")}
        for field in fields
        if field.get("ok_for_final") is not True
    ]
    return {
        "field_count": len(fields),
        "mock_ready": bool(form_kit and form_kit.get("mock_form_ready") is True),
        "final_ready": bool(form_kit and form_kit.get("final_form_ready") is True),
        "public_video_ready": bool(form_kit and form_kit.get("public_video_ready") is True),
        "final_pending_fields": final_pending,
    }


def criteria_rollup(crosswalk: dict[str, Any] | None) -> dict[str, Any]:
    rows = [row for row in list_field(crosswalk, "rows") if isinstance(row, dict)]
    official_criteria = [
        str(item.get("name"))
        for item in list_field(crosswalk, "official_criteria")
        if isinstance(item, dict) and item.get("present") is True
    ]
    return {
        "mode": crosswalk.get("mode") if crosswalk else None,
        "safe_to_submit": crosswalk.get("safe_to_submit") if crosswalk else None,
        "official_criteria": official_criteria,
        "row_count": len(rows),
    }


def build_preview(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(root / "docs/assets/devpost-submission-packet.json")
    form_kit = load_json(root / "docs/assets/devpost-form-kit.json")
    judge_brief = load_json(root / "docs/assets/judge-brief.json")
    crosswalk = load_json(root / "docs/assets/judge-crosswalk.json")
    public_screenshot = load_json(root / "docs/assets/public-demo-screenshot-report.json")
    public_space = load_json(root / "docs/assets/public-space-sync-report.json")
    final_control = load_json(root / "docs/assets/final-submission-control.json")
    submit_checklist = load_json(root / "docs/assets/devpost-submission-checklist.json")
    submission_audit = load_json(root / "docs/assets/submission-audit-report.json")
    secret_scan = load_json(root / "docs/assets/secret-scan-report.json")

    sources = source_status(root)
    source_schemas_ok = all(source["schema_ok"] for source in sources.values())
    screenshot_ok = screenshot_ready(public_screenshot)
    public_space_ok = public_space_ready(public_space)
    form = field_rollup(form_kit)
    blockers = final_blockers(final_control)
    safe_to_share = bool(
        source_schemas_ok
        and screenshot_ok
        and public_space_ok
        and form["mock_ready"]
        and secret_scan
        and secret_scan.get("ok") is True
        and packet
        and packet.get("mode") in {"pre_live_safe", "post_live_verified"}
    )
    safe_to_submit = bool(
        safe_to_share
        and packet
        and packet.get("mode") == "post_live_verified"
        and form["final_ready"]
        and final_control
        and final_control.get("safe_to_submit") is True
        and submit_checklist
        and submit_checklist.get("safe_to_submit") is True
        and submission_audit
        and submission_audit.get("ok") is True
        and not blockers
    )
    mode = "final_preview_ready" if safe_to_submit else "pre_live_preview_ready" if safe_to_share else "preview_blocked"

    links = dict_field(judge_brief, "links")
    project = {
        "name": packet.get("project_name") if packet else "ProofFrame",
        "tagline": packet.get("tagline") if packet else None,
        "one_liner": packet.get("one_liner") if packet else None,
        "repository_url": packet.get("repository_url") if packet else links.get("repository"),
        "demo_url": packet.get("demo_url") if packet else links.get("public_demo"),
        "video_url": packet.get("video_url") if packet else links.get("devpost_video"),
    }
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": mode,
        "ok": safe_to_share,
        "safe_to_share": safe_to_share,
        "safe_to_submit": safe_to_submit,
        "project": project,
        "copy_blocks": {
            "thirty_second_pitch": judge_brief.get("judge_opening_30s") if judge_brief else "",
            "short_description": packet.get("short_description") if packet else "",
            "backblaze_b2_usage": packet.get("b2_usage") if packet else "",
            "genblaze_usage": packet.get("genblaze_usage") if packet else "",
            "accomplishments": text_list(packet.get("accomplishments", []) if packet else []),
            "whats_next": text_list(packet.get("whats_next", []) if packet else []),
            "judge_note": (
                "Use this preview as a copy/reference pack. It is not final-submittable until "
                "safe_to_submit becomes true."
            ),
        },
        "submission_readiness": {
            "packet_mode": packet.get("mode") if packet else None,
            "form_mode": form_kit.get("mode") if form_kit else None,
            "final_control_mode": final_control.get("mode") if final_control else None,
            "submit_checklist_mode": submit_checklist.get("mode") if submit_checklist else None,
            "submission_audit_mode": submission_audit.get("mode") if submission_audit else None,
            "secret_scan_mode": secret_scan.get("mode") if secret_scan else None,
            "public_space_mode": public_space.get("mode") if public_space else None,
            "public_screenshot_mode": public_screenshot.get("mode") if public_screenshot else None,
            "final_blockers": blockers,
        },
        "field_rollup": form,
        "criteria_rollup": criteria_rollup(crosswalk),
        "evidence_links": {
            "public_demo": project["demo_url"],
            "repository": project["repository_url"],
            "public_screenshot": "docs/assets/proofframe-hf-public-smoke.png",
            "screenshot_report": "docs/assets/public-demo-screenshot-report.json",
            "public_space_sync": "docs/assets/public-space-sync-report.json",
            "judge_brief": "docs/assets/judge-brief.json",
            "judge_crosswalk": "docs/assets/judge-crosswalk.json",
            "form_kit": "docs/assets/devpost-form-kit.json",
            "final_control": "docs/assets/final-submission-control.json",
            "submission_bundle": "docs/assets/submission-bundle-manifest.json",
        },
        "claim_boundary": [
            "Public demo evidence proves only the credential-free local/mock judge flow.",
            "Do not claim completed live Backblaze B2 storage until T020 has sanitized live evidence.",
            "Do not claim completed live Genblaze generation until T021 has sanitized live evidence.",
            "Do not submit this packet as final until safe_to_submit is true.",
        ],
        "source_status": sources,
        "next_actions": next_actions(
            safe_to_submit=safe_to_submit,
            blockers=blockers,
            form=form,
            public_space_ok=public_space_ok,
            screenshot_ok=screenshot_ok,
        ),
    }


def next_actions(
    *,
    safe_to_submit: bool,
    blockers: list[dict[str, Any]],
    form: dict[str, Any],
    public_space_ok: bool,
    screenshot_ok: bool,
) -> list[str]:
    if safe_to_submit:
        return ["Use this preview to fill Devpost and archive the submission receipt."]
    actions: list[str] = []
    if not public_space_ok:
        actions.append("Refresh the public Hugging Face Space and rerun public_space_sync.")
    if not screenshot_ok:
        actions.append("Regenerate the public judge-mode screenshot report.")
    if form["final_pending_fields"]:
        labels = ", ".join(str(item["label"]) for item in form["final_pending_fields"][:4])
        actions.append(f"Finalize Devpost fields: {labels}.")
    for blocker in blockers:
        actions.append(f"Resolve final blocker: {blocker['label']}.")
    actions.append("Rerun secret scan, strict final audit, and final submission control before Devpost submit.")
    return list(dict.fromkeys(actions))[:8]


def render_markdown(preview: dict[str, Any]) -> str:
    project = preview["project"]
    readiness = preview["submission_readiness"]
    lines = [
        "# ProofFrame Devpost Submission Preview",
        "",
        f"Mode: `{preview['mode']}`",
        f"Safe to share: `{str(preview['safe_to_share']).lower()}`",
        f"Safe to submit: `{str(preview['safe_to_submit']).lower()}`",
        "",
        "## Project",
        "",
        f"- Name: {project.get('name')}",
        f"- Tagline: {project.get('tagline')}",
        f"- Repository: {project.get('repository_url')}",
        f"- Demo: {project.get('demo_url')}",
        f"- Video: {project.get('video_url')}",
        "",
        "## Copy Blocks",
        "",
        "### 30-Second Pitch",
        "",
        preview["copy_blocks"]["thirty_second_pitch"],
        "",
        "### Short Description",
        "",
        preview["copy_blocks"]["short_description"],
        "",
        "### Backblaze B2 Usage",
        "",
        preview["copy_blocks"]["backblaze_b2_usage"],
        "",
        "### Genblaze Usage",
        "",
        preview["copy_blocks"]["genblaze_usage"],
        "",
        "## Evidence Links",
        "",
    ]
    for label, value in preview["evidence_links"].items():
        lines.append(f"- `{label}`: {value}")
    lines.extend(["", "## Readiness", ""])
    for key in [
        "packet_mode",
        "form_mode",
        "final_control_mode",
        "submit_checklist_mode",
        "submission_audit_mode",
        "secret_scan_mode",
        "public_space_mode",
        "public_screenshot_mode",
    ]:
        lines.append(f"- `{key}`: `{readiness.get(key)}`")
    lines.extend(["", "## Final Blockers", ""])
    if readiness["final_blockers"]:
        for blocker in readiness["final_blockers"]:
            lines.append(f"- `{blocker['id']}`: {blocker['label']} - {blocker['detail']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in preview["claim_boundary"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in preview["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(preview: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(preview, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(preview), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a claim-safe ProofFrame Devpost preview.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless safe_to_submit is true.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    preview = build_preview(args.root)
    write_outputs(preview, args.json_out, args.markdown_out)
    ok = preview["safe_to_submit"] if args.strict_final else preview["safe_to_share"]
    print(
        json.dumps(
            {
                "ok": ok,
                "mode": preview["mode"],
                "safe_to_share": preview["safe_to_share"],
                "safe_to_submit": preview["safe_to_submit"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": preview["next_actions"][:4],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
