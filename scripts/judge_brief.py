#!/usr/bin/env python3
"""Build a concise, judge-facing ProofFrame brief from public-safe reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.judge_brief.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "judge-brief.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "judge-brief.md"


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


def safe_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def build_brief(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json")
    award = load_json(root / "docs" / "assets" / "award-readiness-report.json")
    control = load_json(root / "docs" / "assets" / "final-submission-control.json")
    launch = load_json(root / "docs" / "assets" / "final-launch-plan.json")
    public_sync = load_json(root / "docs" / "assets" / "public-space-sync-report.json")
    event_snapshot = load_json(root / "docs" / "assets" / "devpost-event-snapshot.json")
    statuses = task_statuses(root)
    final_gate_ready = bool(control.get("safe_to_submit"))
    final_closure = award.get("readiness_interpretation", {})
    safe_claims = [
        "ProofFrame is a working provenance and approval desk for generated media.",
        "The public demo is credential-free and runs in deterministic local/mock mode.",
        "The repository includes Backblaze B2-compatible storage and Genblaze/GMICloud provider paths.",
        "Every public claim is gated by reports, task status, and secret-scan artifacts.",
    ]
    if final_gate_ready:
        safe_claims.append("The final B2 plus Genblaze proof gate is complete.")
    not_yet_claimed = []
    if statuses.get("T020") != "done":
        not_yet_claimed.append("Completed Backblaze B2 live storage proof.")
    if statuses.get("T021") != "done":
        not_yet_claimed.append("Completed Genblaze live generation proof.")
    if statuses.get("T042") != "done":
        not_yet_claimed.append("Submitted Devpost project receipt.")
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "project": packet.get("project_name", "ProofFrame"),
        "tagline": packet.get("tagline", "A provenance-first vault for generated media."),
        "one_liner": packet.get("one_liner"),
        "judge_opening_30s": (
            "ProofFrame is not another image generator. It is a media operations desk that turns "
            "each generated asset into a reviewable packet: prompt, provider/model metadata, "
            "storage reference, checksum, approval state, risk note, manifest, and exportable evidence."
        ),
        "why_it_can_win": [
            "Storage and provenance are the product surface, not a hidden implementation detail.",
            "Backblaze B2 and Genblaze integration code paths are implemented and gated; live proofs remain explicit final blockers.",
            "The app feels useful after the hackathon: teams can approve, reject, search, export, and audit generated media.",
            "Fail-closed reports make the submission defensible and prevent overclaiming before live proof.",
        ],
        "status": {
            "packet_mode": packet.get("mode"),
            "safe_to_submit": final_gate_ready,
            "launch_mode": launch.get("mode"),
            "current_phase": launch.get("current_phase"),
            "next_command": launch.get("next_command"),
            "award_mode": award.get("mode"),
            "award_score": award.get("score"),
            "award_max_score": award.get("max_score"),
            "final_closure_score": final_closure.get("final_closure_score"),
            "final_closure_max_score": final_closure.get("final_closure_max_score"),
            "public_space_mode": public_sync.get("mode"),
            "event_submission_open": (event_snapshot.get("validation") or {}).get("submission_open"),
        },
        "links": {
            "public_demo": packet.get("demo_url"),
            "repository": packet.get("repository_url"),
            "devpost_video": packet.get("video_url"),
        },
        "safe_claims": safe_claims,
        "not_yet_claimed": not_yet_claimed,
        "judge_walkthrough": [
            "Open the public demo in judge mode and create the one-click Judge Demo packet.",
            "Inspect generated assets, provider/model fields, storage references, checksums, and approval state.",
            "Approve or reject an asset and download the evidence ZIP.",
            "Read the final control and launch plan reports to see exactly what remains before final sponsor proof.",
        ],
        "evidence_artifacts": [
            "docs/assets/devpost-form-kit.md",
            "docs/assets/final-submission-control.md",
            "docs/assets/final-launch-plan.md",
            "docs/assets/award-readiness-report.md",
            "docs/assets/public-space-sync-report.md",
            "docs/assets/submission-bundle-manifest.md",
        ],
        "tasks": {
            task_id: statuses.get(task_id, "missing")
            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "copy_blocks": {
            "devpost_intro": (
                "ProofFrame makes generated media operationally trustworthy: the demo creates "
                "media packets that include prompts, provider/model metadata, storage references, "
                "checksums, review state, risk notes, and downloadable manifests."
            ),
            "judge_note": (
                "Current public demo is safe local/mock mode. Final sponsor claims stay gated until "
                "Backblaze B2 live storage proof, Genblaze live generation proof, final video, audit, "
                "and Devpost receipt are complete."
            ),
        },
    }


def render_markdown(brief: dict[str, Any]) -> str:
    status = brief["status"]
    lines = [
        "# ProofFrame Judge Brief",
        "",
        f"Created: `{brief['created_at']}`",
        f"Tagline: {brief['tagline']}",
        f"Public demo: {brief['links']['public_demo']}",
        f"Repository: {brief['links']['repository']}",
        "",
        "## 30-Second Opening",
        "",
        brief["judge_opening_30s"],
        "",
        "## Why It Can Win",
        "",
    ]
    lines.extend(f"- {item}" for item in brief["why_it_can_win"])
    lines.extend(
        [
            "",
            "## Current Status",
            "",
            f"- Packet mode: `{status['packet_mode']}`",
            f"- Safe to submit: `{str(status['safe_to_submit']).lower()}`",
            f"- Launch phase: `{status['current_phase']}`",
            f"- Next command: `{status['next_command']}`",
            f"- Award readiness: `{status['award_score']}/{status['award_max_score']}` ({status['award_mode']})",
            f"- Final closure: `{status['final_closure_score']}/{status['final_closure_max_score']}`",
            f"- Public Space: `{status['public_space_mode']}` (see `docs/assets/public-space-sync-report.md` for runtime sha)",
            f"- Devpost submission open: `{status['event_submission_open']}`",
            "",
            "## Safe Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in brief["safe_claims"])
    lines.extend(["", "## Not Yet Claimed", ""])
    if brief["not_yet_claimed"]:
        lines.extend(f"- {item}" for item in brief["not_yet_claimed"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Judge Walkthrough", ""])
    lines.extend(f"- {item}" for item in brief["judge_walkthrough"])
    lines.extend(["", "## Evidence Artifacts", ""])
    lines.extend(f"- `{item}`" for item in brief["evidence_artifacts"])
    lines.extend(["", "## Copy Blocks", ""])
    for key, value in brief["copy_blocks"].items():
        lines.extend([f"### {key}", "", value, ""])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(brief: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(brief), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a public-safe ProofFrame judge brief.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    brief = build_brief(args.root)
    write_outputs(brief, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": True,
                "schema": brief["schema"],
                "safe_to_submit": brief["status"]["safe_to_submit"],
                "current_phase": brief["status"]["current_phase"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
