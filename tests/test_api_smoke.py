import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "api_smoke.py"
SPEC = importlib.util.spec_from_file_location("api_smoke", SCRIPT_PATH)
api_smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(api_smoke)


def test_require_backend_passes_when_expected_matches():
    api_smoke.require_backend("storage_backend", "b2", "b2")
    api_smoke.require_backend("storage_backend", "local", None)


def test_require_backend_exits_when_expected_mismatches():
    with pytest.raises(SystemExit, match="Expected generation_backend=genblaze"):
        api_smoke.require_backend("generation_backend", "mock", "genblaze")


def test_write_evidence_creates_safe_json(tmp_path):
    output = tmp_path / "proof" / "evidence.json"

    api_smoke.write_evidence(output, {"ok": True, "storage_backend": "b2"})

    assert json.loads(output.read_text(encoding="utf-8")) == {
        "ok": True,
        "storage_backend": "b2",
    }


def test_write_evidence_refuses_secret_like_key(tmp_path):
    output = tmp_path / "proof" / "evidence.json"

    with pytest.raises(SystemExit, match="forbidden evidence key"):
        api_smoke.write_evidence(output, {"GENBLAZE_API_KEY": "placeholder"})

    assert not output.exists()


def test_write_evidence_refuses_signed_url_value(tmp_path):
    output = tmp_path / "proof" / "evidence.json"
    signature_key = "X-Amz-" + "Signature"

    with pytest.raises(SystemExit, match="forbidden evidence value"):
        api_smoke.write_evidence(
            output,
            {
                "asset_url": (
                    "https://example.test/object.png?"
                    f"{signature_key}=0123456789abcdef0123456789abcdef"
                )
            },
        )

    assert not output.exists()
