#!/usr/bin/env python3
"""Build and smoke-test the ProofFrame Docker image without reading secrets."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from http.client import RemoteDisconnected
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.docker_smoke.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "docker-smoke-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "docker-smoke-report.md"
DEFAULT_IMAGE = "proofframe:submission-smoke"
DEFAULT_CONTAINER = "proofframe-submission-smoke"
DEFAULT_PORT = 18088
OUTPUT_TAIL_CHARS = 3000

CommandRunner = Callable[[list[str], Path, int, dict[str, str] | None], dict[str, Any]]
HealthFetcher = Callable[[str, int], dict[str, Any]]
SleepFn = Callable[[float], None]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tail_text(value: str | None) -> str:
    text = value or ""
    return text[-OUTPUT_TAIL_CHARS:]


def run_command(args: list[str], cwd: Path, timeout: int, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            env=merged_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout_tail": tail_text(completed.stdout),
            "stderr_tail": tail_text(completed.stderr),
        }
    except FileNotFoundError as exc:
        return {"ok": False, "returncode": None, "stdout_tail": "", "stderr_tail": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout_tail": tail_text(exc.stdout if isinstance(exc.stdout, str) else None),
            "stderr_tail": f"Timed out after {timeout}s. {tail_text(exc.stderr if isinstance(exc.stderr, str) else None)}",
        }


def fetch_health(url: str, timeout: int) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "ProofFrame Docker smoke"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            return {
                "ok": True,
                "status": response.status,
                "json": parsed if isinstance(parsed, dict) else {},
                "error": None,
            }
    except (HTTPError, URLError, TimeoutError, RemoteDisconnected, json.JSONDecodeError) as exc:
        return {"ok": False, "status": getattr(exc, "code", None), "json": {}, "error": str(exc)}


def dockerignore_status(root: Path) -> dict[str, Any]:
    path = root / ".dockerignore"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_patterns = {
        ".env",
        ".env.*",
        ".env.final.local",
        ".venv/",
        "var/",
        "output/",
        ".git/",
    }
    allow_patterns = {"!.env.example", "!.env.final.example"}
    lines = {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}
    return {
        "path": ".dockerignore",
        "present": path.exists(),
        "required_patterns_present": required_patterns <= lines,
        "missing_required_patterns": sorted(required_patterns - lines),
        "example_env_allowed": allow_patterns <= lines,
        "missing_allow_patterns": sorted(allow_patterns - lines),
    }


def check_item(check_id: str, label: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"id": check_id, "label": label, "ok": ok, "detail": detail}


def command_record(command_id: str, args: list[str], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": command_id,
        "command": args,
        "ok": result.get("ok") is True,
        "returncode": result.get("returncode"),
        "stdout_tail": result.get("stdout_tail", ""),
        "stderr_tail": result.get("stderr_tail", ""),
    }


def build_report(
    *,
    root: Path = ROOT,
    image: str = DEFAULT_IMAGE,
    container: str = DEFAULT_CONTAINER,
    port: int = DEFAULT_PORT,
    timeout_seconds: int = 90,
    command_runner: CommandRunner = run_command,
    health_fetcher: HealthFetcher = fetch_health,
    sleep_fn: SleepFn = time.sleep,
) -> dict[str, Any]:
    root = root.resolve()
    base_url = f"http://127.0.0.1:{port}"
    health_url = f"{base_url}/api/health"
    commands: list[dict[str, Any]] = []

    dockerignore = dockerignore_status(root)
    docker_info_args = ["docker", "info", "--format", "{{json .ServerVersion}}"]
    docker_info = command_runner(docker_info_args, root, 30, None)
    commands.append(command_record("docker_info", docker_info_args, docker_info))

    build_args = ["docker", "build", "-t", image, "."]
    build = command_runner(build_args, root, 600, None) if docker_info.get("ok") else {"ok": False}
    commands.append(command_record("docker_build", build_args, build))

    remove_args = ["docker", "rm", "-f", container]
    command_runner(remove_args, root, 30, None)

    run_args = ["docker", "run", "-d", "--name", container, "-p", f"{port}:8088", image]
    run = command_runner(run_args, root, 60, None) if build.get("ok") else {"ok": False}
    commands.append(command_record("docker_run", run_args, run))

    health: dict[str, Any] = {"ok": False, "json": {}, "error": "container did not start"}
    api_smoke: dict[str, Any] = {"ok": False}
    logs: dict[str, Any] = {"ok": False}
    cleanup: dict[str, Any] = {"ok": True, "returncode": 0}
    if run.get("ok"):
        try:
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                health = health_fetcher(health_url, 5)
                if health.get("ok"):
                    break
                sleep_fn(1)

            api_args = [sys.executable, "scripts/api_smoke.py", "--base-url", base_url]
            api_env = {"PYTHONPATH": "src"}
            api_smoke = command_runner(api_args, root, 90, api_env) if health.get("ok") else {"ok": False}

            logs_args = ["docker", "logs", "--tail", "80", container]
            logs = command_runner(logs_args, root, 30, None)
        except Exception as exc:  # pragma: no cover - exercised through injected fakes.
            error = f"{type(exc).__name__}: {exc}"
            if not health.get("ok"):
                health = {"ok": False, "json": {}, "error": error}
            if not api_smoke.get("ok"):
                api_smoke = {"ok": False, "returncode": None, "stdout_tail": "", "stderr_tail": error}
            logs = {"ok": False, "returncode": None, "stdout_tail": "", "stderr_tail": error}
        finally:
            cleanup = command_runner(remove_args, root, 30, None)

    api_args = [sys.executable, "scripts/api_smoke.py", "--base-url", base_url]
    commands.append(command_record("api_smoke", api_args, api_smoke))

    logs_args = ["docker", "logs", "--tail", "80", container]
    commands.append(command_record("docker_logs", logs_args, logs))

    commands.append(command_record("docker_cleanup", remove_args, cleanup))

    checks = [
        check_item(
            "dockerignore_secret_exclusions",
            ".dockerignore excludes local secrets and heavy runtime paths",
            bool(
                dockerignore["present"]
                and dockerignore["missing_required_patterns"] == []
                and dockerignore["missing_allow_patterns"] == []
            ),
            (
                f"missing_required={dockerignore['missing_required_patterns']}; "
                f"missing_allow={dockerignore['missing_allow_patterns']}."
            ),
        ),
        check_item("docker_daemon", "Docker daemon is reachable", docker_info.get("ok") is True, "docker info completed."),
        check_item("docker_build", "Docker image builds", build.get("ok") is True, "docker build completed."),
        check_item("docker_run", "Docker container starts", run.get("ok") is True, "docker run returned a container id."),
        check_item(
            "docker_health",
            "Dockerized app reports local/mock health",
            bool(
                health.get("ok")
                and health.get("json", {}).get("ready") is True
                and health.get("json", {}).get("storage_backend") == "local"
                and health.get("json", {}).get("generation_backend") == "mock"
                and health.get("json", {}).get("b2_configured") is False
                and health.get("json", {}).get("genblaze_configured") is False
            ),
            f"health={health.get('json')}; error={health.get('error')}.",
        ),
        check_item("api_smoke", "API smoke passes against the Docker container", api_smoke.get("ok") is True, "api_smoke.py completed."),
        check_item("docker_cleanup", "Smoke container is removed", cleanup.get("ok") is True, "docker rm -f completed."),
    ]
    ok = all(check["ok"] for check in checks)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "docker_smoke_ready" if ok else "docker_smoke_blocked",
        "safe_to_share": True,
        "image": image,
        "container": container,
        "base_url": base_url,
        "dockerignore": dockerignore,
        "health": health,
        "checks": checks,
        "commands": commands,
        "secret_policy": (
            "This smoke test uses local/mock mode, does not read .env.final.local, and requires .dockerignore "
            "to exclude local env files from the Docker build context."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Docker Smoke Report",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Image: `{report['image']}`",
        f"Base URL: `{report['base_url']}`",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        marker = "OK" if check["ok"] else "FAIL"
        lines.append(f"- {marker} `{check['id']}`: {check['detail']}")
    lines.extend(["", "## Docker Context Policy", "", report["secret_policy"], "", "## Commands", ""])
    for command in report["commands"]:
        marker = "OK" if command["ok"] else "FAIL"
        lines.append(f"- {marker} `{command['id']}`: `{' '.join(command['command'])}`")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and smoke-test the ProofFrame Docker image.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(
        root=args.root,
        image=args.image,
        container=args.container,
        port=args.port,
        timeout_seconds=args.timeout_seconds,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "image": report["image"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
