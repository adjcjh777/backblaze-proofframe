#!/usr/bin/env python3
"""Audit sponsor-fit clarity without requiring live credentials."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "sponsor-fit-audit.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "sponsor-fit-audit.md"


def load_script(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


claim_lint = load_script("claim_lint", "scripts/claim_lint.py")
demo_storyboard = load_script("demo_storyboard", "scripts/demo_storyboard.py")


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


def seconds_from_timestamp(value: str) -> int:
    minutes, seconds = value.split(":", maxsplit=1)
    return int(minutes) * 60 + int(seconds)


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def text_has_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def signal(signal_id: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"id": signal_id, "ok": ok, "detail": detail}


def early_storyboard_has(storyboard: dict[str, Any], needle: str, max_start_seconds: int) -> bool:
    needle = needle.lower()
    for segment in storyboard.get("segments", []):
        haystack = " ".join(
            str(segment.get(key, "")) for key in ("title", "screen", "safe_narration")
        ).lower()
        if needle in haystack and seconds_from_timestamp(str(segment["start"])) <= max_start_seconds:
            return True
    return False


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json") or {}
    storyboard = demo_storyboard.build_storyboard(root)
    claim_report = claim_lint.build_claim_report(root)
    gate = build_submission_gate(root)
    statuses = task_statuses(root)
    b2_usage = str(packet.get("b2_usage", ""))
    genblaze_usage = str(packet.get("genblaze_usage", ""))
    matrix_text = read_text(root / "docs" / "sponsor_fit_matrix.md")
    ui_text = read_text(root / "apps" / "web" / "index.html")
    signals = [
        signal(
            "matrix_present",
            text_has_all(matrix_text, ["Official judging angle", "Backblaze B2", "Genblaze"]),
            "docs/sponsor_fit_matrix.md maps judging criteria to safe claims and final gates.",
        ),
        signal(
            "ui_sponsor_model_present",
            text_has_all(ui_text, ["Sponsor Evidence Model", "Genblaze Step", "B2 Object Route"]),
            "Judge mode first viewport exposes the sponsor evidence model inside the product UI.",
        ),
        signal(
            "b2_usage_specific",
            len(b2_usage) >= 300
            and text_has_all(
                b2_usage,
                ["manifest", "checksum", "storage key", "private B2 bucket", "final submission gate"],
            ),
            "Devpost B2 copy explains the object model, prepared bucket, and final live gate.",
        ),
        signal(
            "genblaze_usage_specific",
            len(genblaze_usage) >= 220
            and text_has_all(genblaze_usage, ["Pipeline API", "provider", "model", "final submission gate"]),
            "Devpost Genblaze copy explains the adapter and final provider/model proof.",
        ),
        signal(
            "storyboard_b2_early",
            early_storyboard_has(storyboard, "b2", 45)
            or early_storyboard_has(storyboard, "backblaze", 45),
            "The video introduces Backblaze/B2 relevance within the first 45 seconds.",
        ),
        signal(
            "storyboard_genblaze_present",
            any(
                "genblaze" in " ".join(str(segment.get(key, "")) for key in segment).lower()
                for segment in storyboard.get("segments", [])
            ),
            "The storyboard still covers the Genblaze generation path.",
        ),
        signal(
            "claim_lint_safe",
            bool(claim_report["ok"]) and claim_report["mode"] in {"pre_live_safe", "post_live_verified"},
            "Public copy remains claim-safe for the current evidence mode.",
        ),
        signal(
            "final_gate_controls_claims",
            (
                gate["ok"]
                or (
                    gate["mode"] == "pre_live_safe"
                    and (statuses.get("T020") != "done" or statuses.get("T021") != "done")
                )
            ),
            "Final sponsor claims remain controlled by T020/T021 and final evidence.",
        ),
    ]
    return {
        "schema": "proofframe.sponsor_fit_audit.v1",
        "ok": all(item["ok"] for item in signals),
        "mode": "sponsor_fit_ready" if all(item["ok"] for item in signals) else "needs_sponsor_fit_work",
        "packet_mode": packet.get("mode"),
        "storyboard_mode": storyboard["mode"],
        "submission_gate_mode": gate["mode"],
        "signals": signals,
        "next_actions": [
            item["detail"] for item in signals if not item["ok"]
        ]
        or ["Use sponsor-fit matrix while recording and filling Devpost."],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Sponsor Fit Audit",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Packet mode: `{report['packet_mode']}`",
        f"Storyboard mode: `{report['storyboard_mode']}`",
        f"Submission gate: `{report['submission_gate_mode']}`",
        "",
        "## Signals",
        "",
    ]
    for item in report["signals"]:
        marker = "OK" if item["ok"] else "TODO"
        lines.append(f"- {marker} `{item['id']}`: {item['detail']}")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit ProofFrame sponsor-fit clarity.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": report["next_actions"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
