import argparse
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_final_live_proof.py"
SPEC = importlib.util.spec_from_file_location("run_final_live_proof", SCRIPT_PATH)
run_final_live_proof = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(run_final_live_proof)


def test_build_uvicorn_command_uses_requested_host_and_port():
    command = run_final_live_proof.build_uvicorn_command("127.0.0.1", 8099)

    assert command[:3] == [run_final_live_proof.sys.executable, "-m", "uvicorn"]
    assert "proofframe.app:app" in command
    assert "127.0.0.1" in command
    assert "8099" in command


def test_wait_for_live_app_accepts_only_b2_and_genblaze():
    calls = []

    def fake_read(url):
        calls.append(url)
        if len(calls) == 1:
            return {"ready": True, "storage_backend": "local", "generation_backend": "mock"}
        return {"ready": True, "storage_backend": "b2", "generation_backend": "genblaze"}

    health = run_final_live_proof.wait_for_live_app(
        "http://127.0.0.1:8088",
        timeout_seconds=1,
        read=fake_read,
    )

    assert health["storage_backend"] == "b2"
    assert health["generation_backend"] == "genblaze"
    assert calls == ["http://127.0.0.1:8088", "http://127.0.0.1:8088"]


def test_preflight_only_fails_closed_without_live_env(monkeypatch, tmp_path):
    for key in [
        "PROOFFRAME_STORAGE_BACKEND",
        "B2_ENDPOINT_URL",
        "B2_BUCKET",
        "B2_KEY_ID",
        "B2_APPLICATION_KEY",
        "B2_APP_KEY",
        "PROOFFRAME_GENERATION_BACKEND",
        "GENBLAZE_API_KEY",
        "GMI_API_KEY",
        "GENBLAZE_IMAGE_MODEL",
    ]:
        monkeypatch.delenv(key, raising=False)

    args = argparse.Namespace(
        host="127.0.0.1",
        port=8088,
        timeout_seconds=0.1,
        evidence_out=tmp_path / "evidence.json",
        log_path=tmp_path / "uvicorn.log",
        preflight_only=True,
    )

    assert run_final_live_proof.run_final_live_proof(args) == 2
    assert not args.evidence_out.exists()
