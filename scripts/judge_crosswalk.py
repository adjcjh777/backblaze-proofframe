#!/usr/bin/env python3
"""Build a judge-facing crosswalk from official criteria to ProofFrame evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.judge_crosswalk.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "judge-crosswalk.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "judge-crosswalk.md"

SOURCE_SCHEMAS = {
    "docs/assets/devpost-event-snapshot.json": "proofframe.devpost_event_snapshot.v1",
    "docs/assets/judge-brief.json": "proofframe.judge_brief.v1",
    "docs/assets/sponsor-fit-audit.json": "proofframe.sponsor_fit_audit.v1",
    "docs/assets/award-readiness-report.json": "proofframe.award_readiness.v1",
    "docs/assets/final-submission-control.json": "proofframe.final_submission_control.v1",
}

REQUIRED_EVIDENCE_FILES = [
    "README.md",
    "docs/prd.md",
    "docs/spec.md",
    "docs/sponsor_fit_matrix.md",
    "docs/assets/devpost-form-kit.md",
    "docs/assets/devpost-submission-checklist.md",
    "docs/assets/public-video-check.md",
    "apps/web/index.html",
    "scripts/run_b2_live_proof.py",
    "scripts/run_final_live_proof.py",
    "scripts/submission_audit.py",
]

DEFAULT_CRITERIA = [
    "Real-world Utility",
    "Production Readiness",
    "B2 Storage + Data Orchestration",
    "Use of Genblaze",
]

SUBMISSION_REQUIREMENT_LABELS = {
    "working_app_url": "Working application URL",
    "github_repo_url": "GitHub repository URL",
    "demo_video": "Demonstration video",
    "video_under_three_minutes": "Video under three minutes",
    "public_video_host": "Public video host",
    "b2_usage": "Backblaze B2 usage",
    "genblaze_usage": "Genblaze usage",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def task_statuses(root: Path) -> dict[str, str]:
    data = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in data.get("tasks", [])
    }


def source_record(root: Path, relative_path: str, expected_schema: str) -> dict[str, Any]:
    report = load_json(root / relative_path)
    actual_schema = report.get("schema") if report else None
    return {
        "path": relative_path,
        "present": report is not None,
        "expected_schema": expected_schema,
        "actual_schema": actual_schema,
        "ok": report is not None and actual_schema == expected_schema,
    }


def source_reports(root: Path) -> list[dict[str, Any]]:
    return [
        source_record(root, relative_path, schema)
        for relative_path, schema in SOURCE_SCHEMAS.items()
    ]


def evidence_file_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for relative_path in REQUIRED_EVIDENCE_FILES:
        path = root / relative_path
        records.append({"path": relative_path, "present": path.exists()})
    return records


def official_criteria(event_snapshot: dict[str, Any] | None) -> list[dict[str, Any]]:
    criteria = (event_snapshot or {}).get("rules", {}).get("judging_criteria") or []
    if not criteria:
        return [{"name": name, "present": False} for name in DEFAULT_CRITERIA]
    return [
        {"name": str(item.get("name", "")), "present": bool(item.get("present"))}
        for item in criteria
    ]


def criterion_present(criteria: list[dict[str, Any]], name: str) -> bool:
    return any(item["name"] == name and item["present"] for item in criteria)


def blocking_items(final_control: dict[str, Any] | None) -> list[dict[str, str]]:
    return [
        {
            "id": str(item.get("id", "")),
            "label": str(item.get("label", "")),
            "detail": str(item.get("detail", "")),
            "evidence": str(item.get("evidence", "")),
        }
        for item in (final_control or {}).get("blocking_items", [])
    ]


def requirement_crosswalk(event_snapshot: dict[str, Any] | None) -> list[dict[str, Any]]:
    requirements = (event_snapshot or {}).get("rules", {}).get("requirements") or {}
    evidence = {
        "working_app_url": "Public mock demo URL in README and Devpost form kit",
        "github_repo_url": "Public GitHub repository and submission bundle manifest",
        "demo_video": "Public video check and storyboard reports; final URL still gated",
        "video_under_three_minutes": "Demo storyboard duration gate",
        "public_video_host": "Public video check URL rules",
        "b2_usage": "B2 adapter, B2 live setup record, and T020 live proof runner",
        "genblaze_usage": "Genblaze provider adapter and T021 final live proof runner",
    }
    return [
        {
            "id": requirement_id,
            "label": SUBMISSION_REQUIREMENT_LABELS.get(requirement_id, requirement_id),
            "official_marker_present": bool(present),
            "evidence": evidence.get(requirement_id, "Tracked in submission docs."),
        }
        for requirement_id, present in requirements.items()
    ]


def row(
    *,
    criterion_id: str,
    criterion: str,
    official_present: bool,
    evidence: list[str],
    safe_claim: str,
    final_gate: str,
    demo_shot: str,
    readiness: str,
) -> dict[str, Any]:
    return {
        "id": criterion_id,
        "criterion": criterion,
        "official_present": official_present,
        "readiness": readiness,
        "evidence": evidence,
        "safe_claim": safe_claim,
        "final_gate": final_gate,
        "demo_shot": demo_shot,
    }


def build_rows(criteria: list[dict[str, Any]], statuses: dict[str, str]) -> list[dict[str, Any]]:
    b2_done = statuses.get("T020") == "done"
    genblaze_done = statuses.get("T021") == "done"
    return [
        row(
            criterion_id="real_world_utility",
            criterion="Real-world Utility",
            official_present=criterion_present(criteria, "Real-world Utility"),
            readiness="public_mock_ready",
            evidence=[
                "docs/prd.md",
                "docs/spec.md",
                "apps/web/index.html",
                "docs/assets/judge-brief.md",
                "Downloadable evidence ZIP from /api/campaigns/{id}/packet.zip",
            ],
            safe_claim=(
                "ProofFrame is a working provenance and review desk for generated media, "
                "with the public demo running in credential-free local/mock mode."
            ),
            final_gate="Final video must show one creator workflow end-to-end with live proof context.",
            demo_shot="Judge Demo packet, asset review, approval state, manifest preview, evidence ZIP.",
        ),
        row(
            criterion_id="production_readiness",
            criterion="Production Readiness",
            official_present=criterion_present(criteria, "Production Readiness"),
            readiness="pre_live_fail_closed",
            evidence=[
                ".github/workflows/ci.yml",
                "scripts/secret_scan.py",
                "scripts/claim_lint.py",
                "scripts/final_submission_control.py",
                "scripts/submission_audit.py",
            ],
            safe_claim=(
                "The repo has fail-closed readiness gates, CI checks, secret scanning, "
                "claim linting, and generated submission reports."
            ),
            final_gate="T041A secret scan, T041 strict audit, and T042 receipt must close before submit.",
            demo_shot="Final gate dashboard and judge recording slate showing current safe-to-submit state.",
        ),
        row(
            criterion_id="b2_storage_data_orchestration",
            criterion="B2 Storage + Data Orchestration",
            official_present=criterion_present(criteria, "B2 Storage + Data Orchestration"),
            readiness="live_verified" if b2_done else "code_ready_live_proof_pending",
            evidence=[
                "src/proofframe/storage.py",
                "docs/assets/b2-live-setup.md",
                "scripts/run_b2_live_proof.py",
                "docs/assets/live-credential-handoff.md",
                "docs/assets/final-submission-control.md",
            ],
            safe_claim=(
                "ProofFrame includes B2-compatible storage paths and B2-ready manifests; "
                "completed live B2 proof is not claimed until T020 is done."
            ),
            final_gate="T020 must capture sanitized B2 asset and manifest object keys plus checksums.",
            demo_shot="B2 Object Route and manifest checksum fields in the first-screen evidence model.",
        ),
        row(
            criterion_id="use_of_genblaze",
            criterion="Use of Genblaze",
            official_present=criterion_present(criteria, "Use of Genblaze"),
            readiness="live_verified" if genblaze_done else "adapter_ready_live_proof_pending",
            evidence=[
                "src/proofframe/providers.py",
                "scripts/run_final_live_proof.py",
                ".env.final.example",
                "docs/assets/live-credential-handoff.md",
                "docs/assets/devpost-submission-packet.md",
            ],
            safe_claim=(
                "ProofFrame includes a Genblaze-compatible provider path and manifest fields; "
                "completed live Genblaze proof is not claimed until T021 is done."
            ),
            final_gate="T021 must capture live provider/model metadata from the final Genblaze path.",
            demo_shot="Genblaze Step, provider/model metadata, and prompt lineage in the manifest preview.",
        ),
    ]


def build_crosswalk(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    reports = {
        relative_path: load_json(root / relative_path)
        for relative_path in SOURCE_SCHEMAS
    }
    event_snapshot = reports["docs/assets/devpost-event-snapshot.json"]
    final_control = reports["docs/assets/final-submission-control.json"]
    judge_brief = reports["docs/assets/judge-brief.json"]
    sponsor_audit = reports["docs/assets/sponsor-fit-audit.json"]
    award = reports["docs/assets/award-readiness-report.json"]
    statuses = task_statuses(root)
    sources = source_reports(root)
    evidence_files = evidence_file_records(root)
    criteria = official_criteria(event_snapshot)
    source_ok = all(item["ok"] for item in sources)
    evidence_ok = all(item["present"] for item in evidence_files)
    official_ok = bool((event_snapshot or {}).get("validation", {}).get("ok")) and all(
        item["present"] for item in criteria
    )
    safe_to_submit = bool((final_control or {}).get("safe_to_submit"))
    ok = source_ok and evidence_ok and official_ok
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": (
            "final_crosswalk_ready"
            if ok and safe_to_submit
            else "pre_live_crosswalk_ready"
            if ok
            else "needs_crosswalk_sources"
        ),
        "ok": ok,
        "safe_to_submit": safe_to_submit,
        "event": {
            "name": (event_snapshot or {}).get("event", {}).get("name", "Backblaze Generative Media Hackathon"),
            "deadline_utc": (event_snapshot or {}).get("event", {}).get("deadline_utc"),
            "deadline_beijing": (event_snapshot or {}).get("event", {}).get("deadline_beijing"),
            "devpost_url": (event_snapshot or {}).get("event", {}).get("devpost_url"),
            "rules_url": (event_snapshot or {}).get("event", {}).get("rules_url"),
        },
        "source_reports": sources,
        "missing_evidence_files": [item["path"] for item in evidence_files if not item["present"]],
        "official_criteria": criteria,
        "submission_requirements": requirement_crosswalk(event_snapshot),
        "rows": build_rows(criteria, statuses),
        "summary": {
            "judge_brief_safe_to_submit": (judge_brief or {}).get("status", {}).get("safe_to_submit"),
            "sponsor_fit_mode": (sponsor_audit or {}).get("mode"),
            "sponsor_fit_ok": (sponsor_audit or {}).get("ok"),
            "award_score": (award or {}).get("score"),
            "award_max_score": (award or {}).get("max_score"),
            "final_control_mode": (final_control or {}).get("mode"),
        },
        "task_statuses": {
            task_id: statuses.get(task_id, "missing")
            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "blocking_items": blocking_items(final_control),
        "claim_boundaries": [
            "Do not claim completed B2 live storage until T020 is done and evidence is sanitized.",
            "Do not claim completed Genblaze live generation until T021 is done and provider/model metadata is captured.",
            "Do not mark safe_to_submit true until public video, strict audit, final secret scan, and Devpost receipt are complete.",
        ],
        "next_actions": [
            "Use this crosswalk as the judge-facing map while recording the final video and filling Devpost.",
            "After T020/T021 and the public video URL are ready, rerun final reports and regenerate this crosswalk.",
            "Submit only after final_submission_control.py --strict-final and submission_audit.py --strict-final pass.",
        ],
    }


def compact_list(items: list[str]) -> str:
    return "<br>".join(f"`{item}`" if item.startswith(("docs/", "scripts/", "src/", "apps/", ".github/")) else item for item in items)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Judge Crosswalk",
        "",
        f"Created: `{report['created_at']}`",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        f"Event: {report['event']['name']}",
        f"Deadline: `{report['event']['deadline_utc']}` / `{report['event']['deadline_beijing']}`",
        "",
        "## Source Health",
        "",
    ]
    for source in report["source_reports"]:
        marker = "OK" if source["ok"] else "TODO"
        lines.append(
            f"- {marker} `{source['path']}` schema `{source['actual_schema']}` "
            f"(expected `{source['expected_schema']}`)"
        )
    if report["missing_evidence_files"]:
        lines.extend(["", "Missing evidence files:"])
        lines.extend(f"- `{path}`" for path in report["missing_evidence_files"])

    lines.extend(
        [
            "",
            "## Official Requirements",
            "",
            "| Requirement | Official Marker | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for requirement in report["submission_requirements"]:
        marker = "yes" if requirement["official_marker_present"] else "no"
        lines.append(f"| {requirement['label']} | `{marker}` | {requirement['evidence']} |")

    lines.extend(
        [
            "",
            "## Judging Crosswalk",
            "",
            "| Official angle | Current evidence | Safe claim | Final gate | Demo shot |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["rows"]:
        criterion = f"{item['criterion']}<br>`{item['readiness']}`"
        evidence = compact_list(item["evidence"])
        lines.append(
            f"| {criterion} | {evidence} | {item['safe_claim']} | "
            f"{item['final_gate']} | {item['demo_shot']} |"
        )

    lines.extend(["", "## Blocking Items", ""])
    if report["blocking_items"]:
        for item in report["blocking_items"]:
            lines.append(f"- `{item['id']}`: {item['detail']} Evidence: `{item['evidence']}`")
    else:
        lines.append("- None.")

    lines.extend(["", "## Claim Boundaries", ""])
    lines.extend(f"- {item}" for item in report["claim_boundaries"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ProofFrame judge evidence crosswalk.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_crosswalk(args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "safe_to_submit": report["safe_to_submit"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "blocking_items": len(report["blocking_items"]),
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
