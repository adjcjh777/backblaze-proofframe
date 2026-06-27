#!/usr/bin/env python3
"""Run an end-to-end ProofFrame API smoke test against a running server."""

from __future__ import annotations

import argparse
from io import BytesIO
import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZipFile


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


def run_smoke(base_url: str) -> dict[str, Any]:
    base = base_url.rstrip("/")
    health = request_json("GET", f"{base}/api/health")
    if not health.get("ready"):
        raise SystemExit(f"App is not ready: {health}")

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

    return {
        "ok": True,
        "base_url": base,
        "generation_backend": health["generation_backend"],
        "storage_backend": health["storage_backend"],
        "campaign_id": campaign["id"],
        "asset_id": asset["id"],
        "asset_status": approved["status"],
        "asset_sha256": asset["sha256"],
        "manifest_key": exported["stored_manifest"]["storage_key"],
        "manifest_sha256": exported["stored_manifest"]["sha256"],
        "packet_bytes": len(packet_bytes),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test a running ProofFrame API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(json.dumps(run_smoke(args.base_url), indent=2))


if __name__ == "__main__":
    main()
