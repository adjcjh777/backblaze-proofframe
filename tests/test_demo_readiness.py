import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "demo_readiness.py"
SPEC = importlib.util.spec_from_file_location("demo_readiness", SCRIPT_PATH)
demo_readiness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(demo_readiness)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_tasks(root: Path, *, live_done: bool = False) -> None:
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
                "project": "ProofFrame",
                "tasks": [
                    {"id": task_id, "status": status, "title": task_id}
                    for task_id, status in statuses.items()
                ],
            }
        ),
    )


def write_demo_fixtures(root: Path, *, live_done: bool = False) -> None:
    write_tasks(root, live_done=live_done)
    write_file(root, "README.md", "ProofFrame includes a B2-compatible storage adapter.\n")
    write_file(
        root,
        "docs/submission.md",
        "The final submission target is B2-backed media after live proof.\n",
    )
    write_file(root, "docs/demo_script.md", "# Demo\n")
    write_file(
        root,
        "docs/public_claim_freeze.md",
        "Run claim lint before recording.\n",
    )
    packet_mode = "post_live_verified" if live_done else "pre_live_safe"
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(
            {
                "mode": packet_mode,
                "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "claim_warning": "safe",
            }
        ),
    )
    write_file(root, "docs/assets/devpost-submission-packet.md", "Final submission gate verifies B2.\n")
    write_file(root, "docs/assets/devpost-form-kit.json", "{}\n")
    write_file(root, "docs/assets/devpost-form-kit.md", "# Form Kit\n")
    write_file(root, "docs/assets/submission-bundle-manifest.json", "{}\n")
    write_file(root, "docs/assets/submission-bundle-manifest.md", "# Bundle\n")
    write_file(root, "docs/assets/live-credential-handoff.json", "{}\n")
    write_file(root, "docs/assets/live-credential-handoff.md", "# Handoff\n")
    write_file(root, "docs/assets/demo-storyboard.json", "{}\n")
    write_file(root, "docs/assets/demo-storyboard.md", "# Storyboard\n")
    write_file(root, "docs/assets/public-video-check.json", "{}\n")
    write_file(root, "docs/assets/public-video-check.md", "# Public Video Check\n")
    for screenshot in [
        "docs/assets/proofframe-local-ui-smoke.png",
        "docs/assets/proofframe-review-console-smoke.png",
        "docs/assets/proofframe-hf-public-smoke.png",
    ]:
        write_file(root, screenshot, b"\x89PNG\r\n\x1a\nfixture")
    write_file(root, ".env.final.example", "PROOFFRAME_STORAGE_BACKEND=b2\n")
    write_file(root, "scripts/claim_lint.py", "# claim lint\n")
    write_file(root, "scripts/devpost_form_kit.py", "# devpost form kit\n")
    write_file(root, "scripts/demo_storyboard.py", "# demo storyboard\n")
    write_file(root, "scripts/public_video_check.py", "# public video check\n")
    write_file(root, "scripts/live_env_handoff.py", "# live env handoff\n")
    write_file(root, "scripts/run_b2_live_proof.py", "# b2 live proof\n")
    write_file(root, "scripts/secret_scan.py", "# secret scan\n")
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


def test_demo_readiness_passes_for_mock_recording(tmp_path):
    write_demo_fixtures(tmp_path)

    report = demo_readiness.build_report(tmp_path)

    assert report["mock_recording_ready"] is True
    assert report["final_recording_ready"] is False
    assert report["mode"] == "pre_live_mock_ready"


def test_demo_readiness_fails_when_required_file_missing(tmp_path):
    write_demo_fixtures(tmp_path)
    (tmp_path / "docs/assets/proofframe-hf-public-smoke.png").unlink()

    report = demo_readiness.build_report(tmp_path)

    assert report["mock_recording_ready"] is False
    assert "docs/assets/proofframe-hf-public-smoke.png" in report["missing_files"]


def test_demo_readiness_passes_final_when_live_evidence_and_tasks_are_done(tmp_path):
    write_demo_fixtures(tmp_path, live_done=True)

    report = demo_readiness.build_report(tmp_path)

    assert report["mock_recording_ready"] is True
    assert report["final_recording_ready"] is True
    assert report["mode"] == "final_ready"


def test_demo_readiness_writes_reports(tmp_path):
    write_demo_fixtures(tmp_path)
    report = demo_readiness.build_report(tmp_path)
    json_path = tmp_path / "out" / "demo.json"
    markdown_path = tmp_path / "out" / "demo.md"

    demo_readiness.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.demo_readiness.v1"
    assert "# ProofFrame Demo Readiness" in markdown
