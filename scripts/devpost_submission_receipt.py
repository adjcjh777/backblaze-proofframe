#!/usr/bin/env python3
"""Create a public-safe Devpost final submission receipt."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.devpost_submission_receipt.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-submission-receipt.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-submission-receipt.md"
SAFE_QUERY_KEYS = {"ref_content", "ref_feature", "utm_source", "utm_medium", "utm_campaign"}
SECRET_QUERY_RE = re.compile(r"(?i)(token|cookie|key|secret|signature|session|auth|credential)")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def is_placeholder(value: str | None) -> bool:
    text = normalize_text(value).lower()
    return not text or text.startswith(("tbd", "<", "pending", "todo"))


def parse_submitted_at(value: str | None) -> tuple[str | None, str | None]:
    if is_placeholder(value):
        return None, "Submitted timestamp is missing."
    text = normalize_text(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None, "Submitted timestamp must be ISO-8601, for example 2026-08-03T21:00:00Z."
    if parsed.tzinfo is None:
        return None, "Submitted timestamp must include a timezone."
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), None


def validate_project_url(value: str | None) -> tuple[str | None, list[str]]:
    if is_placeholder(value):
        return None, ["Public Devpost project URL is missing."]
    text = normalize_text(value)
    parsed = urlparse(text)
    findings: list[str] = []
    if parsed.scheme != "https":
        findings.append("Devpost project URL must use https.")
    if parsed.netloc.lower() != "devpost.com":
        findings.append("Devpost project URL must use devpost.com.")
    if not parsed.path.startswith("/software/") or len(parsed.path.rstrip("/").split("/")) < 3:
        findings.append("Devpost project URL must point to /software/<project-slug>.")
    if parsed.username or parsed.password or parsed.fragment:
        findings.append("Devpost project URL must not include userinfo or fragments.")
    query_keys = {key for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    unsafe_query = sorted(key for key in query_keys if key not in SAFE_QUERY_KEYS or SECRET_QUERY_RE.search(key))
    if unsafe_query:
        findings.append("Devpost project URL contains unsafe query parameters: " + ", ".join(unsafe_query))
    clean_url = parsed._replace(query="", fragment="").geturl().rstrip("/")
    return clean_url, findings


def validate_confirmation(value: str | None) -> tuple[str | None, str | None]:
    text = normalize_text(value)
    if len(text) < 10:
        return None, "Confirmation note should briefly state that Devpost accepted/submitted the project."
    if SECRET_QUERY_RE.search(text):
        return None, "Confirmation note must not contain token/cookie/key/session-like text."
    return text, None


def validate_screenshot(root: Path, value: str | None) -> tuple[str | None, str | None]:
    if is_placeholder(value):
        return None, None
    path = Path(normalize_text(value))
    if path.is_absolute():
        try:
            relative = path.resolve().relative_to(root.resolve())
        except ValueError:
            return None, "Screenshot path must stay inside the project."
    else:
        relative = path
    if not str(relative).startswith("docs/assets/"):
        return None, "Screenshot path must be under docs/assets/."
    if relative.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None, "Screenshot must be a png, jpg, jpeg, or webp file."
    if not (root / relative).exists():
        return None, "Screenshot path does not exist."
    return str(relative), None


def build_receipt(
    *,
    root: Path = ROOT,
    project_url: str | None = None,
    submitted_at: str | None = None,
    confirmation_note: str | None = None,
    screenshot: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    clean_url, url_findings = validate_project_url(project_url)
    clean_submitted_at, submitted_error = parse_submitted_at(submitted_at)
    clean_confirmation, confirmation_error = validate_confirmation(confirmation_note)
    clean_screenshot, screenshot_error = validate_screenshot(root, screenshot)

    findings: list[dict[str, str]] = []
    findings.extend({"field": "project_url", "detail": detail} for detail in url_findings)
    if submitted_error:
        findings.append({"field": "submitted_at", "detail": submitted_error})
    if confirmation_error:
        findings.append({"field": "confirmation_note", "detail": confirmation_error})
    if screenshot_error:
        findings.append({"field": "screenshot", "detail": screenshot_error})

    ok = not findings
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "submitted" if ok else "pending_submission",
        "ok": ok,
        "project": "ProofFrame",
        "event": "Backblaze Generative Media Hackathon",
        "project_url": clean_url,
        "submitted_at": clean_submitted_at,
        "confirmation_note": clean_confirmation,
        "screenshot": clean_screenshot,
        "findings": findings,
        "secret_policy": "Receipt stores only public Devpost URL, timestamp, and confirmation text; no cookies, browser sessions, tokens, or private form data.",
        "next_actions": [
            "Submit the project in Devpost after strict final gates are green.",
            'Run python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."',
            "Mark T042 done only after this receipt is ok.",
            "Rerun python scripts/final_submission_control.py --strict-final.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Devpost Submission Receipt",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Project URL: {report['project_url'] or '`pending`'}",
        f"Submitted at: `{report['submitted_at'] or 'pending'}`",
        "",
        report["secret_policy"],
        "",
        "## Confirmation",
        "",
        report["confirmation_note"] or "Pending final Devpost submission.",
        "",
        "## Findings",
        "",
    ]
    if report["findings"]:
        lines.extend(f"- `{item['field']}`: {item['detail']}" for item in report["findings"])
    else:
        lines.append("- None")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a public-safe Devpost submission receipt.")
    parser.add_argument("--project-url", help="Public Devpost /software/<slug> URL after final submission.")
    parser.add_argument("--submitted-at", help="ISO-8601 submitted timestamp, for example 2026-08-03T21:00:00Z.")
    parser.add_argument("--confirmation-note", help="Short public-safe confirmation note.")
    parser.add_argument("--screenshot", help="Optional public-safe screenshot under docs/assets/.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Exit nonzero unless the receipt is complete.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_receipt(
        project_url=args.project_url,
        submitted_at=args.submitted_at,
        confirmation_note=args.confirmation_note,
        screenshot=args.screenshot,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "project_url": report["project_url"],
                "findings": len(report["findings"]),
            },
            indent=2,
        )
    )
    if args.strict_final and not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
