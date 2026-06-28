#!/usr/bin/env python3
"""Capture and verify the public judge-mode demo screenshot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.public_demo_screenshot.v1"
PUBLIC_JUDGE_URL = "https://adjcjh-backblaze-proofframe.hf.space/?judge=1"
DEFAULT_SCREENSHOT = ROOT / "docs" / "assets" / "proofframe-hf-public-smoke.png"
DEFAULT_JSON = ROOT / "docs" / "assets" / "public-demo-screenshot-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "public-demo-screenshot-report.md"
VIEWPORT = {"width": 1440, "height": 1200}

VISIBLE_MARKERS = {
    "proof_frame_title": "ProofFrame",
    "sponsor_evidence_model": "Sponsor Evidence Model",
    "final_reports_pending": "Final reports pending",
    "recording_runbook": "Recording Runbook",
    "criteria_crosswalk": "Criteria Crosswalk",
    "devpost_kit": "Devpost Kit",
    "submit_checklist": "Submit Checklist",
    "judge_brief": "30-Second Judge Brief",
    "local_storage": "local / B2 pending",
    "mock_generation": "mock / Genblaze pending",
}

HTML_MARKERS = {
    "judge_recording_slate": "Judge recording slate",
    "auto_load_judge_demo": "shouldAutoLoadJudgeDemo",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def marker_report(body_text: str, html_text: str) -> dict[str, Any]:
    visible = {
        marker_id: {"needle": needle, "present": needle in body_text}
        for marker_id, needle in VISIBLE_MARKERS.items()
    }
    html = {
        marker_id: {"needle": needle, "present": needle in html_text}
        for marker_id, needle in HTML_MARKERS.items()
    }
    return {
        "visible": visible,
        "html": html,
        "visible_ok": all(item["present"] for item in visible.values()),
        "html_ok": all(item["present"] for item in html.values()),
    }


def image_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"present": False, "path": rel(path), "ok": False}
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        return {
            "present": True,
            "path": rel(path),
            "ok": False,
            "error": f"Pillow is required for image verification: {exc}",
        }

    with Image.open(path) as image:
        grayscale = image.convert("L")
        stat = ImageStat.Stat(grayscale)
        width, height = image.size
    return {
        "present": True,
        "path": rel(path),
        "ok": width >= 1200 and height >= 900 and path.stat().st_size > 100_000 and stat.stddev[0] > 10,
        "bytes": path.stat().st_size,
        "width": width,
        "height": height,
        "luma_mean": round(float(stat.mean[0]), 2),
        "luma_stddev": round(float(stat.stddev[0]), 2),
    }


def capture_public_demo(url: str, screenshot_path: Path) -> dict[str, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(f"Playwright is required for screenshot capture: {exc}") from exc

    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto(url, wait_until="networkidle", timeout=60_000)
        for marker in VISIBLE_MARKERS.values():
            page.wait_for_selector(f"text={marker}", timeout=30_000)
        page.wait_for_function(
            "() => document.documentElement.innerHTML.includes('Judge recording slate')",
            timeout=30_000,
        )
        page.screenshot(path=str(screenshot_path), full_page=True)
        body_text = page.locator("body").inner_text(timeout=10_000)
        html_text = page.content()
        browser.close()
    return {"body_text": body_text, "html_text": html_text}


def build_report(
    *,
    url: str,
    screenshot_path: Path,
    body_text: str,
    html_text: str,
) -> dict[str, Any]:
    markers = marker_report(body_text, html_text)
    screenshot = image_record(screenshot_path)
    ok = bool(markers["visible_ok"] and markers["html_ok"] and screenshot.get("ok"))
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "public_judge_screenshot_ready" if ok else "public_judge_screenshot_blocked",
        "ok": ok,
        "safe_to_commit": True,
        "url": url,
        "screenshot": screenshot,
        "viewport": VIEWPORT,
        "markers": markers,
        "claim_boundary": (
            "This screenshot verifies the public local/mock judge demo view only. It does not "
            "prove live B2 storage, live Genblaze generation, final video readiness, or Devpost submission."
        ),
        "secret_policy": {
            "public_url_only": True,
            "no_login": True,
            "no_cookies_recorded": True,
            "no_secret_values_recorded": True,
        },
        "next_actions": [
            "Use this screenshot as the public mock demo visual evidence before live proof.",
            "After live B2 and Genblaze proof, record the final public video and run strict final gates.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    screenshot = report["screenshot"]
    lines = [
        "# ProofFrame Public Demo Screenshot",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Safe to commit: `{str(report['safe_to_commit']).lower()}`",
        f"URL: {report['url']}",
        f"Screenshot: `{screenshot.get('path')}`",
        "",
        "## Image Check",
        "",
        f"- Present: `{str(screenshot.get('present')).lower()}`",
        f"- Bytes: `{screenshot.get('bytes')}`",
        f"- Size: `{screenshot.get('width')}x{screenshot.get('height')}`",
        f"- Luma mean/stddev: `{screenshot.get('luma_mean')}` / `{screenshot.get('luma_stddev')}`",
        "",
        "## Markers",
        "",
    ]
    for group_name in ["visible", "html"]:
        lines.append(f"### {group_name.title()}")
        for marker_id, marker in report["markers"][group_name].items():
            label = "OK" if marker["present"] else "MISSING"
            lines.append(f"- {label} `{marker_id}`: `{marker['needle']}`")
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            report["claim_boundary"],
            "",
            "No credentials, cookies, signed URLs, account dashboards, or provider keys are captured.",
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture the public ProofFrame judge screenshot.")
    parser.add_argument("--url", default=PUBLIC_JUDGE_URL)
    parser.add_argument("--screenshot-out", type=Path, default=DEFAULT_SCREENSHOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict", action="store_true", help="Fail unless screenshot verification passes.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    captured = capture_public_demo(args.url, args.screenshot_out)
    report = build_report(
        url=args.url,
        screenshot_path=args.screenshot_out,
        body_text=captured["body_text"],
        html_text=captured["html_text"],
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "screenshot": str(args.screenshot_out),
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "markers_ok": {
                    "visible": report["markers"]["visible_ok"],
                    "html": report["markers"]["html_ok"],
                },
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] or not args.strict else 2)


if __name__ == "__main__":
    main()
