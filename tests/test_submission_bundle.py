import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from zipfile import ZipFile

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "submission_bundle.py"
SPEC = importlib.util.spec_from_file_location("submission_bundle", SCRIPT_PATH)
submission_bundle = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(submission_bundle)


def write_fixture_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_bundle_fixtures(root: Path) -> None:
    for _, relative_path, _ in submission_bundle.ARTIFACTS:
        if relative_path.endswith(".png"):
            write_fixture_file(root, relative_path, b"\x89PNG\r\n\x1a\nfixture")
        elif relative_path == "tasks.json":
            write_fixture_file(
                root,
                relative_path,
                json.dumps(
                    {
                        "project": "ProofFrame",
                        "updated_at": "2026-06-27T00:00:00Z",
                        "tasks": [
                            {
                                "id": task_id,
                                "title": f"{task_id} gate",
                                "phase": "P4 Submit",
                                "owner": "tester",
                                "status": "done",
                                "done_criteria": "Gate passes.",
                                "notes": "",
                            }
                            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
                        ],
                    }
                ),
            )
        elif relative_path.endswith("devpost-submission-packet.json"):
            write_fixture_file(
                root,
                relative_path,
                json.dumps(
                    {
                        "mode": "pre_live_safe",
                        "project_name": "ProofFrame",
                        "tagline": "A provenance-first vault for generated media.",
                        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
                        "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                        "claim_warning": "safe",
                    }
                ),
            )
        elif relative_path.endswith("sponsor-fit-audit.json"):
            write_fixture_file(root, relative_path, json.dumps({"ok": True}))
        elif relative_path.endswith("award-readiness-report.json"):
            write_fixture_file(root, relative_path, json.dumps({"score": 80}))
        elif relative_path.endswith("secret-scan-report.json"):
            write_fixture_file(
                root,
                relative_path,
                json.dumps(
                    {
                        "schema": "proofframe.secret_scan.v1",
                        "mode": "clear",
                        "ok": True,
                    }
                ),
            )
        elif relative_path.endswith("submission-audit-report.json"):
            write_fixture_file(
                root,
                relative_path,
                json.dumps(
                    {
                        "schema": "proofframe.submission_audit.v1",
                        "mode": "pre_submit_audit_ready",
                        "ok": True,
                    }
                ),
            )
        elif relative_path.endswith("devpost-submission-receipt.json"):
            write_fixture_file(
                root,
                relative_path,
                json.dumps(
                    {
                        "schema": "proofframe.devpost_submission_receipt.v1",
                        "mode": "submitted",
                        "ok": True,
                    }
                ),
            )
        else:
            write_fixture_file(root, relative_path, "# ProofFrame\n")


