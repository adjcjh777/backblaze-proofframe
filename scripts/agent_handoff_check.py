#!/usr/bin/env python3
"""Verify repo handoff metadata for Agent Bus and future Codex sessions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "agent-handoff-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "agent-handoff-report.md"
SCHEMA = "proofframe.agent_handoff.v1"
EXPECTED_BRANCH = "feature/backblaze-proofframe"
EXPECTED_TEAM_ID = "proofframe-hackathon-58c62c50"
BUS_CLI = Path.home() / ".codex" / "tools" / "codex-agent-bus" / "bin" / "agent-bus"

WORK_PATH_RE = re.compile(r"Work only inside `([^`]+)`")
BRANCH_RE = re.compile(r"Current branch:\s*`([^`]+)`")
TEAM_ID_RE = re.compile(r"Team id:\s*`([^`]+)`")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve(strict=False)


def extract(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None


def check_item(check_id: str, label: str, ok: bool, detail: str, evidence: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "ok": ok,
        "detail": detail,
        "evidence": evidence,
    }


def load_agents_text(root: Path) -> tuple[str, bool]:
    path = root / "AGENTS.md"
    try:
        return path.read_text(encoding="utf-8"), True
    except FileNotFoundError:
        return "", False


def run_bus_json(root: Path, args: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    result = subprocess.run(
        [str(BUS_CLI), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None, result.stderr.strip() or result.stdout.strip() or "agent-bus command failed."
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError:
        return None, "agent-bus command did not return JSON."


def resolve_agent_summary(root: Path, session_id: str) -> dict[str, Any]:
    payload, error = run_bus_json(root, ["resolve", session_id])
    if error:
        return {
            "session_id": session_id,
            "resolved": False,
            "cwd": None,
            "cwd_matches_repo": False,
            "status": "resolve_error",
            "detail": error,
        }
    agent = (payload or {}).get("agent") or {}
    cwd = agent.get("cwd")
    cwd_matches = bool(cwd) and normalize_path(str(cwd)) == root.resolve()
    return {
        "session_id": session_id,
        "resolved": True,
        "agent_id": agent.get("agent_id"),
        "name": agent.get("name"),
        "cwd": cwd,
        "cwd_matches_repo": cwd_matches,
        "status": agent.get("status"),
        "stale": bool(agent.get("stale")),
        "last_seen": agent.get("last_seen"),
        "detail": (
            "Agent registry cwd matches this repo."
            if cwd_matches
            else "Agent registry cwd is stale, missing, or unresolved."
        ),
    }


def active_role_summaries(root: Path, roles: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for role_name, role in sorted(roles.items()):
        session_id = role.get("session_id") or role.get("thread_id")
        if role.get("status") != "active" or not session_id:
            continue
        summary = resolve_agent_summary(root, str(session_id))
        summary.update(
            {
                "role": role_name,
                "role_status": role.get("status"),
                "thread_id": role.get("thread_id"),
            }
        )
        summaries.append(summary)
    return summaries


def bus_team_summary(root: Path, team_id: str = EXPECTED_TEAM_ID) -> dict[str, Any]:
    if not BUS_CLI.exists():
        return {
            "checked": True,
            "ok": False,
            "status": "unavailable",
            "team_id": team_id,
            "detail": f"Agent Bus CLI not found at {BUS_CLI}.",
            "active_roles": [],
            "active_role_cwd_ok": False,
        }

    payload, error = run_bus_json(root, ["team", "show", team_id])
    if error:
        return {
            "checked": True,
            "ok": False,
            "status": "error",
            "team_id": team_id,
            "detail": error,
            "active_roles": [],
            "active_role_cwd_ok": False,
        }

    team = (payload or {}).get("team") or {}
    project = team.get("project")
    project_matches = bool(project) and normalize_path(str(project)) == root.resolve()
    active_roles = active_role_summaries(root, team.get("roles") or {})
    active_role_cwd_ok = bool(active_roles) and all(role.get("cwd_matches_repo") for role in active_roles)
    return {
        "checked": True,
        "ok": project_matches,
        "status": "current" if project_matches else "stale",
        "team_id": team.get("team_id") or team_id,
        "project": project,
        "expected_project": str(root.resolve()),
        "active_roles": active_roles,
        "active_role_cwd_ok": active_role_cwd_ok,
        "detail": (
            "Agent Bus team project path matches this repo."
            if project_matches
            else "Agent Bus team project path is stale or missing; AGENTS.md is the repo authority."
        ),
    }


def build_report(
    root: Path = ROOT,
    *,
    check_bus: bool = False,
    strict_bus: bool = False,
    team_id: str = EXPECTED_TEAM_ID,
) -> dict[str, Any]:
    root = root.resolve()
    agents_text, agents_present = load_agents_text(root)
    work_path = extract(WORK_PATH_RE, agents_text) if agents_present else None
    branch = extract(BRANCH_RE, agents_text) if agents_present else None
    documented_team_id = extract(TEAM_ID_RE, agents_text) if agents_present else None
    expected_root = str(root)
    normalized_work_path = str(normalize_path(work_path)) if work_path else None

    checks = [
        check_item(
            "agents_present",
            "AGENTS.md is present",
            agents_present,
            "AGENTS.md found." if agents_present else "AGENTS.md is missing.",
            "AGENTS.md",
        ),
        check_item(
            "work_path_matches_repo",
            "AGENTS work path matches this repo",
            bool(work_path) and normalized_work_path == expected_root,
            f"AGENTS path is {work_path!r}; expected {expected_root!r}.",
            "AGENTS.md",
        ),
        check_item(
            "work_path_exists",
            "AGENTS work path exists",
            bool(work_path) and normalize_path(work_path).exists(),
            f"AGENTS path is {work_path!r}.",
            "AGENTS.md",
        ),
        check_item(
            "branch_matches",
            "AGENTS branch matches current project branch",
            branch == EXPECTED_BRANCH,
            f"AGENTS branch is {branch!r}; expected {EXPECTED_BRANCH!r}.",
            "AGENTS.md",
        ),
        check_item(
            "team_id_matches",
            "AGENTS team id matches ProofFrame team",
            documented_team_id == team_id,
            f"AGENTS team id is {documented_team_id!r}; expected {team_id!r}.",
            "AGENTS.md",
        ),
    ]

    bus = (
        bus_team_summary(root, team_id)
        if check_bus
        else {
            "checked": False,
            "ok": None,
            "status": "skipped",
            "team_id": team_id,
            "detail": "Pass --check-bus for local durable Agent Bus metadata inspection.",
            "active_roles": [],
            "active_role_cwd_ok": None,
        }
    )
    if strict_bus:
        checks.append(
            check_item(
                "bus_project_matches_repo",
                "Durable Agent Bus project path matches this repo",
                bool(bus.get("ok")),
                str(bus.get("detail")),
                "agent-bus team show",
            )
        )

    ok = all(item["ok"] for item in checks)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "handoff_ready" if ok else "handoff_mismatch",
        "repo_root": expected_root,
        "agents": {
            "path": "AGENTS.md",
            "work_path": work_path,
            "normalized_work_path": normalized_work_path,
            "branch": branch,
            "team_id": documented_team_id,
        },
        "bus": bus,
        "checks": checks,
        "next_actions": next_actions(checks, bus),
    }


def next_actions(checks: list[dict[str, Any]], bus: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    failed = {item["id"] for item in checks if not item["ok"]}
    if "work_path_matches_repo" in failed or "work_path_exists" in failed:
        actions.append("Update AGENTS.md so Work only inside points to the current repo path.")
    if "branch_matches" in failed:
        actions.append("Update AGENTS.md Current branch when the long-lived feature branch changes.")
    if "team_id_matches" in failed:
        actions.append("Update AGENTS.md Team id if a new ProofFrame Agent Bus team is created.")
    if bus.get("status") == "stale":
        actions.append("Do not trust stale durable Agent Bus project metadata; use AGENTS.md as repo authority.")
    if bus.get("checked") and bus.get("active_roles") and not bus.get("active_role_cwd_ok"):
        actions.append("Reattach active Agent Bus roles with --cwd pointing to the current repo path.")
    if not actions:
        actions.append("Handoff metadata is ready for future Codex or Agent Bus sessions.")
    return actions


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Agent Handoff Report",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Repo root: `{report['repo_root']}`",
        "",
        "## AGENTS.md",
        "",
        f"- Work path: `{report['agents']['work_path']}`",
        f"- Branch: `{report['agents']['branch']}`",
        f"- Team id: `{report['agents']['team_id']}`",
        "",
        "## Agent Bus",
        "",
        f"- Checked: `{str(report['bus']['checked']).lower()}`",
        f"- Status: `{report['bus']['status']}`",
        f"- Detail: {report['bus']['detail']}",
        f"- Active role cwd ok: `{str(report['bus'].get('active_role_cwd_ok')).lower()}`",
        "",
        "### Active Roles",
        "",
        "| Role | Session | Status | CWD matches repo | CWD |",
        "| --- | --- | --- | --- | --- |",
    ]
    if report["bus"].get("active_roles"):
        for role in report["bus"]["active_roles"]:
            lines.append(
                "| "
                f"{role.get('role')} | "
                f"`{role.get('session_id')}` | "
                f"`{role.get('status')}` | "
                f"`{str(role.get('cwd_matches_repo')).lower()}` | "
                f"`{role.get('cwd')}` |"
            )
    else:
        lines.append("| none | `n/a` | `n/a` | `n/a` | `n/a` |")
    lines.extend(
        [
            "",
        "## Checks",
        "",
        "| Status | Check | Detail | Evidence |",
        "| --- | --- | --- | --- |",
        ]
    )
    for item in report["checks"]:
        status = "OK" if item["ok"] else "FAIL"
        lines.append(f"| {status} | {item['label']} | {item['detail']} | `{item['evidence']}` |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify ProofFrame Agent Bus handoff metadata.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check-bus", action="store_true", help="Inspect local durable Agent Bus metadata.")
    parser.add_argument("--strict-bus", action="store_true", help="Fail if local durable Bus project path is stale.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(ROOT, check_bus=args.check_bus, strict_bus=args.strict_bus)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "bus_status": report["bus"]["status"],
                "failed_checks": [item["id"] for item in report["checks"] if not item["ok"]],
            },
            indent=2,
        )
    )
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
