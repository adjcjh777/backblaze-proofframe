import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "genblaze_contract_check.py"
SPEC = importlib.util.spec_from_file_location("genblaze_contract_check", SCRIPT_PATH)
genblaze_contract_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(genblaze_contract_check)


def test_genblaze_contract_check_passes_with_installed_integrations():
    report = genblaze_contract_check.build_report()

    assert report["schema"] == "proofframe.genblaze_contract_check.v1"
    assert report["ok"] is True
    assert report["mode"] == "sdk_contract_ready"
    assert report["failed_checks"] == []
    assert report["package_versions"]["genblaze_core"]
    assert "does not read environment variables" in report["secret_policy"]
    check_ids = {check["id"] for check in report["checks"]}
    assert "gmicloud_image_provider_ctor" in check_ids
    assert "s3_for_backblaze_signature" in check_ids
    assert "s3_readback_methods" in check_ids
    assert "pipeline_step_aspect_ratio" in check_ids


def test_genblaze_contract_check_fails_closed_when_package_missing():
    def missing_importer(module_name):
        raise ModuleNotFoundError(module_name)

    report = genblaze_contract_check.build_report(importer=missing_importer)

    assert report["ok"] is False
    assert report["mode"] == "sdk_contract_blocked"
    assert "genblaze_core_import" in report["failed_checks"]
    assert "gmicloud_image_provider_ctor" in report["failed_checks"]


def test_genblaze_contract_check_fails_closed_on_import_error():
    def broken_importer(module_name):
        raise ImportError(f"{module_name} dependency mismatch")

    report = genblaze_contract_check.build_report(importer=broken_importer)

    assert report["ok"] is False
    assert report["mode"] == "sdk_contract_blocked"
    assert "genblaze_core_import" in report["failed_checks"]
    assert any("ImportError" in check["detail"] for check in report["checks"])


def test_genblaze_contract_check_fails_when_pipeline_step_cannot_accept_aspect_ratio():
    class Pipeline:
        def __init__(self, name, project_id):
            self.name = name
            self.project_id = project_id

        def step(self, provider, model, prompt, modality):
            return self

        def run(self, sink, timeout, max_retries, raise_on_failure):
            return None

    class GMICloudImageProvider:
        def __init__(self, api_key, base_url, http_timeout):
            self.api_key = api_key
            self.base_url = base_url
            self.http_timeout = http_timeout

    class S3StorageBackend:
        @classmethod
        def for_backblaze(cls, bucket, region, key_id, app_key, public_url_base, preflight):
            return cls()

        def close(self):
            return None

        def get(self, key):
            return None

        def key_from_url(self, url):
            return url

    class ObjectStorageSink:
        def __init__(self, backend, prefix, key_strategy):
            self.backend = backend
            self.prefix = prefix
            self.key_strategy = key_strategy

    class KeyStrategy:
        HIERARCHICAL = "hierarchical"

    modules = {
        "genblaze_core": SimpleNamespace(
            KeyStrategy=KeyStrategy,
            Modality=SimpleNamespace(IMAGE="image"),
            ObjectStorageSink=ObjectStorageSink,
            Pipeline=Pipeline,
        ),
        "genblaze_gmicloud": SimpleNamespace(GMICloudImageProvider=GMICloudImageProvider),
        "genblaze_s3": SimpleNamespace(S3StorageBackend=S3StorageBackend),
    }

    report = genblaze_contract_check.build_report(importer=modules.__getitem__)

    assert report["ok"] is False
    assert "pipeline_step_aspect_ratio" in report["failed_checks"]


def test_genblaze_contract_check_writes_json_and_markdown(tmp_path):
    report = genblaze_contract_check.build_report()
    json_path = tmp_path / "contract.json"
    markdown_path = tmp_path / "contract.md"

    genblaze_contract_check.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.genblaze_contract_check.v1"
    assert "# Genblaze SDK Contract Check" in markdown
    assert "Backblaze keys" in markdown


def test_genblaze_contract_check_cli_exits_nonzero_on_failed_contract(tmp_path, monkeypatch):
    def fake_report():
        return {
            "schema": "proofframe.genblaze_contract_check.v1",
            "created_at": "2026-06-29T00:00:00Z",
            "ok": False,
            "mode": "sdk_contract_blocked",
            "package_versions": {},
            "checks": [],
            "failed_checks": ["fixture"],
            "secret_policy": "No secrets.",
        }

    monkeypatch.setattr(genblaze_contract_check, "build_report", fake_report)
    monkeypatch.setattr(
        genblaze_contract_check,
        "build_parser",
        lambda: SimpleNamespace(
            parse_args=lambda: SimpleNamespace(
                json_out=tmp_path / "contract.json",
                markdown_out=tmp_path / "contract.md",
            )
        ),
    )

    with pytest.raises(SystemExit) as exc:
        genblaze_contract_check.main()

    assert exc.value.code == 2
