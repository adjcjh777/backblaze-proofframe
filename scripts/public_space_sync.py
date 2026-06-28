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
EXPECTED_SPACE_SHA = "2f1532df85103b7114cfba5a1267764ee8a00fd6"
TIMEOUT_SECONDS = 30
DRAFT_VIDEO_MIN_BYTES = 100_000
EVENT_SNAPSHOT_MAX_AGE_DAYS = 14
POST_CREDENTIAL_REQUIRED_SEQUENCE = (
    "credential_handoff",
    "b2_live_proof",
    "validate_b2_evidence",
    "final_live_proof",
    "validate_final_evidence",
)
SECRET_POLICY_REQUIRED_TERMS = (
    "never stores",
    "backblaze keys",
    "genblaze/gmi keys",
    "devpost cookies",
    "provider responses",
    "signed urls",
)
SECRET_POLICY_FORBIDDEN_TERMS = (
    "store secrets",
    "stores secrets",
    "store backblaze",
    "store genblaze",
    "store devpost",
    "store signed urls",
    "save secrets",
    "saves secrets",
    "include secrets",
    "includes secrets",
)
TASK_UPDATE_COMMAND_MARKERS = ("scripts/task.py", " task.py ", "--update-tasks")
REQUIRED_BUNDLE_ARTIFACT_IDS = {
    "repo_readme",
    "devpost_packet_json",
    "public_space_sync_json",
    "post_credential_live_proof_json",
    "post_credential_live_proof_script",
    "b2_key_scope_checklist_json",
    "b2_key_scope_checklist_script",
    "final_submission_control_json",
    "secret_scan_json",
    "submission_audit_json",
    "devpost_submission_checklist_json",
    "demo_video_draft_mp4",
    "task_ledger",
}

HTML_MARKERS = {
    "judge_recording_slate": "Judge recording slate",
    "sponsor_evidence_model": "Sponsor Evidence Model",
    "judge_brief_panel": "30-Second Judge Brief",
    "criteria_crosswalk_link": "Criteria crosswalk",
    "recording_runbook_panel": "Recording Runbook",
    "devpost_kit_panel": "Devpost Kit",
    "submit_checklist_panel": "Submit Checklist",
    "auto_load_judge_demo": "shouldAutoLoadJudgeDemo",
    "final_reports_pending": "Final reports pending",
}

FetchResult = dict[str, Any]
Fetcher = Callable[[str, int], FetchResult]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def checked_at_age_days(checked_at: Any) -> int | None:
    if not isinstance(checked_at, str) or not checked_at:
        return None
    try:
        checked = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    now = datetime.now(timezone.utc)
    return max(0, (now - checked.astimezone(timezone.utc)).days)


