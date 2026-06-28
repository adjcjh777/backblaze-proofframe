#!/usr/bin/env python3
"""Build a fail-closed public demo video URL check for Devpost submission."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.public_video_check.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "public-video-check.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "public-video-check.md"
TIMEOUT_SECONDS = 20
TOKEN_PARAM_HINTS = {
    "access_key",
    "access_token",
    "auth",
    "authorization",
    "expires",
    "key",
    "signature",
    "sig",
    "signed",
    "token",
}
PRIVATE_HOST_PREFIXES = ("localhost", "127.", "0.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "192.168.")

FetchResult = dict[str, Any]
Fetcher = Callable[[str, int], FetchResult]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def has_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or lowered.startswith("tbd") or "tbd after" in lowered or lowered in {"https://...", "http://..."}


def candidate_video_url(root: Path, explicit_url: str | None = None) -> str:
    if explicit_url:
        return explicit_url.strip()
    env_url = os.environ.get("PROOFFRAME_PUBLIC_VIDEO_URL", "").strip()
    if env_url:
        return env_url
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json")
    return str(packet.get("video_url") or "").strip()


def event_requirements(root: Path) -> dict[str, Any]:
    snapshot = load_json(root / "docs" / "assets" / "devpost-event-snapshot.json")
    requirements = ((snapshot.get("rules") or {}).get("requirements") or {})
    validation = snapshot.get("validation") or {}
    return {
        "path": "docs/assets/devpost-event-snapshot.json",
        "schema_ok": snapshot.get("schema") == "proofframe.devpost_event_snapshot.v1",
        "validation_ok": validation.get("ok") is True,
        "demo_video": requirements.get("demo_video") is True,
        "video_under_three_minutes": requirements.get("video_under_three_minutes") is True,
        "public_video_host": requirements.get("public_video_host") is True,
    }


def storyboard_requirements(root: Path) -> dict[str, Any]:
    storyboard = load_json(root / "docs" / "assets" / "demo-storyboard.json")
    return {
        "path": "docs/assets/demo-storyboard.json",
        "schema_ok": storyboard.get("schema") == "proofframe.demo_storyboard.v1",
        "under_time_limit": storyboard.get("under_time_limit") is True,
        "total_seconds": storyboard.get("total_seconds"),
        "max_seconds": storyboard.get("max_seconds"),
        "public_video_ready": storyboard.get("public_video_ready"),
    }


def video_url_analysis(url: str) -> dict[str, Any]:
    if has_placeholder(url):
        return {
            "url": url,
            "present": False,
            "scheme_ok": False,
            "host": None,
            "host_public": False,
            "has_credentials": False,
            "token_params": [],
            "safe_query": False,
            "ok": False,
            "reason": "missing_or_placeholder",
        }
    parsed = urlparse(url)
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    token_params = sorted(key for key in query_keys if key in TOKEN_PARAM_HINTS or "token" in key or "sig" in key)
    host = (parsed.hostname or "").lower()
    host_public = bool(host) and not host.startswith(PRIVATE_HOST_PREFIXES)
    has_credentials = bool(parsed.username or parsed.password)
    scheme_ok = parsed.scheme in {"http", "https"}
    safe_query = not token_params
    ok = bool(scheme_ok and host_public and not has_credentials and safe_query)
    reason = "ok" if ok else "unsafe_or_private_url"
    return {
        "url": url,
        "present": True,
        "scheme_ok": scheme_ok,
        "host": host,
        "host_public": host_public,
        "has_credentials": has_credentials,
        "token_params": token_params,
        "safe_query": safe_query,
        "ok": ok,
        "reason": reason,
    }


def fetch_url(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": "ProofFrame public video verifier",
            "Range": "bytes=0-2048",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            response.read(2048)
            return {
                "checked": True,
                "ok": 200 <= int(response.status) < 400,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
                "final_url": response.geturl(),
                "error": None,
            }
    except HTTPError as error:
        return {
            "checked": True,
            "ok": 200 <= int(error.code) < 400,
            "status": error.code,
            "content_type": error.headers.get("content-type") if error.headers else None,
            "final_url": url,
            "error": str(error),
        }
    except (URLError, TimeoutError) as error:
        return {
            "checked": True,
            "ok": False,
            "status": None,
            "content_type": None,
            "final_url": url,
            "error": str(error),
        }


def unchecked_url(url: str) -> FetchResult:
    return {
        "checked": False,
        "ok": False,
        "status": None,
        "content_type": None,
        "final_url": url,
        "error": "URL verification was not requested.",
    }


def check_item(check_id: str, ok: bool, detail: str, evidence: str) -> dict[str, Any]:
    return {"id": check_id, "ok": ok, "detail": detail, "evidence": evidence}


def build_checks(
    *,
    event: dict[str, Any],
    storyboard: dict[str, Any],
    url: dict[str, Any],
    access: FetchResult,
) -> list[dict[str, Any]]:
    return [
        check_item(
            "official_event_video_requirements",
            bool(event["schema_ok"] and event["validation_ok"] and event["demo_video"] and event["public_video_host"]),
            (
                f"demo_video={event['demo_video']}; public_video_host={event['public_video_host']}; "
                f"snapshot validation={event['validation_ok']}."
            ),
            event["path"],
        ),
        check_item(
            "storyboard_under_three_minutes",
            bool(storyboard["schema_ok"] and storyboard["under_time_limit"] and event["video_under_three_minutes"]),
            f"Storyboard duration is {storyboard['total_seconds']}s / {storyboard['max_seconds']}s.",
            storyboard["path"],
        ),
        check_item(
            "video_url_present",
            bool(url["present"]),
            f"Video URL source is {'present' if url['present'] else 'missing or placeholder'}.",
            "docs/assets/devpost-submission-packet.json or PROOFFRAME_PUBLIC_VIDEO_URL",
        ),
        check_item(
            "video_url_public_and_safe",
            bool(url["ok"]),
            (
                f"scheme_ok={url['scheme_ok']}; host={url['host']}; "
                f"host_public={url['host_public']}; token_params={url['token_params']}."
            ),
            "public video URL",
        ),
        check_item(
            "video_url_accessible",
            bool(access["checked"] and access["ok"]),
            f"checked={access['checked']}; status={access['status']}; error={access['error']}.",
            "public video URL",
        ),
    ]


def build_report(
    root: Path = ROOT,
    *,
    video_url: str | None = None,
    verify_url: bool = False,
    fetcher: Fetcher = fetch_url,
) -> dict[str, Any]:
    root = root.resolve()
    selected_url = candidate_video_url(root, video_url)
    event = event_requirements(root)
    storyboard = storyboard_requirements(root)
    url = video_url_analysis(selected_url)
    access = fetcher(selected_url, TIMEOUT_SECONDS) if verify_url and url["ok"] else unchecked_url(selected_url)
    checks = build_checks(event=event, storyboard=storyboard, url=url, access=access)
    safe_to_submit = all(item["ok"] for item in checks)
    if safe_to_submit:
        mode = "public_video_verified"
    elif not url["present"]:
        mode = "pending_video_url"
    elif not url["ok"]:
        mode = "unsafe_video_url"
    else:
        mode = "needs_url_verification"
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": mode,
        "ok": safe_to_submit,
        "safe_to_submit": safe_to_submit,
        "video_url": selected_url,
        "event_requirements": event,
        "storyboard_requirements": storyboard,
        "url_analysis": url,
        "access_check": access,
        "checks": checks,
        "next_actions": build_next_actions(mode, checks),
    }


def build_next_actions(mode: str, checks: list[dict[str, Any]]) -> list[str]:
    failed = {item["id"] for item in checks if not item["ok"]}
    actions: list[str] = []
    if mode == "pending_video_url":
        actions.append("Record and upload the final demo video, then set PROOFFRAME_PUBLIC_VIDEO_URL.")
    if "storyboard_under_three_minutes" in failed:
        actions.append("Keep the final demo video under the event's 3-minute limit.")
    if "video_url_public_and_safe" in failed:
        actions.append("Use a public http(s) video URL without credential, token, signature, or expiry query parameters.")
    if "video_url_accessible" in failed:
        actions.append("Run python scripts/public_video_check.py --video-url \"$PROOFFRAME_PUBLIC_VIDEO_URL\" --verify-url --strict-final after upload.")
    if "official_event_video_requirements" in failed:
        actions.append("Refresh docs/assets/devpost-event-snapshot.json from Devpost before final submission.")
    return list(dict.fromkeys(actions))[:6]


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Public Video Check",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        f"Video URL: `{report['video_url'] or 'missing'}`",
        "",
        "## Checks",
        "",
    ]
    for item in report["checks"]:
        marker = "OK" if item["ok"] else "BLOCKED"
        lines.append(f"- {marker} `{item['id']}`: {item['detail']} Evidence: `{item['evidence']}`")
    access = report["access_check"]
    lines.extend(
        [
            "",
            "## Access Check",
            "",
            f"- Checked: `{str(access.get('checked')).lower()}`",
            f"- Status: `{access.get('status')}`",
            f"- Content type: `{access.get('content_type')}`",
            f"- Final URL: `{access.get('final_url')}`",
        ]
    )
    lines.extend(["", "## Next Actions", ""])
    if report["next_actions"]:
        lines.extend(f"- {action}" for action in report["next_actions"])
    else:
        lines.append("- Public video URL is ready for final Devpost copy.")
    lines.append("")
    lines.append("This report stores only a public video URL and accessibility metadata, never credentials or browser state.")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a public video URL check for final Devpost submission.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--video-url")
    parser.add_argument("--verify-url", action="store_true", help="Perform a GET-only public URL accessibility check.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless the public video is verified.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.root, video_url=args.video_url, verify_url=args.verify_url)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "safe_to_submit": report["safe_to_submit"],
                "next_actions": report["next_actions"],
            },
            indent=2,
        )
    )
    if args.strict_final and not report["safe_to_submit"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
