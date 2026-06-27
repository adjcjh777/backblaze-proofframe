#!/usr/bin/env python3
"""Fail-closed public claim lint for pre-live ProofFrame submissions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PUBLIC_COPY_FILES = [
    "README.md",
    "docs/submission.md",
    "docs/assets/devpost-submission-packet.md",
    "docs/assets/devpost-submission-packet.json",
]
PRE_LIVE_ALLOWED_MARKERS = (
    "final gate",
    "final submission gate",
    "submission gate",
    "target",
    "pending",
    "requires",
    "require ",
    "after t020",
    "after t021",
    "after proof",
    "until live",
    "not ",
    "do not say",
    "safe after",
    "verified run",
)
PRE_LIVE_FORBIDDEN_PATTERNS = [
    re.compile(r"(?i)\bstores?\b.*\b(?:in|through|to)\b.*\bbackblaze b2\b"),
    re.compile(r"(?i)\bbackblaze b2-backed\b"),
    re.compile(r"(?i)\bgenerates?\b.*\b(?:with|through)\b.*\bgenblaze\b"),
    re.compile(r"(?i)\bgenblaze-generated\b"),
    re.compile(r"(?i)\buses?\b.*\bb2 storage\b.*\bend[- ]to[- ]end\b"),
    re.compile(r"(?i)\bevery asset\b.*\bb2\b"),
    re.compile(r"(?i)\blive b2 object packet\b"),
]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def line_is_contextualized(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in PRE_LIVE_ALLOWED_MARKERS)


def scan_public_copy(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for relative_path in ACTIVE_PUBLIC_COPY_FILES:
        path = root / relative_path
        if not path.exists():
            findings.append(
                {
                    "path": relative_path,
                    "line": None,
                    "status": "missing",
                    "detail": "Active public copy file is missing.",
                }
            )
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line_is_contextualized(line):
                continue
            for pattern in PRE_LIVE_FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": relative_path,
                            "line": line_number,
                            "status": "unsafe-pre-live-claim",
                            "detail": line.strip(),
                        }
                    )
                    break
    return findings


def proof_ready_from_gate(gate: dict[str, Any]) -> bool:
    task_statuses = {item["id"]: item["ok"] for item in gate.get("task_gates", [])}
    return bool(gate["evidence_gate"]["ok"] and task_statuses.get("T020") and task_statuses.get("T021"))


def check_packet_mode(root: Path, proof_ready: bool) -> list[dict[str, Any]]:
    packet_path = root / "docs" / "assets" / "devpost-submission-packet.json"
    packet = load_json(packet_path)
    if packet is None:
        return [
            {
                "path": str(packet_path.relative_to(root)),
                "line": None,
                "status": "missing",
                "detail": "Devpost packet JSON is missing or invalid.",
            }
        ]
    mode = packet.get("mode")
    if not proof_ready and mode != "pre_live_safe":
        return [
            {
                "path": str(packet_path.relative_to(root)),
                "line": None,
                "status": "unsafe-packet-mode",
                "detail": f"Expected pre_live_safe before final evidence, got {mode!r}.",
            }
        ]
    return []


def build_claim_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    gate = build_submission_gate(root)
    proof_ready = proof_ready_from_gate(gate)
    findings: list[dict[str, Any]] = []
    findings.extend(check_packet_mode(root, proof_ready))
    if not proof_ready:
        findings.extend(scan_public_copy(root))
    return {
        "ok": not findings,
        "mode": "post_live_verified" if proof_ready else "pre_live_safe",
        "final_gate": {
            "ok": gate["ok"],
            "proof_ready": proof_ready,
            "summary": gate["summary"],
            "evidence_status": gate["evidence_gate"]["status"],
            "packet_status": gate["packet_gate"]["status"],
        },
        "scanned_files": ACTIVE_PUBLIC_COPY_FILES,
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lint ProofFrame public copy for unsafe claims.")
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_claim_report(args.root)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