def fetch_text(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    request = Request(url, headers={"User-Agent": "ProofFrame public Space sync verifier"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read()
            body = raw_body.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "status": response.status,
                "body": body,
                "bytes": len(raw_body),
                "content_type": response.headers.get("content-type"),
                "error": None,
            }
    except HTTPError as error:
        raw_body = error.read()
        body = raw_body.decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": error.code,
            "body": body,
            "bytes": len(raw_body),
            "content_type": error.headers.get("content-type") if error.headers else None,
            "error": str(error),
        }
    except URLError as error:
        return {"ok": False, "status": None, "body": "", "bytes": 0, "content_type": None, "error": str(error.reason)}
    except TimeoutError as error:
        return {"ok": False, "status": None, "body": "", "bytes": 0, "content_type": None, "error": str(error)}


def parse_json(result: FetchResult) -> dict[str, Any] | None:
    try:
        parsed = json.loads(str(result.get("body") or ""))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def dict_field(value: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not value:
        return {}
    field = value.get(key)
    return field if isinstance(field, dict) else {}


def list_field(value: dict[str, Any] | None, key: str) -> list[Any]:
    if not value:
        return []
    field = value.get(key)
    return field if isinstance(field, list) else []


def dict_list_field(value: dict[str, Any] | None, key: str) -> list[dict[str, Any]]:
    items = list_field(value, key)
    if not all(isinstance(item, dict) for item in items):
        return []
    return items


def command_dicts(plan: dict[str, Any] | None) -> list[dict[str, Any]]:
    commands = dict_list_field(plan, "commands")
    if not commands:
        return []
    for command in commands:
        if not isinstance(command.get("id"), str) or not command.get("id"):
            return []
    return commands


def secret_policy_is_safe(policy: Any) -> bool:
    if not isinstance(policy, str):
        return False
    normalized = policy.lower()
    return all(term in normalized for term in SECRET_POLICY_REQUIRED_TERMS) and not any(
        term in normalized for term in SECRET_POLICY_FORBIDDEN_TERMS
    )


def no_task_update_commands(commands: list[dict[str, Any]]) -> bool:
    for command in commands:
        command_text = str(command.get("command") or "").lower()
        if any(marker in command_text for marker in TASK_UPDATE_COMMAND_MARKERS):
            return False
    return True


def sha256_like(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def artifact_is_present(artifact: dict[str, Any]) -> bool:
    path = artifact.get("path")
    return bool(
        isinstance(artifact.get("id"), str)
        and artifact.get("present") is True
        and isinstance(path, str)
        and path
        and not path.startswith("/")
        and isinstance(artifact.get("bytes"), int)
        and artifact.get("bytes", 0) > 0
        and sha256_like(artifact.get("sha256"))
    )


def report_status(reports: list[dict[str, Any]], report_id: str) -> dict[str, Any]:
    for report in reports:
        if report.get("id") == report_id:
            return report
    return {}


def space_api_url(space_id: str) -> str:
    return f"https://huggingface.co/api/spaces/{space_id}"


def runtime_api_url(space_id: str) -> str:
    return f"https://huggingface.co/api/spaces/{space_id}/runtime"


def raw_file_url(space_id: str, relative_path: str) -> str:
    return f"https://huggingface.co/spaces/{space_id}/raw/main/{relative_path}"


def resolve_file_url(space_id: str, relative_path: str) -> str:
    return f"https://huggingface.co/spaces/{space_id}/resolve/main/{relative_path}"


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
    event_snapshot_url = raw_file_url(space_id, "docs/assets/devpost-event-snapshot.json")
    launch_plan_url = raw_file_url(space_id, "docs/assets/final-launch-plan.json")
    b2_key_scope_checklist_url = raw_file_url(space_id, "docs/assets/b2-key-scope-checklist.json")
    judge_brief_url = raw_file_url(space_id, "docs/assets/judge-brief.json")
    judge_crosswalk_url = raw_file_url(space_id, "docs/assets/judge-crosswalk.json")
    recording_assets_url = raw_file_url(space_id, "docs/assets/recording-assets.json")
    demo_video_draft_url = raw_file_url(space_id, "docs/assets/demo-video-draft.json")
    demo_video_draft_mp4_url = resolve_file_url(space_id, "docs/assets/proofframe-demo-draft.mp4")
    devpost_form_kit_url = raw_file_url(space_id, "docs/assets/devpost-form-kit.json")
    submit_checklist_url = raw_file_url(space_id, "docs/assets/devpost-submission-checklist.json")
    post_credential_plan_url = raw_file_url(space_id, "docs/assets/post-credential-live-proof-plan.json")
    submission_bundle_url = raw_file_url(space_id, "docs/assets/submission-bundle-manifest.json")
    judge_url = public_url(public_host, "/?judge=1")
    health_url = public_url(public_host, "/api/health")
    gate_url = public_url(public_host, "/api/submission/gate")

    space_result = fetcher(api_url, TIMEOUT_SECONDS)
    runtime_result = fetcher(runtime_url, TIMEOUT_SECONDS)
    handoff_result = fetcher(handoff_url, TIMEOUT_SECONDS)
    event_snapshot_result = fetcher(event_snapshot_url, TIMEOUT_SECONDS)
    launch_plan_result = fetcher(launch_plan_url, TIMEOUT_SECONDS)
    b2_key_scope_checklist_result = fetcher(b2_key_scope_checklist_url, TIMEOUT_SECONDS)
    judge_brief_result = fetcher(judge_brief_url, TIMEOUT_SECONDS)
    judge_crosswalk_result = fetcher(judge_crosswalk_url, TIMEOUT_SECONDS)
    recording_assets_result = fetcher(recording_assets_url, TIMEOUT_SECONDS)
    demo_video_draft_result = fetcher(demo_video_draft_url, TIMEOUT_SECONDS)
    demo_video_draft_mp4_result = fetcher(demo_video_draft_mp4_url, TIMEOUT_SECONDS)
    devpost_form_kit_result = fetcher(devpost_form_kit_url, TIMEOUT_SECONDS)
    submit_checklist_result = fetcher(submit_checklist_url, TIMEOUT_SECONDS)
    post_credential_plan_result = fetcher(post_credential_plan_url, TIMEOUT_SECONDS)
    submission_bundle_result = fetcher(submission_bundle_url, TIMEOUT_SECONDS)
    judge_result = fetcher(judge_url, TIMEOUT_SECONDS)
    health_result = fetcher(health_url, TIMEOUT_SECONDS)
    gate_result = fetcher(gate_url, TIMEOUT_SECONDS)

    space = parse_json(space_result)
    runtime = parse_json(runtime_result)
    handoff = parse_json(handoff_result)
    event_snapshot = parse_json(event_snapshot_result)
    launch_plan = parse_json(launch_plan_result)
    b2_key_scope_checklist = parse_json(b2_key_scope_checklist_result)
    judge_brief = parse_json(judge_brief_result)
    judge_crosswalk = parse_json(judge_crosswalk_result)
    recording_assets = parse_json(recording_assets_result)
    demo_video_draft = parse_json(demo_video_draft_result)
    devpost_form_kit = parse_json(devpost_form_kit_result)
    submit_checklist = parse_json(submit_checklist_result)
    post_credential_plan = parse_json(post_credential_plan_result)
    submission_bundle = parse_json(submission_bundle_result)
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
    report_gate_status = dict_field(gate, "report_gate").get("status") if gate else None
    event_snapshot_event = dict_field(event_snapshot, "event")
    event_snapshot_rules = dict_field(event_snapshot, "rules")
    event_snapshot_validation = dict_field(event_snapshot, "validation")
    event_snapshot_sources = dict_list_field(event_snapshot, "sources")
    event_snapshot_requirements = dict_field(event_snapshot_rules, "requirements")
    event_snapshot_criteria = dict_list_field(event_snapshot_rules, "judging_criteria")
    event_snapshot_age_days = checked_at_age_days(event_snapshot.get("checked_at") if event_snapshot else None)
    event_snapshot_sources_ok = len(event_snapshot_sources) >= 2 and all(
        source.get("ok") is True and source.get("status") == 200 for source in event_snapshot_sources
    )
    event_snapshot_requirements_ok = bool(event_snapshot_requirements) and all(
        present is True for present in event_snapshot_requirements.values()
    )
    event_snapshot_criteria_ok = len(event_snapshot_criteria) >= 4 and all(
        criterion.get("present") is True for criterion in event_snapshot_criteria
    )
    post_credential_commands = command_dicts(post_credential_plan)
    post_credential_command_ids = [str(command["id"]) for command in post_credential_commands]
    post_credential_sequence_ok = (
        post_credential_command_ids[: len(POST_CREDENTIAL_REQUIRED_SEQUENCE)]
        == list(POST_CREDENTIAL_REQUIRED_SEQUENCE)
    )
    post_credential_no_task_update = no_task_update_commands(post_credential_commands)
    post_credential_secret_policy_ok = secret_policy_is_safe(
        post_credential_plan.get("secret_policy") if post_credential_plan else None
    )
    submission_bundle_artifacts = dict_list_field(submission_bundle, "artifacts")
    submission_bundle_artifact_ids = {
        str(artifact.get("id")) for artifact in submission_bundle_artifacts if isinstance(artifact.get("id"), str)
    }
    submission_bundle_required_artifacts_ok = REQUIRED_BUNDLE_ARTIFACT_IDS <= submission_bundle_artifact_ids
    submission_bundle_artifacts_valid = bool(submission_bundle_artifacts) and all(
        artifact_is_present(artifact) for artifact in submission_bundle_artifacts
    )
    submission_bundle_missing_artifacts = list_field(submission_bundle, "missing_artifacts")
    submission_bundle_devpost_packet = dict_field(submission_bundle, "devpost_packet")
    submission_bundle_gate = dict_field(submission_bundle, "submission_gate")
    submission_bundle_packet_gate = dict_field(submission_bundle_gate, "packet_gate")
    submission_bundle_evidence_gate = dict_field(submission_bundle_gate, "evidence_gate")
    submission_bundle_report_gate = dict_field(submission_bundle_gate, "report_gate")
    submission_bundle_reports = dict_list_field(submission_bundle_report_gate, "reports")
    submission_bundle_secret_scan = report_status(submission_bundle_reports, "secret_scan")
    submission_bundle_submission_audit = report_status(submission_bundle_reports, "submission_audit")
    submission_bundle_next_actions = list_field(submission_bundle_gate, "next_actions")
    b2_key_scope_expected = dict_field(b2_key_scope_checklist, "expected_key")
    b2_key_scope_bucket = dict_field(b2_key_scope_expected, "bucket_scope")
    b2_key_scope_prefix = dict_field(b2_key_scope_expected, "file_name_prefix")
    b2_key_scope_secret_policy = dict_field(b2_key_scope_checklist, "secret_policy")
    b2_key_scope_required_capabilities = {
        str(item.get("capability"))
        for item in dict_list_field(b2_key_scope_expected, "required_capabilities")
    }
    b2_key_scope_conditional_capabilities = {
        str(item.get("capability")): item
        for item in dict_list_field(b2_key_scope_expected, "conditional_capabilities")
    }
    b2_key_scope_forbidden_capabilities = {
        str(item.get("capability"))
        for item in dict_list_field(b2_key_scope_expected, "forbidden_capabilities")
    }
    b2_key_scope_ok = bool(
        b2_key_scope_checklist_result.get("ok")
        and b2_key_scope_checklist
        and b2_key_scope_checklist.get("schema") == "proofframe.b2_key_scope_checklist.v1"
        and b2_key_scope_checklist.get("ok") is True
        and b2_key_scope_checklist.get("safe_to_commit") is True
        and b2_key_scope_checklist.get("requires_user_confirmation_before_key_creation") is True
        and b2_key_scope_secret_policy.get("forbidden_setup_fields") == []
        and b2_key_scope_bucket.get("mode") == "single_bucket"
        and b2_key_scope_bucket.get("bucket_name") == "proofframe-demo-a6b4e49"
        and b2_key_scope_bucket.get("forbidden") == "all_buckets"
        and b2_key_scope_prefix.get("value") == "campaigns/"
        and {"writeFiles", "listAllBucketNames"} <= b2_key_scope_required_capabilities
        and b2_key_scope_conditional_capabilities.get("readFiles", {}).get("required_now") == "false"
        and b2_key_scope_conditional_capabilities.get("listFiles", {}).get("required_now") == "false"
        and "deleteFiles" in b2_key_scope_forbidden_capabilities
        and "writeBuckets/deleteBuckets" in b2_key_scope_forbidden_capabilities
    )

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
            "raw_event_snapshot",
            "Raw Devpost event snapshot is public and fresh",
            bool(
                event_snapshot_result.get("ok")
                and event_snapshot
                and event_snapshot.get("schema") == "proofframe.devpost_event_snapshot.v1"
                and event_snapshot.get("mode") == "live_official_snapshot"
                and event_snapshot_validation.get("ok") is True
                and event_snapshot_validation.get("submission_open") is True
                and event_snapshot_sources_ok
                and event_snapshot_requirements_ok
                and event_snapshot_criteria_ok
                and isinstance(event_snapshot_event.get("participant_count_observed"), int)
                and event_snapshot_event.get("participant_count_observed", 0) > 0
                and event_snapshot_event.get("deadline_utc") == "2026-08-03T21:00:00Z"
                and event_snapshot_age_days is not None
                and event_snapshot_age_days <= EVENT_SNAPSHOT_MAX_AGE_DAYS
            ),
            (
                f"Event snapshot schema is {event_snapshot.get('schema') if event_snapshot else None}; "
                f"submission_open={event_snapshot_validation.get('submission_open') if event_snapshot else None}; "
                f"age_days={event_snapshot_age_days}; "
                f"participants={event_snapshot_event.get('participant_count_observed') if event_snapshot else None}."
            ),
            event_snapshot_url,
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
            "raw_b2_key_scope_checklist",
            "Raw B2 key scope checklist is public and no-secret",
            b2_key_scope_ok,
            (
                f"Checklist schema is {b2_key_scope_checklist.get('schema') if b2_key_scope_checklist else None}; "
                f"safe_to_commit={b2_key_scope_checklist.get('safe_to_commit') if b2_key_scope_checklist else None}; "
                f"bucket={b2_key_scope_bucket.get('bucket_name') if b2_key_scope_checklist else None}; "
                f"prefix={b2_key_scope_prefix.get('value') if b2_key_scope_checklist else None}; "
                f"required={sorted(b2_key_scope_required_capabilities)}."
            ),
            b2_key_scope_checklist_url,
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
            "raw_demo_video_draft",
            "Raw mock demo video draft report is public and fail-closed",
            bool(
                demo_video_draft_result.get("ok")
                and demo_video_draft
                and demo_video_draft.get("schema") == "proofframe.demo_video_draft.v1"
                and demo_video_draft.get("ok") is True
                and demo_video_draft.get("safe_to_submit") is False
                and demo_video_draft.get("final_video_ready") is False
                and demo_video_draft.get("video_path") == "docs/assets/proofframe-demo-draft.mp4"
                and (demo_video_draft.get("video_probe", {}).get("bytes") or 0) >= DRAFT_VIDEO_MIN_BYTES
            ),
            (
                f"Draft schema is {demo_video_draft.get('schema') if demo_video_draft else None}; "
                f"mode is {demo_video_draft.get('mode') if demo_video_draft else None}; "
                f"safe_to_submit is {demo_video_draft.get('safe_to_submit') if demo_video_draft else None}."
            ),
            demo_video_draft_url,
        ),
        check_item(
            "public_demo_video_draft_mp4",
            "Mock demo video draft MP4 is publicly readable",
            bool(
                demo_video_draft_mp4_result.get("ok")
                and demo_video_draft_mp4_result.get("status") in {200, 206}
                and (demo_video_draft_mp4_result.get("bytes") or 0) >= DRAFT_VIDEO_MIN_BYTES
                and "video" in str(demo_video_draft_mp4_result.get("content_type") or "").lower()
            ),
            (
                f"status={demo_video_draft_mp4_result.get('status')}; "
                f"bytes={demo_video_draft_mp4_result.get('bytes')}; "
                f"content_type={demo_video_draft_mp4_result.get('content_type')}."
            ),
            demo_video_draft_mp4_url,
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
            "raw_submit_checklist",
            "Raw Devpost submit checklist is public and fail-closed",
            bool(
                submit_checklist_result.get("ok")
                and submit_checklist
                and submit_checklist.get("schema") == "proofframe.devpost_submission_checklist.v1"
                and submit_checklist.get("safe_to_submit") is False
                and submit_checklist.get("mode") == "pre_submit_blocked"
                and isinstance(submit_checklist.get("preflight"), list)
                and len(submit_checklist.get("preflight", [])) >= 3
            ),
            (
                f"Submit checklist schema is {submit_checklist.get('schema') if submit_checklist else None}; "
                f"mode is {submit_checklist.get('mode') if submit_checklist else None}; "
                f"safe_to_submit is {submit_checklist.get('safe_to_submit') if submit_checklist else None}."
            ),
            submit_checklist_url,
        ),
        check_item(
            "raw_post_credential_plan",
            "Raw post-credential live proof plan is public and task-safe",
            bool(
                post_credential_plan_result.get("ok")
                and post_credential_plan
                and post_credential_plan.get("schema") == "proofframe.post_credential_live_proof.v1"
                and post_credential_plan.get("ok") is True
                and post_credential_plan.get("mode") == "plan_only"
                and post_credential_plan.get("execute") is False
                and post_credential_plan.get("update_tasks") is False
                and post_credential_sequence_ok
                and post_credential_no_task_update
                and post_credential_secret_policy_ok
            ),
            (
                f"Post-credential schema is {post_credential_plan.get('schema') if post_credential_plan else None}; "
                f"mode is {post_credential_plan.get('mode') if post_credential_plan else None}; "
                f"required sequence={post_credential_sequence_ok}; "
                f"secret policy safe={post_credential_secret_policy_ok}."
            ),
            post_credential_plan_url,
        ),
        check_item(
            "raw_submission_bundle",
            "Raw submission bundle separates shareability from final submit readiness",
            bool(
                submission_bundle_result.get("ok")
                and submission_bundle
                and submission_bundle.get("schema") == "proofframe.submission_bundle.v1"
                and submission_bundle.get("safe_to_share") is True
                and submission_bundle.get("safe_to_submit") is False
                and submission_bundle_missing_artifacts == []
                and submission_bundle_artifacts_valid
                and submission_bundle_required_artifacts_ok
                and submission_bundle_devpost_packet.get("present") is True
                and submission_bundle_devpost_packet.get("mode") == "pre_live_safe"
                and "Do not submit" in str(submission_bundle_devpost_packet.get("claim_warning") or "")
                and submission_bundle_gate.get("ok") is False
                and submission_bundle_gate.get("mode") == "pre_live_safe"
                and submission_bundle_packet_gate.get("status") == "pre_live_packet_pending"
                and submission_bundle_evidence_gate.get("status") == "missing"
                and submission_bundle_report_gate.get("status") == "incomplete"
                and submission_bundle_secret_scan.get("ok") is True
                and submission_bundle_secret_scan.get("status") == "verified"
                and submission_bundle_submission_audit.get("ok") is False
                and submission_bundle_submission_audit.get("status") == "incomplete"
                and any("Backblaze B2" in str(action) for action in submission_bundle_next_actions)
                and any("Genblaze" in str(action) for action in submission_bundle_next_actions)
            ),
            (
                f"Bundle schema is {submission_bundle.get('schema') if submission_bundle else None}; "
                f"safe_to_share={submission_bundle.get('safe_to_share') if submission_bundle else None}; "
                f"safe_to_submit={submission_bundle.get('safe_to_submit') if submission_bundle else None}; "
                f"required artifacts={submission_bundle_required_artifacts_ok}."
            ),
            submission_bundle_url,
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
            "event_snapshot": {
                "checked_at": event_snapshot.get("checked_at") if event_snapshot else None,
                "age_days": event_snapshot_age_days,
                "participant_count_observed": (
                    event_snapshot_event.get("participant_count_observed") if event_snapshot else None
                ),
                "submission_open": event_snapshot_validation.get("submission_open") if event_snapshot else None,
                "requirements_ok": event_snapshot_requirements_ok,
                "criteria_ok": event_snapshot_criteria_ok,
            },
            "launch_plan_mode": launch_plan.get("mode") if launch_plan else None,
            "launch_plan_phase": launch_plan.get("current_phase") if launch_plan else None,
            "b2_key_scope_checklist": {
                "schema": b2_key_scope_checklist.get("schema") if b2_key_scope_checklist else None,
                "ok": b2_key_scope_checklist.get("ok") if b2_key_scope_checklist else None,
                "safe_to_commit": (
                    b2_key_scope_checklist.get("safe_to_commit") if b2_key_scope_checklist else None
                ),
                "requires_user_confirmation_before_key_creation": (
                    b2_key_scope_checklist.get("requires_user_confirmation_before_key_creation")
                    if b2_key_scope_checklist
                    else None
                ),
                "bucket_name": b2_key_scope_bucket.get("bucket_name"),
                "prefix": b2_key_scope_prefix.get("value"),
                "required_capabilities": sorted(b2_key_scope_required_capabilities),
                "forbidden_setup_fields": b2_key_scope_secret_policy.get("forbidden_setup_fields"),
            },
            "judge_brief_schema": judge_brief.get("schema") if judge_brief else None,
            "judge_brief_safe_to_submit": (
                judge_brief.get("status", {}).get("safe_to_submit") if judge_brief else None
            ),
            "judge_crosswalk_schema": judge_crosswalk.get("schema") if judge_crosswalk else None,
            "judge_crosswalk_mode": judge_crosswalk.get("mode") if judge_crosswalk else None,
            "judge_crosswalk_safe_to_submit": (
                judge_crosswalk.get("safe_to_submit") if judge_crosswalk else None
            ),
            "demo_video_draft_mode": demo_video_draft.get("mode") if demo_video_draft else None,
            "demo_video_draft_safe_to_submit": (
                demo_video_draft.get("safe_to_submit") if demo_video_draft else None
            ),
            "post_credential_plan_mode": post_credential_plan.get("mode") if post_credential_plan else None,
            "post_credential_plan_validators": {
                "validate_b2_evidence": "validate_b2_evidence" in post_credential_command_ids,
                "validate_final_evidence": "validate_final_evidence" in post_credential_command_ids,
            },
            "post_credential_plan_required_sequence": post_credential_sequence_ok,
            "post_credential_plan_secret_policy_safe": post_credential_secret_policy_ok,
            "submission_bundle": {
                "safe_to_share": submission_bundle.get("safe_to_share") if submission_bundle else None,
                "safe_to_submit": submission_bundle.get("safe_to_submit") if submission_bundle else None,
                "gate_mode": (
                    submission_bundle_gate.get("mode") if submission_bundle else None
                ),
                "required_artifacts_present": submission_bundle_required_artifacts_ok,
                "missing_artifacts": len(submission_bundle_missing_artifacts),
                "artifact_count": len(submission_bundle_artifacts),
            },
            "demo_video_draft_mp4": {
                "status": demo_video_draft_mp4_result.get("status"),
                "bytes": demo_video_draft_mp4_result.get("bytes"),
                "content_type": demo_video_draft_mp4_result.get("content_type"),
            },
            "html_markers": html_markers,
        },
        "urls": {
            "space_api": api_url,
            "runtime_api": runtime_url,
            "raw_handoff_report": handoff_url,
            "raw_event_snapshot": event_snapshot_url,
            "raw_launch_plan": launch_plan_url,
            "raw_b2_key_scope_checklist": b2_key_scope_checklist_url,
            "raw_judge_brief": judge_brief_url,
            "raw_judge_crosswalk": judge_crosswalk_url,
            "raw_demo_video_draft": demo_video_draft_url,
            "demo_video_draft_mp4": demo_video_draft_mp4_url,
            "raw_post_credential_plan": post_credential_plan_url,
            "raw_submission_bundle": submission_bundle_url,
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
    if "raw_event_snapshot" in failed:
        actions.append("Regenerate and upload docs/assets/devpost-event-snapshot.json to the Space.")
    if "raw_launch_plan" in failed:
        actions.append("Regenerate and upload docs/assets/final-launch-plan.json to the Space.")
    if "raw_b2_key_scope_checklist" in failed:
        actions.append("Regenerate and upload docs/assets/b2-key-scope-checklist.json to the Space.")
    if "raw_judge_brief" in failed:
        actions.append("Regenerate and upload docs/assets/judge-brief.json to the Space.")
    if "raw_judge_crosswalk" in failed:
        actions.append("Regenerate and upload docs/assets/judge-crosswalk.json to the Space.")
    if "raw_recording_assets" in failed:
        actions.append("Regenerate and upload docs/assets/recording-assets.json to the Space.")
    if "raw_demo_video_draft" in failed:
        actions.append("Regenerate and upload docs/assets/demo-video-draft.json to the Space.")
    if "public_demo_video_draft_mp4" in failed:
        actions.append("Regenerate and upload docs/assets/proofframe-demo-draft.mp4 to the Space.")
    if "raw_devpost_form_kit" in failed:
        actions.append("Regenerate and upload docs/assets/devpost-form-kit.json to the Space.")
    if "raw_submit_checklist" in failed:
        actions.append("Regenerate and upload docs/assets/devpost-submission-checklist.json to the Space.")
    if "raw_post_credential_plan" in failed:
        actions.append("Regenerate and upload docs/assets/post-credential-live-proof-plan.json to the Space.")
    if "raw_submission_bundle" in failed:
        actions.append("Regenerate and upload docs/assets/submission-bundle-manifest.json to the Space.")
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
