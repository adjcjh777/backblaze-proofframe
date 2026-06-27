#!/usr/bin/env python3
"""Fail-closed audit for ProofFrame's final Devpost submission gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DONE_TASKS = ["T020", "T021", "T040", "T041", "T041A", "T042"]
REQUIRED_PUBLIC_FILES = [
    "README.md",
    "docs/prd.md",
    "docs/spec.md",
    "docs/devpost_draft.md",
    "docs/assets/devpost-form-kit.json",
    "docs/assets/devpost-form-kit.md",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_map(tasks_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"].upper(): task for task in tasks_data["tasks"]}


def check_tasks(tasks_data: dict[str, Any]) -> list[dict[str, str]]:
    tasks = task_map(tasks_data)
    findings: list[dict[str, str]] = []
    for task_id in REQUIRED_DONE_TASKS:
        task = tasks.get(task_id)
        if not task:
            findings.append({"gate": task_id, "status": "missing", "detail": "Task is absent."})
        elif task.get("status") != "done":
            findings.append(
                {
                    "gate": task_id,
                    "status": str(task.get("status")),
                    "detail": f"{task.get('title', task_id)} is not done.",
                }
            )
    return findings


def check_files(paths: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            findings.append(
                {
                    "gate": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                    "status": "missing",
                    "detail": "Required submission artifact is missing.",
                }
            )
    return findings


def check_final_evidence(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return [
            {
                "gate": "final-live-proof-evidence",
                "status": "missing",
                "detail": f"{path} does not exist.",
            }
        ]
    evidence = load_json(path)
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
                {
                    "gate": f"evidence.{key}",
                    "status": "mismatch",
                    "detail": f"Expected {expected_value!r}, got {actual!r}.",
                }
            )
    for key in ("asset_sha256", "manifest_sha256", "asset_storage_key", "manifest_key"):
        if not evidence.get(key):
            findings.append(
                {
                    "gate": f"evidence.{key}",
                    "status": "missing",
                    "detail": "Final evidence is missing this field.",
                }
            )
    return findings


def build_audit_report(tasks_path: Path, final_evidence_path: Path) -> dict[str, Any]:
    tasks_data = load_json(tasks_path)
    required_files = [ROOT / path for path in REQUIRED_PUBLIC_FILES + REQUIRED_SCREENSHOTS]
    findings = [
        *check_tasks(tasks_data),
        *check_files(required_files),
        *check_final_evidence(final_evidence_path),
    ]
    return {
        "ok": not findings,
        "required_done_tasks": REQUIRED_DONE_TASKS,
        "final_evidence_path": str(final_evidence_path),
        "findings": findings,
        "next_commands": [
            "python scripts/secret_scan.py",
            "python scripts/live_proof.py --base-url <final-demo-url> --evidence-out docs/assets/final-live-proof-evidence.json",
            "python scripts/submission_audit.py",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit final Devpost submission readiness.")
    parser.add_argument("--tasks", type=Path, default=ROOT / "tasks.json")
    parser.add_argument(
        "--final-evidence",
        type=Path,
        default=ROOT / "docs" / "assets" / "final-live-proof-evidence.json",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_audit_report(args.tasks, args.final_evidence)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
