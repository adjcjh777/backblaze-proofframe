import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_form_kit.py"
SPEC = importlib.util.spec_from_file_location("devpost_form_kit", SCRIPT_PATH)
devpost_form_kit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_form_kit)


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def packet(*, live: bool = False, video_url: str | None = None) -> dict[str, object]:
    return {
        "mode": "post_live_verified" if live else "pre_live_safe",
        "claim_warning": "Use only after live proof." if live else "Safe for public mock demo only.",
        "project_name": "ProofFrame",
        "tagline": "A provenance-first vault for generated media.",
        "one_liner": "ProofFrame turns generated media into reviewable evidence packets.",
        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
        "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "video_url": video_url or "TBD after final B2 and Genblaze proof.",
        "short_description": "A review desk for generated media evidence packets.",
        "inspiration": "Generated media needs operational provenance.",
        "what_it_does": ["Create a campaign.", "Review assets.", "Export evidence."],
        "how_we_built_it": "FastAPI, local demo mode, B2 storage adapter, Genblaze adapter.",
        "b2_usage": "B2 live proof is a final submission gate.",
        "genblaze_usage": "Genblaze live proof is a final submission gate.",
        "challenges": "Avoiding shallow sponsor integration.",
        "accomplishments": ["Working product.", "Public mock demo.", "Fail-closed gates."],
        "what_we_learned": "The useful unit is an evidence packet.",
        "whats_next": ["Live B2 proof.", "Live Genblaze proof.", "Final video."],
    }


def write_fixtures(root: Path, *, live: bool = False, video_url: str | None = None) -> None:
    task_ids = ["T020", "T021", "T040", "T041", "T041A", "T042"]
    statuses = {
        task_id: "done" if live and task_id in {"T020", "T021", "T040", "T041A"} else "todo"
        for task_id in task_ids
    }
    statuses["T040"] = "done"
    write_file(
        root,
        "tasks.json",
        json.dumps(
            {
                "tasks": [
                    {"id": task_id, "title": task_id, "status": status}
                    for task_id, status in statuses.items()
                ]
            }
        ),
    )
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(packet(live=live, video_url=video_url)),
    )
    if live:
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
                    "asset_storage_key": "campaigns/cmp/assets/asset.png",
                    "manifest_key": "campaigns/cmp/manifests/manifest.json",
                }
            ),
        )


def test_devpost_form_kit_is_mock_ready_but_not_final(tmp_path):
    write_fixtures(tmp_path)

    kit = devpost_form_kit.build_form_kit(tmp_path)

    assert kit["mock_form_ready"] is True
    assert kit["final_form_ready"] is False
    assert kit["public_video_ready"] is False
    assert "Regenerate the Devpost packet in post-live mode" in kit["next_actions"][0]


def test_devpost_form_kit_flags_overlong_fields(tmp_path):
    write_fixtures(tmp_path)
    packet_path = tmp_path / "docs/assets/devpost-submission-packet.json"
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    data["tagline"] = "x" * 141
    packet_path.write_text(json.dumps(data), encoding="utf-8")

    kit = devpost_form_kit.build_form_kit(tmp_path)
    tagline = next(field for field in kit["fields"] if field["id"] == "tagline")

    assert kit["mock_form_ready"] is False
    assert tagline["too_long"] is True


def test_devpost_form_kit_passes_final_with_live_proof_and_video(tmp_path):
    write_fixtures(tmp_path, live=True, video_url="https://youtu.be/example-proof")

    kit = devpost_form_kit.build_form_kit(tmp_path)

    assert kit["mock_form_ready"] is True
    assert kit["final_form_ready"] is True
    assert kit["mode"] == "final_form_ready"


def test_devpost_form_kit_writes_outputs(tmp_path):
    write_fixtures(tmp_path)
    kit = devpost_form_kit.build_form_kit(tmp_path)
    json_path = tmp_path / "out" / "kit.json"
    markdown_path = tmp_path / "out" / "kit.md"

    devpost_form_kit.write_outputs(kit, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.devpost_form_kit.v1"
    assert "# ProofFrame Devpost Form Kit" in markdown
    assert "## Fields" in markdown
