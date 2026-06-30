#!/usr/bin/env python3
"""Upload the public ProofFrame bundle to Hugging Face Space without local secrets."""

from __future__ import annotations

import argparse
import fnmatch
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "public-space-upload-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "public-space-upload-report.md"
SCHEMA = "proofframe.public_space_upload.v1"
SPACE_ID = "ADJCJH/backblaze-proofframe"
DEFAULT_COMMIT_MESSAGE = "Sync ProofFrame public Space"

IGNORE_PATTERNS = [
    ".git/**",
    ".venv/**",
    "__pycache__/**",
    "**/__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
    ".ruff_cache/**",
    ".mypy_cache/**",
    ".DS_Store",
    "var/**",
    "dist/**",
    "build/**",
    "node_modules/**",
    ".env",
    ".env.local",
    ".env.final.local",
    ".env.*.local",
]

REQUIRED_IGNORE_PATTERNS = {
    ".git/**",
    ".venv/**",
    ".env",
    ".env.local",
    ".env.final.local",
    ".env.*.local",
    "var/**",
    "node_modules/**",
}

SENSITIVE_PATHS = [
    ".env",
    ".env.local",
    ".env.final.local",
    ".env.production.local",
]

Uploader = Callable[..., Any]
SecretProbe = Callable[[str, int], dict[str, Any]]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path(path: Path) -> str:
    return path.as_posix()


