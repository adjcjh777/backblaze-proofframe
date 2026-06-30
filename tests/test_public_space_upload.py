import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "public_space_upload.py"
SPEC = importlib.util.spec_from_file_location("public_space_upload", SCRIPT_PATH)
public_space_upload = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_space_upload)


def write_file(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_dry_run_excludes_local_secret_files(tmp_path: Path) -> None:
    write_file(tmp_path, ".env.final.local", "B2_APPLICATION_KEY=secret")
    write_file(tmp_path, ".env.example", "")
    write_file(tmp_path, ".env.final.example", "")
    write_file(tmp_path, ".git/config", "[remote]\n")
    write_file(tmp_path, ".venv/pyvenv.cfg", "home = /tmp")
    write_file(tmp_path, "apps/web/index.html", "<main>ProofFrame</main>")

    report = public_space_upload.build_report(root=tmp_path)

    assert report["ok"] is True
    assert report["mode"] == "dry_run_ready"
    assert report["upload"]["attempted"] is False
    assert report["file_plan"]["included_sensitive"] == []
    assert ".env.final.local" in report["file_plan"]["excluded_samples"]
    assert ".env.final.example" in report["file_plan"]["included_samples"]
    assert ".git/config" in report["file_plan"]["excluded_samples"]
    assert ".venv/pyvenv.cfg" in report["file_plan"]["excluded_samples"]


def test_execute_uses_uploader_and_secret_probe(tmp_path: Path) -> None:
    write_file(tmp_path, "README.md", "# ProofFrame\n")
    calls: list[dict[str, object]] = []
    probes: list[tuple[str, int]] = []

    def fake_uploader(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return {
            "ok": True,
            "commit_oid": "abc123",
            "commit_url": "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/commit/abc123",
        }

    def fake_probe(raw_base: str, timeout: int) -> dict[str, object]:
        probes.append((raw_base, timeout))
        return {
            "ok": True,
            "status": 404,
            "url": f"{raw_base}/.env.final.local",
        }

    report = public_space_upload.build_report(
        root=tmp_path,
        execute=True,
        uploader=fake_uploader,
        secret_probe=fake_probe,
    )

    assert report["ok"] is True
    assert report["mode"] == "uploaded"
    assert report["upload"]["commit_oid"] == "abc123"
    assert calls
    assert ".env.final.local" in calls[0]["ignore_patterns"]
    assert probes == [(report["space_raw_base"], 20)]
    assert report["secret_probe"]["ok"] is True


def test_execute_refuses_when_required_ignore_missing(tmp_path: Path) -> None:
    write_file(tmp_path, ".env.final.local", "B2_APPLICATION_KEY=secret")
    write_file(tmp_path, "README.md", "# ProofFrame\n")
    patterns = [
        pattern
        for pattern in public_space_upload.IGNORE_PATTERNS
        if pattern != ".env.final.local"
    ]

    def forbidden_uploader(**_: object) -> dict[str, object]:
        raise AssertionError("Uploader must not be called after a failed safety preflight.")

    report = public_space_upload.build_report(
        root=tmp_path,
        execute=True,
        ignore_patterns=patterns,
        uploader=forbidden_uploader,
    )

    assert report["ok"] is False
    assert report["mode"] == "blocked"
    assert report["upload"]["attempted"] is False
    assert ".env.final.local" in report["ignore_check"]["missing_patterns"]


def test_execute_reports_upload_failure(tmp_path: Path) -> None:
    write_file(tmp_path, "README.md", "# ProofFrame\n")

    def failing_uploader(**_: object) -> dict[str, object]:
        return {"ok": False, "error": "token missing"}

    report = public_space_upload.build_report(
        root=tmp_path,
        execute=True,
        uploader=failing_uploader,
    )

    assert report["ok"] is False
    assert report["mode"] == "upload_failed"
    assert report["secret_probe"]["attempted"] is False


def test_execute_reports_public_secret_probe_failure(tmp_path: Path) -> None:
    write_file(tmp_path, "README.md", "# ProofFrame\n")

    def fake_uploader(**_: object) -> dict[str, object]:
        return {"ok": True, "commit_oid": "abc123"}

    def exposed_secret_probe(raw_base: str, timeout: int) -> dict[str, object]:
        return {
            "ok": False,
            "status": 200,
            "url": f"{raw_base}/.env.final.local",
            "timeout": timeout,
        }

    report = public_space_upload.build_report(
        root=tmp_path,
        execute=True,
        uploader=fake_uploader,
        secret_probe=exposed_secret_probe,
    )

    assert report["ok"] is False
    assert report["mode"] == "post_upload_secret_probe_failed"
    assert report["secret_probe"]["status"] == 200


def test_markdown_mentions_raw_secret_probe(tmp_path: Path) -> None:
    write_file(tmp_path, "README.md", "# ProofFrame\n")

    def fake_uploader(**_: object) -> dict[str, object]:
        return {"ok": True, "commit_oid": "abc123"}

    def fake_probe(raw_base: str, timeout: int) -> dict[str, object]:
        return {"ok": True, "status": 404, "url": f"{raw_base}/.env.final.local"}

    report = public_space_upload.build_report(
        root=tmp_path,
        execute=True,
        uploader=fake_uploader,
        secret_probe=fake_probe,
    )
    markdown = public_space_upload.render_markdown(report)

    assert "Raw `.env.final.local` public check OK: `true`" in markdown
    assert "Raw base:" in markdown
