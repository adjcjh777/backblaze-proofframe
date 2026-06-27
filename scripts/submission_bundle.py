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
    ("devpost_form_kit_script", "scripts/devpost_form_kit.py", "Field-by-field Devpost form kit"),
    ("devpost_form_kit_json", "docs/assets/devpost-form-kit.json", "Machine-readable Devpost form kit"),
    ("devpost_form_kit_md", "docs/assets/devpost-form-kit.md", "Human-readable Devpost form kit"),
    ("frontend_ui", "apps/web/index.html", "Browser proof ledger UI"),
    ("demo_script", "docs/demo_script.md", "Video shot list and narration"),
    ("demo_storyboard_script", "scripts/demo_storyboard.py", "Machine-checked demo video storyboard"),
    ("demo_storyboard_json", "docs/assets/demo-storyboard.json", "Machine-readable demo storyboard"),
    ("demo_storyboard_md", "docs/assets/demo-storyboard.md", "Human-readable demo storyboard"),
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
    ("b2_live_runner", "scripts/run_b2_live_proof.py", "One-command B2 storage proof runner"),
    ("live_env_handoff_script", "scripts/live_env_handoff.py", "Redacted live credential handoff gate"),
    ("live_env_handoff_json", "docs/assets/live-credential-handoff.json", "Machine-readable live credential handoff"),
    ("live_env_handoff_md", "docs/assets/live-credential-handoff.md", "Human-readable live credential handoff"),
    ("final_env_wizard", "scripts/final_env_wizard.py", "Local final credential env wizard"),
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
    print(
        json.dumps(
            {
                "ok": manifest["safe_to_share"],
                "mode": manifest["submission_gate"]["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "zip": str(args.zip_out) if args.zip_out else None,
                "missing_artifacts": manifest["missing_artifacts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
