import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "b2_key_scope_checklist.py"
SPEC = importlib.util.spec_from_file_location("b2_key_scope_checklist", SCRIPT_PATH)
b2_key_scope_checklist = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(b2_key_scope_checklist)


def write_setup(root: Path, payload: dict) -> Path:
    path = root / "docs/assets/b2-live-setup.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def valid_setup() -> dict:
    return {
        "schema": "proofframe.b2_live_setup.v1",
        "status": "bucket_created_key_pending",
        "bucket_name": "proofframe-demo-a6b4e49",
        "bucket_type": "private",
        "endpoint": "s3.us-west-004.backblazeb2.com",
        "application_key_name": "proofframe-demo-live-proof",
        "application_key_status": "form_prepared_not_created",
        "safe_to_commit": True,
        "secret_policy": "No secrets are stored.",
    }


def test_b2_key_scope_checklist_builds_no_secret_scope_report(tmp_path):
    setup_path = write_setup(tmp_path, valid_setup())

    report = b2_key_scope_checklist.build_report(setup_path)
    serialized = json.dumps(report)

    assert report["schema"] == "proofframe.b2_key_scope_checklist.v1"
    assert report["ok"] is True
    assert report["mode"] == "scope_ready_key_not_created"
    assert report["requires_user_confirmation_before_key_creation"] is True
    confirmation = report["pre_key_creation_confirmation"]
    assert confirmation["status"] == "required_before_key_creation"
    assert "proofframe-demo-a6b4e49" in confirmation["required_phrase"]
    assert "campaigns/" in confirmation["required_phrase"]
    assert "no delete/admin permissions" in confirmation["required_phrase"]
    assert confirmation["safe_to_store"] is True
    assert report["expected_key"]["bucket_scope"]["mode"] == "single_bucket"
    assert report["expected_key"]["file_name_prefix"]["value"] == "campaigns/"
    required = {item["capability"] for item in report["expected_key"]["required_capabilities"]}
    forbidden = {item["capability"] for item in report["expected_key"]["forbidden_capabilities"]}
    assert {"writeFiles", "listAllBucketNames"} <= required
    assert "deleteFiles" in forbidden
    assert "B2_APPLICATION_KEY=" not in serialized


def test_b2_key_scope_checklist_blocks_secret_fields_and_wide_setup(tmp_path):
    payload = {
        **valid_setup(),
        "bucket_type": "public",
        "safe_to_commit": False,
        "application_key_status": "created_with_secret",
        "application_key": "super-" + "secret-b2-value-1234567890",
    }
    setup_path = write_setup(tmp_path, payload)

    report = b2_key_scope_checklist.build_report(setup_path)

    assert report["ok"] is False
    assert report["mode"] == "scope_blocked"
    assert report["safe_to_commit"] is False
    assert "$.application_key" in report["secret_policy"]["forbidden_setup_fields"]
    failed_checks = {check["id"] for check in report["setup"]["checks"] if not check["ok"]}
    assert {"safe_to_commit", "private_bucket", "application_key_status_safe"} <= failed_checks


def test_b2_key_scope_checklist_markdown_and_outputs_do_not_leak(tmp_path):
    setup_path = write_setup(tmp_path, valid_setup())
    report = b2_key_scope_checklist.build_report(setup_path)
    json_path = tmp_path / "out/checklist.json"
    markdown_path = tmp_path / "out/checklist.md"

    b2_key_scope_checklist.write_outputs(report, json_path=json_path, markdown_path=markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.b2_key_scope_checklist.v1"
    assert saved["pre_key_creation_confirmation"]["status"] == "required_before_key_creation"
    assert "proofframe-demo-live-proof" in markdown
    assert "Required Pre-Key Confirmation" in markdown
    assert "no secrets in chat/docs/git" in markdown
    assert "`listAllBucketNames`" in markdown
    assert "No key id, application key, token, cookie, signed URL, or account secret is stored here." in markdown
