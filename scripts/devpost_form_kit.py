#!/usr/bin/env python3
"""Build a field-by-field Devpost form kit from the current submission packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-form-kit.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-form-kit.md"
DEFAULT_PACKET = ROOT / "docs" / "assets" / "devpost-submission-packet.json"

BUILT_WITH = [
    "Python",
    "FastAPI",
    "Backblaze B2 S3-compatible API",
    "Genblaze/GMICloud",
    "Hugging Face Spaces",
    "GitHub Actions",
]
TAGS = [
    "AI",
    "Generative media",
    "Backblaze B2",
    "Genblaze",
    "Provenance",
    "Media operations",
]
FINAL_FORM_TASKS = ["T020", "T021", "T040", "T041A"]


FORM_FIELD_SPECS = [
    {
        "id": "project_name",
        "label": "Project name",
        "source": "packet.project_name",
        "max_chars": 80,
        "required": True,
    },
    {
        "id": "tagline",
        "label": "Tagline",
        "source": "packet.tagline",
        "max_chars": 140,
        "required": True,
    },
    {
        "id": "one_liner",
        "label": "One-liner",
        "source": "packet.one_liner",
        "max_chars": 280,
        "required": True,
    },
    {
        "id": "short_description",
        "label": "Short description",
        "source": "packet.short_description",
        "max_chars": 2000,
        "required": True,
    },
    {
        "id": "repository_url",
        "label": "Repository URL",
        "source": "packet.repository_url",
        "max_chars": 300,
        "required": True,
        "kind": "url",
    },
    {
        "id": "demo_url",
        "label": "Demo URL",
        "source": "packet.demo_url",
        "max_chars": 300,
        "required": True,
        "kind": "url",
    },
    {
        "id": "video_url",
        "label": "Demo video URL",
        "source": "packet.video_url",
        "max_chars": 300,
        "required": True,
        "kind": "url",
        "allow_placeholder_before_final": True,
    },
    {
        "id": "built_with",
        "label": "Built with",
        "source": "form.built_with",
        "max_chars": 800,
        "required": True,
    },
    {
        "id": "tags",
        "label": "Suggested tags",
        "source": "form.tags",
        "max_chars": 500,
        "required": True,
    },
    {
        "id": "inspiration",
        "label": "Inspiration",
        "source": "packet.inspiration",
        "max_chars": 2000,
        "required": True,
    },
    {
        "id": "what_it_does",
        "label": "What it does",
        "source": "packet.what_it_does",
        "max_chars": 2500,
        "required": True,
    },
    {
        "id": "how_we_built_it",
        "label": "How we built it",
        "source": "packet.how_we_built_it",
        "max_chars": 2500,
        "required": True,
    },
    {
        "id": "backblaze_b2_usage",
        "label": "Backblaze B2 usage",
        "source": "packet.b2_usage",
        "max_chars": 1500,
        "required": True,
    },
    {
        "id": "genblaze_usage",
        "label": "Genblaze usage",
        "source": "packet.genblaze_usage",
        "max_chars": 1500,
        "required": True,
    },
    {
        "id": "challenges",
        "label": "Challenges",
        "source": "packet.challenges",
        "max_chars": 2000,
        "required": True,
    },
    {
        "id": "accomplishments",
        "label": "Accomplishments",
        "source": "packet.accomplishments",
        "max_chars": 2500,
        "required": True,
    },
    {
        "id": "what_we_learned",
        "label": "What we learned",
        "source": "packet.what_we_learned",
        "max_chars": 2000,
        "required": True,
    },
    {
        "id": "whats_next",
        "label": "What's next",
        "source": "packet.whats_next",
        "max_chars": 1800,
        "required": True,
    },
    {
        "id": "judging_note",
        "label": "Judging note",
        "source": "form.judging_note",
        "max_chars": 1000,
        "required": True,
    },
]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def stringify(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    if value is None:
        return ""
    return str(value).strip()


def packet_value(packet: dict[str, Any], source: str) -> str:
    if source == "form.built_with":
        return ", ".join(BUILT_WITH)
    if source == "form.tags":
        return ", ".join(TAGS)
    if source == "form.judging_note":
        return (
            f"Current packet mode: {packet.get('mode', 'unknown')}. "
            f"{packet.get('claim_warning', '')}"
        ).strip()
    if source.startswith("packet."):
        return stringify(packet.get(source.removeprefix("packet.")))
    return ""


def usable_url(value: str) -> bool:
    value = value.strip()
    return value.startswith(("https://", "http://")) and not has_placeholder(value)


def has_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or lowered.startswith("tbd") or "tbd after" in lowered


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def build_form_fields(packet: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for spec in FORM_FIELD_SPECS:
        value = packet_value(packet, spec["source"])
        too_long = len(value) > int(spec["max_chars"])
        missing = bool(spec["required"]) and not value
        placeholder = has_placeholder(value)
        url_missing = spec.get("kind") == "url" and not usable_url(value)
        if spec.get("allow_placeholder_before_final"):
            url_missing = False
        fields.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "source": spec["source"],
                "required": spec["required"],
                "value": value,
                "chars": len(value),
                "max_chars": spec["max_chars"],
                "too_long": too_long,
                "missing": missing,
                "placeholder": placeholder,
                "url_missing": url_missing,
                "ok_for_mock": not too_long and not missing and not url_missing,
                "ok_for_final": (
                    not too_long
                    and not missing
                    and not placeholder
                    and (spec.get("kind") != "url" or usable_url(value))
                ),
            }
        )
    return fields


def final_task_gate(statuses: dict[str, str]) -> dict[str, Any]:
    tasks = [
        {"id": task_id, "status": statuses.get(task_id, "missing")}
        for task_id in FINAL_FORM_TASKS
    ]
    return {
        "ok": all(task["status"] == "done" for task in tasks),
        "tasks": tasks,
    }


def next_actions(
    *,
    fields: list[dict[str, Any]],
    packet: dict[str, Any],
    evidence_ready: bool,
    task_gate: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if packet.get("mode") != "post_live_verified":
        actions.append("Regenerate the Devpost packet in post-live mode after B2 and Genblaze proof.")
    if not evidence_ready:
        actions.append("Capture sanitized final B2 plus Genblaze live proof evidence.")
    if not task_gate["ok"]:
        missing = ", ".join(
            task["id"] for task in task_gate["tasks"] if task["status"] != "done"
        )
        actions.append(f"Finish final form prerequisite tasks: {missing}.")
    for field in fields:
        if not field["ok_for_final"]:
            actions.append(f"Finalize Devpost field: {field['label']}.")
    actions.append("Run final secret scan, final audit, then submit Devpost.")
    return list(dict.fromkeys(actions))[:8]


def build_form_kit(root: Path = ROOT, packet_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(packet_path or root / "docs" / "assets" / "devpost-submission-packet.json")
    if packet is None:
        packet = {}
    gate = build_submission_gate(root)
    fields = build_form_fields(packet)
    statuses = task_statuses(root)
    task_gate = final_task_gate(statuses)
    mock_form_ready = bool(packet) and all(field["ok_for_mock"] for field in fields)
    public_video_ready = usable_url(str(packet.get("video_url", "")))
    final_form_ready = (
        mock_form_ready
        and all(field["ok_for_final"] for field in fields)
        and packet.get("mode") == "post_live_verified"
        and gate["evidence_gate"]["ok"]
        and task_gate["ok"]
        and public_video_ready
    )
    return {
        "schema": "proofframe.devpost_form_kit.v1",
        "mode": "final_form_ready" if final_form_ready else "pre_live_form_ready",
        "packet_mode": packet.get("mode"),
        "mock_form_ready": mock_form_ready,
        "final_form_ready": final_form_ready,
        "public_video_ready": public_video_ready,
        "field_count": len(fields),
        "fields": fields,
        "task_gate": task_gate,
        "evidence_gate": {
            "ok": gate["evidence_gate"]["ok"],
            "status": gate["evidence_gate"]["status"],
        },
        "next_actions": next_actions(
            fields=fields,
            packet=packet,
            evidence_ready=gate["evidence_gate"]["ok"],
            task_gate=task_gate,
        ),
    }


def render_markdown(kit: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Devpost Form Kit",
        "",
        f"Mode: `{kit['mode']}`",
        f"Packet mode: `{kit['packet_mode']}`",
        f"Mock form ready: `{str(kit['mock_form_ready']).lower()}`",
        f"Final form ready: `{str(kit['final_form_ready']).lower()}`",
        f"Public video ready: `{str(kit['public_video_ready']).lower()}`",
        "",
        "## Fields",
        "",
    ]
    for field in kit["fields"]:
        status = "OK" if field["ok_for_mock"] else "CHECK"
        final_status = "FINAL OK" if field["ok_for_final"] else "FINAL PENDING"
        lines.extend(
            [
                f"### {field['label']}",
                "",
                f"- Status: `{status}` / `{final_status}`",
                f"- Source: `{field['source']}`",
                f"- Length: `{field['chars']} / {field['max_chars']}`",
                "",
                "```text",
                field["value"],
                "```",
                "",
            ]
        )

    lines.extend(["## Final Prerequisite Tasks", ""])
    for task in kit["task_gate"]["tasks"]:
        lines.append(f"- `{task['id']}`: `{task['status']}`")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in kit["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(kit: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(kit, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(kit), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a field-by-field Devpost form kit.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Fail unless final live proof, public video URL, and final form fields are ready.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    kit = build_form_kit(args.root, args.packet)
    write_outputs(kit, args.json_out, args.markdown_out)
    ok = kit["final_form_ready"] if args.strict_final else kit["mock_form_ready"]
    print(
        json.dumps(
            {
                "ok": ok,
                "mode": kit["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": kit["next_actions"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
