import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "demo_storyboard.py"
SPEC = importlib.util.spec_from_file_location("demo_storyboard", SCRIPT_PATH)
demo_storyboard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(demo_storyboard)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_fixtures(root: Path, *, live_done: bool = False, video_url: str | None = None) -> None:
    statuses = {
        "T020": "done" if live_done else "doing",
        "T021": "done" if live_done else "doing",
        "T040": "done",
        "T041": "todo",
        "T041A": "done" if live_done else "todo",
        "T042": "todo",
    }
    write_file(
        root,
        "tasks.json",
        json.dumps(
            {
                "tasks": [
                    {"id": task_id, "status": status, "title": task_id}
                    for task_id, status in statuses.items()
                ]
            }
        ),
    )
    packet_mode = "post_live_verified" if live_done else "pre_live_safe"
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(
            {
                "mode": packet_mode,
                "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "video_url": video_url or "TBD after final B2 and Genblaze proof.",
            }
        ),
    )
    for path in demo_storyboard.REQUIRED_ASSETS:
        if path.endswith(".json"):
            continue
        if path.endswith(".png"):
            write_file(root, path, b"\x89PNG\r\n\x1a\nfixture")
        else:
            write_file(root, path, "# ProofFrame\n")
    if live_done:
        write_file(
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
                    "asset_storage_key": "campaigns/cmp/media/asset.png",
                    "manifest_key": "campaigns/cmp/manifests/manifest.json",
                }
            ),
        )


def test_demo_storyboard_is_ready_for_mock_video_but_not_final(tmp_path):
    write_fixtures(tmp_path)

    storyboard = demo_storyboard.build_storyboard(tmp_path)

    assert storyboard["mock_storyboard_ready"] is True
    assert storyboard["final_video_ready"] is False
    assert storyboard["under_time_limit"] is True
    assert storyboard["total_seconds"] == 135
    assert storyboard["segments"][1]["title"] == "Sponsor evidence model"
    assert "Record and upload the final public demo video under 3 minutes." in storyboard["next_actions"]


def test_demo_storyboard_fails_when_required_asset_is_missing(tmp_path):
    write_fixtures(tmp_path)
    (tmp_path / "docs/assets/proofframe-local-ui-smoke.png").unlink()

    storyboard = demo_storyboard.build_storyboard(tmp_path)

    assert storyboard["mock_storyboard_ready"] is False
    assert "docs/assets/proofframe-local-ui-smoke.png" in storyboard["missing_assets"]


def test_demo_storyboard_passes_final_with_live_evidence_and_public_video(tmp_path):
    write_fixtures(tmp_path, live_done=True, video_url="https://youtu.be/example-proof")

    storyboard = demo_storyboard.build_storyboard(tmp_path)

    assert storyboard["mock_storyboard_ready"] is True
    assert storyboard["final_video_ready"] is True
    assert storyboard["mode"] == "final_video_ready"


def test_demo_storyboard_writes_outputs(tmp_path):
    write_fixtures(tmp_path)
    storyboard = demo_storyboard.build_storyboard(tmp_path)
    json_path = tmp_path / "out" / "storyboard.json"
    markdown_path = tmp_path / "out" / "storyboard.md"

    demo_storyboard.write_outputs(storyboard, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.demo_storyboard.v1"
    assert "# ProofFrame Demo Storyboard" in markdown
    assert "## Timeline" in markdown
