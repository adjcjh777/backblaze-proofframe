import importlib.util
from pathlib import Path

from proofframe.config import Settings


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "live_proof.py"
SPEC = importlib.util.spec_from_file_location("live_proof", SCRIPT_PATH)
live_proof = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(live_proof)


def test_preflight_report_lists_missing_b2_and_genblaze_config():
    settings = Settings()

    report = live_proof.build_preflight_report(
        settings,
        require_storage_backend="b2",
        require_generation_backend="genblaze",
        available=lambda module: False,
    )

    missing_names = {item["name"] for item in report["missing"]}
    assert report["ok"] is False
    assert "storage backend mode" in missing_names
    assert "generation backend mode" in missing_names
    assert "B2 endpoint" in missing_names
    assert "B2 application key" in missing_names
    assert "B2 region for Genblaze sink" in missing_names
    assert "Genblaze provider API key" in missing_names
    assert "genblaze_core package" in missing_names
    assert "genblaze_s3 package" in missing_names
    assert "secret_policy" in report


def test_preflight_report_passes_with_complete_config():
    settings = Settings(
        storage_backend="b2",
        generation_backend="genblaze",
        b2_endpoint_url="https://s3.us-west-004.backblazeb2.com",
        b2_bucket="proof-bucket",
        b2_key_id="key-id",
        b2_application_key="application-key",
        genblaze_api_key="provider-key",
        genblaze_image_model="seedream-test",
    )

    report = live_proof.build_preflight_report(
        settings,
        require_storage_backend="b2",
        require_generation_backend="genblaze",
        available=lambda module: module
        in {"boto3", "genblaze_core", "genblaze_gmicloud", "genblaze_s3"},
    )

    assert report["ok"] is True
    assert report["missing"] == []


def test_preflight_report_accepts_openai_provider_package():
    settings = Settings(
        storage_backend="b2",
        generation_backend="genblaze",
        b2_endpoint_url="https://s3.us-west-004.backblazeb2.com",
        b2_bucket="proof-bucket",
        b2_key_id="key-id",
        b2_application_key="application-key",
        genblaze_provider="openai",
        openai_api_key="provider-key",
        genblaze_image_model="gpt-image-1",
    )

    report = live_proof.build_preflight_report(
        settings,
        require_storage_backend="b2",
        require_generation_backend="genblaze",
        available=lambda module: module in {"boto3", "genblaze_core", "genblaze_openai", "genblaze_s3"},
    )

    assert report["ok"] is True
    assert report["genblaze_provider"] == "openai"
    assert report["missing"] == []


def test_build_api_smoke_command_targets_final_backends(tmp_path):
    evidence_path = tmp_path / "final-evidence.json"

    command = live_proof.build_api_smoke_command(
        base_url="http://127.0.0.1:8088",
        evidence_out=evidence_path,
        require_storage_backend="b2",
        require_generation_backend="genblaze",
    )

    assert "--require-storage-backend" in command
    assert "b2" in command
    assert "--require-generation-backend" in command
    assert "genblaze" in command
    assert "--evidence-out" in command
    assert str(evidence_path) in command
