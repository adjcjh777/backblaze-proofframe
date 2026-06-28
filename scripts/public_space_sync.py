#!/usr/bin/env python3
"""Verify the public Hugging Face Space is synced with judge-facing artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "public-space-sync-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "public-space-sync-report.md"
SCHEMA = "proofframe.public_space_sync.v1"

SPACE_ID = "ADJCJH/backblaze-proofframe"
SPACE_HOST = "https://adjcjh-backblaze-proofframe.hf.space"
EXPECTED_SPACE_SHA = "bd6cbae7231e7e3c2b1531ad0459bec41189c4f8"
TIMEOUT_SECONDS = 30

HTML_MARKERS = {
    "judge_recording_slate": "Judge recording slate",
    "sponsor_evidence_model": "Sponsor Evidence Model",
    "judge_brief_panel": "30-Second Judge Brief",
    "criteria_crosswalk_link": "Criteria crosswalk",
    "recording_runbook_panel": "Recording Runbook",
    "devpost_kit_panel": "Devpost Kit",
    "auto_load_judge_demo": "shouldAutoLoadJudgeDemo",
    "final_reports_pending": "Final reports pending",
}

FetchResult = dict[str, Any]
Fetcher = Callable[[str, int], FetchResult]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_text(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    request = Request(url, headers={"User-Agent": "ProofFrame public Space sync verifier"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": response.status, "body": body, "error": None}
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": error.code, "body": body, "error": str(error)}
    except URLError as error:
        return {"ok": False, "status": None, "body": "", "error": str(error.reason)}
    except TimeoutError as error:
        return {"ok": False, "status": None, "body": "", "error": str(error)}


def parse_json(result: FetchResult) -> dict[str, Any] | None:
    try:
        return json.loads(str(result.get("body") or ""))
    except json.JSONDecodeError:
        return None


def space_api_url(space_id: str) -> str:
    return f"https://huggingface.co/api/spaces/{space_id}"


def runtime_api_url(space_id: str) -> str:
    return f"https://huggingface.co/api/spaces/{space_id}/runtime"


def raw_file_url(space_id: str, relative_path: str) -> str:
    return f"https://huggingface.co/spaces/{space_id}/raw/main/{relative_path}"


def public_url(host: str, path: str) -> str:
    return f"{host.rstrip('/')}{path}"


def check_item(check_id: str, label: str, ok: bool, detail: str, evidence: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "ok": ok,
        "detail": detail,
        "evidence": evidence,
    }


def build_report(
    *,
    space_id: str = SPACE_ID,
    public_host: str = SPACE_HOST,
    expected_sha: str = EXPECTED_SPACE_SHA,
    fetcher: Fetcher = fetch_text,
) -> dict[str, Any]:
    api_url = space_api_url(space_id)
    runtime_url = runtime_api_url(space_id)
    handoff_url = raw_file_url(space_id, "docs/assets/agent-handoff-report.json")
    launch_plan_url = raw_file_url(space_id, "docs/assets/final-launch-plan.json")
    judge_brief_url = raw_file_url(space_id, "docs/assets/judge-brief.json")
    judge_crosswalk_url = raw_file_url(space_id, "docs/assets/judge-crosswalk.json")
    recording_assets_url = raw_file_url(space_id, "docs/assets/recording-assets.json")
    devpost_form_kit_url = raw_file_url(space_id, "docs/assets/devpost-form-kit.json")
    judge_url = public_url(public_host, "/?judge=1")
    health_url = public_url(public_host, "/api/health")
    gate_url = public_url(public_host, "/api/submission/gate")

    space_result = fetcher(api_url, TIMEOUT_SECONDS)
    runtime_result = fetcher(runtime_url, TIMEOUT_SECONDS)
    handoff_result = fetcher(handoff_url, TIMEOUT_SECONDS)
    launch_plan_result = fetcher(launch_plan_url, TIMEOUT_SECONDS)
    judge_brief_result = fetcher(judge_brief_url, TIMEOUT_SECONDS)
    judge_crosswalk_result = fetcher(judge_crosswalk_url, TIMEOUT_SECONDS)
    recording_assets_result = fetcher(recording_assets_url, TIMEOUT_SECONDS)
    devpost_form_kit_result = fetcher(devpost_form_kit_url, TIMEOUT_SECONDS)
    judge_result = fetcher(judge_url, TIMEOUT_SECONDS)
    health_result = fetcher(health_url, TIMEOUT_SECONDS)
    gate_result = fetcher(gate_url, TIMEOUT_SECONDS)

    space = parse_json(space_result)
    runtime = parse_json(runtime_result)
    handoff = parse_json(handoff_result)
    launch_plan = parse_json(launch_plan_result)
    judge_brief = parse_json(judge_brief_result)
    judge_crosswalk = parse_json(judge_crosswalk_result)
    recording_assets = parse_json(recording_assets_result)
    devpost_form_kit = parse_json(devpost_form_kit_result)
    health = parse_json(health_result)
    gate = parse_json(gate_result)
    html = str(judge_result.get("body") or "")

    space_sha = space.get("sha") if space else None
    runtime_sha = runtime.get("sha") if runtime else None
    runtime_stage = runtime.get("stage") if runtime else None
    domain_ready = any(
        domain.get("stage") == "READY" for domain in (runtime.get("domains", []) if runtime else [])
    )
    html_markers = {marker_id: marker in html for marker_id, marker in HTML_MARKERS.items()}
    gate_paths = [
        gate.get("tasks_path") if gate else None,
        gate.get("evidence_gate", {}).get("path") if gate else None,
        gate.get("packet_gate", {}).get("path") if gate else None,
    ]
    gate_paths_relative = bool(
        gate and all(isinstance(path, str) and path and not path.startswith("/") for path in gate_paths)
    )
    report_gate_status = gate.get("report_gate", {}).get("status") if gate else None

    checks = [
        check_item(
            "space_metadata",
            "Space metadata points at the expected commit",
            bool(
                space_result.get("ok")
                and space
                and space.get("private") is False
                and space.get("disabled") is False
                and space.get("sdk") == "docker"
                and space_sha == expected_sha
            ),
            f"Space sha is {space_sha}; expected {expected_sha}.",
            api_url,
        ),
        check_item(
            "runtime_ready",
            "Space runtime is running the expected commit",
            bool(runtime_result.get("ok") and runtime_sha == expected_sha and runtime_stage == "RUNNING" and domain_ready),
            f"Runtime stage is {runtime_stage}; runtime sha is {runtime_sha}; domain ready is {domain_ready}.",
            runtime_url,
        ),
        check_item(
            "raw_handoff_report",
            "Raw handoff report is public and ready",
            bool(
                handoff_result.get("ok")
                and handoff
                and handoff.get("schema") == "proofframe.agent_handoff.v1"
                and handoff.get("ok") is True
                and handoff.get("mode") == "handoff_ready"
            ),
            f"Handoff schema is {handoff.get('schema') if handoff else None}; mode is {handoff.get('mode') if handoff else None}.",
            handoff_url,
        ),
        check_item(
            "raw_launch_plan",
            "Raw final launch plan is public and phase-aware",
            bool(
                launch_plan_result.get("ok")
                and launch_plan
                and launch_plan.get("schema") == "proofframe.final_launch_plan.v1"
                and launch_plan.get("mode") == "ready_for_credential_entry"
                and launch_plan.get("current_phase") == "credential_entry"
            ),
            (
                f"Launch plan schema is {launch_plan.get('schema') if launch_plan else None}; "
                f"mode is {launch_plan.get('mode') if launch_plan else None}; "
                f"current phase is {launch_plan.get('current_phase') if launch_plan else None}."
            ),
            launch_plan_url,
        ),
        check_item(
            "raw_judge_brief",
            "Raw judge brief is public and claim-safe",
            bool(
                judge_brief_result.get("ok")
                and judge_brief
                and judge_brief.get("schema") == "proofframe.judge_brief.v1"
                and judge_brief.get("status", {}).get("safe_to_submit") is False
            ),
            (
                f"Judge brief schema is {judge_brief.get('schema') if judge_brief else None}; "
                f"safe_to_submit is {judge_brief.get('status', {}).get('safe_to_submit') if judge_brief else None}."
            ),
            judge_brief_url,
        ),
        check_item(
            "raw_judge_crosswalk",
            "Raw judge crosswalk is public and claim-safe",
            bool(
                judge_crosswalk_result.get("ok")
                and judge_crosswalk
                and judge_crosswalk.get("schema") == "proofframe.judge_crosswalk.v1"
                and judge_crosswalk.get("ok") is True
                and judge_crosswalk.get("safe_to_submit") is False
                and judge_crosswalk.get("mode") in {"pre_live_crosswalk_ready", "final_crosswalk_ready"}
            ),
            (
                f"Judge crosswalk schema is {judge_crosswalk.get('schema') if judge_crosswalk else None}; "
                f"mode is {judge_crosswalk.get('mode') if judge_crosswalk else None}; "
                f"safe_to_submit is {judge_crosswalk.get('safe_to_submit') if judge_crosswalk else None}."
            ),
            judge_crosswalk_url,
        ),
        check_item(
            "raw_recording_assets",
            "Raw recording runbook is public and final-video gated",
            bool(
                recording_assets_result.get("ok")
                and recording_assets
                and recording_assets.get("schema") == "proofframe.recording_assets.v1"
                and recording_assets.get("mock_recording_ready") is True
                and recording_assets.get("final_video_ready") is False
                and isinstance(recording_assets.get("shot_plan"), list)
                and len(recording_assets.get("shot_plan", [])) >= 3
            ),
            (
                f"Recording schema is {recording_assets.get('schema') if recording_assets else None}; "
                f"mode is {recording_assets.get('mode') if recording_assets else None}; "
                f"final_video_ready is {recording_assets.get('final_video_ready') if recording_assets else None}."
            ),
            recording_assets_url,
        ),
        check_item(
            "raw_devpost_form_kit",
            "Raw Devpost form kit is public and final-form gated",
            bool(
                devpost_form_kit_result.get("ok")
                and devpost_form_kit
                and devpost_form_kit.get("schema") == "proofframe.devpost_form_kit.v1"
                and devpost_form_kit.get("mock_form_ready") is True
                and devpost_form_kit.get("final_form_ready") is False
                and isinstance(devpost_form_kit.get("fields"), list)
                and len(devpost_form_kit.get("fields", [])) >= 10
            ),
            (
                f"Devpost form schema is {devpost_form_kit.get('schema') if devpost_form_kit else None}; "
                f"mode is {devpost_form_kit.get('mode') if devpost_form_kit else None}; "
                f"final_form_ready is {devpost_form_kit.get('final_form_ready') if devpost_form_kit else None}."
            ),
            devpost_form_kit_url,
        ),
        check_item(
            "public_health",
            "Public demo health is local/mock and ready",
            bool(
                health_result.get("ok")
                and health
                and health.get("ready") is True
                and health.get("storage_backend") == "local"
                and health.get("generation_backend") == "mock"
                and health.get("b2_configured") is False
                and health.get("genblaze_configured") is False
            ),
            (
                f"Health storage={health.get('storage_backend') if health else None}, "
                f"generation={health.get('generation_backend') if health else None}, "
                f"ready={health.get('ready') if health else None}."
            ),
            health_url,
        ),
        check_item(
            "submission_gate",
            "Public submission gate is fail-closed with repo-relative paths",
            bool(
                gate_result.get("ok")
                and gate
                and gate.get("mode") in {"pre_live_safe", "final_ready"}
                and isinstance(gate.get("report_gate"), dict)
                and report_gate_status in {"incomplete", "verified"}
                and gate_paths_relative
            ),
            f"Gate mode is {gate.get('mode') if gate else None}; report gate is {report_gate_status}; relative paths={gate_paths_relative}.",
            gate_url,
        ),
        check_item(
            "judge_html_markers",
            "Judge-mode HTML contains recording and sponsor markers",
            bool(judge_result.get("ok") and all(html_markers.values())),
            f"Markers: {', '.join(f'{key}={value}' for key, value in html_markers.items())}.",
            judge_url,
        ),
    ]

    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": all(item["ok"] for item in checks),
        "mode": "public_space_synced" if all(item["ok"] for item in checks) else "public_space_mismatch",
        "space_id": space_id,
        "public_host": public_host,
        "expected_sha": expected_sha,
        "observed": {
            "space_sha": space_sha,
            "runtime_sha": runtime_sha,
            "runtime_stage": runtime_stage,
            "domain_ready": domain_ready,
            "last_modified": space.get("lastModified") if space else None,
            "health": {
                "ready": health.get("ready") if health else None,
                "storage_backend": health.get("storage_backend") if health else None,
                "generation_backend": health.get("generation_backend") if health else None,
            },
            "submission_gate": {
                "mode": gate.get("mode") if gate else None,
                "summary": gate.get("summary") if gate else None,
                "report_gate_status": report_gate_status,
                "paths_relative": gate_paths_relative,
            },
            "handoff_mode": handoff.get("mode") if handoff else None,
            "launch_plan_mode": launch_plan.get("mode") if launch_plan else None,
            "launch_plan_phase": launch_plan.get("current_phase") if launch_plan else None,
            "judge_brief_schema": judge_brief.get("schema") if judge_brief else None,
            "judge_brief_safe_to_submit": (
                judge_brief.get("status", {}).get("safe_to_submit") if judge_brief else None
            ),
            "judge_crosswalk_schema": judge_crosswalk.get("schema") if judge_crosswalk else None,
            "judge_crosswalk_mode": judge_crosswalk.get("mode") if judge_crosswalk else None,
            "judge_crosswalk_safe_to_submit": (
                judge_crosswalk.get("safe_to_submit") if judge_crosswalk else None
            ),
            "html_markers": html_markers,
        },
        "urls": {
            "space_api": api_url,
            "runtime_api": runtime_url,
            "raw_handoff_report": handoff_url,
            "raw_launch_plan": launch_plan_url,
            "raw_judge_brief": judge_brief_url,
            "raw_judge_crosswalk": judge_crosswalk_url,
            "judge": judge_url,
            "health": health_url,
            "submission_gate": gate_url,
        },
        "checks": checks,
        "next_actions": next_actions(checks),
    }


def next_actions(checks: list[dict[str, Any]]) -> list[str]:
    failed = {item["id"] for item in checks if not item["ok"]}
    actions: list[str] = []
    if "space_metadata" in failed or "runtime_ready" in failed:
        actions.append("Upload the current public demo bundle to the Hugging Face Space and wait for RUNNING.")
    if "raw_handoff_report" in failed:
        actions.append("Regenerate and upload docs/assets/agent-handoff-report.json to the Space.")
    if "raw_launch_plan" in failed:
        actions.append("Regenerate and upload docs/assets/final-launch-plan.json to the Space.")
    if "raw_judge_brief" in failed:
        actions.append("Regenerate and upload docs/assets/judge-brief.json to the Space.")
    if "raw_judge_crosswalk" in failed:
        actions.append("Regenerate and upload docs/assets/judge-crosswalk.json to the Space.")
    if "public_health" in failed or "submission_gate" in failed or "judge_html_markers" in failed:
        actions.append("Rebuild the public Space and rerun public API/HTML smoke checks.")
    if not actions:
        actions.append("Public Space sync evidence is ready for the pre-live Devpost demo.")
    return actions


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Public Space Sync Report",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        f"Space: `{report['space_id']}`",
        f"Public host: {report['public_host']}",
        f"Expected sha: `{report['expected_sha']}`",
        f"Runtime sha: `{report['observed']['runtime_sha']}`",
        f"Runtime stage: `{report['observed']['runtime_stage']}`",
        "",
        "## Checks",
        "",
        "| Status | Check | Detail | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["checks"]:
        status = "OK" if item["ok"] else "FAIL"
        lines.append(f"| {status} | {item['label']} | {item['detail']} | {item['evidence']} |")
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
    parser = argparse.ArgumentParser(description="Verify the public ProofFrame Hugging Face Space sync.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--space-id", default=SPACE_ID)
    parser.add_argument("--public-host", default=SPACE_HOST)
    parser.add_argument("--expected-sha", default=EXPECTED_SPACE_SHA)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(
        space_id=args.space_id,
        public_host=args.public_host,
        expected_sha=args.expected_sha,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "runtime_sha": report["observed"]["runtime_sha"],
                "failed_checks": [item["id"] for item in report["checks"] if not item["ok"]],
            },
            indent=2,
        )
    )
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
