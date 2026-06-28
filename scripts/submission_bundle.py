#!/usr/bin/env python3
"""Build a safe, judge-facing evidence bundle manifest for Devpost submission."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "submission-bundle-manifest.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "submission-bundle-manifest.md"

ARTIFACTS = [
    ("repo_readme", "README.md", "Core public project overview"),
    ("dockerfile", "Dockerfile", "Docker deployment image contract"),
    ("prd", "docs/prd.md", "Product requirements"),
    ("technical_spec", "docs/spec.md", "Implementation specification"),
    ("deployment_runbook", "docs/deployment.md", "Public demo deployment runbook"),
    ("devpost_draft", "docs/devpost_draft.md", "Copy-ready Devpost fields"),
    ("devpost_packet_json", "docs/assets/devpost-submission-packet.json", "Machine-readable Devpost copy"),
    ("devpost_packet_md", "docs/assets/devpost-submission-packet.md", "Human-readable Devpost copy"),
    ("devpost_event_snapshot_script", "scripts/devpost_event_snapshot.py", "Official Devpost event snapshot checker"),
    ("devpost_event_snapshot_json", "docs/assets/devpost-event-snapshot.json", "Machine-readable Devpost event snapshot"),
    ("devpost_event_snapshot_md", "docs/assets/devpost-event-snapshot.md", "Human-readable Devpost event snapshot"),
    ("agent_handoff_script", "scripts/agent_handoff_check.py", "Agent Bus and Codex handoff path checker"),
    ("agent_handoff_json", "docs/assets/agent-handoff-report.json", "Machine-readable Agent handoff report"),
    ("agent_handoff_md", "docs/assets/agent-handoff-report.md", "Human-readable Agent handoff report"),
    ("public_space_sync_script", "scripts/public_space_sync.py", "Public Hugging Face Space sync verifier"),
    ("public_space_sync_json", "docs/assets/public-space-sync-report.json", "Machine-readable public Space sync report"),
    ("public_space_sync_md", "docs/assets/public-space-sync-report.md", "Human-readable public Space sync report"),
    ("public_demo_screenshot_script", "scripts/public_demo_screenshot.py", "Public judge-mode screenshot verifier"),
    ("public_demo_screenshot_json", "docs/assets/public-demo-screenshot-report.json", "Machine-readable public screenshot report"),
    ("public_demo_screenshot_md", "docs/assets/public-demo-screenshot-report.md", "Human-readable public screenshot report"),
    ("devpost_form_kit_script", "scripts/devpost_form_kit.py", "Field-by-field Devpost form kit"),
    ("devpost_form_kit_json", "docs/assets/devpost-form-kit.json", "Machine-readable Devpost form kit"),
    ("devpost_form_kit_md", "docs/assets/devpost-form-kit.md", "Human-readable Devpost form kit"),
    ("devpost_submission_checklist_script", "scripts/devpost_submission_checklist.py", "No-secret final Devpost web submission checklist"),
    ("devpost_submission_checklist_json", "docs/assets/devpost-submission-checklist.json", "Machine-readable final Devpost submission checklist"),
    ("devpost_submission_checklist_md", "docs/assets/devpost-submission-checklist.md", "Human-readable final Devpost submission checklist"),
    ("judge_brief_script", "scripts/judge_brief.py", "Public-safe 30-second judge brief"),
    ("judge_brief_json", "docs/assets/judge-brief.json", "Machine-readable judge brief"),
    ("judge_brief_md", "docs/assets/judge-brief.md", "Human-readable judge brief"),
    ("judge_crosswalk_script", "scripts/judge_crosswalk.py", "Official criteria to evidence crosswalk"),
    ("judge_crosswalk_json", "docs/assets/judge-crosswalk.json", "Machine-readable judge crosswalk"),
    ("judge_crosswalk_md", "docs/assets/judge-crosswalk.md", "Human-readable judge crosswalk"),
    ("frontend_ui", "apps/web/index.html", "Browser proof ledger UI"),
    ("demo_script", "docs/demo_script.md", "Video shot list and narration"),
    ("demo_storyboard_script", "scripts/demo_storyboard.py", "Machine-checked demo video storyboard"),
    ("demo_storyboard_json", "docs/assets/demo-storyboard.json", "Machine-readable demo storyboard"),
    ("demo_storyboard_md", "docs/assets/demo-storyboard.md", "Human-readable demo storyboard"),
    ("demo_video_draft_script", "scripts/demo_video_draft.py", "Mock demo video draft builder"),
    ("demo_video_draft_json", "docs/assets/demo-video-draft.json", "Machine-readable demo video draft report"),
    ("demo_video_draft_md", "docs/assets/demo-video-draft.md", "Human-readable demo video draft report"),
    ("demo_video_draft_mp4", "docs/assets/proofframe-demo-draft.mp4", "Public-safe mock demo video draft"),
    ("public_video_check_script", "scripts/public_video_check.py", "Public demo video URL verifier"),
    ("public_video_check_json", "docs/assets/public-video-check.json", "Machine-readable public video check"),
    ("public_video_check_md", "docs/assets/public-video-check.md", "Human-readable public video check"),
    ("sponsor_fit_matrix", "docs/sponsor_fit_matrix.md", "Sponsor judging matrix and claim boundary"),
    ("sponsor_fit_audit_script", "scripts/sponsor_fit_audit.py", "Sponsor-fit clarity audit"),
    ("sponsor_fit_audit_json", "docs/assets/sponsor-fit-audit.json", "Machine-readable sponsor-fit audit"),
    ("sponsor_fit_audit_md", "docs/assets/sponsor-fit-audit.md", "Human-readable sponsor-fit audit"),
    ("award_readiness_script", "scripts/award_readiness.py", "Judge-facing award readiness scorecard"),
    ("award_readiness_json", "docs/assets/award-readiness-report.json", "Machine-readable award readiness report"),
    ("award_readiness_md", "docs/assets/award-readiness-report.md", "Human-readable award readiness report"),
    ("final_submission_control_script", "scripts/final_submission_control.py", "Final submission control tower"),
    ("final_submission_control_json", "docs/assets/final-submission-control.json", "Machine-readable final control report"),
    ("final_submission_control_md", "docs/assets/final-submission-control.md", "Human-readable final control report"),
    ("final_operator_brief_script", "scripts/final_operator_brief.py", "No-secret final operator brief"),
    ("final_operator_brief_json", "docs/assets/final-operator-brief.json", "Machine-readable final operator brief"),
    ("final_operator_brief_md", "docs/assets/final-operator-brief.md", "Human-readable final operator brief"),
    ("final_launch_plan_script", "scripts/final_launch_plan.py", "No-secret final launch phase plan"),
    ("final_launch_plan_json", "docs/assets/final-launch-plan.json", "Machine-readable final launch plan"),
    ("final_launch_plan_md", "docs/assets/final-launch-plan.md", "Human-readable final launch plan"),
    ("final_rehearsal_script", "scripts/final_rehearsal.py", "No-secret final submission rehearsal checklist"),
    ("final_rehearsal_json", "docs/assets/final-rehearsal-checklist.json", "Machine-readable final rehearsal checklist"),
    ("final_rehearsal_md", "docs/assets/final-rehearsal-checklist.md", "Human-readable final rehearsal checklist"),
    ("submission_audit_script", "scripts/submission_audit.py", "Pre-submit audit gate"),
    ("submission_audit_json", "docs/assets/submission-audit-report.json", "Machine-readable submission audit report"),
    ("submission_audit_md", "docs/assets/submission-audit-report.md", "Human-readable submission audit report"),
    ("devpost_receipt_script", "scripts/devpost_submission_receipt.py", "Public-safe Devpost submission receipt generator"),
    ("devpost_receipt_json", "docs/assets/devpost-submission-receipt.json", "Machine-readable Devpost submission receipt"),
    ("devpost_receipt_md", "docs/assets/devpost-submission-receipt.md", "Human-readable Devpost submission receipt"),
    ("evidence_package", "docs/evidence_package.md", "Evidence package plan"),
    ("public_claim_freeze", "docs/public_claim_freeze.md", "Verified-claim boundary"),
    ("verification_runbook", "docs/verification.md", "Local, CI, Docker, and live proof runbook"),
    ("final_env_template", ".env.final.example", "Redacted final B2 plus Genblaze env template"),
    ("secret_scan_script", "scripts/secret_scan.py", "Final secret scanner"),
    ("secret_scan_json", "docs/assets/secret-scan-report.json", "Machine-readable secret scan report"),
    ("secret_scan_md", "docs/assets/secret-scan-report.md", "Human-readable secret scan report"),
    ("b2_live_setup_json", "docs/assets/b2-live-setup.json", "Non-secret B2 bucket setup record"),
    ("b2_live_setup_md", "docs/assets/b2-live-setup.md", "Human-readable B2 bucket setup record"),
    ("b2_key_scope_checklist_script", "scripts/b2_key_scope_checklist.py", "No-secret Backblaze B2 application key scope checklist"),
    ("b2_key_scope_checklist_json", "docs/assets/b2-key-scope-checklist.json", "Machine-readable B2 key scope checklist"),
    ("b2_key_scope_checklist_md", "docs/assets/b2-key-scope-checklist.md", "Human-readable B2 key scope checklist"),
    ("b2_live_runner", "scripts/run_b2_live_proof.py", "One-command B2 storage proof runner"),
    ("live_env_handoff_script", "scripts/live_env_handoff.py", "Redacted live credential handoff gate"),
    ("live_env_handoff_json", "docs/assets/live-credential-handoff.json", "Machine-readable live credential handoff"),
    ("live_env_handoff_md", "docs/assets/live-credential-handoff.md", "Human-readable live credential handoff"),
    ("final_env_wizard", "scripts/final_env_wizard.py", "Local final credential env wizard"),
    ("post_credential_live_proof_script", "scripts/post_credential_live_proof.py", "Post-credential live proof sequence runner"),
    ("post_credential_live_proof_json", "docs/assets/post-credential-live-proof-plan.json", "Machine-readable post-credential live proof plan"),
    ("post_credential_live_proof_md", "docs/assets/post-credential-live-proof-plan.md", "Human-readable post-credential live proof plan"),
    ("public_claim_lint", "scripts/claim_lint.py", "Fail-closed public claim lint"),
    ("demo_readiness_script", "scripts/demo_readiness.py", "Demo recording readiness gate"),
    ("demo_readiness_json", "docs/assets/demo-readiness-report.json", "Machine-readable demo readiness report"),
    ("demo_readiness_md", "docs/assets/demo-readiness-report.md", "Human-readable demo readiness report"),
    ("recording_assets_script", "scripts/recording_assets.py", "Public-safe recording asset gate"),
    ("recording_assets_json", "docs/assets/recording-assets.json", "Machine-readable recording asset report"),
    ("recording_assets_md", "docs/assets/recording-assets.md", "Human-readable recording asset report"),
    ("final_live_runner", "scripts/run_final_live_proof.py", "One-command final B2 plus Genblaze proof runner"),
    ("submission_plan", "docs/submission.md", "Registration and submission plan"),
    ("task_ledger", "tasks.json", "Machine-readable task board"),
    ("local_ui_smoke", "docs/assets/proofframe-local-ui-smoke.png", "Local UI screenshot"),
    ("review_console_smoke", "docs/assets/proofframe-review-console-smoke.png", "Review console screenshot"),
    ("public_hf_smoke", "docs/assets/proofframe-hf-public-smoke.png", "Public mock demo screenshot"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(root: Path, artifact_id: str, relative_path: str, label: str) -> dict[str, Any]:
    path = root / relative_path
    record: dict[str, Any] = {
        "id": artifact_id,
        "path": relative_path,
        "label": label,
        "present": path.exists(),
    }
    if path.exists():
        record.update({"bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return record


def load_packet_summary(root: Path) -> dict[str, Any]:
    packet_path = root / "docs" / "assets" / "devpost-submission-packet.json"
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"present": False, "mode": None, "claim_warning": "Devpost packet missing."}
    return {
        "present": True,
        "mode": packet.get("mode"),
        "project_name": packet.get("project_name"),
        "tagline": packet.get("tagline"),
        "repository_url": packet.get("repository_url"),
        "demo_url": packet.get("demo_url"),
        "claim_warning": packet.get("claim_warning"),
    }


def build_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    artifacts = [artifact_record(root, *artifact) for artifact in ARTIFACTS]
    missing = [artifact for artifact in artifacts if not artifact["present"]]
    gate = build_submission_gate(root)
    return {
        "schema": "proofframe.submission_bundle.v1",
        "created_at": utc_now(),
        "project": "ProofFrame",
        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
        "public_demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "safe_to_share": not missing,
        "safe_to_submit": gate["ok"],
        "devpost_packet": load_packet_summary(root),
        "submission_gate": {
            "ok": gate["ok"],
            "mode": gate["mode"],
            "summary": gate["summary"],
            "packet_gate": gate["packet_gate"],
            "evidence_gate": gate["evidence_gate"],
            "report_gate": gate["report_gate"],
            "next_actions": gate["next_actions"],
        },
        "artifacts": artifacts,
        "missing_artifacts": [artifact["path"] for artifact in missing],
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    gate = manifest["submission_gate"]
    packet = manifest["devpost_packet"]
    lines = [
        "# ProofFrame Submission Bundle",
        "",
        f"Created: `{manifest['created_at']}`",
        f"Repository: {manifest['repository_url']}",
        f"Public mock demo: {manifest['public_demo_url']}",
        f"Devpost packet mode: `{packet.get('mode')}`",
        f"Final gate mode: `{gate['mode']}`",
        f"Final gate ready: `{str(gate['ok']).lower()}`",
        "",
        "## Current Gate",
        "",
        (
            f"- Tasks: {gate['summary']['done']} done / {gate['summary']['required']} required; "
            f"{gate['summary']['doing']} doing, {gate['summary']['blocked']} blocked, "
            f"{gate['summary']['todo']} todo."
        ),
        f"- Live evidence: `{gate['evidence_gate']['status']}`",
        f"- Devpost copy packet: `{gate['packet_gate']['status']}`",
        f"- Final reports: `{gate['report_gate']['status']}`",
        "",
        "## Next Actions",
        "",
    ]
    if gate["next_actions"]:
        lines.extend(f"- {action}" for action in gate["next_actions"])
    else:
        lines.append("- Ready for final Devpost submit.")

    lines.extend(["", "## Artifacts", ""])
    for artifact in manifest["artifacts"]:
        if artifact["present"]:
            lines.append(
                f"- `{artifact['path']}` ({artifact['bytes']} bytes, sha256 `{artifact['sha256'][:16]}...`) - {artifact['label']}"
            )
        else:
            lines.append(f"- MISSING `{artifact['path']}` - {artifact['label']}")
    lines.append("")
    lines.append("No credentials, browser cookies, signed URLs, or raw provider keys are included.")
    return "\n".join(lines) + "\n"


def write_outputs(
    manifest: dict[str, Any],
    *,
    json_path: Path = DEFAULT_JSON,
    markdown_path: Path = DEFAULT_MD,
    zip_path: Path | None = None,
    root: Path = ROOT,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(manifest), encoding="utf-8")
    if zip_path:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            archive.writestr("submission-bundle-manifest.json", json.dumps(manifest, indent=2) + "\n")
            archive.writestr("submission-bundle-manifest.md", render_markdown(manifest))
            for artifact in manifest["artifacts"]:
                if artifact["present"]:
                    archive.write(root / artifact["path"], artifact["path"])


def cli_summary(manifest: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ok": manifest["safe_to_submit"],
        "mode": manifest["submission_gate"]["mode"],
        "safe_to_share": manifest["safe_to_share"],
        "safe_to_submit": manifest["safe_to_submit"],
        "json": str(args.json_out),
        "markdown": str(args.markdown_out),
        "zip": str(args.zip_out) if args.zip_out else None,
        "missing_artifacts": manifest["missing_artifacts"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a safe ProofFrame submission bundle manifest.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--zip-out", type=Path, help="Optionally write a zip with public artifacts.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    manifest = build_manifest(ROOT)
    write_outputs(
        manifest,
        json_path=args.json_out,
        markdown_path=args.markdown_out,
        zip_path=args.zip_out,
        root=ROOT,
    )
    print(json.dumps(cli_summary(manifest, args), indent=2))


if __name__ == "__main__":
    main()
