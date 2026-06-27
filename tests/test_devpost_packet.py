import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_packet.py"
SPEC = importlib.util.spec_from_file_location("devpost_packet", SCRIPT_PATH)
devpost_packet = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_packet)


def test_default_packet_uses_pre_live_safe_claims():
    packet = devpost_packet.build_packet()

    assert packet["mode"] == "pre_live_safe"
    assert "local demo" in packet["short_description"]
    assert "live B2 proof is a final submission gate" in packet["b2_usage"]
    assert "live Genblaze proof is a final submission gate" in packet["genblaze_usage"]
    assert packet["repository_url"] == "https://github.com/adjcjh777/backblaze-proofframe"
    assert packet["demo_url"].endswith("/?judge=1")
    assert {"task": "T040", "label": "Devpost registration complete", "status": "done", "required_for_final": True} in packet[
        "submission_checklist"
    ]


def test_live_packet_uses_verified_claim_copy():
    packet = devpost_packet.build_packet(live=True)

    assert packet["mode"] == "post_live_verified"
    assert "Backblaze B2-backed evidence packets" in packet["short_description"]
    assert "stores generated media" in packet["b2_usage"]
    assert "generates media through Genblaze" in packet["genblaze_usage"]


def test_write_packet_creates_json_and_markdown(tmp_path):
    json_path = tmp_path / "packet.json"
    markdown_path = tmp_path / "packet.md"
    packet = devpost_packet.build_packet()

    devpost_packet.write_packet(packet, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["project_name"] == "ProofFrame"
    assert "# Devpost Submission Packet" in markdown
    assert "Mode: `pre_live_safe`" in markdown
    assert "## Backblaze B2 Usage" in markdown
    assert "## Submission Checklist" in markdown
    assert "T040 [done] Devpost registration complete" in markdown


def test_packet_can_read_task_statuses_from_custom_task_file(tmp_path):
    tasks_path = tmp_path / "tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {"id": "T020", "status": "done"},
                    {"id": "T021", "status": "doing"},
                    {"id": "T040", "status": "done"},
                    {"id": "T041", "status": "todo"},
                    {"id": "T041A", "status": "todo"},
                    {"id": "T042", "status": "todo"},
                ]
            }
        ),
        encoding="utf-8",
    )

    packet = devpost_packet.build_packet(tasks_path=tasks_path)

    statuses = {item["task"]: item["status"] for item in packet["submission_checklist"]}
    assert statuses == {
        "T020": "done",
        "T021": "doing",
        "T040": "done",
        "T041": "todo",
        "T041A": "todo",
        "T042": "todo",
    }
