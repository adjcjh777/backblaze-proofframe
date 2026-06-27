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
