#!/usr/bin/env python3
"""Build a public-safe index of judge-facing ProofFrame evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.judge_evidence_index.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "judge-evidence-index.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "judge-evidence-index.md"
SPACE_ID = "ADJCJH/backblaze-proofframe"
PUBLIC_DEMO_URL = "https://adjcjh-backblaze-proofframe.hf.space/?judge=1"

LINKS = [
    (
        "public_demo",
        "Open the public judge-mode demo",
        "app",
        PUBLIC_DEMO_URL,
        None,
        "Start here: live credential-free ProofFrame workflow.",
    ),
    (
        "judge_brief",
        "30-second judge brief",
        "report",
        None,
        "docs/assets/judge-brief.md",
        "Concise product story, safe claims, and current status.",
    ),
    (
        "judge_crosswalk",
        "Official criteria crosswalk",
        "report",
        None,
        "docs/assets/judge-crosswalk.md",
        "Maps Devpost criteria to concrete evidence and final gates.",
    ),
    (
        "judge_decision_brief",
        "Judge decision brief",
        "report",
        None,
        "docs/assets/judge-decision-brief.md",
        "One-page decision card with reasons to score high, public state, and final blockers.",
    ),
    (
        "final_submission_control",
        "Final submission control",
        "gate",
        None,
        "docs/assets/final-submission-control.md",
        "Top-level control health, safe_to_submit, and remaining blockers.",
    ),
    (
        "devpost_preview",
        "Devpost submission preview",
        "submission",
        None,
        "docs/assets/devpost-submission-preview.md",
        "Public-safe one-page Devpost field and evidence preview.",
    ),
    (
        "submission_checklist",
        "Devpost submit checklist",
        "gate",
        None,
        "docs/assets/devpost-submission-checklist.md",
        "Field, video, proof, and final receipt gate.",
    ),
    (
        "submission_bundle",
        "Submission bundle manifest",
        "bundle",
        None,
        "docs/assets/submission-bundle-manifest.md",
        "Shareable artifact index and final bundle gate.",
    ),
    (
        "award_readiness",
        "Award readiness scorecard",
        "scorecard",
        None,
        "docs/assets/award-readiness-report.md",
        "Sponsor-fit and product-readiness score with final closure separated.",
    ),
    (
        "public_space_sync",
        "Public Space sync report",
        "verification",
        None,
        "docs/assets/public-space-sync-report.md",
        "Verifies HF Space runtime, raw artifacts, and public API markers.",
    ),
    (
        "recording_assets",
        "Recording runbook",
        "video",
        None,
        "docs/assets/recording-assets.md",
        "Shot list and public-safe recording assets for the final demo.",
    ),
    (
        "demo_video_draft",
        "Mock demo video draft",
        "video",
        None,
        "docs/assets/demo-video-draft.md",
        "Public-safe draft video status; final video remains gated.",
    ),
    (
        "final_video_publish_kit",
        "Final video publish kit",
        "video",
        None,
        "docs/assets/final-video-publish-kit.md",
        "Upload title, description, chapters, host rules, and Devpost video field gate.",
    ),
    (
        "public_video_check",
        "Public video check",
        "gate",
        None,
        "docs/assets/public-video-check.md",
        "Official-host and final-video readiness gate.",
    ),
    (
        "b2_key_scope_checklist",
        "B2 key scope checklist",
        "live-proof",
        None,
        "docs/assets/b2-key-scope-checklist.md",
        "No-secret Backblaze key scope and user confirmation requirements.",
    ),
    (
        "post_credential_live_proof",
        "Post-credential live proof plan",
        "live-proof",
        None,
        "docs/assets/post-credential-live-proof-plan.md",
        "Exact no-secret sequence to close B2 and Genblaze proof.",
    ),
    (
        "secret_scan",
        "Secret scan report",
        "safety",
        None,
        "docs/assets/secret-scan-report.md",
        "Current public artifact secret-scan state.",
    ),
]

SECTION_LINKS = {
    "start_here": ["public_demo", "judge_brief", "judge_crosswalk", "judge_decision_brief"],
    "submission_controls": [
        "final_submission_control",
        "devpost_preview",
        "submission_checklist",
        "submission_bundle",
    ],
    "award_case": ["award_readiness", "public_space_sync", "secret_scan"],
    "recording": ["recording_assets", "demo_video_draft", "final_video_publish_kit", "public_video_check"],
    "live_proof_gates": ["b2_key_scope_checklist", "post_credential_live_proof"],
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


def raw_file_url(relative_path: str) -> str:
    return f"https://huggingface.co/spaces/{SPACE_ID}/raw/main/{relative_path}"


def link_record(root: Path, link: tuple[str, str, str, str | None, str | None, str]) -> dict[str, Any]:
    link_id, label, kind, public_url, path, purpose = link
    record: dict[str, Any] = {
        "id": link_id,
        "label": label,
        "kind": kind,
        "purpose": purpose,
        "public_url": public_url,
        "path": path,
        "raw_url": raw_file_url(path) if path else public_url,
        "present": True,
    }
    if path:
        artifact_path = root / path
        record["present"] = artifact_path.exists()
        record["bytes"] = artifact_path.stat().st_size if artifact_path.exists() else 0
    return record


def build_sections(links_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    labels = {
        "start_here": "Start Here",
        "submission_controls": "Submission Controls",
        "award_case": "Award Case",
        "recording": "Recording",
        "live_proof_gates": "Live Proof Gates",
    }
    for section_id, link_ids in SECTION_LINKS.items():
        section_links = [links_by_id[link_id] for link_id in link_ids]
        sections.append(
            {
                "id": section_id,
                "label": labels[section_id],
                "links": link_ids,
                "ready": all(link["present"] for link in section_links),
            }
        )
    return sections


def build_index(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    judge_brief = load_json(root / "docs" / "assets" / "judge-brief.json")
    judge_crosswalk = load_json(root / "docs" / "assets" / "judge-crosswalk.json")
    control = load_json(root / "docs" / "assets" / "final-submission-control.json")
    public_sync = load_json(root / "docs" / "assets" / "public-space-sync-report.json")
    award = load_json(root / "docs" / "assets" / "award-readiness-report.json")
    secret_scan = load_json(root / "docs" / "assets" / "secret-scan-report.json")
    devpost_preview = load_json(root / "docs" / "assets" / "devpost-submission-preview.json")
    statuses = task_statuses(root)
    links = [link_record(root, link) for link in LINKS]
    links_by_id = {link["id"]: link for link in links}
    blocking_items = [
        item.get("id")
        for item in control.get("blocking_items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    safe_to_submit = bool(control.get("safe_to_submit"))
    control_health_ok = bool(control.get("control_health_ok", control.get("ok")))
    source_health = {
        "judge_brief": judge_brief.get("schema") == "proofframe.judge_brief.v1",
        "judge_crosswalk": judge_crosswalk.get("schema") == "proofframe.judge_crosswalk.v1",
        "final_submission_control": control.get("schema") == "proofframe.final_submission_control.v1",
        "public_space_sync": public_sync.get("schema") == "proofframe.public_space_sync.v1"
        and public_sync.get("ok") is True,
        "secret_scan": secret_scan.get("schema") == "proofframe.secret_scan.v1"
        and secret_scan.get("ok") is True,
        "devpost_preview": devpost_preview.get("schema") == "proofframe.devpost_submission_preview.v1"
        and devpost_preview.get("safe_to_share") is True,
    }
    ok = control_health_ok and all(source_health.values()) and all(link["present"] for link in links)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "final_evidence_index_ready" if safe_to_submit else "pre_live_evidence_index_ready",
        "safe_to_share": ok,
        "safe_to_submit": safe_to_submit,
        "project": judge_brief.get("project", "ProofFrame"),
        "public_demo_url": (judge_brief.get("links") or {}).get("public_demo", PUBLIC_DEMO_URL),
        "repository_url": (judge_brief.get("links") or {}).get(
            "repository",
            "https://github.com/adjcjh777/backblaze-proofframe",
        ),
        "status": {
            "control_health_ok": control_health_ok,
            "award_score": award.get("score"),
            "award_max_score": award.get("max_score"),
            "public_space_mode": public_sync.get("mode"),
            "final_blocker_count": len(blocking_items),
            "final_blockers": blocking_items,
        },
        "source_health": source_health,
        "task_statuses": {
            task_id: statuses.get(task_id, "missing")
            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "links": links,
        "sections": build_sections(links_by_id),
        "claim_boundary": (
            "This index is public-safe evidence navigation. It does not claim completed B2 or "
            "Genblaze live proof until final_submission_control.safe_to_submit is true."
        ),
    }


def render_markdown(index: dict[str, Any]) -> str:
    links_by_id = {link["id"]: link for link in index["links"]}
    lines = [
        "# ProofFrame Judge Evidence Index",
        "",
        f"Mode: `{index['mode']}`",
        f"OK: `{str(index['ok']).lower()}`",
        f"Safe to submit: `{str(index['safe_to_submit']).lower()}`",
        f"Created: `{index['created_at']}`",
        f"Public demo: {index['public_demo_url']}",
        f"Repository: {index['repository_url']}",
        "",
        "## Status",
        "",
        f"- Control health OK: `{str(index['status']['control_health_ok']).lower()}`",
        f"- Award readiness: `{index['status']['award_score']}/{index['status']['award_max_score']}`",
        f"- Public Space: `{index['status']['public_space_mode']}`",
        f"- Final blockers: `{index['status']['final_blocker_count']}`",
        "",
        "## Sections",
        "",
    ]
    for section in index["sections"]:
        lines.extend([f"### {section['label']}", ""])
        for link_id in section["links"]:
            link = links_by_id[link_id]
            target = link["raw_url"] or link["public_url"]
            status = "OK" if link["present"] else "MISSING"
            lines.append(f"- {status} [{link['label']}]({target}) - {link['purpose']}")
        lines.append("")
    lines.extend(["## Final Blockers", ""])
    if index["status"]["final_blockers"]:
        lines.extend(f"- `{item}`" for item in index["status"]["final_blockers"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Claim Boundary", "", index["claim_boundary"], ""])
    return "\n".join(lines)


def write_outputs(index: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(index), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the public-safe ProofFrame judge evidence index.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    index = build_index(args.root)
    write_outputs(index, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": index["ok"],
                "mode": index["mode"],
                "safe_to_submit": index["safe_to_submit"],
                "links": len(index["links"]),
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )
    if not index["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
