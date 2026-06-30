#!/usr/bin/env python3
"""Build a one-page judge decision brief from public-safe ProofFrame reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.judge_decision_brief.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "judge-decision-brief.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "judge-decision-brief.md"
PUBLIC_DEMO_URL = "https://adjcjh-backblaze-proofframe.hf.space/?judge=1"
REPOSITORY_URL = "https://github.com/adjcjh777/backblaze-proofframe"
SPACE_RAW_BASE = "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main"


SOURCE_SPECS = {
    "judge_brief": ("docs/assets/judge-brief.json", "proofframe.judge_brief.v1"),
    "judge_crosswalk": ("docs/assets/judge-crosswalk.json", "proofframe.judge_crosswalk.v1"),
    "judge_evidence_index": ("docs/assets/judge-evidence-index.json", "proofframe.judge_evidence_index.v1"),
    "award_readiness": ("docs/assets/award-readiness-report.json", "proofframe.award_readiness.v1"),
    "final_control": ("docs/assets/final-submission-control.json", "proofframe.final_submission_control.v1"),
    "public_space_sync": ("docs/assets/public-space-sync-report.json", "proofframe.public_space_sync.v1"),
    "devpost_preview": ("docs/assets/devpost-submission-preview.json", "proofframe.devpost_submission_preview.v1"),
    "video_publish_kit": ("docs/assets/final-video-publish-kit.json", "proofframe.final_video_publish_kit.v1"),
    "secret_scan": ("docs/assets/secret-scan-report.json", "proofframe.secret_scan.v1"),
    "event_snapshot": ("docs/assets/devpost-event-snapshot.json", "proofframe.devpost_event_snapshot.v1"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def task_statuses(root: Path) -> dict[str, str]:
    data = load_json(root / "tasks.json")
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in data.get("tasks", [])
        if isinstance(task, dict)
    }


def source_summary(root: Path, source_id: str) -> dict[str, Any]:
    relative_path, expected_schema = SOURCE_SPECS[source_id]
    data = load_json(root / relative_path)
    return {
        "id": source_id,
        "path": relative_path,
        "present": bool(data),
        "schema": data.get("schema"),
        "schema_ok": data.get("schema") == expected_schema,
        "mode": data.get("mode"),
        "ok": data.get("ok"),
        "safe_to_share": data.get("safe_to_share"),
        "safe_to_submit": data.get("safe_to_submit"),
    }


def all_source_schemas_ok(sources: dict[str, dict[str, Any]]) -> bool:
    return all(source.get("schema_ok") is True for source in sources.values())


def source_health_ok(reports: dict[str, dict[str, Any]]) -> bool:
    return bool(
        reports["judge_brief"].get("schema") == "proofframe.judge_brief.v1"
        and reports["judge_crosswalk"].get("ok") is True
        and reports["judge_evidence_index"].get("ok") is True
        and reports["award_readiness"].get("score", 0) >= 75
        and reports["final_control"].get("ok") is True
        and reports["public_space_sync"].get("ok") is True
        and reports["devpost_preview"].get("safe_to_share") is True
        and reports["video_publish_kit"].get("ok") is True
        and reports["secret_scan"].get("ok") is True
        and reports["event_snapshot"].get("validation", {}).get("ok") is True
    )


def evidence_link(index: dict[str, Any], link_id: str) -> str | None:
    for link in index.get("links", []):
        if isinstance(link, dict) and link.get("id") == link_id:
            return link.get("raw_url") or link.get("public_url")
    return None


def raw_space_url(path: str) -> str:
    return f"{SPACE_RAW_BASE}/{path}"


def build_decision_brief(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    reports = {
        source_id: load_json(root / relative_path)
        for source_id, (relative_path, _expected_schema) in SOURCE_SPECS.items()
    }
    sources = {source_id: source_summary(root, source_id) for source_id in SOURCE_SPECS}
    statuses = task_statuses(root)
    control = reports["final_control"]
    evidence_index = reports["judge_evidence_index"]
    award = reports["award_readiness"]
    public_sync = reports["public_space_sync"]
    event_snapshot = reports["event_snapshot"]
    video_kit = reports["video_publish_kit"]
    blocking_items = [
        item.get("id")
        for item in control.get("blocking_items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    safe_to_submit = bool(control.get("safe_to_submit"))
    source_ok = all_source_schemas_ok(sources) and source_health_ok(reports)
    links = {
        "public_demo": reports["judge_brief"].get("links", {}).get("public_demo") or PUBLIC_DEMO_URL,
        "repository": reports["judge_brief"].get("links", {}).get("repository") or REPOSITORY_URL,
        "evidence_index": raw_space_url("docs/assets/judge-evidence-index.md"),
        "criteria_crosswalk": evidence_link(evidence_index, "judge_crosswalk"),
        "award_readiness": evidence_link(evidence_index, "award_readiness"),
        "final_control": evidence_link(evidence_index, "final_submission_control"),
        "video_publish_kit": evidence_link(evidence_index, "final_video_publish_kit"),
    }
    decision_checks = [
        {
            "id": "public_demo_runs",
            "label": "Public judge-mode demo runs in credential-free local/mock mode",
            "ok": public_sync.get("ok") is True,
            "evidence": "docs/assets/public-space-sync-report.json",
        },
        {
            "id": "criteria_are_mapped",
            "label": "Official criteria are mapped to concrete evidence",
            "ok": reports["judge_crosswalk"].get("ok") is True,
            "evidence": "docs/assets/judge-crosswalk.json",
        },
        {
            "id": "award_case_is_competitive",
            "label": "Pre-live award score is competitive",
            "ok": award.get("score", 0) >= 75,
            "evidence": "docs/assets/award-readiness-report.json",
        },
        {
            "id": "claims_are_fail_closed",
            "label": "Public claims are either fail-closed or backed by final control",
            "ok": control.get("ok") is True
            and (
                control.get("safe_to_submit") is False
                or (control.get("safe_to_submit") is True and control.get("mode") == "final_submit_ready")
            ),
            "evidence": "docs/assets/final-submission-control.json",
        },
        {
            "id": "video_submission_is_gated",
            "label": "Final video copy is ready and its submission state is explicit",
            "ok": video_kit.get("ok") is True
            and (
                video_kit.get("safe_to_submit") is False
                or (
                    video_kit.get("safe_to_submit") is True
                    and video_kit.get("mode") == "public_video_ready"
                    and video_kit.get("final_video_ready") is True
                )
            ),
            "evidence": "docs/assets/final-video-publish-kit.json",
        },
        {
            "id": "no_secret_exposure",
            "label": "Public artifact scan is clear",
            "ok": reports["secret_scan"].get("ok") is True,
            "evidence": "docs/assets/secret-scan-report.json",
        },
    ]
    ok = bool(source_ok and all(item["ok"] for item in decision_checks))
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "final_decision_ready" if safe_to_submit else "pre_live_decision_ready",
        "safe_to_share": ok,
        "safe_to_submit": safe_to_submit,
        "project": "ProofFrame",
        "headline": "ProofFrame turns generated media into auditable, approval-ready asset packets.",
        "judge_decision": (
            "Advance this project if you want a generative media submission where Backblaze storage, "
            "Genblaze generation, provenance, review state, and safety gates are the product surface."
        ),
        "why_now": [
            "Most generative media demos stop at output creation; ProofFrame shows the operational layer after generation.",
            "The public demo is live and credential-free, so judges can inspect the workflow immediately.",
            "The remaining blockers are explicit sponsor-proof steps, not ambiguous product gaps.",
        ],
        "top_reasons_to_score_high": [
            "Provenance packet: prompt, provider/model, storage route, checksum, approval state, and risk note travel together.",
            "Production posture: evidence ZIPs, manifest exports, review console, final control tower, and secret scanning are already wired.",
            "Sponsor fit: B2-compatible storage and Genblaze provider paths are implemented, with live proof gated rather than overclaimed.",
            "Submission clarity: judge brief, criteria crosswalk, evidence index, final video kit, and Devpost preview are all generated artifacts.",
        ],
        "current_scores": {
            "award_score": award.get("score"),
            "award_max_score": award.get("max_score"),
            "award_mode": award.get("mode"),
            "final_closure_score": award.get("readiness_interpretation", {}).get("final_closure_score"),
            "final_closure_max_score": award.get("readiness_interpretation", {}).get("final_closure_max_score"),
        },
        "public_state": {
            "space_sync_ok": public_sync.get("ok"),
            "space_mode": public_sync.get("mode"),
            "space_sync_checked_at": public_sync.get("created_at"),
            "event_submission_open": event_snapshot.get("validation", {}).get("submission_open"),
            "participant_count_observed": event_snapshot.get("event", {}).get("participant_count_observed"),
            "final_video_ready": video_kit.get("final_video_ready"),
        },
        "decision_checks": decision_checks,
        "source_reports": sources,
        "task_statuses": {
            task_id: statuses.get(task_id, "missing")
            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "final_blockers": blocking_items,
        "links": links,
        "claim_boundary": (
            "This brief is public-safe and decision-oriented. It does not claim completed Backblaze B2 "
            "or Genblaze live proof until final_submission_control.safe_to_submit is true."
        ),
        "next_actions": [
            "Use this brief as the top-level judge handoff before opening the public demo.",
            "After live B2 and Genblaze proof, regenerate final control, video publish kit, and this brief.",
            "After Devpost submission, regenerate receipt, closeout reports, submission bundle, and this brief.",
        ],
    }


def render_markdown(brief: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Judge Decision Brief",
        "",
        f"Mode: `{brief['mode']}`",
        f"OK: `{str(brief['ok']).lower()}`",
        f"Safe to submit: `{str(brief['safe_to_submit']).lower()}`",
        f"Created: `{brief['created_at']}`",
        "",
        brief["headline"],
        "",
        "## Judge Decision",
        "",
        brief["judge_decision"],
        "",
        "## Why Now",
        "",
    ]
    lines.extend(f"- {item}" for item in brief["why_now"])
    lines.extend(["", "## Top Reasons To Score High", ""])
    lines.extend(f"- {item}" for item in brief["top_reasons_to_score_high"])
    scores = brief["current_scores"]
    public_state = brief["public_state"]
    lines.extend(
        [
            "",
            "## Current Scores",
            "",
            f"- Award readiness: `{scores['award_score']}/{scores['award_max_score']}` ({scores['award_mode']})",
            f"- Final closure: `{scores['final_closure_score']}/{scores['final_closure_max_score']}`",
            "",
            "## Public State",
            "",
            f"- Space mode: `{public_state['space_mode']}`",
            f"- Space sync checked: `{public_state['space_sync_checked_at']}`",
            f"- Devpost submission open: `{public_state['event_submission_open']}`",
            f"- Observed participants: `{public_state['participant_count_observed']}`",
            f"- Final video ready: `{str(public_state['final_video_ready']).lower()}`",
            "",
            "## Decision Checks",
            "",
        ]
    )
    for item in brief["decision_checks"]:
        status = "OK" if item["ok"] else "PENDING"
        lines.append(f"- {status} `{item['id']}`: {item['label']} (`{item['evidence']}`)")
    lines.extend(["", "## Final Blockers", ""])
    if brief["final_blockers"]:
        lines.extend(f"- `{item}`" for item in brief["final_blockers"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Links", ""])
    for key, value in brief["links"].items():
        if value:
            lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Claim Boundary", "", brief["claim_boundary"], "", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in brief["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(brief: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(brief), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ProofFrame judge decision brief.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    brief = build_decision_brief(args.root)
    write_outputs(brief, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": brief["ok"],
                "mode": brief["mode"],
                "safe_to_submit": brief["safe_to_submit"],
                "checks": len(brief["decision_checks"]),
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )
    if not brief["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
