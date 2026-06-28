#!/usr/bin/env python3
"""Build a fail-closed demo recording readiness report."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "demo-readiness-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "demo-readiness-report.md"
CLAIM_LINT_PATH = ROOT / "scripts" / "claim_lint.py"
CLAIM_LINT_SPEC = importlib.util.spec_from_file_location("claim_lint", CLAIM_LINT_PATH)
claim_lint = importlib.util.module_from_spec(CLAIM_LINT_SPEC)
assert CLAIM_LINT_SPEC.loader is not None
CLAIM_LINT_SPEC.loader.exec_module(claim_lint)

REQUIRED_MOCK_RECORDING_FILES = [
    "README.md",
    "docs/demo_script.md",
    "docs/public_claim_freeze.md",
    "docs/assets/devpost-submission-packet.json",
    "docs/assets/devpost-submission-packet.md",
    "docs/assets/devpost-form-kit.json",
    "docs/assets/devpost-form-kit.md",
    "docs/assets/submission-bundle-manifest.json",
    "docs/assets/submission-bundle-manifest.md",
    "docs/assets/live-credential-handoff.json",
    "docs/assets/live-credential-handoff.md",
    "docs/assets/demo-storyboard.json",
    "docs/assets/demo-storyboard.md",
    "docs/assets/public-video-check.json",
    "docs/assets/public-video-check.md",
    "docs/assets/proofframe-local-ui-smoke.png",
    "docs/assets/proofframe-review-console-smoke.png",
    "docs/assets/proofframe-hf-public-smoke.png",
    ".env.final.example",
    "scripts/claim_lint.py",
    "scripts/devpost_form_kit.py",
    "scripts/demo_storyboard.py",
    "scripts/public_video_check.py",
    "scripts/live_env_handoff.py",
    "scripts/run_b2_live_proof.py",
    "scripts/secret_scan.py",
]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json")
    if not tasks:
        return {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def file_record(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    return {
        "path": relative_path,
        "present": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def missing_files(records: list[dict[str, Any]]) -> list[str]:
    return [record["path"] for record in records if not record["present"]]


def build_next_actions(
    *,
    missing: list[str],
    claim_ok: bool,
    statuses: dict[str, str],
    evidence_ok: bool,
) -> list[str]:
    actions: list[str] = []
    if missing:
        actions.append("Restore missing demo recording files before recording.")
    if not claim_ok:
        actions.append("Run python scripts/claim_lint.py and fix unsafe public claims.")
    if statuses.get("T020") != "done":
        actions.append("Capture the live Backblaze B2 asset and manifest proof.")
    if statuses.get("T021") != "done":
        actions.append("Capture the live Genblaze generation proof.")
    if not evidence_ok:
        actions.append("Write docs/assets/final-live-proof-evidence.json with sanitized live proof.")
    if statuses.get("T041A") != "done":
        actions.append("Run the final secret scan before recording the final sponsor-backed video.")
    return actions[:6]


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    files = [file_record(root, path) for path in REQUIRED_MOCK_RECORDING_FILES]
    missing = missing_files(files)
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json") or {}
    gate = build_submission_gate(root)
    statuses = task_statuses(root)
    claim_report = claim_lint.build_claim_report(root)
    mock_recording_ready = (
        not missing
        and claim_report["ok"]
        and packet.get("mode") in {"pre_live_safe", "post_live_verified"}
        and str(packet.get("demo_url", "")).endswith("/?judge=1")
        and statuses.get("T040") == "done"
    )
    final_recording_ready = (
        mock_recording_ready
        and gate["evidence_gate"]["ok"]
        and statuses.get("T020") == "done"
        and statuses.get("T021") == "done"
        and statuses.get("T041A") == "done"
    )
    return {
        "schema": "proofframe.demo_readiness.v1",
        "mode": "final_ready" if final_recording_ready else "pre_live_mock_ready",
        "mock_recording_ready": mock_recording_ready,
        "final_recording_ready": final_recording_ready,
        "public_demo_url": packet.get("demo_url"),
        "devpost_packet_mode": packet.get("mode"),
        "task_statuses": {task: statuses.get(task, "missing") for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]},
        "submission_gate": {
            "ok": gate["ok"],
            "mode": gate["mode"],
            "summary": gate["summary"],
            "evidence_status": gate["evidence_gate"]["status"],
            "packet_status": gate["packet_gate"]["status"],
        },
        "claim_lint": {
            "ok": claim_report["ok"],
            "mode": claim_report["mode"],
            "findings": claim_report["findings"],
        },
        "files": files,
        "missing_files": missing,
        "next_actions": build_next_actions(
            missing=missing,
            claim_ok=claim_report["ok"],
            statuses=statuses,
            evidence_ok=gate["evidence_gate"]["ok"],
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Demo Readiness",
        "",
        f"Mode: `{report['mode']}`",
        f"Mock recording ready: `{str(report['mock_recording_ready']).lower()}`",
        f"Final recording ready: `{str(report['final_recording_ready']).lower()}`",
        f"Public demo: {report['public_demo_url']}",
        f"Devpost packet mode: `{report['devpost_packet_mode']}`",
        "",
        "## Current Gate",
        "",
        f"- Submission gate: `{report['submission_gate']['mode']}`",
        f"- Live evidence: `{report['submission_gate']['evidence_status']}`",
        f"- Claim lint: `{str(report['claim_lint']['ok']).lower()}`",
        "",
        "## Task Status",
        "",
    ]
    lines.extend(f"- {task}: `{status}`" for task, status in report["task_statuses"].items())
    lines.extend(["", "## Required Recording Files", ""])
    for item in report["files"]:
        marker = "OK" if item["present"] else "MISSING"
        lines.append(f"- {marker} `{item['path']}`")
    lines.extend(["", "## Next Actions", ""])
    if report["next_actions"]:
        lines.extend(f"- {action}" for action in report["next_actions"])
    else:
        lines.append("- Ready to record the final sponsor-backed demo.")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a ProofFrame demo recording readiness report.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Fail unless final B2/Genblaze recording evidence is ready.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["final_recording_ready"] if args.strict_final else report["mock_recording_ready"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": report["next_actions"],
            },
            indent=2,
        )
    )
    raise SystemExit(
        0
        if (report["final_recording_ready"] if args.strict_final else report["mock_recording_ready"])
        else 2
    )


if __name__ == "__main__":
    main()
