#!/usr/bin/env python3
"""Fail-closed secret scanner for public submission artifacts and local logs."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.secret_scan.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "secret-scan-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "secret-scan-report.md"
HARD_SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
LOCAL_SECRET_FILES = {
    ".env",
    ".env.local",
    ".env.final.local",
}
TEXT_EXTENSIONS = {
    ".css",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".log",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}
BINARY_REVIEW_EXTENSIONS = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".pdf",
    ".png",
    ".webm",
    ".webp",
    ".zip",
}


class Pattern(NamedTuple):
    pattern_id: str
    label: str
    regex: re.Pattern[str]


PATTERNS = [
    Pattern("aws_access_key", "AWS-style access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    Pattern(
        "assigned_secret",
        "Assigned API key, application key, token, cookie, or secret",
        re.compile(
            r"(?i)['\"]?(api[_-]?key|application[_-]?key|secret|token|cookie)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"
        ),
    ),
    Pattern(
        "bearer_token",
        "Bearer authorization token",
        re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{20,}"),
    ),
    Pattern("gmi_key", "GMI/Genblaze-style key", re.compile(r"(?i)gmi-[A-Za-z0-9_\-]{16,}")),
    Pattern(
        "signed_url_signature",
        "S3/B2 signed URL signature",
        re.compile(r"(?i)(x-amz-signature|x-bz-signature|X-Amz-Signature)=[A-Fa-f0-9]{32,}"),
    ),
    Pattern(
        "aws_query_credential",
        "AWS/B2 S3 signed URL credential",
        re.compile(r"(?i)(AWSAccessKeyId|X-Amz-Credential)=[^&\\s]{12,}"),
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def is_hard_skipped(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part in HARD_SKIP_DIRS for part in parts)


def is_local_secret_file(path: Path) -> bool:
    return path.name in LOCAL_SECRET_FILES


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".env.example", "Dockerfile"}


def is_binary_review_file(path: Path) -> bool:
    return path.suffix.lower() in BINARY_REVIEW_EXTENSIONS


def should_scan(path: Path, root: Path = ROOT) -> bool:
    if is_hard_skipped(path, root) or is_local_secret_file(path):
        return False
    return is_text_file(path)


def line_is_placeholder(line: str) -> bool:
    stripped = line.strip()
    lowered = stripped.lower()
    return (
        not stripped
        or "placeholder" in lowered
        or "redacted" in lowered
        or stripped.endswith("=")
        or stripped.endswith('=""')
        or stripped.endswith("=''")
    )


def finding(path: Path, root: Path, line_number: int, pattern: Pattern) -> dict[str, Any]:
    return {
        "path": display_path(path, root),
        "line": line_number,
        "pattern": pattern.pattern_id,
        "label": pattern.label,
        "detail": "Potential secret-like value detected. Line content is intentionally not stored.",
    }


def scan_path(path: Path, root: Path = ROOT) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line_is_placeholder(line):
            continue
        for pattern in PATTERNS:
            if pattern.regex.search(line):
                findings.append(finding(path, root, line_number, pattern))
                break
    return findings


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def collect_scan(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    text_files: list[str] = []
    binary_review_files: list[dict[str, Any]] = []
    skipped_local_secret_files: list[str] = []
    skipped_hard_files = 0
    findings: list[dict[str, Any]] = []

    for path in iter_files(root):
        if is_hard_skipped(path, root):
            skipped_hard_files += 1
            continue
        if is_local_secret_file(path):
            skipped_local_secret_files.append(display_path(path, root))
            continue
        if is_text_file(path):
            text_files.append(display_path(path, root))
            findings.extend(scan_path(path, root))
            continue
        if is_binary_review_file(path):
            binary_review_files.append(
                {
                    "path": display_path(path, root),
                    "bytes": path.stat().st_size,
                    "review": "inventoried_binary_media",
                }
            )

    docs_assets_scanned = [path for path in text_files if path.startswith("docs/assets/")]
    var_logs_scanned = [path for path in text_files if path.startswith("var/")]
    screenshot_inventory = [
        item for item in binary_review_files if item["path"].startswith("docs/assets/") and item["path"].lower().endswith(".png")
    ]
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "clear" if not findings else "findings_detected",
        "ok": not findings,
        "root": ".",
        "findings": findings,
        "counts": {
            "scanned_text_files": len(text_files),
            "inventoried_binary_files": len(binary_review_files),
            "skipped_local_secret_files": len(skipped_local_secret_files),
            "skipped_hard_files": skipped_hard_files,
            "findings": len(findings),
        },
        "coverage": {
            "public_text_files_scanned": True,
            "docs_assets_text_files_scanned": bool(docs_assets_scanned),
            "var_log_text_files_scanned": bool(var_logs_scanned),
            "screenshot_binary_inventory": bool(screenshot_inventory),
            "local_secret_files_excluded_without_reading": skipped_local_secret_files,
            "notes": [
                "Text files are scanned for key-like assignments, bearer tokens, signed URL parameters, and GMI-style keys.",
                "Binary screenshots/media are inventoried by path and size; review visible content before marking final T041A done.",
                "Local credential files such as .env.final.local are intentionally excluded without reading values.",
            ],
        },
        "scanned_text_files": text_files,
        "binary_review_files": binary_review_files,
    }


def run_scan(root: Path = ROOT) -> list[str]:
    report = collect_scan(root)
    return [
        f"{item['path']}:{item['line']}: possible secret ({item['pattern']})"
        for item in report["findings"]
    ]


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    coverage = report["coverage"]
    lines = [
        "# ProofFrame Secret Scan Report",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        "",
        "## Counts",
        "",
        f"- Scanned text files: `{counts['scanned_text_files']}`",
        f"- Inventoried binary files: `{counts['inventoried_binary_files']}`",
        f"- Skipped local secret files: `{counts['skipped_local_secret_files']}`",
        f"- Findings: `{counts['findings']}`",
        "",
        "## Coverage",
        "",
        f"- Docs/assets text scanned: `{str(coverage['docs_assets_text_files_scanned']).lower()}`",
        f"- Var/log text scanned: `{str(coverage['var_log_text_files_scanned']).lower()}`",
        f"- Screenshot/media inventory: `{str(coverage['screenshot_binary_inventory']).lower()}`",
        f"- Local secret files excluded without reading: `{', '.join(coverage['local_secret_files_excluded_without_reading']) or 'none'}`",
        "",
    ]
    for note in coverage["notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for item in report["findings"]:
            lines.append(
                f"- `{item['path']}:{item['line']}` {item['label']} ({item['pattern']})"
            )
    else:
        lines.append("- None")
    lines.extend(["", "No credential values, matched line text, browser cookies, or signed URLs are printed in this report."])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan public ProofFrame files for obvious secrets.")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Only print legacy scan output; do not write JSON/Markdown reports.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = collect_scan(ROOT)
    if not args.no_report:
        write_outputs(report, args.json_out, args.markdown_out)
    if report["findings"]:
        print(
            "\n".join(
                f"{item['path']}:{item['line']}: possible secret ({item['pattern']})"
                for item in report["findings"]
            )
        )
        raise SystemExit(1)
    if not args.quiet:
        if args.no_report:
            print("No obvious secrets found.")
        else:
            print(
                json.dumps(
                    {
                        "ok": report["ok"],
                        "mode": report["mode"],
                        "json": str(args.json_out),
                        "markdown": str(args.markdown_out),
                        "scanned_text_files": report["counts"]["scanned_text_files"],
                        "inventoried_binary_files": report["counts"]["inventoried_binary_files"],
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    main()