def matches_pattern(relative_path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return relative_path == prefix or relative_path.startswith(prefix + "/")
    return fnmatch.fnmatch(relative_path, pattern)


def is_ignored(relative_path: str, patterns: list[str]) -> bool:
    return any(matches_pattern(relative_path, pattern) for pattern in patterns)


def walk_files(root: Path) -> list[str]:
    files: list[str] = []
    for path in root.rglob("*"):
        if path.is_file():
            files.append(normalize_path(path.relative_to(root)))
    return sorted(files)


def classify_files(root: Path, patterns: list[str]) -> dict[str, Any]:
    files = walk_files(root)
    included = [path for path in files if not is_ignored(path, patterns)]
    excluded = [path for path in files if is_ignored(path, patterns)]
    sensitive = [
        {
            "path": path,
            "present": (root / path).exists(),
            "excluded": is_ignored(path, patterns),
        }
        for path in SENSITIVE_PATHS
    ]
    included_sensitive = [
        item["path"] for item in sensitive if item["present"] and not item["excluded"]
    ]
    return {
        "total_files": len(files),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "included_samples": included[:20],
        "excluded_samples": excluded[:20],
        "sensitive_files": sensitive,
        "included_sensitive": included_sensitive,
    }


def required_ignore_check(patterns: list[str]) -> dict[str, Any]:
    missing = sorted(REQUIRED_IGNORE_PATTERNS - set(patterns))
    return {
        "ok": not missing,
        "missing_patterns": missing,
        "required_patterns": sorted(REQUIRED_IGNORE_PATTERNS),
    }


def default_raw_base(repo_id: str, revision: str) -> str:
    return f"https://huggingface.co/spaces/{repo_id}/raw/{revision}"


def probe_raw_secret(space_raw_base: str, timeout: int = 20) -> dict[str, Any]:
    url = f"{space_raw_base.rstrip('/')}/.env.final.local"
    request = Request(url, headers={"User-Agent": "ProofFrame public Space upload verifier"})
    try:
        with urlopen(request, timeout=timeout) as response:
            response.read(128)
            return {"ok": False, "status": response.status, "url": url}
    except HTTPError as error:
        return {"ok": error.code == 404, "status": error.code, "url": url}
    except (TimeoutError, URLError) as error:
        return {"ok": False, "status": None, "url": url, "error": str(error)}


def upload_folder(
    *,
    root: Path,
    repo_id: str,
    repo_type: str,
    revision: str,
    commit_message: str,
    ignore_patterns: list[str],
) -> dict[str, Any]:
    try:
        from huggingface_hub import HfApi
    except ImportError as error:
        return {"ok": False, "error": f"huggingface_hub is not installed: {error}"}
    info = HfApi().upload_folder(
        folder_path=str(root),
        repo_id=repo_id,
        repo_type=repo_type,
        revision=revision,
        commit_message=commit_message,
        ignore_patterns=ignore_patterns,
    )
    commit_url = getattr(info, "commit_url", None)
    commit_oid = getattr(info, "oid", None) or getattr(info, "commit_oid", None)
    return {"ok": bool(commit_url or commit_oid), "commit_url": commit_url, "commit_oid": commit_oid}


def build_report(
    *,
    root: Path = ROOT,
    repo_id: str = SPACE_ID,
    repo_type: str = "space",
    revision: str = "main",
    commit_message: str = DEFAULT_COMMIT_MESSAGE,
    execute: bool = False,
    skip_secret_probe: bool = False,
    space_raw_base: str | None = None,
    ignore_patterns: list[str] | None = None,
    uploader: Uploader | None = None,
    secret_probe: SecretProbe = probe_raw_secret,
) -> dict[str, Any]:
    root = root.resolve()
    patterns = list(ignore_patterns or IGNORE_PATTERNS)
    raw_base = space_raw_base or default_raw_base(repo_id, revision)
    file_plan = classify_files(root, patterns)
    ignore_check = required_ignore_check(patterns)
    safety_ok = bool(ignore_check["ok"] and not file_plan["included_sensitive"])
    upload: dict[str, Any] = {"attempted": False, "ok": None}
    secret_probe_report: dict[str, Any] = {"attempted": False, "ok": None}

    if execute and safety_ok:
        upload_runner = uploader or upload_folder
        upload = {
            "attempted": True,
            **upload_runner(
                root=root,
                repo_id=repo_id,
                repo_type=repo_type,
                revision=revision,
                commit_message=commit_message,
                ignore_patterns=patterns,
            ),
        }
        if upload.get("ok") and not skip_secret_probe:
            secret_probe_report = {"attempted": True, **secret_probe(raw_base, 20)}
        elif skip_secret_probe:
            secret_probe_report = {"attempted": False, "ok": None, "skipped": True}
    elif execute:
        upload = {
            "attempted": False,
            "ok": False,
            "error": "Refusing upload because the no-secret safety preflight failed.",
        }

    ok = bool(
        safety_ok
        and (not execute or (upload.get("ok") and secret_probe_report.get("ok") is not False))
    )
    if not safety_ok:
        mode = "blocked"
    elif not execute:
        mode = "dry_run_ready"
    elif not upload.get("ok"):
        mode = "upload_failed"
    elif secret_probe_report.get("ok") is False:
        mode = "post_upload_secret_probe_failed"
    else:
        mode = "uploaded"
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": mode,
        "ok": ok,
        "execute": execute,
        "repo_id": repo_id,
        "repo_type": repo_type,
        "revision": revision,
        "space_raw_base": raw_base,
        "commit_message": commit_message,
        "ignore_patterns": patterns,
        "ignore_check": ignore_check,
        "file_plan": file_plan,
        "upload": upload,
        "secret_probe": secret_probe_report,
        "next_commands": [
            "python scripts/public_space_upload.py --execute --commit-message \"Sync ProofFrame public Space\"",
            "python scripts/public_space_sync.py",
            "python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space",
        ],
        "secret_policy": (
            "This uploader excludes local env files, git state, virtualenvs, caches, runtime output, "
            "and node_modules before calling Hugging Face. It records file names and commit metadata only, "
            "never credential values."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    upload = report["upload"]
    file_plan = report["file_plan"]
    lines = [
        "# ProofFrame Public Space Upload Report",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Execute: `{str(report['execute']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Repo: `{report['repo_id']}`",
        f"Revision: `{report['revision']}`",
        f"Raw base: {report['space_raw_base']}",
        "",
        "## Safety",
        "",
        f"- Required ignore patterns OK: `{str(report['ignore_check']['ok']).lower()}`",
        f"- Included files: `{file_plan['included_count']}`",
        f"- Excluded files: `{file_plan['excluded_count']}`",
        f"- Included sensitive files: `{', '.join(file_plan['included_sensitive']) or 'none'}`",
        "",
        "## Sensitive File Checks",
        "",
    ]
    for item in file_plan["sensitive_files"]:
        marker = "OK" if item["excluded"] else "BLOCKED"
        present = "present" if item["present"] else "absent"
        lines.append(f"- {marker} `{item['path']}` is {present}; excluded `{str(item['excluded']).lower()}`.")
    lines.extend(["", "## Upload", ""])
    if upload.get("attempted"):
        lines.append(f"- Upload OK: `{str(upload.get('ok')).lower()}`")
        if upload.get("commit_oid"):
            lines.append(f"- Commit: `{upload['commit_oid']}`")
        if upload.get("commit_url"):
            lines.append(f"- Commit URL: {upload['commit_url']}")
        if upload.get("error"):
            lines.append(f"- Error: {upload['error']}")
    else:
        lines.append("- Upload not attempted.")
    lines.extend(["", "## Secret Probe", ""])
    probe = report["secret_probe"]
    if probe.get("attempted"):
        lines.append(f"- Raw `.env.final.local` public check OK: `{str(probe.get('ok')).lower()}`")
        lines.append(f"- Status: `{probe.get('status')}`")
    elif probe.get("skipped"):
        lines.append("- Secret probe skipped by operator flag.")
    else:
        lines.append("- Secret probe not attempted.")
    lines.extend(["", "## Next Commands", ""])
    lines.extend(f"```bash\n{command}\n```" for command in report["next_commands"])
    lines.extend(["", report["secret_policy"], ""])
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upload ProofFrame public artifacts to Hugging Face Space.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--repo-id", default=SPACE_ID)
    parser.add_argument("--repo-type", default="space")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--commit-message", default=DEFAULT_COMMIT_MESSAGE)
    parser.add_argument("--execute", action="store_true", help="Actually upload to Hugging Face.")
    parser.add_argument("--skip-secret-probe", action="store_true")
    parser.add_argument("--space-raw-base", help="Override the raw public Space URL base for probing.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(
        root=args.root,
        repo_id=args.repo_id,
        repo_type=args.repo_type,
        revision=args.revision,
        commit_message=args.commit_message,
        execute=args.execute,
        skip_secret_probe=args.skip_secret_probe,
        space_raw_base=args.space_raw_base,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "execute": report["execute"],
                "commit_oid": report["upload"].get("commit_oid"),
                "included_sensitive": report["file_plan"]["included_sensitive"],
                "secret_probe_ok": report["secret_probe"].get("ok"),
            },
            indent=2,
        )
    )
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
