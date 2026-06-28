#!/usr/bin/env python3
"""Build a public-safe recording asset report for the final demo workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "recording-assets.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "recording-assets.md"
PUBLIC_BASE_URL = "https://adjcjh-backblaze-proofframe.hf.space"
PUBLIC_JUDGE_PATH = "/?judge=1"
TIMEOUT_SECONDS = 20

REQUIRED_RECORDING_ASSETS = [
    "README.md",
    "docs/demo_script.md",
    "docs/assets/demo-storyboard.json",
    "docs/assets/demo-storyboard.md",
    "docs/assets/demo-video-draft.json",
    "docs/assets/demo-video-draft.md",
    "docs/assets/proofframe-demo-draft.mp4",
    "docs/assets/public-video-check.json",
    "docs/assets/public-video-check.md",
    "docs/assets/demo-readiness-report.json",
    "docs/assets/demo-readiness-report.md",
    "docs/assets/devpost-form-kit.json",
    "docs/assets/devpost-form-kit.md",
    "docs/assets/final-submission-control.json",
    "docs/assets/final-submission-control.md",
    "docs/assets/proofframe-local-ui-smoke.png",
    "docs/assets/proofframe-review-console-smoke.png",
    "docs/assets/proofframe-hf-public-smoke.png",
    "docs/assets/proofframe-sponsor-model-smoke.png",
    "docs/assets/proofframe-sponsor-model-mobile-smoke.png",
]

SHOT_PLAN = [
    {
        "id": "judge_slate",
        "source": "Public judge URL",
        "screen": "First viewport with judge recording slate and claim boundary.",
    },
    {
        "id": "sponsor_model",
        "source": "Public judge URL",
        "screen": "Sponsor Evidence Model showing Genblaze step, B2 route, manifest, and claim mode.",
    },
    {
        "id": "creative_brief",
        "source": "Local or public mock demo",
        "screen": "Campaign brief with audience, tone, and prompt context.",
    },
    {
        "id": "asset_ledger",
        "source": "Local or public mock demo",
        "screen": "Generated asset ledger with provider/model/checksum/storage fields.",
    },
    {
        "id": "review_console",
        "source": "Committed screenshot or live UI",
        "screen": "Review console filters, approval state, and copy-safe summary.",
    },
    {
        "id": "final_gate",
        "source": "Final submission control report",
        "screen": "Fail-closed final gate with remaining B2/Genblaze/video blockers.",
    },
]

RECORDING_COMMANDS = [
    "uvicorn proofframe.app:app --host 127.0.0.1 --port 8088",
    "python scripts/recording_assets.py --verify-public",
    "python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space",
    "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
    "python scripts/demo_storyboard.py --strict-final",
    "python scripts/demo_video_draft.py --build-video",
    'python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final',
    "python scripts/demo_readiness.py --strict-final",
    "python scripts/final_submission_control.py --strict-final",
]


FetchResult = dict[str, Any]
Fetcher = Callable[[str, int], FetchResult]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def fetch_text(url: str, timeout: int = TIMEOUT_SECONDS) -> FetchResult:
    request = Request(url, headers={"User-Agent": "ProofFrame recording asset verifier"})
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


def public_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def file_record(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    return {
        "path": relative_path,
        "present": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def report_summary(
    root: Path,
    relative_path: str,
    expected_schema: str,
    fields: list[str],
) -> dict[str, Any]:
    data = load_json(root / relative_path)
    if data is None:
        return {"present": False, "path": relative_path, "schema_ok": False, "schema": None}
    summary = {
        "present": True,
        "path": relative_path,
        "schema_ok": data.get("schema") == expected_schema,
        "schema": data.get("schema"),
        "mode": data.get("mode"),
    }
    summary.update({field: data.get(field) for field in fields})
    return summary


def parse_json_body(result: FetchResult) -> dict[str, Any] | None:
    try:
        return json.loads(str(result.get("body") or ""))
    except json.JSONDecodeError:
        return None


def verify_public_demo(base_url: str, fetcher: Fetcher = fetch_text) -> dict[str, Any]:
    judge_url = public_url(base_url, PUBLIC_JUDGE_PATH)
    health_url = public_url(base_url, "/api/health")
    gate_url = public_url(base_url, "/api/submission/gate")

    html = fetcher(judge_url, TIMEOUT_SECONDS)
    health = fetcher(health_url, TIMEOUT_SECONDS)
    gate = fetcher(gate_url, TIMEOUT_SECONDS)
    html_body = str(html.get("body") or "")
    health_json = parse_json_body(health)
    gate_json = parse_json_body(gate)

    html_markers = {
        "judge_recording_slate": "Judge recording slate" in html_body,
        "sponsor_evidence_model": "Sponsor Evidence Model" in html_body,
        "recording_runbook": "Recording Runbook" in html_body,
        "auto_load_judge_demo": "shouldAutoLoadJudgeDemo" in html_body,
        "final_report_gate_copy": "Final reports pending" in html_body,
    }
    health_ok = bool(
        health_json
        and health_json.get("ready") is True
        and health_json.get("storage_backend") == "local"
        and health_json.get("generation_backend") == "mock"
    )
    gate_paths = [
        gate_json.get("tasks_path") if gate_json else None,
        gate_json.get("evidence_gate", {}).get("path") if gate_json else None,
        gate_json.get("packet_gate", {}).get("path") if gate_json else None,
    ]
    gate_paths_relative = bool(
        gate_json
        and all(isinstance(path, str) and path and not path.startswith("/") for path in gate_paths)
    )
    report_gate_present = bool(gate_json and isinstance(gate_json.get("report_gate"), dict))
    gate_ok = bool(
        gate_json
        and gate_json.get("mode") in {"pre_live_safe", "final_ready"}
        and report_gate_present
        and gate_paths_relative
    )
    ok = bool(
        html.get("ok")
        and health.get("ok")
        and gate.get("ok")
        and all(html_markers.values())
        and health_ok
        and gate_ok
    )
    return {
        "checked": True,
        "ok": ok,
        "judge_url": judge_url,
        "health_url": health_url,
        "gate_url": gate_url,
        "html_status": html.get("status"),
        "health_status": health.get("status"),
        "gate_status": gate.get("status"),
        "html_markers": html_markers,
        "health": {
            "ok": health_ok,
            "storage_backend": health_json.get("storage_backend") if health_json else None,
            "generation_backend": health_json.get("generation_backend") if health_json else None,
            "ready": health_json.get("ready") if health_json else None,
        },
        "submission_gate": {
            "ok": gate_ok,
            "mode": gate_json.get("mode") if gate_json else None,
            "summary": gate_json.get("summary") if gate_json else None,
            "report_gate_present": report_gate_present,
            "report_gate_status": (
                gate_json.get("report_gate", {}).get("status") if gate_json else None
            ),
            "paths_relative": gate_paths_relative,
        },
        "errors": [
            str(item.get("error"))
            for item in [html, health, gate]
            if item.get("error")
        ],
    }


def unchecked_public_demo(base_url: str) -> dict[str, Any]:
    return {
        "checked": False,
        "ok": None,
        "judge_url": public_url(base_url, PUBLIC_JUDGE_PATH),
        "health_url": public_url(base_url, "/api/health"),
        "gate_url": public_url(base_url, "/api/submission/gate"),
    }


def build_next_actions(
    *,
    missing_assets: list[str],
    source_reports_ok: bool,
    public_verification: dict[str, Any],
    final_video_ready: bool,
) -> list[str]:
    actions: list[str] = []
    if missing_assets:
        actions.append("Restore missing recording assets before recording the demo.")
    if not source_reports_ok:
        actions.append("Regenerate storyboard, readiness, Devpost form, and final control reports.")
    if not public_verification.get("checked"):
        actions.append("Run python scripts/recording_assets.py --verify-public before recording.")
    elif not public_verification.get("ok"):
        actions.append("Refresh or redeploy the public mock demo before recording.")
    if not final_video_ready:
        actions.append("After live B2/Genblaze proof, record and upload the final public video.")
    actions.append("Run python scripts/final_submission_control.py --strict-final before Devpost submit.")
    return actions[:6]


def build_report(
    root: Path = ROOT,
    *,
    verify_public: bool = False,
    public_base_url: str = PUBLIC_BASE_URL,
    fetcher: Fetcher = fetch_text,
) -> dict[str, Any]:
    root = root.resolve()
    assets = [file_record(root, path) for path in REQUIRED_RECORDING_ASSETS]
    missing_assets = [asset["path"] for asset in assets if not asset["present"]]
    source_reports = {
        "storyboard": report_summary(
            root,
            "docs/assets/demo-storyboard.json",
            "proofframe.demo_storyboard.v1",
            ["mock_storyboard_ready", "final_video_ready", "public_video_ready"],
        ),
        "readiness": report_summary(
            root,
            "docs/assets/demo-readiness-report.json",
            "proofframe.demo_readiness.v1",
            ["mock_recording_ready", "final_recording_ready"],
        ),
        "public_video_check": report_summary(
            root,
            "docs/assets/public-video-check.json",
            "proofframe.public_video_check.v1",
            ["safe_to_submit"],
        ),
        "demo_video_draft": report_summary(
            root,
            "docs/assets/demo-video-draft.json",
            "proofframe.demo_video_draft.v1",
            ["safe_to_submit", "final_video_ready", "public_video_draft_url"],
        ),
        "devpost_form": report_summary(
            root,
            "docs/assets/devpost-form-kit.json",
            "proofframe.devpost_form_kit.v1",
            ["final_form_ready", "public_video_ready"],
        ),
        "final_control": report_summary(
            root,
            "docs/assets/final-submission-control.json",
            "proofframe.final_submission_control.v1",
            ["safe_to_submit"],
        ),
    }
    source_reports_ok = all(report.get("present") and report.get("schema_ok") for report in source_reports.values())
    public_verification = (
        verify_public_demo(public_base_url, fetcher) if verify_public else unchecked_public_demo(public_base_url)
    )
    mock_recording_ready = bool(
        not missing_assets
        and source_reports_ok
        and source_reports["storyboard"].get("mock_storyboard_ready")
        and source_reports["readiness"].get("mock_recording_ready")
        and (public_verification.get("ok") if verify_public else True)
    )
    final_video_ready = bool(
        mock_recording_ready
        and source_reports["storyboard"].get("final_video_ready")
        and source_reports["public_video_check"].get("safe_to_submit")
        and source_reports["readiness"].get("final_recording_ready")
        and source_reports["devpost_form"].get("public_video_ready")
    )
    mode = "missing_recording_assets"
    if final_video_ready:
        mode = "final_video_ready"
    elif mock_recording_ready and public_verification.get("ok"):
        mode = "public_mock_verified"
    elif mock_recording_ready:
        mode = "mock_recording_ready"
    return {
        "schema": "proofframe.recording_assets.v1",
        "mode": mode,
        "mock_recording_ready": mock_recording_ready,
        "public_mock_verified": bool(public_verification.get("ok")),
        "final_video_ready": final_video_ready,
        "public_base_url": public_base_url,
        "required_assets": assets,
        "missing_assets": missing_assets,
        "source_reports": source_reports,
        "public_verification": public_verification,
        "shot_plan": SHOT_PLAN,
        "recording_commands": RECORDING_COMMANDS,
        "next_actions": build_next_actions(
            missing_assets=missing_assets,
            source_reports_ok=source_reports_ok,
            public_verification=public_verification,
            final_video_ready=final_video_ready,
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Recording Assets",
        "",
        f"Mode: `{report['mode']}`",
        f"Mock recording ready: `{str(report['mock_recording_ready']).lower()}`",
        f"Public mock verified: `{str(report['public_mock_verified']).lower()}`",
        f"Final video ready: `{str(report['final_video_ready']).lower()}`",
        f"Public judge URL: {report['public_verification']['judge_url']}",
        "",
        "## Source Reports",
        "",
    ]
    for name, source in report["source_reports"].items():
        marker = "OK" if source.get("present") and source.get("schema_ok") else "MISSING"
        lines.append(f"- {marker} `{name}`: `{source.get('path')}` mode `{source.get('mode')}`")
    lines.extend(["", "## Required Assets", ""])
    for asset in report["required_assets"]:
        marker = "OK" if asset["present"] else "MISSING"
        lines.append(f"- {marker} `{asset['path']}`")
    public = report["public_verification"]
    lines.extend(["", "## Public GET-only Verification", ""])
    if public.get("checked"):
        lines.extend(
            [
                f"- Overall: `{str(public.get('ok')).lower()}`",
                f"- HTML status: `{public.get('html_status')}`",
                f"- Health: `{public.get('health', {}).get('storage_backend')}` / `{public.get('health', {}).get('generation_backend')}`",
                f"- Submission gate: `{public.get('submission_gate', {}).get('mode')}`",
            ]
        )
    else:
        lines.append("- Not checked in this run. Use `python scripts/recording_assets.py --verify-public`.")
    lines.extend(["", "## Shot Plan", ""])
    for shot in report["shot_plan"]:
        lines.append(f"- `{shot['id']}` - {shot['source']}: {shot['screen']}")
    lines.extend(["", "## Commands", "", "```bash"])
    lines.extend(report["recording_commands"])
    lines.append("```")
    lines.extend(["", "## Next Actions", ""])
    if report["next_actions"]:
        lines.extend(f"- {action}" for action in report["next_actions"])
    else:
        lines.append("- Recording assets are complete.")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a ProofFrame recording asset report.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--public-base-url", default=PUBLIC_BASE_URL)
    parser.add_argument("--verify-public", action="store_true", help="Run GET-only checks against the public demo.")
    parser.add_argument("--strict-final", action="store_true", help="Fail unless final video assets are ready.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(
        args.root,
        verify_public=args.verify_public,
        public_base_url=args.public_base_url,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    ok = report["final_video_ready"] if args.strict_final else report["mock_recording_ready"]
    print(
        json.dumps(
            {
                "ok": ok,
                "mode": report["mode"],
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
