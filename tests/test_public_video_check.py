import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "public_video_check.py"
SPEC = importlib.util.spec_from_file_location("public_video_check", SCRIPT_PATH)
public_video_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_video_check)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_fixtures(root: Path, *, video_url: str = "TBD after final proof.") -> None:
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {
            "schema": "proofframe.devpost_event_snapshot.v1",
            "rules": {
                "requirements": {
                    "demo_video": True,
                    "video_under_three_minutes": True,
                    "public_video_host": True,
                }
            },
            "validation": {"ok": True, "submission_open": True},
        },
    )
    write_json(
        root,
        "docs/assets/demo-storyboard.json",
        {
            "schema": "proofframe.demo_storyboard.v1",
            "under_time_limit": True,
            "total_seconds": 135,
            "max_seconds": 180,
            "public_video_ready": video_url.startswith("https://"),
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "schema": "proofframe.devpost_packet.v1",
            "mode": "post_live_verified",
            "video_url": video_url,
        },
    )


def ok_fetcher(url: str, timeout: int) -> dict:
    return {
        "checked": True,
        "ok": True,
        "status": 200,
        "content_type": "text/html",
        "final_url": url,
        "error": None,
    }


def test_public_video_check_blocks_missing_video_url(tmp_path):
    write_fixtures(tmp_path)

    report = public_video_check.build_report(tmp_path)

    assert report["mode"] == "pending_video_url"
    assert report["safe_to_submit"] is False
    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert "video_url_present" in failed
    assert "video_url_accessible" in failed


def test_public_video_check_blocks_tokenized_url(tmp_path):
    write_fixtures(tmp_path, video_url="https://video.example.com/watch?id=demo&token=secretish")

    report = public_video_check.build_report(tmp_path, verify_url=True, fetcher=ok_fetcher)

    assert report["mode"] == "unsafe_video_url"
    assert report["safe_to_submit"] is False
    assert report["url_analysis"]["token_params"] == ["token"]
    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert "video_url_public_and_safe" in failed


def test_public_video_check_passes_public_verified_url(tmp_path):
    write_fixtures(tmp_path, video_url="https://youtu.be/proofframe-demo")

    report = public_video_check.build_report(tmp_path, verify_url=True, fetcher=ok_fetcher)

    assert report["mode"] == "public_video_verified"
    assert report["safe_to_submit"] is True
    assert report["access_check"]["status"] == 200


def test_public_video_check_writes_outputs(tmp_path):
    write_fixtures(tmp_path)
    report = public_video_check.build_report(tmp_path)
    json_path = tmp_path / "out" / "video.json"
    markdown_path = tmp_path / "out" / "video.md"

    public_video_check.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.public_video_check.v1"
    assert "# ProofFrame Public Video Check" in markdown
    assert "never credentials or browser state" in markdown
