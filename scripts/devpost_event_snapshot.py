#!/usr/bin/env python3
"""Refresh and validate the official Devpost event snapshot."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-event-snapshot.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-event-snapshot.md"
OVERVIEW_URL = "https://backblaze-generative-media.devpost.com/"
RULES_URL = "https://backblaze-generative-media.devpost.com/rules"
SCHEMA = "proofframe.devpost_event_snapshot.v1"
TIMEOUT_SECONDS = 20
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

REQUIRED_RULE_MARKERS = {
    "working_app_url": "Provide a URL to a working application",
    "github_repo_url": "Provide a URL to your public or private GitHub code repository",
    "demo_video": "Include a demonstration video",
    "video_under_three_minutes": "less than three (3) minutes",
    "public_video_host": "YouTube, Vimeo, or Youku",
    "b2_usage": "Backblaze B2",
    "genblaze_usage": "Genblaze",
}

JUDGING_CRITERIA = [
    {"name": "Real-world Utility", "marker": "Real-world Utility"},
    {"name": "Production Readiness", "marker": "Production Readiness"},
    {"name": "B2 Storage + Data Orchestration", "marker": "B2 Storage + Data Orchestration"},
    {"name": "Use of Genblaze", "marker": "Use of Genblaz"},
]


FetchResult = dict[str, Any]
Fetcher = Callable[[str, int], FetchResult]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def format_utc_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def beijing_date(now: datetime) -> str:
    return now.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d Asia/Shanghai")


def fetch_text(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": BROWSER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            if response.status == 202 or len(body) < 5000:
                return fetch_text_with_curl(url, timeout)
            return {"ok": True, "status": response.status, "body": body, "error": None, "transport": "urllib"}
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": error.code, "body": body, "error": str(error)}
    except URLError as error:
        return {"ok": False, "status": None, "body": "", "error": str(error.reason)}
    except TimeoutError as error:
        return {"ok": False, "status": None, "body": "", "error": str(error)}


def fetch_text_with_curl(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    marker = "\n__PROOFFRAME_HTTP_STATUS__:"
    try:
        completed = subprocess.run(
            [
                "curl",
                "-L",
                "--compressed",
                "-sS",
                "-A",
                BROWSER_USER_AGENT,
                "-w",
                f"{marker}%{{http_code}}",
                url,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"ok": False, "status": None, "body": "", "error": str(error), "transport": "curl"}
    body, _, status_text = completed.stdout.rpartition(marker)
    status = parse_int(status_text)
    return {
        "ok": completed.returncode == 0 and status is not None and 200 <= status < 400,
        "status": status,
        "body": body,
        "error": completed.stderr.strip() or None,
        "transport": "curl",
    }


def text_from_html(raw_html: str) -> str:
    raw_text = re.sub(r"<(script|style).*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    raw_text = re.sub(r"<[^>]+>", "\n", raw_text)
    raw_text = html.unescape(raw_text)
    raw_text = re.sub(r"\s+", " ", raw_text)
    return raw_text.strip()


def first_match(pattern: str, text: str, default: str | None = None) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return default
    return " ".join(match.group(1).split())


def parse_int(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def parse_deadline_display(text: str) -> str | None:
    return first_match(r"Deadline:\s*([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s+@\s+\d{1,2}:\d{2}[ap]m\s+EDT)", text)


def parse_edt_deadline(deadline_display: str | None) -> datetime | None:
    if not deadline_display:
        return None
    match = re.search(
        r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})\s+@\s+(\d{1,2}):(\d{2})(am|pm)\s+EDT",
        deadline_display,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    month = MONTHS.get(match.group(1).lower())
    if not month:
        return None
    hour = int(match.group(4))
    minute = int(match.group(5))
    am_pm = match.group(6).lower()
    if am_pm == "pm" and hour != 12:
        hour += 12
    if am_pm == "am" and hour == 12:
        hour = 0
    return datetime(
        int(match.group(3)),
        month,
        int(match.group(2)),
        hour,
        minute,
        tzinfo=ZoneInfo("America/New_York"),
    )


def parse_event_window(label: str, text: str) -> str | None:
    stop_labels = "|".join(
        [
            "Judging Period:",
            "Winners Announced:",
            "Winner Announced:",
            "2\\. Sponsor",
            "Requirements",
            "Submission Requirements",
        ]
    )
    pattern = rf"{re.escape(label)}:\s*(.+?)(?:{stop_labels}|$)"
    return first_match(pattern, text)


def parse_overview(text: str) -> dict[str, Any]:
    deadline_display = parse_deadline_display(text)
    deadline_dt = parse_edt_deadline(deadline_display)
    participant_count = parse_int(
        first_match(r"Participants\s*\(([\d,]+)\)", text)
        or first_match(r"([\d,]+)\s+participants", text)
    )
    prize_total = parse_int(
        first_match(r"\$\s*([\d,]+)\s+in\s+cash", text)
        or first_match(r"\$\s*([\d,]+)\s+in\s+prizes", text)
    )
    return {
        "name": first_match(r"(Backblaze Generative Media Hackathon)", text, "Backblaze Generative Media Hackathon"),
        "deadline_display": deadline_display,
        "deadline_utc": deadline_dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if deadline_dt else None,
        "deadline_et": deadline_display,
        "deadline_beijing": (
            deadline_dt.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M Asia/Shanghai")
            if deadline_dt
            else None
        ),
        "participant_count_observed": participant_count,
        "prize_total_usd": prize_total,
        "sponsor_tech": ["Backblaze B2", "Genblaze"],
    }


def parse_rules(text: str) -> dict[str, Any]:
    rules_participants = parse_int(
        first_match(r"Participants\s*\(([\d,]+)\)", text)
        or first_match(r"([\d,]+)\s+participants", text)
    )
    requirements = {
        requirement_id: marker.lower() in text.lower()
        for requirement_id, marker in REQUIRED_RULE_MARKERS.items()
    }
    criteria = [
        {"name": criterion["name"], "present": criterion["marker"].lower() in text.lower()}
        for criterion in JUDGING_CRITERIA
    ]
    return {
        "rules_participant_count_observed": rules_participants,
        "registration_period": parse_event_window("Registration and Submission Period", text),
        "judging_period": parse_event_window("Judging Period", text),
        "winner_announced": parse_event_window("Winners Announced", text)
        or parse_event_window("Winner Announced", text),
        "requirements": requirements,
        "judging_criteria": criteria,
        "feedback_prize_present": "Feedback Prize".lower() in text.lower(),
    }


def source_record(source_id: str, url: str, result: FetchResult) -> dict[str, Any]:
    return {
        "id": source_id,
        "url": url,
        "ok": bool(result.get("ok")),
        "status": result.get("status"),
        "bytes": len(str(result.get("body") or "").encode("utf-8")),
        "error": result.get("error"),
        "transport": result.get("transport"),
    }


def build_snapshot_from_text(
    overview_html: str,
    rules_html: str,
    *,
    fetched_at: str | None = None,
    overview_status: int | None = 200,
    rules_status: int | None = 200,
) -> dict[str, Any]:
    now = utc_now()
    fetched_at = fetched_at or now.isoformat().replace("+00:00", "Z")
    overview_text = text_from_html(overview_html)
    rules_text = text_from_html(rules_html)
    overview = parse_overview(overview_text)
    rules = parse_rules(rules_text)
    participant_note = "Dynamic Devpost count; recheck before final public claims."
    if (
        overview.get("participant_count_observed")
        and rules.get("rules_participant_count_observed")
        and overview["participant_count_observed"] != rules["rules_participant_count_observed"]
    ):
        participant_note = "Overview and rules pages showed different dynamic participant counts; use overview count for the snapshot."
    event = {
        **overview,
        "devpost_url": OVERVIEW_URL,
        "rules_url": RULES_URL,
        "participant_count_checked_at": beijing_date(now),
        "participant_count_note": participant_note,
        "registration_period": rules.get("registration_period"),
        "judging_period": rules.get("judging_period"),
        "winner_announced": rules.get("winner_announced"),
    }
    snapshot = {
        "schema": SCHEMA,
        "checked_at": fetched_at,
        "mode": "live_official_snapshot",
        "event": event,
        "rules": {
            "requirements": rules["requirements"],
            "judging_criteria": rules["judging_criteria"],
            "feedback_prize_present": rules["feedback_prize_present"],
            "rules_participant_count_observed": rules["rules_participant_count_observed"],
        },
        "sources": [
            {
                "id": "overview",
                "url": OVERVIEW_URL,
                "ok": overview_status is not None and 200 <= overview_status < 400,
                "status": overview_status,
                "bytes": len(overview_html.encode("utf-8")),
                "error": None,
            },
            {
                "id": "rules",
                "url": RULES_URL,
                "ok": rules_status is not None and 200 <= rules_status < 400,
                "status": rules_status,
                "bytes": len(rules_html.encode("utf-8")),
                "error": None,
            },
        ],
    }
    snapshot["validation"] = validate_snapshot(snapshot)
    return snapshot


def build_live_snapshot(fetcher: Fetcher = fetch_text) -> dict[str, Any]:
    overview = fetcher(OVERVIEW_URL, TIMEOUT_SECONDS)
    rules = fetcher(RULES_URL, TIMEOUT_SECONDS)
    snapshot = build_snapshot_from_text(
        str(overview.get("body") or ""),
        str(rules.get("body") or ""),
        fetched_at=format_utc_now(),
        overview_status=overview.get("status"),
        rules_status=rules.get("status"),
    )
    snapshot["sources"] = [
        source_record("overview", OVERVIEW_URL, overview),
        source_record("rules", RULES_URL, rules),
    ]
    snapshot["validation"] = validate_snapshot(snapshot)
    return snapshot


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def checked_at_age_days(snapshot: dict[str, Any], now: datetime | None = None) -> int | None:
    checked_at = snapshot.get("checked_at")
    if not checked_at:
        return None
    try:
        checked = datetime.fromisoformat(str(checked_at).replace("Z", "+00:00"))
    except ValueError:
        return None
    now = now or utc_now()
    return max(0, (now - checked.astimezone(timezone.utc)).days)


def submission_is_open(snapshot: dict[str, Any], now: datetime | None = None) -> bool:
    deadline = snapshot.get("event", {}).get("deadline_utc")
    if not deadline:
        return False
    try:
        deadline_dt = datetime.fromisoformat(str(deadline).replace("Z", "+00:00"))
    except ValueError:
        return False
    now = now or utc_now()
    return now < deadline_dt.astimezone(timezone.utc)


def validate_snapshot(
    snapshot: dict[str, Any] | None,
    *,
    max_age_days: int = 14,
    now: datetime | None = None,
) -> dict[str, Any]:
    findings: list[str] = []
    if not snapshot:
        return {"ok": False, "findings": ["Snapshot JSON is missing or invalid."]}
    if snapshot.get("schema") != SCHEMA:
        findings.append(f"Expected schema {SCHEMA}, got {snapshot.get('schema')!r}.")
    sources = snapshot.get("sources", [])
    if len(sources) < 2 or not all(source.get("ok") for source in sources):
        findings.append("Official overview and rules sources must both fetch successfully.")
    event = snapshot.get("event", {})
    rules = snapshot.get("rules", {})
    if event.get("participant_count_observed") is None:
        findings.append("Participant count is missing.")
    if event.get("deadline_utc") is None:
        findings.append("Deadline is missing.")
    if not submission_is_open(snapshot, now=now):
        findings.append("Submission deadline appears closed or could not be parsed.")
    missing_requirements = [
        requirement_id
        for requirement_id, present in rules.get("requirements", {}).items()
        if present is not True
    ]
    if missing_requirements:
        findings.append(f"Submission requirement markers missing: {', '.join(missing_requirements)}.")
    missing_criteria = [
        criterion.get("name")
        for criterion in rules.get("judging_criteria", [])
        if criterion.get("present") is not True
    ]
    if missing_criteria:
        findings.append(f"Judging criteria markers missing: {', '.join(str(item) for item in missing_criteria)}.")
    age_days = checked_at_age_days(snapshot, now=now)
    if age_days is None:
        findings.append("checked_at is missing or invalid.")
    elif age_days > max_age_days:
        findings.append(f"Snapshot is {age_days} days old, above {max_age_days} day limit.")
    return {
        "ok": not findings,
        "findings": findings,
        "age_days": age_days,
        "max_age_days": max_age_days,
        "submission_open": submission_is_open(snapshot, now=now),
    }


def render_markdown(snapshot: dict[str, Any]) -> str:
    event = snapshot["event"]
    validation = snapshot.get("validation", {})
    lines = [
        "# ProofFrame Devpost Event Snapshot",
        "",
        f"Mode: `{snapshot['mode']}`",
        f"Checked: `{snapshot['checked_at']}`",
        f"Validation ok: `{str(validation.get('ok')).lower()}`",
        f"Submission open: `{str(validation.get('submission_open')).lower()}`",
        "",
        "## Official Event Facts",
        "",
        f"- Event: {event.get('name')}",
        f"- Devpost: {event.get('devpost_url')}",
        f"- Rules: {event.get('rules_url')}",
        f"- Deadline: {event.get('deadline_et')} / {event.get('deadline_beijing')}",
        f"- Prize total: `${event.get('prize_total_usd')}`",
        f"- Participants observed: `{event.get('participant_count_observed')}` checked `{event.get('participant_count_checked_at')}`",
        f"- Participant note: {event.get('participant_count_note')}",
        f"- Registration window: {event.get('registration_period')}",
        f"- Judging window: {event.get('judging_period')}",
        f"- Winner announced: {event.get('winner_announced')}",
        "",
        "## Submission Requirements",
        "",
    ]
    for requirement_id, present in snapshot["rules"]["requirements"].items():
        marker = "OK" if present else "MISSING"
        lines.append(f"- {marker} `{requirement_id}`")
    lines.extend(["", "## Judging Criteria", ""])
    for criterion in snapshot["rules"]["judging_criteria"]:
        marker = "OK" if criterion["present"] else "MISSING"
        lines.append(f"- {marker} {criterion['name']}")
    lines.extend(["", "## Sources", ""])
    for source in snapshot["sources"]:
        marker = "OK" if source["ok"] else "FAILED"
        lines.append(f"- {marker} `{source['id']}` {source['url']} status `{source['status']}`")
    lines.extend(["", "## Validation Findings", ""])
    if validation.get("findings"):
        lines.extend(f"- {finding}" for finding in validation["findings"])
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def write_outputs(snapshot: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(snapshot), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh or validate the official Devpost event snapshot.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--fetch-live", action="store_true", help="Fetch official Devpost overview and rules pages.")
    parser.add_argument("--validate-committed", action="store_true", help="Validate the committed JSON without network.")
    parser.add_argument("--max-age-days", type=int, default=14)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.fetch_live:
        snapshot = build_live_snapshot()
        snapshot["validation"] = validate_snapshot(snapshot, max_age_days=args.max_age_days)
        write_outputs(snapshot, args.json_out, args.markdown_out)
        validation = snapshot["validation"]
    else:
        snapshot = load_json(args.json_out)
        validation = validate_snapshot(snapshot, max_age_days=args.max_age_days)
        if snapshot and not args.validate_committed:
            snapshot["validation"] = validation
            write_outputs(snapshot, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": validation["ok"],
                "mode": snapshot.get("mode") if snapshot else None,
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "submission_open": validation.get("submission_open"),
                "age_days": validation.get("age_days"),
                "findings": validation["findings"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if validation["ok"] else 2)


if __name__ == "__main__":
    main()
