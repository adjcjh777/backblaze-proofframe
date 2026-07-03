#!/usr/bin/env python3
"""Preflight and run ProofFrame's final live sponsor proof gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from proofframe.config import Settings


ROOT = Path(__file__).resolve().parents[1]
API_SMOKE = ROOT / "scripts" / "api_smoke.py"


def package_available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def add_requirement(
    checks: list[dict[str, Any]], name: str, ok: bool, remediation: str
) -> None:
    checks.append({"name": name, "ok": ok, "remediation": "" if ok else remediation})


def build_preflight_report(
    settings: Settings,
    *,
    require_storage_backend: str,
    require_generation_backend: str,
    available: Callable[[str], bool] = package_available,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    add_requirement(
        checks,
        "storage backend mode",
        settings.storage_backend == require_storage_backend,
        f"Set PROOFFRAME_STORAGE_BACKEND={require_storage_backend}.",
    )
    add_requirement(
        checks,
        "generation backend mode",
        settings.generation_backend == require_generation_backend,
        f"Set PROOFFRAME_GENERATION_BACKEND={require_generation_backend}.",
    )

    if require_storage_backend == "b2":
        add_requirement(checks, "B2 endpoint", bool(settings.b2_endpoint_url), "Set B2_ENDPOINT_URL.")
        add_requirement(checks, "B2 bucket", bool(settings.b2_bucket), "Set B2_BUCKET.")
        add_requirement(checks, "B2 key id", bool(settings.b2_key_id), "Set B2_KEY_ID.")
        add_requirement(
            checks,
            "B2 application key",
            bool(settings.b2_application_key),
            "Set B2_APPLICATION_KEY or B2_APP_KEY.",
        )
        add_requirement(
            checks,
            "boto3 package",
            available("boto3"),
            "Install integrations with `pip install -e '.[integrations]'`.",
        )
        if require_generation_backend == "genblaze":
            add_requirement(
                checks,
                "B2 region for Genblaze sink",
                bool(settings.b2_region_for_backblaze()),
                (
                    "Set B2_REGION or use a Backblaze S3 endpoint like "
                    "https://s3.us-west-004.backblazeb2.com."
                ),
            )

    if require_generation_backend == "genblaze":
        add_requirement(
            checks,
            "Genblaze provider",
            settings.genblaze_provider_supported(),
            "Set GENBLAZE_PROVIDER=gmicloud, openai, or local.",
        )
        add_requirement(
            checks,
            "Genblaze provider API key",
            (not settings.genblaze_provider_requires_key()) or bool(settings.genblaze_provider_key()),
            settings.genblaze_key_remediation(),
        )
        add_requirement(
            checks,
            "Genblaze image model",
            bool(settings.genblaze_image_model),
            "Set GENBLAZE_IMAGE_MODEL.",
        )
        modules = ["genblaze_core", *settings.genblaze_provider_modules()]
        if require_storage_backend == "b2":
            modules.append("genblaze_s3")
        for module in modules:
            add_requirement(
                checks,
                f"{module} package",
                available(module),
                "Install integrations with `pip install -e '.[integrations]'`.",
            )

    missing = [check for check in checks if not check["ok"]]
    return {
        "ok": not missing,
        "storage_backend": settings.storage_backend,
        "generation_backend": settings.generation_backend,
        "genblaze_provider": settings.genblaze_provider,
        "required_storage_backend": require_storage_backend,
        "required_generation_backend": require_generation_backend,
        "checks": checks,
        "missing": missing,
        "secret_policy": (
            "No credential values are printed. Evidence output is delegated to api_smoke.py, "
            "which refuses secret-like keys, bearer tokens, signed URL parameters, and GMI-style keys."
        ),
    }


def build_api_smoke_command(
    *,
    base_url: str,
    evidence_out: Path,
    require_storage_backend: str,
    require_generation_backend: str,
) -> list[str]:
    return [
        sys.executable,
        str(API_SMOKE),
        "--base-url",
        base_url,
        "--require-storage-backend",
        require_storage_backend,
        "--require-generation-backend",
        require_generation_backend,
        "--evidence-out",
        str(evidence_out),
    ]


def run_live_proof(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    report = build_preflight_report(
        settings,
        require_storage_backend=args.require_storage_backend,
        require_generation_backend=args.require_generation_backend,
    )
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        return 2
    if args.preflight_only:
        return 0

    command = build_api_smoke_command(
        base_url=args.base_url,
        evidence_out=args.evidence_out,
        require_storage_backend=args.require_storage_backend,
        require_generation_backend=args.require_generation_backend,
    )
    completed = subprocess.run(command, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight and run the final B2/Genblaze live proof gate."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument(
        "--require-storage-backend",
        choices=["b2", "local"],
        default="b2",
        help="Expected storage backend reported by the running app.",
    )
    parser.add_argument(
        "--require-generation-backend",
        choices=["genblaze", "mock"],
        default="genblaze",
        help="Expected generation backend reported by the running app.",
    )
    parser.add_argument(
        "--evidence-out",
        type=Path,
        default=Path("docs/assets/final-live-proof-evidence.json"),
        help="Safe evidence JSON path written by api_smoke.py.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Only check required env/packages; do not call api_smoke.py.",
    )
    return parser


def main() -> None:
    raise SystemExit(run_live_proof(build_parser().parse_args()))


if __name__ == "__main__":
    main()
