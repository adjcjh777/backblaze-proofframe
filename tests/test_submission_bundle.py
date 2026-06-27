import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile


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


def test_submission_bundle_fails_closed_when_artifacts_are_missing(tmp_path):
    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["safe_to_share"] is False
    assert "README.md" in manifest["missing_artifacts"]
    assert manifest["submission_gate"]["mode"] == "pre_live_safe"


def test_submission_bundle_manifest_records_artifacts_and_gate(tmp_path):
    write_bundle_fixtures(tmp_path)

    manifest = submission_bundle.build_manifest(tmp_path)

    assert manifest["safe_to_share"] is True
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
