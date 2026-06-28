import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "post_credential_live_proof.py"
SPEC = importlib.util.spec_from_file_location("post_credential_live_proof", SCRIPT_PATH)
post_credential_live_proof = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = post_credential_live_proof
SPEC.loader.exec_module(post_credential_live_proof)


def test_build_commands_orders_live_proof_and_task_updates():
    commands = post_credential_live_proof.build_commands(
        env_file=Path(".env.final.local"),
        update_tasks=True,
        python="python",
    )
    command_ids = [command.command_id for command in commands]

    assert command_ids[:5] == [
        "credential_handoff",
        "b2_live_proof",
        "validate_b2_evidence",
        "mark_t020_done",
        "final_live_proof",
    ]
    assert command_ids[5:7] == [
        "validate_final_evidence",
        "mark_t021_done",
    ]
    assert "final_submission_control" in command_ids
    assert "submission_bundle" == command_ids[-1]
    assert "--env-file" in commands[0].command
    assert ".env.final.local" in commands[0].command


def test_plan_only_does_not_execute_commands():
    commands = post_credential_live_proof.build_commands(
        env_file=Path(".env.final.local"),
        update_tasks=False,
        python="python",
    )

    def forbidden_runner(*args, **kwargs):  # pragma: no cover - called only on failure
        raise AssertionError("plan-only mode should not execute subprocesses")

    sequence = post_credential_live_proof.run_sequence(
        commands,
        execute=False,
        runner=forbidden_runner,
    )

    assert sequence["ok"] is True
    assert sequence["mode"] == "plan_only"
    assert sequence["failed_command"] is None
    assert {command["status"] for command in sequence["commands"]} == {"planned"}


def test_execute_stops_on_first_failure():
    commands = post_credential_live_proof.build_commands(
        env_file=Path(".env.final.local"),
        update_tasks=True,
        python="python",
    )
    calls: list[list[str]] = []

    def fake_runner(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 2 if len(calls) == 2 else 0)

    sequence = post_credential_live_proof.run_sequence(
        commands,
        execute=True,
        runner=fake_runner,
    )

    assert sequence["ok"] is False
    assert sequence["mode"] == "failed"
    assert sequence["failed_command"] == "b2_live_proof"
    assert [command["status"] for command in sequence["commands"][:3]] == [
        "passed",
        "failed",
        "skipped",
    ]
    assert len(calls) == 2


def test_report_never_stores_secret_values():
    commands = post_credential_live_proof.build_commands(
        env_file=Path(".env.final.local"),
        update_tasks=False,
        python="python",
    )
    sequence = post_credential_live_proof.run_sequence(commands, execute=False)
    args = argparse.Namespace(
        env_file=Path(".env.final.local"),
        update_tasks=False,
        execute=False,
    )
    report = post_credential_live_proof.build_report(args, sequence)
    markdown = post_credential_live_proof.render_markdown(report)

    assert report["schema"] == "proofframe.post_credential_live_proof.v1"
    assert "Backblaze keys" in report["secret_policy"]
    assert "B2_APPLICATION_KEY=" not in markdown
    assert "GENBLAZE_API_KEY=" not in markdown


def test_validate_evidence_accepts_expected_b2_and_final_files(tmp_path):
    b2_evidence = {
        "ok": True,
        "storage_backend": "b2",
        "generation_backend": "mock",
        "asset_storage_backend": "b2",
        "asset_provider": "mock",
        "manifest_storage_backend": "b2",
        "asset_sha256": "a" * 64,
        "manifest_sha256": "b" * 64,
        "asset_storage_key": "campaigns/demo/assets/asset.png",
        "manifest_key": "campaigns/demo/manifests/manifest.json",
    }
    final_evidence = {
        **b2_evidence,
        "generation_backend": "genblaze",
        "asset_provider": "genblaze/gmicloud-image",
    }
    b2_path = tmp_path / "b2.json"
    final_path = tmp_path / "final.json"
    b2_path.write_text(json.dumps(b2_evidence), encoding="utf-8")
    final_path.write_text(json.dumps(final_evidence), encoding="utf-8")

    assert post_credential_live_proof.validate_evidence("b2", b2_path)["ok"] is True
    assert post_credential_live_proof.validate_evidence("final", final_path)["ok"] is True


def test_validate_evidence_rejects_wrong_backend_and_secret_shapes(tmp_path):
    evidence_path = tmp_path / "unsafe.json"
    evidence_path.write_text(
        json.dumps(
            {
                "ok": True,
                "storage_backend": "b2",
                "generation_backend": "mock",
                "asset_storage_backend": "b2",
                "asset_provider": "mock",
                "manifest_storage_backend": "b2",
                "asset_sha256": "a" * 64,
                "manifest_sha256": "b" * 64,
                "asset_storage_key": "campaigns/demo/assets/asset.png",
                "manifest_key": "campaigns/demo/manifests/manifest.json",
                "debug_url": "https://example.test/file?X-Amz-Signature=123456789abcdef",
            }
        ),
        encoding="utf-8",
    )

    report = post_credential_live_proof.validate_evidence("final", evidence_path)

    assert report["ok"] is False
    fields = {finding["field"] for finding in report["findings"]}
    assert "generation_backend" in fields
    assert "asset_provider" in fields
    assert "secret_safety" in fields
