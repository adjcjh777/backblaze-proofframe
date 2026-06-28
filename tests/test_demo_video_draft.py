import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "demo_video_draft.py"
SPEC = importlib.util.spec_from_file_location("demo_video_draft", SCRIPT_PATH)
demo_video_draft = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(demo_video_draft)


def create_slide_inputs(root: Path) -> None:
    for slide in demo_video_draft.SLIDES:
        path = root / slide["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"png")


def test_demo_video_draft_ready_is_not_final_submit_ready(tmp_path):
    create_slide_inputs(tmp_path)
    video_path = tmp_path / "docs" / "assets" / "proofframe-demo-draft.mp4"
    video_path.write_bytes(b"video")

    def fake_probe(path: Path) -> dict:
        assert path == video_path.resolve()
        return {
            "checked": True,
            "ok": True,
            "duration_seconds": 54.0,
            "bytes": 1234,
            "width": 1280,
            "height": 720,
            "error": None,
        }

    report = demo_video_draft.build_report(tmp_path, video_path=video_path, prober=fake_probe)

    assert report["schema"] == "proofframe.demo_video_draft.v1"
    assert report["mode"] == "mock_video_draft_ready"
    assert report["ok"] is True
    assert report["safe_to_submit"] is False
    assert report["final_video_ready"] is False
    assert "not the final Devpost video" in report["claim_boundary"]
    assert all(check["ok"] for check in report["checks"])


def test_demo_video_draft_blocks_missing_slides(tmp_path):
    video_path = tmp_path / "docs" / "assets" / "proofframe-demo-draft.mp4"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    video_path.write_bytes(b"video")

    def fake_probe(path: Path) -> dict:
        return {
            "checked": True,
            "ok": True,
            "duration_seconds": 54.0,
            "bytes": 1234,
            "width": 1280,
            "height": 720,
            "error": None,
        }

    report = demo_video_draft.build_report(tmp_path, video_path=video_path, prober=fake_probe)

    assert report["ok"] is False
    assert report["mode"] == "missing_draft_inputs"
    assert len(report["missing_slides"]) == len(demo_video_draft.SLIDES)


def test_demo_video_draft_writes_reports(tmp_path):
    create_slide_inputs(tmp_path)
    video_path = tmp_path / "docs" / "assets" / "proofframe-demo-draft.mp4"
    video_path.write_bytes(b"video")

    def fake_probe(path: Path) -> dict:
        return {
            "checked": True,
            "ok": True,
            "duration_seconds": 54.0,
            "bytes": 1234,
            "width": 1280,
            "height": 720,
            "error": None,
        }

    report = demo_video_draft.build_report(tmp_path, video_path=video_path, prober=fake_probe)
    json_path = tmp_path / "draft.json"
    markdown_path = tmp_path / "draft.md"

    demo_video_draft.write_outputs(report, json_path, markdown_path)

    assert "proofframe.demo_video_draft.v1" in json_path.read_text(encoding="utf-8")
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# ProofFrame Demo Video Draft" in markdown
    assert "Safe to submit: `false`" in markdown
