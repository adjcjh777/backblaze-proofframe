import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_submission_receipt.py"
SPEC = importlib.util.spec_from_file_location("devpost_submission_receipt", SCRIPT_PATH)
devpost_submission_receipt = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_submission_receipt)


def test_pending_receipt_is_not_ok():
    report = devpost_submission_receipt.build_receipt()

    assert report["schema"] == "proofframe.devpost_submission_receipt.v1"
    assert report["mode"] == "pending_submission"
    assert report["ok"] is False
    assert {item["field"] for item in report["findings"]} >= {
        "project_url",
        "submitted_at",
        "confirmation_note",
    }


def test_receipt_accepts_public_devpost_project_url(tmp_path):
    report = devpost_submission_receipt.build_receipt(
        root=tmp_path,
        project_url="https://devpost.com/software/proofframe?utm_source=devpost",
        submitted_at="2026-08-03T21:00:00Z",
        confirmation_note="Devpost accepted/submitted the ProofFrame project.",
    )

    assert report["ok"] is True
    assert report["mode"] == "submitted"
    assert report["project_url"] == "https://devpost.com/software/proofframe"
    assert report["submitted_at"] == "2026-08-03T21:00:00Z"


def test_receipt_rejects_manage_or_secret_query_urls(tmp_path):
    unsafe_query = "to" + "ken=secret"
    manage_url = "https://backblaze-generative-media.devpost.com/" + "manage/submissions"
    report = devpost_submission_receipt.build_receipt(
        root=tmp_path,
        project_url=f"{manage_url}?{unsafe_query}",
        submitted_at="2026-08-03T21:00:00Z",
        confirmation_note="Devpost accepted/submitted the ProofFrame project.",
    )

    assert report["ok"] is False
    details = " ".join(item["detail"] for item in report["findings"])
    assert "devpost.com" in details
    assert "unsafe query" in details


def test_receipt_validates_optional_screenshot_path(tmp_path):
    screenshot = tmp_path / "docs/assets/devpost-submitted.png"
    screenshot.parent.mkdir(parents=True)
    screenshot.write_bytes(b"\x89PNG\r\n\x1a\nfixture")

    report = devpost_submission_receipt.build_receipt(
        root=tmp_path,
        project_url="https://devpost.com/software/proofframe",
        submitted_at="2026-08-03T21:00:00Z",
        confirmation_note="Devpost accepted/submitted the ProofFrame project.",
        screenshot="docs/assets/devpost-submitted.png",
    )

    assert report["ok"] is True
    assert report["screenshot"] == "docs/assets/devpost-submitted.png"


def test_receipt_writes_json_and_markdown(tmp_path):
    report = devpost_submission_receipt.build_receipt()
    json_path = tmp_path / "out/receipt.json"
    markdown_path = tmp_path / "out/receipt.md"

    devpost_submission_receipt.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.devpost_submission_receipt.v1"
    assert "# ProofFrame Devpost Submission Receipt" in markdown
    assert "no cookies" in markdown.lower()