def write_final_gate_fixtures(root: Path, *, closeout_created_at: str = "2026-08-03T21:10:00Z") -> None:
    write_bundle_fixtures(root)
    tasks = {
        "project": "ProofFrame",
        "updated_at": "2026-08-03T21:15:00Z",
        "tasks": [
            {
                "id": task_id,
                "title": f"{task_id} gate",
                "phase": "P4 Submit",
                "owner": "tester",
                "status": "done",
                "done_criteria": "Gate passes.",
                "notes": "",
            }
            for task_id in ["T020", "T021", "T040", "T041", "T041A", "T042"]
        ],
    }
    write_fixture_file(root, "tasks.json", json.dumps(tasks))
    write_fixture_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(
            {
                "mode": "post_live_verified",
                "project_name": "ProofFrame",
                "tagline": "A provenance-first vault for generated media.",
                "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
                "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "claim_warning": "final",
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/final-live-proof-evidence.json",
        json.dumps(
            {
                "ok": True,
                "storage_backend": "b2",
                "generation_backend": "genblaze",
                "asset_storage_backend": "b2",
                "asset_provider": "genblaze/gmicloud-image",
                "asset_sha256": "a" * 64,
                "manifest_sha256": "b" * 64,
                "asset_storage_key": "campaigns/final/asset.png",
                "manifest_key": "campaigns/final/manifest.json",
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/secret-scan-report.json",
        json.dumps(
            {
                "schema": "proofframe.secret_scan.v1",
                "created_at": closeout_created_at,
                "mode": "clear",
                "ok": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/submission-audit-report.json",
        json.dumps(
            {
                "schema": "proofframe.submission_audit.v1",
                "created_at": closeout_created_at,
                "mode": "pre_submit_audit_ready",
                "ok": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/devpost-submission-receipt.json",
        json.dumps(
            {
                "schema": "proofframe.devpost_submission_receipt.v1",
                "created_at": "2026-08-03T21:05:00Z",
                "mode": "submitted",
                "ok": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/final-submission-control.json",
        json.dumps(
            {
                "schema": "proofframe.final_submission_control.v1",
                "created_at": closeout_created_at,
                "mode": "final_submit_ready",
                "safe_to_submit": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/final-video-publish-kit.json",
        json.dumps(
            {
                "schema": "proofframe.final_video_publish_kit.v1",
                "created_at": closeout_created_at,
                "mode": "public_video_ready",
                "ok": True,
                "safe_to_submit": True,
                "final_video_ready": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/final-launch-plan.json",
        json.dumps(
            {
                "schema": "proofframe.final_launch_plan.v1",
                "created_at": closeout_created_at,
                "mode": "submitted",
                "ok": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/devpost-submission-preview.json",
        json.dumps(
            {
                "schema": "proofframe.devpost_submission_preview.v1",
                "created_at": closeout_created_at,
                "mode": "final_preview_ready",
                "safe_to_submit": True,
                "ok": True,
            }
        ),
    )
    write_fixture_file(
        root,
        "docs/assets/judge-decision-brief.json",
        json.dumps(
            {
                "schema": "proofframe.judge_decision_brief.v1",
                "created_at": closeout_created_at,
                "mode": "final_decision_ready",
                "ok": True,
                "safe_to_submit": True,
            }
        ),
    )


def test_submission_bundle_fails_closed_when_artifacts_are_missing(tmp_path):
    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["safe_to_share"] is False
    assert "README.md" in manifest["missing_artifacts"]
    assert manifest["submission_gate"]["mode"] == "pre_live_safe"


def test_submission_bundle_manifest_records_artifacts_and_gate(tmp_path):
    write_bundle_fixtures(tmp_path)

    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["safe_to_share"] is True
    assert manifest["safe_to_submit"] is False
    assert manifest["devpost_packet"]["project_name"] == "ProofFrame"
    assert manifest["submission_gate"]["summary"]["done"] == 6
    assert manifest["submission_gate"]["report_gate"]["status"] == "verified"
    assert all("sha256" in artifact for artifact in manifest["artifacts"])


def test_submission_bundle_writes_markdown_json_and_optional_zip(tmp_path):
    write_bundle_fixtures(tmp_path)
    manifest = submission_bundle.build_manifest(tmp_path)
    json_path = tmp_path / "out" / "bundle.json"
    markdown_path = tmp_path / "out" / "bundle.md"
    zip_path = tmp_path / "out" / "bundle.zip"

    submission_bundle.write_outputs(
        manifest,
        json_path=json_path,
        markdown_path=markdown_path,
        zip_path=zip_path,
        root=tmp_path,
    )

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.submission_bundle.v1"
    assert "# ProofFrame Submission Bundle" in markdown
    assert "No credentials" in markdown
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "submission-bundle-manifest.json" in names
        assert "README.md" in names


def test_submission_bundle_cli_ok_tracks_final_gate_not_shareability(tmp_path):
    write_bundle_fixtures(tmp_path)
    manifest = submission_bundle.build_manifest(tmp_path)
    args = SimpleNamespace(
        json_out=tmp_path / "bundle.json",
        markdown_out=tmp_path / "bundle.md",
        zip_out=None,
    )

    summary = submission_bundle.cli_summary(manifest, args)

    assert summary["safe_to_share"] is True
    assert summary["safe_to_submit"] is False
    assert summary["ok"] is False


def test_submission_bundle_requires_post_receipt_closeout_reports(tmp_path):
    write_final_gate_fixtures(tmp_path)

    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["safe_to_share"] is True
    assert manifest["submission_gate"]["ok"] is True
    assert manifest["closeout_gate"]["ok"] is True
    assert manifest["safe_to_submit"] is True
    report_ids = {report["id"] for report in manifest["closeout_gate"]["reports"]}
    assert "final_video_publish_kit_after_receipt" in report_ids
    assert "judge_decision_brief_after_receipt" in report_ids


def test_submission_bundle_blocks_stale_closeout_reports(tmp_path):
    write_final_gate_fixtures(tmp_path, closeout_created_at="2026-08-03T21:00:00Z")

    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["submission_gate"]["ok"] is True
    assert manifest["closeout_gate"]["ok"] is False
    assert manifest["safe_to_submit"] is False
    assert any(
        "before the Devpost receipt" in finding
        for report in manifest["closeout_gate"]["reports"]
        for finding in report["findings"]
    )


def test_submission_bundle_strict_final_exits_when_gate_is_not_ready(tmp_path, monkeypatch):
    write_bundle_fixtures(tmp_path)
    monkeypatch.setattr(submission_bundle, "ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "submission_bundle.py",
            "--strict-final",
            "--json-out",
            str(tmp_path / "bundle.json"),
            "--markdown-out",
            str(tmp_path / "bundle.md"),
        ],
    )

    with pytest.raises(SystemExit) as exc:
        submission_bundle.main()

    assert exc.value.code == 2
