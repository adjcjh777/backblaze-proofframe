import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "recording_assets.py"
SPEC = importlib.util.spec_from_file_location("recording_assets", SCRIPT_PATH)
recording_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(recording_assets)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_file(root, relative_path, json.dumps(payload))


def write_fixtures(root: Path, *, final_ready: bool = False) -> None:
    for path in recording_assets.REQUIRED_RECORDING_ASSETS:
        if path.endswith(".png"):
            write_file(root, path, b"\x89PNG\r\n\x1a\nfixture")
        elif path.endswith(".mp4"):
            write_file(root, path, b"mp4-fixture")
        elif path.endswith(".json"):
            continue
        else:
            write_file(root, path, "# ProofFrame\n")
    write_json(
        root,
        "docs/assets/demo-storyboard.json",
        {
            "schema": "proofframe.demo_storyboard.v1",
            "mode": "final_video_ready" if final_ready else "mock_storyboard_ready",
            "mock_storyboard_ready": True,
            "final_video_ready": final_ready,
            "public_video_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/demo-readiness-report.json",
        {
            "schema": "proofframe.demo_readiness.v1",
            "mode": "final_ready" if final_ready else "pre_live_mock_ready",
            "mock_recording_ready": True,
            "final_recording_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/public-video-check.json",
        {
            "schema": "proofframe.public_video_check.v1",
            "mode": "public_video_verified" if final_ready else "pending_video_url",
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/demo-video-draft.json",
        {
            "schema": "proofframe.demo_video_draft.v1",
            "mode": "mock_video_draft_ready",
            "safe_to_submit": False,
            "final_video_ready": False,
            "public_video_draft_url": "https://example.test/proofframe-demo-draft.mp4",
        },
    )
    write_json(
        root,
        "docs/assets/final-video-publish-kit.json",
        {
            "schema": "proofframe.final_video_publish_kit.v1",
            "mode": "public_video_ready" if final_ready else "ready_for_final_upload",
            "ok": True,
            "safe_to_submit": final_ready,
            "final_video_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/public-demo-screenshot-report.json",
        {
            "schema": "proofframe.public_demo_screenshot.v1",
            "mode": "public_judge_screenshot_ready",
            "ok": True,
            "safe_to_commit": True,
            "screenshot": {
                "present": True,
                "path": "docs/assets/proofframe-hf-public-smoke.png",
                "ok": True,
            },
            "markers": {"visible_ok": True, "html_ok": True},
        },
    )
    write_json(
        root,
        "docs/assets/devpost-form-kit.json",
        {
            "schema": "proofframe.devpost_form_kit.v1",
            "mode": "final_form_ready" if final_ready else "pre_live_form_ready",
            "final_form_ready": final_ready,
            "public_video_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "final_submit_ready" if final_ready else "pre_live_control",
            "safe_to_submit": final_ready,
        },
    )


def fake_public_fetcher(url: str, timeout: int) -> dict:
    assert timeout == recording_assets.TIMEOUT_SECONDS
    if url.endswith("/?judge=1"):
        return {
            "ok": True,
            "status": 200,
            "body": (
                "Judge recording slate Sponsor Evidence Model shouldAutoLoadJudgeDemo "
                "Recording Runbook Final reports pending"
            ),
            "error": None,
        }
    if url.endswith("/api/health"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps({"ready": True, "storage_backend": "local", "generation_backend": "mock"}),
            "error": None,
        }
    if url.endswith("/api/submission/gate"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "mode": "pre_live_safe",
                    "tasks_path": "tasks.json",
                    "summary": {"done": 1},
                    "evidence_gate": {"path": "docs/assets/final-live-proof-evidence.json"},
                    "packet_gate": {"path": "docs/assets/devpost-submission-packet.json"},
                    "report_gate": {"status": "incomplete"},
                }
            ),
            "error": None,
        }
    raise AssertionError(f"Unexpected URL: {url}")


def test_recording_assets_ready_offline_without_public_check(tmp_path):
    write_fixtures(tmp_path)

    report = recording_assets.build_report(tmp_path)

    assert report["mock_recording_ready"] is True
    assert report["public_mock_verified"] is False
    assert report["final_video_ready"] is False
    assert report["mode"] == "mock_recording_ready"
    assert report["source_reports"]["final_video_publish_kit"]["schema_ok"] is True
    assert report["source_reports"]["final_video_publish_kit"]["safe_to_submit"] is False


def test_recording_assets_fails_when_asset_missing(tmp_path):
    write_fixtures(tmp_path)
    (tmp_path / "docs/assets/proofframe-sponsor-model-smoke.png").unlink()

    report = recording_assets.build_report(tmp_path)

    assert report["mock_recording_ready"] is False
    assert "docs/assets/proofframe-sponsor-model-smoke.png" in report["missing_assets"]


def test_recording_assets_public_verification_is_get_only_and_ready(tmp_path):
    write_fixtures(tmp_path)

    report = recording_assets.build_report(
        tmp_path,
        verify_public=True,
        public_base_url="https://example.test",
        fetcher=fake_public_fetcher,
    )

    assert report["mock_recording_ready"] is True
    assert report["public_mock_verified"] is True
    assert report["mode"] == "public_mock_verified"
    assert report["public_verification"]["health"]["storage_backend"] == "local"
    assert report["public_verification"]["submission_gate"]["report_gate_present"] is True
    assert report["public_verification"]["submission_gate"]["paths_relative"] is True


def test_recording_assets_final_video_ready_when_source_reports_are_final(tmp_path):
    write_fixtures(tmp_path, final_ready=True)

    report = recording_assets.build_report(tmp_path)

    assert report["mock_recording_ready"] is True
    assert report["final_video_ready"] is True
    assert report["mode"] == "final_video_ready"


def test_recording_assets_writes_reports(tmp_path):
    write_fixtures(tmp_path)
    report = recording_assets.build_report(tmp_path)
    json_path = tmp_path / "out" / "recording.json"
    markdown_path = tmp_path / "out" / "recording.md"

    recording_assets.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.recording_assets.v1"
    assert "# ProofFrame Recording Assets" in markdown
    assert "## Public GET-only Verification" in markdown
