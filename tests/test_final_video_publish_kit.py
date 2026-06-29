import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "final_video_publish_kit.py"
SPEC = importlib.util.spec_from_file_location("final_video_publish_kit", SCRIPT_PATH)
final_video_publish_kit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(final_video_publish_kit)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_video_fixtures(
    root: Path,
    *,
    public_video_ready: bool = False,
    final_control_ready: bool = False,
) -> None:
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "schema": "proofframe.devpost_packet.v1",
            "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
            "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
            "video_url": "https://youtu.be/proofframe-final" if public_video_ready else "TBD after final proof.",
        },
    )
    write_json(
        root,
        "docs/assets/demo-storyboard.json",
        {
            "schema": "proofframe.demo_storyboard.v1",
            "shots": [
                {"id": "open", "title": "Open judge mode", "seconds": 20},
                {"id": "review", "title": "Review evidence packet", "seconds": 45},
            ],
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
            "video_path": "docs/assets/proofframe-demo-draft.mp4",
            "public_video_draft_url": "https://huggingface.co/demo-draft.mp4",
        },
    )
    write_json(
        root,
        "docs/assets/public-video-check.json",
        {
            "schema": "proofframe.public_video_check.v1",
            "mode": "public_video_verified" if public_video_ready else "pending_video_url",
            "ok": public_video_ready,
            "safe_to_submit": public_video_ready,
            "video_url": "https://youtu.be/proofframe-final" if public_video_ready else "TBD after final proof.",
            "url_analysis": {
                "official_host": public_video_ready,
                "official_host_family": "youtube" if public_video_ready else None,
            },
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "ok": True,
            "safe_to_submit": final_control_ready,
        },
    )
    write_json(
        root,
        "docs/assets/judge-evidence-index.json",
        {
            "schema": "proofframe.judge_evidence_index.v1",
            "ok": True,
        },
    )


def test_final_video_publish_kit_is_ready_but_not_final_without_public_url(tmp_path):
    write_video_fixtures(tmp_path)

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["schema"] == final_video_publish_kit.SCHEMA
    assert kit["ok"] is True
    assert kit["mode"] == "ready_for_final_upload"
    assert kit["safe_to_submit"] is False
    assert kit["final_video_ready"] is False
    assert kit["devpost_field"] == {
        "field_id": "video_url",
        "value": "TBD after final upload.",
        "ready": False,
        "source": "docs/assets/public-video-check.json",
    }
    assert "YouTube" in kit["allowed_hosts"]
    assert "does not prove live B2 or Genblaze" not in kit["description"]
    assert "safe_to_submit=false" in kit["description"]
    assert any(item["id"] == "host_family" and item["ok"] is False for item in kit["upload_checklist"])


def test_final_video_publish_kit_video_url_does_not_bypass_final_control(tmp_path):
    write_video_fixtures(tmp_path, public_video_ready=True, final_control_ready=False)

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["mode"] == "public_video_ready"
    assert kit["final_video_ready"] is True
    assert kit["safe_to_submit"] is False
    assert kit["devpost_field"]["ready"] is True
    assert kit["devpost_field"]["value"] == "https://youtu.be/proofframe-final"


def test_final_video_publish_kit_becomes_safe_only_after_video_and_final_control(tmp_path):
    write_video_fixtures(tmp_path, public_video_ready=True, final_control_ready=True)

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["mode"] == "public_video_ready"
    assert kit["final_video_ready"] is True
    assert kit["safe_to_submit"] is True


def test_final_video_publish_kit_fails_on_bad_source_schema(tmp_path):
    write_video_fixtures(tmp_path)
    write_json(tmp_path, "docs/assets/demo-storyboard.json", {"schema": "wrong"})

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["ok"] is False
    assert kit["source_reports"]["storyboard"]["schema_ok"] is False
    assert kit["safe_to_submit"] is False


def test_final_video_publish_kit_does_not_submit_when_public_video_schema_is_bad(tmp_path):
    write_video_fixtures(tmp_path, public_video_ready=True, final_control_ready=True)
    write_json(
        tmp_path,
        "docs/assets/public-video-check.json",
        {
            "schema": "wrong",
            "mode": "public_video_verified",
            "ok": True,
            "safe_to_submit": True,
            "video_url": "https://youtu.be/proofframe-final",
        },
    )

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["ok"] is False
    assert kit["final_video_ready"] is False
    assert kit["safe_to_submit"] is False


def test_final_video_publish_kit_does_not_submit_when_final_control_is_unhealthy(tmp_path):
    write_video_fixtures(tmp_path, public_video_ready=True, final_control_ready=True)
    write_json(
        tmp_path,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "ok": False,
            "safe_to_submit": True,
        },
    )

    kit = final_video_publish_kit.build_kit(tmp_path)

    assert kit["ok"] is True
    assert kit["final_video_ready"] is True
    assert kit["safe_to_submit"] is False


def test_final_video_publish_kit_writes_json_and_markdown(tmp_path):
    write_video_fixtures(tmp_path)
    kit = final_video_publish_kit.build_kit(tmp_path)
    json_path = tmp_path / "out" / "kit.json"
    markdown_path = tmp_path / "out" / "kit.md"

    final_video_publish_kit.write_outputs(kit, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.final_video_publish_kit.v1"
    assert "# ProofFrame Final Video Publish Kit" in markdown
    assert "Safe to submit: `false`" in markdown
    assert "Upload Checklist" in markdown
