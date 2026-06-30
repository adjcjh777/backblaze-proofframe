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
FINAL_CLOSEOUT_REQUIRED_GATES = {
    "credential_handoff",
    "b2_live_proof",
    "genblaze_live_proof",
    "public_video",
    "devpost_receipt",
    "final_control",
}
FINAL_CLOSEOUT_PREFINAL_MODES = {"waiting_for_credentials", "closeout_blocked"}
FINAL_CLOSEOUT_FINAL_MODE = "final_closeout_ready"
FINAL_CLOSEOUT_SECRET_POLICY_TERMS = {
    "never stores",
    "backblaze keys",
    "genblaze/gmi keys",
    "devpost cookies",
    "signed urls",
}


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

    decision_brief = request_json("GET", f"{base}/api/judge/decision-brief")
    if decision_brief.get("schema") != "proofframe.judge_decision_brief.v1":
        raise SystemExit("Judge decision brief endpoint did not return the expected schema.")
    decision_brief_safe_to_submit = decision_brief.get("safe_to_submit")
    if not isinstance(decision_brief_safe_to_submit, bool):
        raise SystemExit("Judge decision brief endpoint did not include a boolean safe_to_submit flag.")
    decision_checks = decision_brief.get("decision_checks")
    if not isinstance(decision_checks, list) or len(decision_checks) < 6:
        raise SystemExit("Judge decision brief endpoint did not include the expected decision checks.")
    if health["storage_backend"] == "local" and health["generation_backend"] == "mock":
        if decision_brief_safe_to_submit:
            raise SystemExit("Mock/local judge decision brief must remain fail closed.")

    evidence_index = request_json("GET", f"{base}/api/judge/evidence-index")
    if evidence_index.get("schema") != "proofframe.judge_evidence_index.v1":
        raise SystemExit("Judge evidence index endpoint did not return the expected schema.")
    evidence_links = evidence_index.get("links")
    if not isinstance(evidence_links, list) or len(evidence_links) < 10:
        raise SystemExit("Judge evidence index endpoint did not include the expected evidence links.")
    evidence_safe_to_submit = evidence_index.get("safe_to_submit")
    if not isinstance(evidence_safe_to_submit, bool):
        raise SystemExit("Judge evidence index endpoint did not include a boolean safe_to_submit flag.")
    evidence_index_status = evidence_index.get("status")
    if not isinstance(evidence_index_status, dict) or "final_blockers" not in evidence_index_status:
        raise SystemExit("Judge evidence index endpoint did not include final blocker status.")

    final_closeout = request_json("GET", f"{base}/api/judge/final-closeout")
    if final_closeout.get("schema") != "proofframe.final_closeout_status.v1":
        raise SystemExit("Judge final closeout endpoint did not return the expected schema.")
    closeout_health_ok = final_closeout.get("closeout_health_ok")
    if closeout_health_ok is not True:
        raise SystemExit("Judge final closeout endpoint did not report closeout_health_ok=true.")
    closeout_safe_to_submit = final_closeout.get("safe_to_submit")
    if not isinstance(closeout_safe_to_submit, bool):
        raise SystemExit("Judge final closeout endpoint did not include a boolean safe_to_submit flag.")
    closeout_gates = final_closeout.get("gates")
    if not isinstance(closeout_gates, list) or len(closeout_gates) < 6:
        raise SystemExit("Judge final closeout endpoint did not include the expected gate ledger.")
    closeout_gate_ids = {
        str(gate.get("id")) for gate in closeout_gates if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    if not FINAL_CLOSEOUT_REQUIRED_GATES <= closeout_gate_ids:
        missing = sorted(FINAL_CLOSEOUT_REQUIRED_GATES - closeout_gate_ids)
        raise SystemExit("Judge final closeout endpoint is missing required gates: " + ", ".join(missing))
    closeout_secret_policy = str(final_closeout.get("secret_policy") or "").lower()
    if not all(term in closeout_secret_policy for term in FINAL_CLOSEOUT_SECRET_POLICY_TERMS):
        raise SystemExit("Judge final closeout endpoint did not include the expected no-secret policy.")
    closeout_mode = final_closeout.get("mode")
    closeout_all_gates_ok = all(isinstance(gate, dict) and gate.get("ok") is True for gate in closeout_gates)
    closeout_has_blocker = any(isinstance(gate, dict) and gate.get("ok") is False for gate in closeout_gates)
    if closeout_safe_to_submit:
        if closeout_mode != FINAL_CLOSEOUT_FINAL_MODE or not closeout_all_gates_ok:
            raise SystemExit("Final closeout safe_to_submit=true requires final_closeout_ready and all gates green.")
    elif closeout_mode not in FINAL_CLOSEOUT_PREFINAL_MODES or not closeout_has_blocker:
        raise SystemExit("Pre-final closeout must remain blocked with a visible blocker gate.")
    if health["storage_backend"] == "local" and health["generation_backend"] == "mock":
        if closeout_safe_to_submit:
            raise SystemExit("Mock/local final closeout must remain fail closed.")

    video_publish_kit = request_json("GET", f"{base}/api/judge/video-publish-kit")
    if video_publish_kit.get("schema") != "proofframe.final_video_publish_kit.v1":
        raise SystemExit("Judge video publish kit endpoint did not return the expected schema.")
    video_publish_safe_to_submit = video_publish_kit.get("safe_to_submit")
    if not isinstance(video_publish_safe_to_submit, bool):
        raise SystemExit("Judge video publish kit endpoint did not include a boolean safe_to_submit flag.")
    video_publish_final_ready = video_publish_kit.get("final_video_ready")
    if not isinstance(video_publish_final_ready, bool):
        raise SystemExit("Judge video publish kit endpoint did not include a boolean final_video_ready flag.")
    if health["storage_backend"] == "local" and health["generation_backend"] == "mock":
        if video_publish_safe_to_submit or video_publish_final_ready:
            raise SystemExit("Mock/local judge video publish kit must remain pre-final and fail closed.")
    upload_checklist = video_publish_kit.get("upload_checklist")
    if not isinstance(upload_checklist, list) or len(upload_checklist) < 4:
        raise SystemExit("Judge video publish kit endpoint did not include the expected upload checklist.")

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
        "judge_decision_brief_schema": decision_brief["schema"],
        "judge_decision_brief_mode": decision_brief.get("mode"),
        "judge_decision_brief_safe_to_submit": decision_brief_safe_to_submit,
        "judge_decision_brief_checks": len(decision_checks),
        "judge_evidence_index_schema": evidence_index["schema"],
        "judge_evidence_index_mode": evidence_index.get("mode"),
        "judge_evidence_index_safe_to_submit": evidence_safe_to_submit,
        "judge_evidence_index_links": len(evidence_links),
        "judge_final_closeout_schema": final_closeout["schema"],
        "judge_final_closeout_mode": final_closeout.get("mode"),
        "judge_final_closeout_health_ok": closeout_health_ok,
        "judge_final_closeout_safe_to_submit": closeout_safe_to_submit,
        "judge_final_closeout_gates": len(closeout_gates),
        "judge_video_publish_kit_schema": video_publish_kit["schema"],
        "judge_video_publish_kit_mode": video_publish_kit.get("mode"),
        "judge_video_publish_kit_safe_to_submit": video_publish_safe_to_submit,
        "judge_video_publish_kit_final_video_ready": video_publish_final_ready,
        "judge_video_publish_kit_upload_checks": len(upload_checklist),
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
