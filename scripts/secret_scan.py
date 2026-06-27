#!/usr/bin/env python3
"""Small fail-closed secret scanner for public submission artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "var",
}
TEXT_EXTENSIONS = {
    ".css",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}
PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|application[_-]?key|secret|token|cookie)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)gmi-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)x-amz-signature=[A-Fa-f0-9]{32,}"),
]


def should_scan(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name in {".env.example", "Dockerfile"}


def scan_path(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "placeholder" in line.lower() or line.strip().endswith("="):
            continue
        for pattern in PATTERNS:
            if pattern.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: possible secret")
                break
    return findings


def run_scan() -> list[str]:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and should_scan(path):
            findings.extend(scan_path(path))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan public ProofFrame files for obvious secrets.")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    findings = run_scan()
    if findings:
        print("\n".join(findings))
        raise SystemExit(1)
    if not args.quiet:
        print("No obvious secrets found.")


if __name__ == "__main__":
    main()
