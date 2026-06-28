#!/usr/bin/env python3
"""Run an end-to-end ProofFrame API smoke test against a running server."""

from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZipFile


FORBIDDEN_EVIDENCE_KEYS = re.compile(
    r"(?i)(api[_-]?key|application[_-]?key|authorization|cookie|password|secret|token)"
)
FORBIDDEN_EVIDENCE_VALUES = [
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|application[_-]?key|secret|token|cookie)=[^&\s]{8,}"),
    re.compile(r"(?i)x-amz-(credential|security-token|signature)=[^&\s]{8,}"),
    re.compile(r"(?i)gmi-[A-Za-z0-9_\-]{16,}"),
]


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} failed: {exc.code} {detail}") from exc


def request_bytes(method: str, url: str) -> tuple[bytes, str]:
    request = Request(url, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            return response.read(), response.headers.get_content_type()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} failed: {exc.code} {detail}") from exc


def require_backend(field: str, actual: str, expected: str | None) -> None:
    if expected and actual != expected:
        raise SystemExit(f"Expected {field}={expected}, got {actual}")


def evidence_findings(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}"
            if FORBIDDEN_EVIDENCE_KEYS.search(str(key)):
                findings.append(f"{key_path}: forbidden evidence key")
            findings.extend(evidence_findings(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(evidence_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        for pattern in FORBIDDEN_EVIDENCE_VALUES:
            if pattern.search(value):
                findings.append(f"{path}: forbidden evidence value")
                break
    return findings


def assert_safe_evidence(evidence: dict[str, Any]) -> None:
    findings = evidence_findings(evidence)
    if findings:
        raise SystemExit("Unsafe evidence JSON refused:\n" + "\n".join(findings))


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    assert_safe_evidence(evidence)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def run_smoke(
    base_url: str,
    *,
    require_storage_backend: str | None = None,
    require_generation_backend: str | None = None,
) -> dict[str, Any]:
    base = base_url.rstrip("/")
    health = request_json("GET", f"{base}/api/health")
    if not health.get("ready"):
        raise SystemExit(f"App is not ready: {health}")
    require_backend("storage_backend", health["storage_backend"], require_storage_backend)
    require_backend("generation_backend", health["generation_backend"], require_generation_backend)

    judge_brief = request_json("GET", f"{base}/api/judge/brief")
    if judge_brief.get("schema") != "proofframe.judge_brief.v1":
        raise SystemExit("Judge brief endpoint did not return the expected schema.")
    safe_to_submit = judge_brief.get("status", {}).get("safe_to_submit")
    if not isinstance(safe_to_submit, bool):
        raise SystemExit("Judge brief endpoint did not include a boolean safe_to_submit flag.")

    judge_crosswalk = request_json("GET", f"{base}/api/judge/crosswalk")
    if judge_crosswalk.get("schema") != "proofframe.judge_crosswalk.v1":
        raise SystemExit("Judge crosswalk endpoint did not return the expected schema.")
    crosswalk_safe_to_submit = judge_crosswalk.get("safe_to_submit")
    if not isinstance(crosswalk_safe_to_submit, bool):
        raise SystemExit("Judge crosswalk endpoint did not include a boolean safe_to_submit flag.")
    crosswalk_rows = judge_crosswalk.get("rows")
    if not isinstance(crosswalk_rows, list) or len(crosswalk_rows) < 4:
        raise SystemExit("Judge crosswalk endpoint did not include the expected criteria rows.")

    judge_recording = request_json("GET", f"{base}/api/judge/recording")
    if judge_recording.get("schema") != "proofframe.recording_assets.v1":
        raise SystemExit("Judge recording endpoint did not return the expected schema.")
    recording_shots = judge_recording.get("shot_plan")
    if not isinstance(recording_shots, list) or len(recording_shots) < 3:
        raise SystemExit("Judge recording endpoint did not include the expected shot plan.")
    recording_final_ready = judge_recording.get("final_video_ready")
    if not isinstance(recording_final_ready, bool):
        raise SystemExit("Judge recording endpoint did not include a boolean final_video_ready flag.")

    judge_devpost = request_json("GET", f"{base}/api/judge/devpost")
    if judge_devpost.get("schema") != "proofframe.devpost_form_kit.v1":
        raise SystemExit("Judge Devpost endpoint did not return the expected schema.")
    devpost_fields = judge_devpost.get("fields")
    if not isinstance(devpost_fields, list) or len(devpost_fields) < 10:
        raise SystemExit("Judge Devpost endpoint did not include the expected form fields.")
    devpost_final_ready = judge_devpost.get("final_form_ready")
    if not isinstance(devpost_final_ready, bool):
        raise SystemExit("Judge Devpost endpoint did not include a boolean final_form_ready flag.")

    submission_checklist = request_json("GET", f"{base}/api/judge/submission-checklist")
    if submission_checklist.get("schema") != "proofframe.devpost_submission_checklist.v1":
        raise SystemExit("Judge submission checklist endpoint did not return the expected schema.")
    checklist_preflight = submission_checklist.get("preflight")
    if not isinstance(checklist_preflight, list) or len(checklist_preflight) < 3:
        raise SystemExit("Judge submission checklist endpoint did not include the expected preflight rows.")
    checklist_safe_to_submit = submission_checklist.get("safe_to_submit")
    if not isinstance(checklist_safe_to_submit, bool):
        raise SystemExit("Judge submission checklist endpoint did not include a boolean safe_to_submit flag.")

    campaign = request_json(
        "POST",
        f"{base}/api/campaigns",
        {
            "title": "Judge packet smoke",
            "brief": "Create one safe campaign visual for a product launch evidence packet.",
            "audience": "hackathon judges",
            "tone": "clear and production-ready",
        },
    )
    assets = request_json("POST", f"{base}/api/campaigns/{campaign['id']}/generate?count=1")
    if len(assets) != 1:
        raise SystemExit(f"Expected one generated asset, received {len(assets)}")
    asset = assets[0]
    approved = request_json(
        "POST",
        f"{base}/api/assets/{asset['id']}/status",
        {"status": "approved", "risk_note": "Approved by API smoke test."},
    )
    exported = request_json("POST", f"{base}/api/campaigns/{campaign['id']}/export")
    manifest_assets = exported["manifest"]["assets"]
    if len(manifest_assets) != 1:
        raise SystemExit("Manifest did not include the generated asset.")

    packet_bytes, packet_content_type = request_bytes(
        "GET",
        f"{base}/api/campaigns/{campaign['id']}/packet.zip",
    )
    if packet_content_type != "application/zip":
        raise SystemExit(f"Packet endpoint returned {packet_content_type}, not application/zip.")
    with ZipFile(BytesIO(packet_bytes)) as packet:
        packet_names = set(packet.namelist())
        if "manifest.json" not in packet_names or "README.txt" not in packet_names:
            raise SystemExit(f"Packet is missing required files: {packet_names}")

    demo = request_json("POST", f"{base}/api/demo/judge-packet")
    demo_assets = demo["assets"]
    if len(demo_assets) != 3 or demo_assets[0]["status"] != "approved":
        raise SystemExit("Judge demo packet did not return three assets with one approved asset.")

    return {
        "ok": True,
        "base_url": base,
        "generation_backend": health["generation_backend"],
        "storage_backend": health["storage_backend"],
        "judge_brief_schema": judge_brief["schema"],
        "judge_safe_to_submit": safe_to_submit,
        "judge_crosswalk_schema": judge_crosswalk["schema"],
        "judge_crosswalk_mode": judge_crosswalk.get("mode"),
        "judge_crosswalk_safe_to_submit": crosswalk_safe_to_submit,
        "judge_crosswalk_rows": len(crosswalk_rows),
        "judge_recording_schema": judge_recording["schema"],
        "judge_recording_mode": judge_recording.get("mode"),
        "judge_recording_final_video_ready": recording_final_ready,
        "judge_recording_shots": len(recording_shots),
        "judge_devpost_schema": judge_devpost["schema"],
        "judge_devpost_mode": judge_devpost.get("mode"),
        "judge_devpost_final_form_ready": devpost_final_ready,
        "judge_devpost_fields": len(devpost_fields),
        "judge_submit_checklist_schema": submission_checklist["schema"],
        "judge_submit_checklist_mode": submission_checklist.get("mode"),
        "judge_submit_checklist_safe_to_submit": checklist_safe_to_submit,
        "judge_submit_checklist_preflight": len(checklist_preflight),
        "campaign_id": campaign["id"],
        "asset_id": asset["id"],
        "asset_provider": asset["provider"],
        "asset_model": asset["model"],
        "asset_storage_backend": asset["storage_backend"],
        "asset_storage_key": asset["storage_key"],
        "asset_public_url_present": bool(asset.get("public_url")),
        "asset_status": approved["status"],
        "asset_sha256": asset["sha256"],
        "manifest_storage_backend": exported["stored_manifest"]["storage_backend"],
        "manifest_key": exported["stored_manifest"]["storage_key"],
        "manifest_sha256": exported["stored_manifest"]["sha256"],
        "packet_bytes": len(packet_bytes),
        "judge_demo_campaign_id": demo["campaign"]["id"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test a running ProofFrame API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument(
        "--require-storage-backend",
        choices=["local", "b2"],
        help="Fail unless /api/health reports this storage backend.",
    )
    parser.add_argument(
        "--require-generation-backend",
        choices=["mock", "genblaze"],
        help="Fail unless /api/health reports this generation backend.",
    )
    parser.add_argument(
        "--evidence-out",
        type=Path,
        help="Write the safe smoke-test evidence JSON to this path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    evidence = run_smoke(
        args.base_url,
        require_storage_backend=args.require_storage_backend,
        require_generation_backend=args.require_generation_backend,
    )
    if args.evidence_out:
        write_evidence(args.evidence_out, evidence)
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
