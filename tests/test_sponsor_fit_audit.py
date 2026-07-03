import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sponsor_fit_audit.py"
SPEC = importlib.util.spec_from_file_location("sponsor_fit_audit", SCRIPT_PATH)
sponsor_fit_audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sponsor_fit_audit)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_fixtures(root: Path) -> None:
    write_file(
        root,
        "tasks.json",
        json.dumps(
            {
                "tasks": [
                    {"id": "T020", "status": "doing", "title": "B2"},
                    {"id": "T021", "status": "doing", "title": "Genblaze"},
                    {"id": "T040", "status": "done", "title": "Register"},
                    {"id": "T041", "status": "todo", "title": "Audit"},
                    {"id": "T041A", "status": "todo", "title": "Secret scan"},
                    {"id": "T042", "status": "todo", "title": "Submit"},
                ]
            }
        ),
    )
    write_file(root, "README.md", "ProofFrame final gate verifies B2.\n")
    write_file(root, "docs/submission.md", "Final submission target uses B2 after proof.\n")
    write_file(
        root,
        "docs/sponsor_fit_matrix.md",
        "# Matrix\nOfficial judging angle Backblaze B2 Genblaze\n",
    )
    write_file(
        root,
        "apps/web/index.html",
        "<section>Sponsor Evidence Model <b>Genblaze Step</b> <b>B2 Object Route</b></section>\n",
    )
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(
            {
                "mode": "pre_live_safe",
                "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "video_url": "TBD after final B2 and Genblaze proof.",
                "b2_usage": (
                    "ProofFrame treats Backblaze B2 as the final durable evidence layer rather "
                    "than a file dump. The local demo records the same manifest shape that will "
                    "be used for B2: storage backend, storage key, checksum, byte size, prompt, "
                    "provider/model metadata, approval state, and risk note. A dedicated private "
                    "B2 bucket is prepared, and a one-command runner verifies asset plus manifest "
                    "upload as the final submission gate before any public B2 storage claim is made."
                ),
                "genblaze_usage": (
                    "ProofFrame includes Genblaze provider adapters around the official "
                    "Pipeline API. The public demo stays on deterministic mock generation, while "
                    "the final submission gate verifies provider, model, and run metadata from a "
                    "live Genblaze-compatible path."
                ),
            }
        ),
    )
    write_file(root, "docs/assets/devpost-submission-packet.md", "Final submission gate B2.\n")
    write_file(root, "docs/assets/devpost-form-kit.json", "{}\n")
    write_file(root, "docs/assets/devpost-form-kit.md", "# Form Kit\n")
    for path in [
        "docs/demo_script.md",
        "docs/assets/proofframe-local-ui-smoke.png",
        "docs/assets/proofframe-review-console-smoke.png",
        "docs/assets/proofframe-hf-public-smoke.png",
        "docs/assets/demo-readiness-report.md",
        "docs/assets/live-credential-handoff.md",
    ]:
        if path.endswith(".png"):
            write_file(root, path, b"\x89PNG\r\n\x1a\nfixture")
        else:
            write_file(root, path, "# ProofFrame\n")


def test_sponsor_fit_audit_passes_when_copy_and_storyboard_are_specific(tmp_path):
    write_fixtures(tmp_path)
    original_segments = sponsor_fit_audit.demo_storyboard.SEGMENTS
    sponsor_fit_audit.demo_storyboard.SEGMENTS = [
        {
            "start": "0:12",
            "end": "0:28",
            "seconds": 16,
            "title": "B2 evidence model",
            "screen": "B2-ready manifest fields.",
            "safe_narration": "Backblaze B2 is the durable evidence target.",
        },
        {
            "start": "0:48",
            "end": "1:10",
            "seconds": 22,
            "title": "Generate variants",
            "screen": "Provider/model fields.",
            "safe_narration": "Genblaze metadata lands in the same manifest fields.",
        },
    ]
    try:
        report = sponsor_fit_audit.build_report(tmp_path)
    finally:
        sponsor_fit_audit.demo_storyboard.SEGMENTS = original_segments

    assert report["ok"] is True
    assert report["mode"] == "sponsor_fit_ready"


def test_sponsor_fit_audit_flags_thin_b2_copy(tmp_path):
    write_fixtures(tmp_path)
    packet_path = tmp_path / "docs/assets/devpost-submission-packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["b2_usage"] = "B2 proof is pending."
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    report = sponsor_fit_audit.build_report(tmp_path)

    signals = {item["id"]: item["ok"] for item in report["signals"]}
    assert signals["b2_usage_specific"] is False


def test_sponsor_fit_audit_writes_reports(tmp_path):
    write_fixtures(tmp_path)
    report = sponsor_fit_audit.build_report(tmp_path)
    json_path = tmp_path / "out" / "sponsor.json"
    markdown_path = tmp_path / "out" / "sponsor.md"

    sponsor_fit_audit.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.sponsor_fit_audit.v1"
    assert "# ProofFrame Sponsor Fit Audit" in markdown
