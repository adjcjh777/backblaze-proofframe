import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "docker_smoke.py"
SPEC = importlib.util.spec_from_file_location("docker_smoke", SCRIPT_PATH)
docker_smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(docker_smoke)


def write_dockerignore(root: Path) -> None:
    (root / ".dockerignore").write_text(
        "\n".join(
            [
                ".git/",
                ".env",
                ".env.*",
                "!.env.example",
                "!.env.final.example",
                ".env.final.local",
                ".venv/",
                "var/",
                "output/",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def fake_runner(args, cwd, timeout, env=None):
    if args[:2] == ["docker", "info"]:
        return {"ok": True, "returncode": 0, "stdout_tail": '"29.3.0"', "stderr_tail": ""}
    if args[:2] == ["docker", "build"]:
        return {"ok": True, "returncode": 0, "stdout_tail": "Successfully tagged", "stderr_tail": ""}
    if args[:2] == ["docker", "run"]:
        return {"ok": True, "returncode": 0, "stdout_tail": "container-id", "stderr_tail": ""}
    if args[:2] == ["docker", "logs"]:
        return {"ok": True, "returncode": 0, "stdout_tail": "Uvicorn running", "stderr_tail": ""}
    if args[:3] == ["docker", "rm", "-f"]:
        return {"ok": True, "returncode": 0, "stdout_tail": "removed", "stderr_tail": ""}
    if args[-1].startswith("http://127.0.0.1:"):
        assert env and env["PYTHONPATH"] == "src"
        return {"ok": True, "returncode": 0, "stdout_tail": '{"ok": true}', "stderr_tail": ""}
    raise AssertionError(f"unexpected command: {args}")


def recording_runner(calls, overrides=None):
    overrides = overrides or {}

    def runner(args, cwd, timeout, env=None):
        calls.append(args)
        command_id = "_".join(args[:2]) if args[:2] != ["docker", "rm"] else "docker_rm"
        if command_id in overrides:
            return overrides[command_id]
        return fake_runner(args, cwd, timeout, env)

    return runner


def healthy_fetcher(url, timeout):
    return {
        "ok": True,
        "status": 200,
        "json": {
            "ready": True,
            "storage_backend": "local",
            "generation_backend": "mock",
            "b2_configured": False,
            "genblaze_configured": False,
        },
        "error": None,
    }


def test_docker_smoke_report_passes_with_fake_runner(tmp_path):
    write_dockerignore(tmp_path)

    report = docker_smoke.build_report(
        root=tmp_path,
        command_runner=fake_runner,
        health_fetcher=healthy_fetcher,
        sleep_fn=lambda seconds: None,
    )

    assert report["schema"] == "proofframe.docker_smoke.v1"
    assert report["ok"] is True
    assert report["mode"] == "docker_smoke_ready"
    assert report["dockerignore"]["missing_required_patterns"] == []
    assert report["dockerignore"]["missing_allow_patterns"] == []
    assert {check["id"] for check in report["checks"]} >= {
        "dockerignore_secret_exclusions",
        "docker_build",
        "docker_health",
        "api_smoke",
    }
    assert "does not read .env.final.local" in report["secret_policy"]


def test_docker_smoke_cleans_up_after_health_exception(tmp_path):
    write_dockerignore(tmp_path)
    calls = []

    def broken_fetcher(url, timeout):
        raise RuntimeError("health exploded")

    report = docker_smoke.build_report(
        root=tmp_path,
        command_runner=recording_runner(calls),
        health_fetcher=broken_fetcher,
        sleep_fn=lambda seconds: None,
    )

    failed = {check["id"] for check in report["checks"] if not check["ok"]}
    assert report["ok"] is False
    assert "docker_health" in failed
    assert ["docker", "rm", "-f", "proofframe-submission-smoke"] in calls
    cleanup = next(command for command in report["commands"] if command["id"] == "docker_cleanup")
    assert cleanup["ok"] is True
    logs = next(command for command in report["commands"] if command["id"] == "docker_logs")
    assert "health exploded" in logs["stderr_tail"]


def test_docker_smoke_cleans_up_when_api_smoke_fails(tmp_path):
    write_dockerignore(tmp_path)
    calls = []
    report = docker_smoke.build_report(
        root=tmp_path,
        command_runner=recording_runner(
            calls,
            overrides={
                f"{docker_smoke.sys.executable}_scripts/api_smoke.py": {
                    "ok": False,
                    "returncode": 1,
                    "stdout_tail": "",
                    "stderr_tail": "api failed",
                }
            },
        ),
        health_fetcher=healthy_fetcher,
        sleep_fn=lambda seconds: None,
    )

    failed = {check["id"] for check in report["checks"] if not check["ok"]}
    assert report["ok"] is False
    assert "api_smoke" in failed
    assert ["docker", "rm", "-f", "proofframe-submission-smoke"] in calls


def test_docker_smoke_fails_closed_without_dockerignore(tmp_path):
    report = docker_smoke.build_report(
        root=tmp_path,
        command_runner=fake_runner,
        health_fetcher=healthy_fetcher,
        sleep_fn=lambda seconds: None,
    )

    failed = {check["id"] for check in report["checks"] if not check["ok"]}
    assert report["ok"] is False
    assert "dockerignore_secret_exclusions" in failed


def test_docker_smoke_writes_json_and_markdown(tmp_path):
    write_dockerignore(tmp_path)
    report = docker_smoke.build_report(
        root=tmp_path,
        command_runner=fake_runner,
        health_fetcher=healthy_fetcher,
        sleep_fn=lambda seconds: None,
    )
    json_path = tmp_path / "docker-smoke.json"
    markdown_path = tmp_path / "docker-smoke.md"

    docker_smoke.write_outputs(report, json_path, markdown_path)

    assert json_path.read_text(encoding="utf-8").startswith("{")
    assert "# ProofFrame Docker Smoke Report" in markdown_path.read_text(encoding="utf-8")
