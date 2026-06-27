#!/usr/bin/env python3
"""Start ProofFrame with B2 storage and mock generation for T020 live proof."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable
from urllib.error import URLError
from urllib.request import urlopen

from proofframe.config import Settings


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / ".env.final.local"
DEFAULT_EVIDENCE = ROOT / "docs" / "assets" / "b2-live-proof-evidence.json"
DEFAULT_LOG = ROOT / "var" / "live-proof" / "b2-uvicorn.log"
LIVE_PROOF_PATH = ROOT / "scripts" / "live_proof.py"
LIVE_ENV_HANDOFF_PATH = ROOT / "scripts" / "live_env_handoff.py"

LIVE_PROOF_SPEC = importlib.util.spec_from_file_location("live_proof", LIVE_PROOF_PATH)
live_proof = importlib.util.module_from_spec(LIVE_PROOF_SPEC)
assert LIVE_PROOF_SPEC.loader is not None
LIVE_PROOF_SPEC.loader.exec_module(live_proof)

LIVE_ENV_HANDOFF_SPEC = importlib.util.spec_from_file_location(
    "live_env_handoff", LIVE_ENV_HANDOFF_PATH
)
live_env_handoff = importlib.util.module_from_spec(LIVE_ENV_HANDOFF_SPEC)
assert LIVE_ENV_HANDOFF_SPEC.loader is not None
LIVE_ENV_HANDOFF_SPEC.loader.exec_module(live_env_handoff)


def build_uvicorn_command(host: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "proofframe.app:app",
        "--host",
        host,
        "--port",
        str(port),
    ]


def base_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def read_health(url: str) -> dict[str, Any]:
    with urlopen(f"{url.rstrip('/')}/api/health", timeout=2) as response:
        return json.loads(response.read().decode("utf-8"))


def apply_env_file(env_file: Path | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if env_file and env_file.exists():
        values.update(live_env_handoff.parse_env_file(env_file))
    values["PROOFFRAME_STORAGE_BACKEND"] = "b2"
    values["PROOFFRAME_GENERATION_BACKEND"] = "mock"
    os.environ.update(values)
    return values


def wait_for_b2_app(
    url: str,
    *,
    timeout_seconds: float,
    read: Callable[[str], dict[str, Any]] = read_health,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        try:
            health = read(url)
        except (OSError, URLError, json.JSONDecodeError) as exc:
            last_error = str(exc)
        else:
            if (
                health.get("ready")
                and health.get("storage_backend") == "b2"
                and health.get("generation_backend") == "mock"
            ):
                return health
            last_error = (
                "App responded but did not report storage_backend=b2 and "
                f"generation_backend=mock: {health}"
            )
        time.sleep(0.5)
    raise RuntimeError(f"B2 ProofFrame app did not become ready. Last error: {last_error}")


def run_b2_live_proof(args: argparse.Namespace) -> int:
    apply_env_file(args.env_file)
    settings = Settings.from_env()
    report = live_proof.build_preflight_report(
        settings,
        require_storage_backend="b2",
        require_generation_backend="mock",
    )
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        return 2
    if args.preflight_only:
        return 0

    url = base_url(args.host, args.port)
    command = build_uvicorn_command(args.host, args.port)
    args.log_path.parent.mkdir(parents=True, exist_ok=True)
    with args.log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        try:
            health = wait_for_b2_app(url, timeout_seconds=args.timeout_seconds)
            print(
                json.dumps(
                    {
                        "ok": True,
                        "base_url": url,
                        "health": health,
                        "log_path": str(args.log_path),
                    },
                    indent=2,
                )
            )
            smoke_command = live_proof.build_api_smoke_command(
                base_url=url,
                evidence_out=args.evidence_out,
                require_storage_backend="b2",
                require_generation_backend="mock",
            )
            completed = subprocess.run(smoke_command, cwd=ROOT, check=False)
            return completed.returncode
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Start a local ProofFrame server with B2 storage plus mock generation and write "
            "sanitized B2 live proof evidence."
        )
    )
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--evidence-out", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Check B2 env/packages only; do not start the app or write evidence.",
    )
    return parser


def main() -> None:
    raise SystemExit(run_b2_live_proof(build_parser().parse_args()))


if __name__ == "__main__":
    main()
