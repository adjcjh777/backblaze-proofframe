#!/usr/bin/env python3
"""Build a redacted live credential handoff report."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "live-credential-handoff.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "live-credential-handoff.md"

PLACEHOLDERS = {"", "placeholder", "change-me", "changeme", "todo", "tbd", "none", "null", "..."}

REQUIRED_GROUPS = [
    {
        "id": "storage_backend_mode",
        "label": "ProofFrame storage backend mode",
        "accepted_names": ["PROOFFRAME_STORAGE_BACKEND"],
        "expected": "b2",
        "remediation": "Set PROOFFRAME_STORAGE_BACKEND=b2.",
    },
    {
        "id": "generation_backend_mode",
        "label": "ProofFrame generation backend mode",
        "accepted_names": ["PROOFFRAME_GENERATION_BACKEND"],
        "expected": "genblaze",
        "remediation": "Set PROOFFRAME_GENERATION_BACKEND=genblaze.",
    },
    {
        "id": "b2_endpoint",
        "label": "Backblaze B2 S3 endpoint",
        "accepted_names": ["B2_ENDPOINT_URL", "B2_S3_ENDPOINT_URL"],
        "remediation": "Set B2_ENDPOINT_URL from the Backblaze bucket S3 endpoint.",
    },
    {
        "id": "b2_bucket",
        "label": "Backblaze B2 bucket",
        "accepted_names": ["B2_BUCKET"],
        "remediation": "Set B2_BUCKET to the dedicated demo bucket name.",
    },
    {
        "id": "b2_key_id",
        "label": "Backblaze B2 key id",
        "accepted_names": ["B2_KEY_ID"],
        "remediation": "Set B2_KEY_ID for a least-privilege application key.",
    },
    {
        "id": "b2_application_key",
        "label": "Backblaze B2 application key",
        "accepted_names": ["B2_APPLICATION_KEY", "B2_APP_KEY"],
        "remediation": "Set B2_APPLICATION_KEY or B2_APP_KEY.",
    },
    {
        "id": "genblaze_api_key",
        "label": "Genblaze/GMI API key",
        "accepted_names": ["GENBLAZE_API_KEY", "GMI_API_KEY"],
        "remediation": "Set GENBLAZE_API_KEY or GMI_API_KEY.",
    },
    {
        "id": "genblaze_image_model",
        "label": "Genblaze image model",
        "accepted_names": ["GENBLAZE_IMAGE_MODEL"],
        "remediation": "Set GENBLAZE_IMAGE_MODEL to the verified image model.",
    },
]

OPTIONAL_GROUPS = [
    {
        "id": "b2_public_base_url",
        "label": "B2 public base URL",
        "accepted_names": ["B2_PUBLIC_BASE_URL"],
    },
    {
        "id": "genblaze_aspect_ratio",
        "label": "Genblaze aspect ratio",
        "accepted_names": ["GENBLAZE_ASPECT_RATIO"],
    },
    {
        "id": "genblaze_timeout",
        "label": "Genblaze timeout seconds",
        "accepted_names": ["GENBLAZE_TIMEOUT_SECONDS"],
    },
]

NEXT_COMMANDS = [
    "python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local",
    "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
    "python scripts/live_env_handoff.py --env-file .env.final.local",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
    'python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"',
    "python scripts/secret_scan.py",
    "python scripts/claim_lint.py",
    "python scripts/submission_audit.py --strict-final",
]


def normalize_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


def has_real_value(value: str | None) -> bool:
    normalized = normalize_value(value)
    if normalized.lower() in PLACEHOLDERS:
        return False
    if normalized.startswith("<") and normalized.endswith(">"):
        return False
    return bool(normalized)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        if key:
            values[key] = normalize_value(value)
    return values


def env_source(env_file: Path | None) -> tuple[dict[str, str], str]:
    values = {key: value for key, value in os.environ.items()}
    source = "process environment"
    if env_file:
        file_values = parse_env_file(env_file)
        values.update(file_values)
        source = str(env_file)
    return values, source


def evaluate_group(group: dict[str, Any], values: dict[str, str]) -> dict[str, Any]:
    present_names = [name for name in group["accepted_names"] if has_real_value(values.get(name))]
    expected = group.get("expected")
    expected_ok = True
    if expected is not None:
        expected_ok = any(normalize_value(values.get(name)).lower() == expected for name in present_names)
    ok = bool(present_names) and expected_ok
    return {
        "id": group["id"],
        "label": group["label"],
        "ok": ok,
        "accepted_names": group["accepted_names"],
        "present_names": present_names,
        "expected": expected,
        "remediation": "" if ok else group.get("remediation", ""),
    }


def build_report(env_file: Path | None = None) -> dict[str, Any]:
    values, source = env_source(env_file)
    required = [evaluate_group(group, values) for group in REQUIRED_GROUPS]
    optional = [evaluate_group(group, values) for group in OPTIONAL_GROUPS]
    missing = [item for item in required if not item["ok"]]
    return {
        "schema": "proofframe.live_credential_handoff.v1",
        "ok": not missing,
        "mode": "live_env_ready" if not missing else "missing_live_env",
        "source": source,
        "required": required,
        "optional": optional,
        "missing_ids": [item["id"] for item in missing],
        "next_commands": NEXT_COMMANDS,
        "secret_policy": (
            "This report records only variable names and presence checks. It never prints, hashes, "
            "stores, or commits credential values."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Live Credential Handoff",
        "",
        f"Mode: `{report['mode']}`",
        f"Ready for live proof: `{str(report['ok']).lower()}`",
        f"Source: `{report['source']}`",
        "",
        report["secret_policy"],
        "",
        "## Required Values",
        "",
    ]
    for item in report["required"]:
        marker = "OK" if item["ok"] else "MISSING"
        names = ", ".join(f"`{name}`" for name in item["accepted_names"])
        present = ", ".join(f"`{name}`" for name in item["present_names"]) or "none"
        expected = f"; expected `{item['expected']}`" if item["expected"] else ""
        lines.append(f"- {marker} {item['label']}: {names}; present {present}{expected}.")
        if item["remediation"]:
            lines.append(f"  Remediation: {item['remediation']}")

    lines.extend(["", "## Optional Values", ""])
    for item in report["optional"]:
        marker = "SET" if item["present_names"] else "UNSET"
        names = ", ".join(f"`{name}`" for name in item["accepted_names"])
        present = ", ".join(f"`{name}`" for name in item["present_names"]) or "none"
        lines.append(f"- {marker} {item['label']}: {names}; present {present}.")

    lines.extend(["", "## Next Commands", ""])
    lines.extend(f"```bash\n{command}\n```" for command in report["next_commands"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a redacted ProofFrame live credential handoff report."
    )
    parser.add_argument("--env-file", type=Path, help="Optional local env file; values are not printed.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when required live variables are missing.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.env_file)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "missing_ids": report["missing_ids"],
            },
            indent=2,
        )
    )
    if args.strict and not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
