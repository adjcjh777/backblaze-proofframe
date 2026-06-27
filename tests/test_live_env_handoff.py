import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "live_env_handoff.py"
SPEC = importlib.util.spec_from_file_location("live_env_handoff", SCRIPT_PATH)
live_env_handoff = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(live_env_handoff)


def test_live_env_handoff_reports_missing_process_env(monkeypatch):
    for group in live_env_handoff.REQUIRED_GROUPS:
        for name in group["accepted_names"]:
            monkeypatch.delenv(name, raising=False)

    report = live_env_handoff.build_report()

    assert report["ok"] is False
    assert report["mode"] == "missing_live_env"
    assert "b2_application_key" in report["missing_ids"]
    assert "credential values" in report["secret_policy"]


def test_live_env_handoff_uses_env_file_without_leaking_values(tmp_path, monkeypatch):
    for group in live_env_handoff.REQUIRED_GROUPS:
        for name in group["accepted_names"]:
            monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env.final.local"
    env_file.write_text(
        "\n".join(
            [
                "PROOFFRAME_STORAGE_BACKEND=b2",
                "PROOFFRAME_GENERATION_BACKEND=genblaze",
                "B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com",
                "B2_BUCKET=proof-bucket",
                "B2_KEY_ID=least-privilege-key-id",
                "B2_APPLICATION_" + "KEY=super-secret-b2-value-1234567890",
                "GMI_API_" + "KEY=" + "g" + "mi-super-secret-value-1234567890",
                "GENBLAZE_IMAGE_MODEL=seedream-5.0-lite",
            ]
        ),
        encoding="utf-8",
    )

    report = live_env_handoff.build_report(env_file)
    rendered = live_env_handoff.render_markdown(report)
    serialized = json.dumps(report)

    assert report["ok"] is True
    assert report["missing_ids"] == []
    assert "B2_APPLICATION_KEY" in serialized
    assert "GMI_API_KEY" in serialized
    assert "super-secret" not in serialized
    assert "super-secret" not in rendered


def test_live_env_handoff_writes_reports(tmp_path):
    report = {
        "schema": "proofframe.live_credential_handoff.v1",
        "ok": False,
        "mode": "missing_live_env",
        "source": "fixture",
        "required": [],
        "optional": [],
        "missing_ids": ["b2_bucket"],
        "next_commands": [
            "python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only"
        ],
        "secret_policy": "No values.",
    }
    json_path = tmp_path / "handoff.json"
    markdown_path = tmp_path / "handoff.md"

    live_env_handoff.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.live_credential_handoff.v1"
    assert "# ProofFrame Live Credential Handoff" in markdown
