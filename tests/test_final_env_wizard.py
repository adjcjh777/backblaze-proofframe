import importlib.util
import json
import os
from pathlib import Path
import sys

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_env_wizard.py"
SPEC = importlib.util.spec_from_file_location("final_env_wizard", SCRIPT_PATH)
final_env_wizard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = final_env_wizard
SPEC.loader.exec_module(final_env_wizard)


def test_final_env_wizard_check_requires_ignored_output(tmp_path):
    (tmp_path / ".gitignore").write_text(".env.*\n!.env.final.example\n", encoding="utf-8")

    report = final_env_wizard.build_check(tmp_path, tmp_path / ".env.final.local")

    assert report["ok"] is True
    assert report["git_ignored"] is True
    assert "B2_APPLICATION_KEY" in report["secret_fields"]
    assert "GMI_API_KEY" in report["secret_fields"]


def test_final_env_wizard_check_fails_for_unignored_output(tmp_path):
    (tmp_path / ".gitignore").write_text("var/\n", encoding="utf-8")

    report = final_env_wizard.build_check(tmp_path, tmp_path / "final.env")

    assert report["ok"] is False
    assert report["git_ignored"] is False


def test_final_env_wizard_collects_from_env_and_mirrors_gmi_key():
    values = final_env_wizard.collect_values(
        from_env=True,
        environ={
            "B2_ENDPOINT_URL": "https://s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proof-bucket",
            "B2_KEY_ID": "least-privilege-key-id",
            "B2_APPLICATION_KEY": "secret-b2-key",
            "GMI_API_KEY": "secret-gmi-key",
        },
    )

    assert values["PROOFFRAME_STORAGE_BACKEND"] == "b2"
    assert values["PROOFFRAME_GENERATION_BACKEND"] == "genblaze"
    assert values["GENBLAZE_API_KEY"] == "secret-gmi-key"
    assert values["GMI_API_KEY"] == "secret-gmi-key"
    assert values["GENBLAZE_IMAGE_MODEL"] == "seedream-5.0-lite"


def test_final_env_wizard_refuses_missing_required_env():
    with pytest.raises(ValueError, match="B2_ENDPOINT_URL"):
        final_env_wizard.collect_values(from_env=True, environ={})


def test_final_env_wizard_writes_0600_and_does_not_print_values(tmp_path):
    path = tmp_path / ".env.final.local"
    values = {
        "PROOFFRAME_STORAGE_BACKEND": "b2",
        "PROOFFRAME_GENERATION_BACKEND": "genblaze",
        "B2_ENDPOINT_URL": "https://s3.us-west-004.backblazeb2.com",
        "B2_BUCKET": "proof-bucket",
        "B2_KEY_ID": "least-privilege-key-id",
        "B2_APPLICATION_KEY": "secret-b2-key",
        "GENBLAZE_API_KEY": "secret-gmi-key",
        "GMI_API_KEY": "secret-gmi-key",
        "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
    }
    content = final_env_wizard.render_env_file(values)

    final_env_wizard.write_env_file(path, content, force=False)
    summary = json.dumps(final_env_wizard.build_success(path, values))

    assert path.exists()
    assert oct(os.stat(path).st_mode & 0o777) == "0o600"
    assert "secret-b2-key" in path.read_text(encoding="utf-8")
    assert "secret-b2-key" not in summary
    assert "secret-gmi-key" not in summary
    with pytest.raises(FileExistsError):
        final_env_wizard.write_env_file(path, content, force=False)
