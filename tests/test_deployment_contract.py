from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_includes_submission_gate_artifacts() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY tasks.json ./tasks.json" in dockerfile
    assert "COPY docs/assets ./docs/assets" in dockerfile
    assert 'ARG INSTALL_EXTRAS=""' in dockerfile
    assert 'pip install --no-cache-dir ".[${INSTALL_EXTRAS}]"' in dockerfile


def test_dockerignore_excludes_local_secret_and_runtime_paths() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    lines = {line.strip() for line in dockerignore.splitlines() if line.strip()}

    assert ".env" in lines
    assert ".env.*" in lines
    assert ".env.final.local" in lines
    assert "!.env.example" in lines
    assert "!.env.final.example" in lines
    assert ".venv/" in lines
    assert "var/" in lines
    assert "output/" in lines
