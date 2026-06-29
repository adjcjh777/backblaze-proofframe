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


def test_final_env_wizard_uses_existing_file_values_as_prompt_defaults(tmp_path):
    existing = tmp_path / ".env.final.local"
    existing.write_text(
        "\n".join(
            [
                "PROOFFRAME_STORAGE_BACKEND=b2",
                "PROOFFRAME_GENERATION_BACKEND=genblaze",
                "B2_ENDPOINT_URL=s3.us-west-004.backblazeb2.com",
                "B2_BUCKET=proofframe-demo-a6b4e49",
                "B2_KEY_ID=existing-key-id",
                "B2_APPLICATION_KEY='existing b2 secret'",
                "GENBLAZE_API_KEY=existing-gmi-secret",
                "GENBLAZE_IMAGE_MODEL=seedream-5.0-lite",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    values = final_env_wizard.collect_values(
        from_env=False,
        initial_values=final_env_wizard.parse_env_file(existing),
        input_func=lambda prompt: "",
        secret_input=lambda prompt: "",
    )

    assert values["B2_ENDPOINT_URL"] == "s3.us-west-004.backblazeb2.com"
    assert values["B2_BUCKET"] == "proofframe-demo-a6b4e49"
    assert values["B2_KEY_ID"] == "existing-key-id"
    assert values["B2_APPLICATION_KEY"] == "existing b2 secret"
    assert values["GENBLAZE_API_KEY"] == "existing-gmi-secret"
    assert values["GMI_API_KEY"] == "existing-gmi-secret"


def test_final_env_wizard_collects_missing_values_only_and_mirrors_gmi_key(tmp_path):
    values, filled_names = final_env_wizard.collect_missing_values(
        initial_values={
            "PROOFFRAME_STORAGE_BACKEND": "b2",
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "B2_ENDPOINT_URL": "s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proofframe-demo-a6b4e49",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
        },
        input_func=lambda prompt: "least-privilege-key-id",
        secret_input=lambda prompt: (
            "secret-b2-key" if "Backblaze" in prompt else "secret-gmi-key"
        ),
    )
    summary = final_env_wizard.build_missing_only_success(
        tmp_path / ".env.final.local",
        values,
        filled_names,
    )

    assert values["B2_KEY_ID"] == "least-privilege-key-id"
    assert values["B2_APPLICATION_KEY"] == "secret-b2-key"
    assert values["GENBLAZE_API_KEY"] == "secret-gmi-key"
    assert values["GMI_API_KEY"] == "secret-gmi-key"
    assert filled_names == [
        "B2_KEY_ID",
        "B2_APPLICATION_KEY",
        "GENBLAZE_API_KEY",
        "GMI_API_KEY",
    ]
    assert "secret-b2-key" not in json.dumps(summary)
    assert "secret-gmi-key" not in json.dumps(summary)


def test_final_env_wizard_missing_only_no_prompts_when_complete():
    prompts: list[str] = []
    values, filled_names = final_env_wizard.collect_missing_values(
        initial_values={
            "PROOFFRAME_STORAGE_BACKEND": "b2",
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "B2_ENDPOINT_URL": "s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proofframe-demo-a6b4e49",
            "B2_KEY_ID": "least-privilege-key-id",
            "B2_APPLICATION_KEY": "secret-b2-key",
            "GMI_API_KEY": "secret-gmi-key",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
        },
        input_func=lambda prompt: prompts.append(prompt) or "",
        secret_input=lambda prompt: prompts.append(prompt) or "",
    )

    assert filled_names == []
    assert values["GMI_API_KEY"] == "secret-gmi-key"
    assert prompts == []


def test_final_env_wizard_missing_only_preserves_extra_local_values():
    values, filled_names = final_env_wizard.collect_missing_values(
        initial_values={
            "PROOFFRAME_STORAGE_BACKEND": "b2",
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "B2_ENDPOINT_URL": "s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proofframe-demo-a6b4e49",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
            "PROOFFRAME_LOCAL_NOTE": "keep-me",
        },
        input_func=lambda prompt: "least-privilege-key-id",
        secret_input=lambda prompt: (
            "secret-b2-key" if "Backblaze" in prompt else "secret-gmi-key"
        ),
    )
    rendered = final_env_wizard.render_env_file_preserving_extra(values)

    assert "PROOFFRAME_LOCAL_NOTE=keep-me" in rendered
    assert "# Preserved local-only values." in rendered
    assert "PROOFFRAME_LOCAL_NOTE" not in filled_names


def test_final_env_wizard_missing_only_from_env_does_not_override_existing_values():
    values, filled_names = final_env_wizard.collect_missing_values(
        initial_values={
            "PROOFFRAME_STORAGE_BACKEND": "b2",
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "B2_ENDPOINT_URL": "s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proofframe-demo-a6b4e49",
            "B2_KEY_ID": "existing-key-id",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
        },
        environ={
            "B2_KEY_ID": "env-key-id",
            "B2_APPLICATION_KEY": "env-b2-secret",
            "GENBLAZE_API_KEY": "env-gmi-secret",
        },
        input_func=lambda prompt: "",
        secret_input=lambda prompt: "",
    )

    assert values["B2_KEY_ID"] == "existing-key-id"
    assert values["B2_APPLICATION_KEY"] == "env-b2-secret"
    assert values["GENBLAZE_API_KEY"] == "env-gmi-secret"
    assert values["GMI_API_KEY"] == "env-gmi-secret"
    assert filled_names == []


def test_final_env_wizard_environment_overrides_existing_defaults(tmp_path):
    existing = tmp_path / ".env.final.local"
    existing.write_text("B2_BUCKET=old-bucket\n", encoding="utf-8")

    values = final_env_wizard.collect_values(
        from_env=True,
        environ={
            "B2_ENDPOINT_URL": "s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "env-bucket",
            "B2_KEY_ID": "env-key-id",
            "B2_APPLICATION_KEY": "env-b2-secret",
            "GENBLAZE_API_KEY": "env-gmi-secret",
        },
        initial_values=final_env_wizard.parse_env_file(existing),
    )

    assert values["B2_BUCKET"] == "env-bucket"


def test_final_env_wizard_prefills_non_secret_b2_values(tmp_path):
    setup_path = tmp_path / "b2-live-setup.json"
    setup_path.write_text(
        json.dumps(
            {
                "safe_to_commit": True,
                "bucket_name": "proofframe-demo-a6b4e49",
                "endpoint": "s3.us-west-004.backblazeb2.com",
            }
        ),
        encoding="utf-8",
    )

    values = final_env_wizard.non_secret_prefill_values(b2_setup_path=setup_path)
    summary = final_env_wizard.build_prefill_success(tmp_path / ".env.final.local", values)
    rendered = final_env_wizard.render_env_file(values)

    assert values["B2_BUCKET"] == "proofframe-demo-a6b4e49"
    assert values["B2_ENDPOINT_URL"] == "s3.us-west-004.backblazeb2.com"
    assert values["B2_REGION"] == "us-west-004"
    assert "B2_APPLICATION_KEY=" in rendered
    assert "GENBLAZE_API_KEY=" in rendered
    assert "B2_APPLICATION_KEY" in summary["missing_required_names"]
    assert "GENBLAZE_API_KEY" in summary["missing_secret_names"]
    assert "secret-b2-key" not in json.dumps(summary)
    assert "secret-gmi-key" not in json.dumps(summary)


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
