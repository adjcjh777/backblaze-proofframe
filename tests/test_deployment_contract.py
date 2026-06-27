from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_includes_submission_gate_artifacts() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY tasks.json ./tasks.json" in dockerfile
    assert "COPY docs/assets ./docs/assets" in dockerfile
    assert 'ARG INSTALL_EXTRAS=""' in dockerfile
    assert 'pip install --no-cache-dir ".[${INSTALL_EXTRAS}]"' in dockerfile
