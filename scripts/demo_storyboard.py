#!/usr/bin/env python3
"""Build a structured demo video storyboard and readiness report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "demo-storyboard.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "demo-storyboard.md"
MAX_SECONDS = 180
TARGET_SECONDS = 135

REQUIRED_ASSETS = [
    "docs/demo_script.md",
    "docs/assets/proofframe-local-ui-smoke.png",
    "docs/assets/proofframe-review-console-smoke.png",
    "docs/assets/proofframe-hf-public-smoke.png",
    "docs/assets/demo-readiness-report.md",
    "docs/assets/live-credential-handoff.md",
    "docs/assets/devpost-submission-packet.json",
]

SEGMENTS = [
    {
        "start": "0:00",
        "end": "0:12",
        "seconds": 12,
        "title": "Product hook",
        "screen": "ProofFrame dashboard and judge recording slate.",
        "safe_narration": (
            "ProofFrame helps teams trust generated media after the prompt is over by turning "
            "each asset into a reviewable packet."
        ),
    },
    {
        "start": "0:12",
        "end": "0:30",
        "seconds": 18,
        "title": "Sponsor evidence model",
        "screen": "Manifest fields plus non-secret B2 setup and final-gate status.",
        "safe_narration": (
            "Before any live credential is shown, the packet already has the B2-ready evidence "
            "shape: storage backend, storage key, checksum, manifest, and approval state. The "
            "private B2 bucket and runner are prepared, while live upload stays a final gate."
        ),
    },
    {
        "start": "0:30",
        "end": "0:48",
        "seconds": 18,
        "title": "Campaign brief",
        "screen": "Campaign, audience, tone, and brief fields.",
        "safe_narration": (
            "The workflow starts with a creative brief while preserving the operational details "
            "teams usually lose."
        ),
    },
    {
        "start": "0:48",
        "end": "1:10",
        "seconds": 22,
        "title": "Generate variants",
        "screen": "Generated asset ledger with provider/model evidence.",
        "safe_narration": (
            "The public demo uses deterministic mock generation; the same manifest fields are "
            "reserved for the final live Genblaze run."
        ),
    },
    {
        "start": "1:10",
        "end": "1:32",
        "seconds": 22,
        "title": "Review and approve",
        "screen": "Approve, reject, search, and filter evidence.",
        "safe_narration": (
            "Every approval decision travels with the packet so downstream teams know which "
            "generated files are safe to use."
        ),
    },
    {
        "start": "1:32",
        "end": "1:55",
        "seconds": 23,
        "title": "Manifest preview",
        "screen": "Provenance chain and manifest JSON.",
        "safe_narration": (
            "The manifest ties each asset to its prompt, provider, model, storage key, checksum, "
            "approval state, and risk note."
        ),
    },
    {
        "start": "1:55",
        "end": "2:08",
        "seconds": 13,
        "title": "Export packet",
        "screen": "Export manifest and download evidence ZIP.",
        "safe_narration": (
            "The local packet exports as a downloadable ZIP; final B2 proof must verify the same "
            "flow through Backblaze storage before public claims are upgraded."
        ),
    },
    {
        "start": "2:08",
        "end": "2:15",
        "seconds": 7,
        "title": "Close",
        "screen": "Repo link, gate status, and ProofFrame title.",
        "safe_narration": (
            "ProofFrame makes generated media creative enough to move fast and traceable enough "
            "to trust."
        ),
    },
]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def task_statuses(root: Path) -> dict[str, str]:
    data = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in data.get("tasks", [])
    }


def asset_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for relative_path in REQUIRED_ASSETS:
        path = root / relative_path
        records.append(
            {
                "path": relative_path,
                "present": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return records


def usable_video_url(value: Any) -> bool:
    text = str(value or "").strip()
    if not text or text.lower().startswith("tbd"):
        return False
    return text.startswith(("https://", "http://"))


def build_next_actions(
    *, statuses: dict[str, str], public_video_ready: bool, evidence_ready: bool
) -> list[str]:
    actions: list[str] = []
    if statuses.get("T020") != "done":
        actions.append("Capture live Backblaze B2 asset and manifest proof.")
    if statuses.get("T021") != "done":
        actions.append("Capture live Genblaze generation proof.")
    if not evidence_ready:
        actions.append("Write sanitized final live proof evidence JSON.")
    if not public_video_ready:
        actions.append("Record and upload the final public demo video under 3 minutes.")
    if statuses.get("T041A") != "done":
        actions.append("Run final secret scan before publishing the video.")
    return actions[:6]


def build_storyboard(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json") or {}
    statuses = task_statuses(root)
    gate = build_submission_gate(root)
    assets = asset_records(root)
    missing_assets = [item["path"] for item in assets if not item["present"]]
    total_seconds = sum(segment["seconds"] for segment in SEGMENTS)
    public_video_ready = usable_video_url(packet.get("video_url"))
    proof_tasks_ready = statuses.get("T020") == "done" and statuses.get("T021") == "done"
    final_secret_scan_ready = statuses.get("T041A") == "done"
    mock_storyboard_ready = (
        not missing_assets
        and total_seconds <= MAX_SECONDS
        and packet.get("mode") in {"pre_live_safe", "post_live_verified"}
        and str(packet.get("demo_url", "")).endswith("/?judge=1")
    )
    final_video_ready = (
        mock_storyboard_ready
        and proof_tasks_ready
        and final_secret_scan_ready
        and gate["evidence_gate"]["ok"]
        and public_video_ready
    )
    return {
        "schema": "proofframe.demo_storyboard.v1",
        "mode": "final_video_ready" if final_video_ready else "mock_storyboard_ready",
        "target_seconds": TARGET_SECONDS,
        "max_seconds": MAX_SECONDS,
        "total_seconds": total_seconds,
        "under_time_limit": total_seconds <= MAX_SECONDS,
        "mock_storyboard_ready": mock_storyboard_ready,
        "final_video_ready": final_video_ready,
        "public_demo_url": packet.get("demo_url"),
        "public_video_url": packet.get("video_url"),
        "public_video_ready": public_video_ready,
        "task_statuses": {
            task: statuses.get(task, "missing") for task in ["T020", "T021", "T041A", "T042"]
        },
        "submission_gate": {
            "mode": gate["mode"],
            "evidence_status": gate["evidence_gate"]["status"],
            "evidence_ok": gate["evidence_gate"]["ok"],
        },
        "segments": SEGMENTS,
        "assets": assets,
        "missing_assets": missing_assets,
        "next_actions": build_next_actions(
            statuses=statuses,
            public_video_ready=public_video_ready,
            evidence_ready=gate["evidence_gate"]["ok"],
        ),
    }


def render_markdown(storyboard: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Demo Storyboard",
        "",
        f"Mode: `{storyboard['mode']}`",
        f"Mock storyboard ready: `{str(storyboard['mock_storyboard_ready']).lower()}`",
        f"Final video ready: `{str(storyboard['final_video_ready']).lower()}`",
        f"Duration: `{storyboard['total_seconds']}s / {storyboard['max_seconds']}s max`",
        f"Public demo: {storyboard['public_demo_url']}",
        f"Video URL: {storyboard['public_video_url']}",
        "",
        "## Timeline",
        "",
        "| Time | Shot | Screen | Narration |",
        "| --- | --- | --- | --- |",
    ]
    for segment in storyboard["segments"]:
        lines.append(
            "| "
            f"{segment['start']}-{segment['end']} | "
            f"{segment['title']} | "
            f"{segment['screen']} | "
            f"{segment['safe_narration']} |"
        )
    lines.extend(["", "## Required Assets", ""])
    for asset in storyboard["assets"]:
        marker = "OK" if asset["present"] else "MISSING"
        lines.append(f"- {marker} `{asset['path']}`")
    lines.extend(["", "## Next Actions", ""])
    if storyboard["next_actions"]:
        lines.extend(f"- {action}" for action in storyboard["next_actions"])
    else:
        lines.append("- Ready to attach the final public video URL to Devpost.")
    return "\n".join(lines) + "\n"


def write_outputs(storyboard: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(storyboard, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(storyboard), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a ProofFrame demo video storyboard.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Fail unless final live proof and public video URL are ready.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    storyboard = build_storyboard(args.root)
    write_outputs(storyboard, args.json_out, args.markdown_out)
    ok = storyboard["final_video_ready"] if args.strict_final else storyboard["mock_storyboard_ready"]
    print(
        json.dumps(
            {
                "ok": ok,
                "mode": storyboard["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": storyboard["next_actions"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
