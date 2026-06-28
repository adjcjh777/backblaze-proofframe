#!/usr/bin/env python3
"""Run the post-credential live proof sequence without storing secrets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any, Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / ".env.final.local"
DEFAULT_JSON = ROOT / "docs" / "assets" / "post-credential-live-proof-plan.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "post-credential-live-proof-plan.md"
SCHEMA = "proofframe.post_credential_live_proof.v1"
B2_EVIDENCE = ROOT / "docs" / "assets" / "b2-live-proof-evidence.json"
FINAL_EVIDENCE = ROOT / "docs" / "assets" / "final-live-proof-evidence.json"
FORBIDDEN_EVIDENCE_KEYS = re.compile(
    r"(?i)(api[_-]?key|application[_-]?key|authorization|cookie|password|secret|token)"
)
FORBIDDEN_EVIDENCE_VALUES = [
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|application[_-]?key|secret|token|cookie)=[^&\s]{8,}"),
    re.compile(r"(?i)x-amz-(credential|security-token|signature)=[^&\s]{8,}"),
    re.compile(r"(?i)gmi-[A-Za-z0-9_\-]{16,}"),
]
REQUIRED_EVIDENCE_VALUES = ("asset_sha256", "manifest_sha256", "asset_storage_key", "manifest_key")
EXPECTED_EVIDENCE_FIELDS = {
    "b2": {
        "ok": True,
        "storage_backend": "b2",
        "generation_backend": "mock",
        "asset_storage_backend": "b2",
        "asset_provider": "mock",
        "manifest_storage_backend": "b2",
    },
    "final": {
        "ok": True,
        "storage_backend": "b2",
        "generation_backend": "genblaze",
        "asset_storage_backend": "b2",
        "asset_provider": "genblaze/gmicloud-image",
        "manifest_storage_backend": "b2",
    },
}


@dataclass(frozen=True)
class CommandSpec:
    command_id: str
    label: str
    command: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def script_command(script: str, *args: str, python: str = sys.executable) -> list[str]:
    return [python, str(ROOT / "scripts" / script), *args]


def task_done_command(task_id: str, note: str, python: str = sys.executable) -> list[str]:
    return script_command("task.py", "done", task_id, "--note", note, python=python)


def validate_evidence_command(kind: str, evidence_path: Path, python: str = sys.executable) -> list[str]:
    return [
        python,
        str(ROOT / "scripts" / "post_credential_live_proof.py"),
        "--validate-evidence",
        kind,
        "--evidence-path",
        rel(evidence_path),
    ]


def build_commands(
    *,
    env_file: Path = DEFAULT_ENV_FILE,
    update_tasks: bool = False,
    python: str = sys.executable,
) -> list[CommandSpec]:
    env_arg = rel(env_file)
    commands = [
        CommandSpec(
            "credential_handoff",
            "Verify local live credential presence without printing values",
            script_command("live_env_handoff.py", "--env-file", env_arg, "--strict", python=python),
        ),
        CommandSpec(
            "b2_live_proof",
            "Capture Backblaze B2 storage proof with mock generation",
            script_command(
                "run_b2_live_proof.py",
                "--env-file",
                env_arg,
                "--evidence-out",
                "docs/assets/b2-live-proof-evidence.json",
                python=python,
            ),
        ),
        CommandSpec(
            "validate_b2_evidence",
            "Validate sanitized B2 evidence before any T020 task update",
            validate_evidence_command("b2", B2_EVIDENCE, python=python),
        ),
    ]
    if update_tasks:
        commands.append(
            CommandSpec(
                "mark_t020_done",
                "Mark T020 done after sanitized B2 evidence exists",
                task_done_command(
                    "T020",
                    "B2 live proof evidence captured in docs/assets/b2-live-proof-evidence.json.",
                    python=python,
                ),
            )
        )
    commands.append(
        CommandSpec(
            "final_live_proof",
            "Capture final B2 plus Genblaze proof",
            script_command(
                "run_final_live_proof.py",
                "--env-file",
                env_arg,
                "--evidence-out",
                "docs/assets/final-live-proof-evidence.json",
                python=python,
            ),
        )
    )
    commands.append(
        CommandSpec(
            "validate_final_evidence",
            "Validate sanitized final B2 plus Genblaze evidence before any T021 task update",
            validate_evidence_command("final", FINAL_EVIDENCE, python=python),
        )
    )
    if update_tasks:
        commands.append(
            CommandSpec(
                "mark_t021_done",
                "Mark T021 done after sanitized final evidence exists",
                task_done_command(
                    "T021",
                    "Final B2 plus Genblaze live proof evidence captured in docs/assets/final-live-proof-evidence.json.",
                    python=python,
                ),
            )
        )
    commands.extend(
        [
            CommandSpec(
                "live_env_handoff_report",
                "Regenerate live credential handoff report",
                script_command("live_env_handoff.py", "--env-file", env_arg, python=python),
            ),
            CommandSpec("devpost_form_kit", "Regenerate Devpost form kit", script_command("devpost_form_kit.py", python=python)),
            CommandSpec(
                "devpost_submission_checklist",
                "Regenerate Devpost submission checklist",
                script_command("devpost_submission_checklist.py", python=python),
            ),
            CommandSpec("judge_brief", "Regenerate judge brief", script_command("judge_brief.py", python=python)),
            CommandSpec("judge_crosswalk", "Regenerate judge crosswalk", script_command("judge_crosswalk.py", python=python)),
            CommandSpec("demo_storyboard", "Regenerate demo storyboard", script_command("demo_storyboard.py", python=python)),
            CommandSpec("demo_readiness", "Regenerate demo readiness report", script_command("demo_readiness.py", python=python)),
            CommandSpec(
                "recording_assets",
                "Regenerate recording assets report and verify public mock assets",
                script_command("recording_assets.py", "--verify-public", python=python),
            ),
            CommandSpec(
                "award_readiness",
                "Regenerate award readiness scorecard",
                script_command("award_readiness.py", "--min-score", "75", python=python),
            ),
            CommandSpec(
                "final_operator_brief",
                "Regenerate final operator brief",
                script_command("final_operator_brief.py", python=python),
            ),
            CommandSpec(
                "final_launch_plan",
                "Regenerate final launch plan",
                script_command("final_launch_plan.py", python=python),
            ),
            CommandSpec(
                "final_rehearsal",
                "Regenerate final rehearsal checklist",
                script_command("final_rehearsal.py", python=python),
            ),
            CommandSpec(
                "final_submission_control",
                "Regenerate final submission control",
                script_command("final_submission_control.py", python=python),
            ),
            CommandSpec(
                "submission_audit",
                "Regenerate pre-submit audit report",
                script_command("submission_audit.py", python=python),
            ),
            CommandSpec("secret_scan", "Run no-value secret scan", script_command("secret_scan.py", python=python)),
            CommandSpec("submission_bundle", "Regenerate submission bundle manifest", script_command("submission_bundle.py", python=python)),
        ]
    )
    return commands


def load_evidence(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "Evidence file is missing."
    except json.JSONDecodeError as exc:
        return None, f"Evidence file is invalid JSON: {exc}"
    if not isinstance(evidence, dict):
        return None, "Evidence JSON must be an object."
    return evidence, None


def evidence_safety_findings(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}"
            if FORBIDDEN_EVIDENCE_KEYS.search(str(key)):
                findings.append(f"{key_path}: forbidden evidence key")
            findings.extend(evidence_safety_findings(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(evidence_safety_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        for pattern in FORBIDDEN_EVIDENCE_VALUES:
            if pattern.search(value):
                findings.append(f"{path}: forbidden evidence value")
                break
    return findings


def validate_evidence(kind: str, path: Path) -> dict[str, Any]:
    evidence, load_error = load_evidence(path)
    findings: list[dict[str, str]] = []
    if load_error:
        findings.append({"field": "file", "detail": load_error})
        evidence = {}

    expected = EXPECTED_EVIDENCE_FIELDS[kind]
    for key, expected_value in expected.items():
        actual = evidence.get(key)
        if actual != expected_value:
            findings.append({"field": key, "detail": f"Expected {expected_value!r}, got {actual!r}."})
    for key in REQUIRED_EVIDENCE_VALUES:
        if not evidence.get(key):
            findings.append({"field": key, "detail": "Required evidence value is missing."})
    for finding in evidence_safety_findings(evidence):
        findings.append({"field": "secret_safety", "detail": finding})

    return {
        "ok": not findings,
        "kind": kind,
        "path": rel(path),
        "checks": {
            "expected_fields": expected,
            "required_values": list(REQUIRED_EVIDENCE_VALUES),
            "secret_safety": "forbidden keys, bearer tokens, signed URL parameters, and GMI-style keys",
        },
        "findings": findings,
    }


def command_record(spec: CommandSpec, status: str, returncode: int | None = None) -> dict[str, Any]:
    return {
        "id": spec.command_id,
        "label": spec.label,
        "status": status,
        "returncode": returncode,
        "command": shlex.join(spec.command),
    }


def run_sequence(
    commands: Sequence[CommandSpec],
    *,
    execute: bool,
    runner: Callable[..., subprocess.CompletedProcess[Any]] = subprocess.run,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    if not execute:
        return {
            "ok": True,
            "mode": "plan_only",
            "commands": [command_record(spec, "planned") for spec in commands],
            "failed_command": None,
        }

    failed_command: str | None = None
    for index, spec in enumerate(commands):
        completed = runner(spec.command, cwd=ROOT, check=False)
        records.append(command_record(spec, "passed" if completed.returncode == 0 else "failed", completed.returncode))
        if completed.returncode != 0:
            failed_command = spec.command_id
            for skipped in commands[index + 1 :]:
                records.append(command_record(skipped, "skipped"))
            break
    return {
        "ok": failed_command is None,
        "mode": "executed" if failed_command is None else "failed",
        "commands": records,
        "failed_command": failed_command,
    }


def build_report(args: argparse.Namespace, sequence: dict[str, Any]) -> dict[str, Any]:
    next_actions = [
        "If mode is plan_only, rerun with --execute after credentials are entered locally.",
        "If live proof succeeds, record and upload the final public demo video.",
        "After the public video is verified, run the final secret scan, strict audit, Devpost submit, and receipt capture.",
    ]
    if sequence.get("failed_command") == "credential_handoff":
        next_actions.insert(
            0,
            "Enter missing local credentials with python scripts/final_env_wizard.py --output .env.final.local --missing-only --force.",
        )
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": sequence["ok"],
        "mode": sequence["mode"],
        "env_file": rel(args.env_file),
        "update_tasks": bool(args.update_tasks),
        "execute": bool(args.execute),
        "commands": sequence["commands"],
        "failed_command": sequence["failed_command"],
        "next_actions": next_actions,
        "secret_policy": (
            "This report stores command strings, statuses, and artifact paths only. It never stores "
            "Backblaze keys, Genblaze/GMI keys, Devpost cookies, provider responses, or signed URLs."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Post-Credential Live Proof Plan",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Env file: `{report['env_file']}`",
        f"Update tasks: `{str(report['update_tasks']).lower()}`",
        "",
        report["secret_policy"],
        "",
        "## Commands",
        "",
        "| Status | ID | Command |",
        "| --- | --- | --- |",
    ]
    for command in report["commands"]:
        lines.append(f"| {command['status'].upper()} | `{command['id']}` | `{command['command']}` |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or run the post-credential ProofFrame live proof sequence."
    )
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--execute", action="store_true", help="Run the live proof sequence.")
    parser.add_argument(
        "--update-tasks",
        action="store_true",
        help="Mark T020/T021 done after their proof commands pass.",
    )
    parser.add_argument(
        "--validate-evidence",
        choices=sorted(EXPECTED_EVIDENCE_FIELDS),
        help="Internal fail-closed evidence validator used before task updates.",
    )
    parser.add_argument("--evidence-path", type=Path, help="Evidence JSON path for --validate-evidence.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.validate_evidence:
        evidence_path = args.evidence_path
        if evidence_path is None:
            evidence_path = B2_EVIDENCE if args.validate_evidence == "b2" else FINAL_EVIDENCE
        report = validate_evidence(args.validate_evidence, evidence_path)
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report["ok"] else 2)

    commands = build_commands(env_file=args.env_file, update_tasks=args.update_tasks)
    sequence = run_sequence(commands, execute=args.execute)
    report = build_report(args, sequence)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "failed_command": report["failed_command"],
                "commands": len(report["commands"]),
            },
            indent=2,
        )
    )
    if args.execute and not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
