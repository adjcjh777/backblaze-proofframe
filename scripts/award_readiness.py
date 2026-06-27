#!/usr/bin/env python3
"""Build a judge-facing award readiness scorecard for ProofFrame."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from proofframe.submission_gate import build_submission_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "award-readiness-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "award-readiness-report.md"


def load_script(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


claim_lint = load_script("claim_lint", "scripts/claim_lint.py")
demo_readiness = load_script("demo_readiness", "scripts/demo_readiness.py")
secret_scan = load_script("secret_scan", "scripts/secret_scan.py")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def task_statuses(root: Path) -> dict[str, str]:
    tasks = load_json(root / "tasks.json") or {}
    return {
        str(task.get("id", "")).upper(): str(task.get("status", "missing"))
        for task in tasks.get("tasks", [])
    }


def has_text(root: Path, relative_path: str, needle: str) -> bool:
    return needle in read_text(root / relative_path)


def has_any_text(root: Path, relative_path: str, needles: list[str]) -> bool:
    text = read_text(root / relative_path).lower()
    return any(needle.lower() in text for needle in needles)


def path_present(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def run_secret_scan(root: Path) -> list[str]:
    original_root = secret_scan.ROOT
    secret_scan.ROOT = root
    try:
        return secret_scan.run_scan()
    finally:
        secret_scan.ROOT = original_root


def signal(signal_id: str, label: str, ok: bool, points: int, detail: str) -> dict[str, Any]:
    return {
        "id": signal_id,
        "label": label,
        "ok": ok,
        "points": points if ok else 0,
        "max_points": points,
        "detail": detail,
    }


def criterion(criterion_id: str, label: str, signals: list[dict[str, Any]]) -> dict[str, Any]:
    earned = sum(item["points"] for item in signals)
    maximum = sum(item["max_points"] for item in signals)
    return {
        "id": criterion_id,
        "label": label,
        "score": earned,
        "max_score": maximum,
        "percent": round(earned / maximum * 100, 1) if maximum else 0,
        "signals": signals,
    }


def b2_setup_ready(root: Path) -> bool:
    setup = load_json(root / "docs" / "assets" / "b2-live-setup.json") or {}
    bucket_name = setup.get("bucket_name") or setup.get("bucket")
    return bool(bucket_name and setup.get("endpoint") and setup.get("bucket_type") == "private")


def packet_has_public_demo(root: Path) -> bool:
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json") or {}
    return str(packet.get("demo_url", "")).endswith("/?judge=1")


def b2_evidence_ready(root: Path) -> bool:
    evidence = load_json(root / "docs" / "assets" / "b2-live-proof-evidence.json") or {}
    return bool(
        evidence.get("ok")
        and evidence.get("storage_backend") == "b2"
        and evidence.get("asset_storage_backend") == "b2"
        and evidence.get("asset_sha256")
        and evidence.get("manifest_sha256")
    )


def sponsor_fit_audit_ready(root: Path) -> bool:
    report = load_json(root / "docs" / "assets" / "sponsor-fit-audit.json") or {}
    return bool(report.get("ok") and report.get("mode") == "sponsor_fit_ready")


def event_snapshot_ready(root: Path) -> bool:
    report = load_json(root / "docs" / "assets" / "devpost-event-snapshot.json") or {}
    criteria = report.get("rules", {}).get("judging_criteria", [])
    requirements = report.get("rules", {}).get("requirements", {})
    return bool(
        report.get("schema") == "proofframe.devpost_event_snapshot.v1"
        and report.get("validation", {}).get("ok")
        and report.get("validation", {}).get("submission_open")
        and all(item.get("present") for item in criteria)
        and all(requirements.get(key) for key in ["working_app_url", "github_repo_url", "demo_video"])
    )


def build_criteria(root: Path, context: dict[str, Any]) -> list[dict[str, Any]]:
    statuses = context["task_statuses"]
    demo = context["demo_readiness"]
    claim = context["claim_lint"]
    secret_findings = context["secret_findings"]
    gate = context["submission_gate"]
    return [
        criterion(
            "sponsor_fit",
            "Sponsor integration fit",
            [
                signal(
                    "b2_backend_code",
                    "B2 storage backend is implemented",
                    has_text(root, "src/proofframe/storage.py", "class B2StorageBackend"),
                    5,
                    "Backblaze B2 has a dedicated S3-compatible storage adapter.",
                ),
                signal(
                    "b2_bucket_setup",
                    "Dedicated private B2 bucket is recorded",
                    b2_setup_ready(root),
                    4,
                    "The non-secret B2 bucket setup record exists for final proof.",
                ),
                signal(
                    "b2_live_runner",
                    "B2-only live proof runner exists",
                    path_present(root, "scripts/run_b2_live_proof.py"),
                    4,
                    "B2 storage can be verified independently before Genblaze is ready.",
                ),
                signal(
                    "genblaze_provider_code",
                    "Genblaze provider path is implemented",
                    has_text(root, "src/proofframe/providers.py", "class GenblazeMediaProvider"),
                    5,
                    "The app has a real Genblaze/GMICloud provider adapter.",
                ),
                signal(
                    "final_live_runner",
                    "Final B2 plus Genblaze runner exists",
                    path_present(root, "scripts/run_final_live_proof.py"),
                    4,
                    "A one-command runner can produce sanitized final evidence once keys are present.",
                ),
                signal(
                    "sponsor_fit_matrix",
                    "Sponsor fit matrix is documented",
                    path_present(root, "docs/sponsor_fit_matrix.md"),
                    4,
                    "Judging angles are mapped to current evidence, safe claims, final gates, and demo shots.",
                ),
                signal(
                    "sponsor_fit_audit",
                    "Sponsor fit audit is green",
                    sponsor_fit_audit_ready(root),
                    4,
                    "Devpost B2/Genblaze copy is specific and the demo introduces B2 early.",
                ),
                signal(
                    "b2_live_evidence",
                    "Live B2 evidence is captured",
                    statuses.get("T020") == "done" and b2_evidence_ready(root),
                    4,
                    "T020 requires a real B2 media and manifest proof.",
                ),
                signal(
                    "genblaze_live_evidence",
                    "Live Genblaze evidence is captured",
                    statuses.get("T021") == "done" and gate["evidence_gate"]["ok"],
                    4,
                    "T021 requires provider/model metadata from a live Genblaze run.",
                ),
            ],
        ),
        criterion(
            "product_depth",
            "Provenance product depth",
            [
                signal(
                    "manifest_model",
                    "Manifest model captures provenance",
                    has_text(root, "src/proofframe/models.py", "CampaignManifest"),
                    4,
                    "Assets, prompts, provider/model metadata, hashes, and review state are modeled.",
                ),
                signal(
                    "packet_zip",
                    "Evidence packet ZIP endpoint exists",
                    has_text(root, "src/proofframe/app.py", "packet.zip"),
                    4,
                    "Judges can inspect a packaged manifest and local media evidence.",
                ),
                signal(
                    "judge_packet",
                    "One-click judge packet exists",
                    has_text(root, "src/proofframe/app.py", "/api/demo/judge-packet"),
                    4,
                    "The demo can be loaded quickly into a believable reviewer workflow.",
                ),
                signal(
                    "review_console",
                    "Review console UI is present",
                    has_any_text(
                        root,
                        "apps/web/index.html",
                        ["review console", "review-console", 'aria-label="Review console"'],
                    ),
                    4,
                    "The app is positioned as an operations desk, not a generic generator.",
                ),
                signal(
                    "sponsor_model_ui",
                    "Sponsor evidence model is visible in the UI",
                    has_text(root, "apps/web/index.html", "Sponsor Evidence Model"),
                    3,
                    "Judge mode foregrounds Genblaze, B2 object route, manifest proof, and claim mode.",
                ),
                signal(
                    "prd_spec",
                    "PRD and technical spec are present",
                    path_present(root, "docs/prd.md") and path_present(root, "docs/spec.md"),
                    4,
                    "The product and implementation story are documented for judges and maintainers.",
                ),
            ],
        ),
        criterion(
            "demo_and_submission",
            "Demo and Devpost readiness",
            [
                signal(
                    "public_judge_demo",
                    "Public judge-mode demo URL is packaged",
                    packet_has_public_demo(root),
                    5,
                    "The Devpost packet points judges to a credential-free public demo.",
                ),
                signal(
                    "devpost_form_kit",
                    "Devpost form kit is generated",
                    path_present(root, "docs/assets/devpost-form-kit.json")
                    and path_present(root, "docs/assets/devpost-form-kit.md"),
                    4,
                    "Field-by-field copy is ready and length checked.",
                ),
                signal(
                    "official_event_snapshot",
                    "Official Devpost snapshot is fresh",
                    event_snapshot_ready(root),
                    4,
                    "Deadline, participants, requirements, and judging criteria are refreshed from Devpost.",
                ),
                signal(
                    "storyboard",
                    "Demo storyboard is machine-checked",
                    path_present(root, "docs/assets/demo-storyboard.json")
                    and path_present(root, "docs/assets/demo-storyboard.md"),
                    4,
                    "The video can be recorded around a clear judge story.",
                ),
                signal(
                    "mock_recording_ready",
                    "Mock recording package is ready",
                    bool(demo["mock_recording_ready"]),
                    4,
                    "The current public demo can be recorded safely before live proof.",
                ),
                signal(
                    "screenshots",
                    "Key screenshots are captured",
                    all(
                        path_present(root, path)
                        for path in [
                            "docs/assets/proofframe-local-ui-smoke.png",
                            "docs/assets/proofframe-review-console-smoke.png",
                            "docs/assets/proofframe-hf-public-smoke.png",
                        ]
                    ),
                    4,
                    "Local, review-console, and public demo screenshots are available.",
                ),
                signal(
                    "devpost_registered",
                    "Devpost registration is done",
                    statuses.get("T040") == "done",
                    4,
                    "The project is through the registration gate.",
                ),
            ],
        ),
        criterion(
            "trust_and_compliance",
            "Trust, safety, and claim discipline",
            [
                signal(
                    "secret_scan",
                    "Secret scan is clean",
                    not secret_findings,
                    4,
                    "No obvious API keys, cookies, signed URLs, or tokens were found in public files.",
                ),
                signal(
                    "claim_lint",
                    "Public claim lint is clean",
                    bool(claim["ok"]),
                    4,
                    "Pre-live copy avoids claiming unverified B2 or Genblaze runs.",
                ),
                signal(
                    "env_ignored",
                    "Local final env file is ignored",
                    has_text(root, ".gitignore", ".env.final.local"),
                    3,
                    "Credential-bearing local env files stay out of Git.",
                ),
                signal(
                    "safe_evidence_writer",
                    "Evidence writer rejects secret-like values",
                    has_text(root, "scripts/api_smoke.py", "assert_safe_evidence"),
                    2,
                    "Live evidence cannot silently include key-like fields or signed URLs.",
                ),
                signal(
                    "claim_freeze_doc",
                    "Public claim freeze is documented",
                    path_present(root, "docs/public_claim_freeze.md"),
                    2,
                    "The team has a written boundary for what can be said before final proof.",
                ),
            ],
        ),
        criterion(
            "final_closure",
            "Final submission closure",
            [
                signal(
                    "final_gate",
                    "Final live proof gate is green",
                    bool(gate["ok"]),
                    6,
                    "Requires T020, T021, T040, T041, T041A, T042, and final live evidence.",
                ),
                signal(
                    "final_audit_done",
                    "Final audit task is done",
                    statuses.get("T041") == "done",
                    2,
                    "The reviewer audit must pass after live evidence exists.",
                ),
                signal(
                    "final_secret_scan_done",
                    "Final secret scan task is done",
                    statuses.get("T041A") == "done",
                    1,
                    "The final scan should run after live proof artifacts are generated.",
                ),
                signal(
                    "devpost_submitted",
                    "Devpost project is submitted",
                    statuses.get("T042") == "done",
                    1,
                    "The submission is not complete until the project page is submitted.",
                ),
            ],
        ),
    ]


def build_next_actions(report: dict[str, Any]) -> list[str]:
    statuses = report["task_statuses"]
    actions: list[str] = []
    if statuses.get("T020") != "done":
        actions.append(
            "After explicit key-creation confirmation, create the scoped B2 key and run "
            "python scripts/run_b2_live_proof.py --env-file .env.final.local."
        )
    if statuses.get("T021") != "done":
        actions.append(
            "Configure Genblaze/GMI credentials and run python scripts/run_final_live_proof.py "
            "--env-file .env.final.local."
        )
    if statuses.get("T041A") != "done":
        actions.append("Run python scripts/secret_scan.py after live evidence is generated.")
    if statuses.get("T041") != "done":
        actions.append(
            "Run python scripts/submission_audit.py --strict-final after live proof, public video URL, and T041A are done."
        )
    if statuses.get("T042") != "done":
        actions.append("Submit the Devpost project only after the final gate turns green.")
    return actions[:5]


def readiness_mode(score: int, gate_ok: bool) -> str:
    if gate_ok and score >= 90:
        return "final_award_ready"
    if score >= 75:
        return "pre_live_competitive"
    return "needs_polish"


def build_report(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    context = {
        "task_statuses": task_statuses(root),
        "submission_gate": build_submission_gate(root),
        "demo_readiness": demo_readiness.build_report(root),
        "claim_lint": claim_lint.build_claim_report(root),
        "secret_findings": run_secret_scan(root),
    }
    criteria = build_criteria(root, context)
    score = sum(item["score"] for item in criteria)
    max_score = sum(item["max_score"] for item in criteria)
    report = {
        "schema": "proofframe.award_readiness.v1",
        "project": "ProofFrame",
        "score": score,
        "max_score": max_score,
        "percent": round(score / max_score * 100, 1) if max_score else 0,
        "mode": readiness_mode(score, context["submission_gate"]["ok"]),
        "public_demo_url": (
            load_json(root / "docs" / "assets" / "devpost-submission-packet.json") or {}
        ).get("demo_url"),
        "task_statuses": {
            task: context["task_statuses"].get(task, "missing")
            for task in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        },
        "submission_gate": {
            "ok": context["submission_gate"]["ok"],
            "mode": context["submission_gate"]["mode"],
            "summary": context["submission_gate"]["summary"],
            "evidence_status": context["submission_gate"]["evidence_gate"]["status"],
        },
        "demo_readiness": {
            "mode": context["demo_readiness"]["mode"],
            "mock_recording_ready": context["demo_readiness"]["mock_recording_ready"],
            "final_recording_ready": context["demo_readiness"]["final_recording_ready"],
        },
        "claim_lint": {
            "ok": context["claim_lint"]["ok"],
            "mode": context["claim_lint"]["mode"],
            "finding_count": len(context["claim_lint"]["findings"]),
        },
        "secret_scan": {
            "ok": not context["secret_findings"],
            "finding_count": len(context["secret_findings"]),
        },
        "criteria": criteria,
    }
    report["next_actions"] = build_next_actions(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Award Readiness",
        "",
        f"Mode: `{report['mode']}`",
        f"Score: `{report['score']}/{report['max_score']}` ({report['percent']}%)",
        f"Public demo: {report['public_demo_url']}",
        "",
        "## Gate Snapshot",
        "",
        f"- Submission gate: `{report['submission_gate']['mode']}`",
        f"- Live evidence: `{report['submission_gate']['evidence_status']}`",
        f"- Mock recording ready: `{str(report['demo_readiness']['mock_recording_ready']).lower()}`",
        f"- Final recording ready: `{str(report['demo_readiness']['final_recording_ready']).lower()}`",
        f"- Claim lint: `{str(report['claim_lint']['ok']).lower()}`",
        f"- Secret scan: `{str(report['secret_scan']['ok']).lower()}`",
        "",
        "## Criteria",
        "",
    ]
    for item in report["criteria"]:
        lines.append(
            f"### {item['label']} - {item['score']}/{item['max_score']} ({item['percent']}%)"
        )
        for sig in item["signals"]:
            marker = "OK" if sig["ok"] else "TODO"
            lines.append(
                f"- {marker} `{sig['id']}` ({sig['points']}/{sig['max_points']}): {sig['detail']}"
            )
        lines.append("")
    lines.extend(["## Next Actions", ""])
    if report["next_actions"]:
        lines.extend(f"- {action}" for action in report["next_actions"])
    else:
        lines.append("- Ready to submit and defend with verified live evidence.")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a ProofFrame award readiness scorecard.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--min-score", type=int, default=75)
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Fail unless the final B2 plus Genblaze gate is award-ready.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.root)
    write_outputs(report, args.json_out, args.markdown_out)
    ok = report["mode"] == "final_award_ready" if args.strict_final else report["score"] >= args.min_score
    print(
        json.dumps(
            {
                "ok": ok,
                "mode": report["mode"],
                "score": report["score"],
                "max_score": report["max_score"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "next_actions": report["next_actions"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
