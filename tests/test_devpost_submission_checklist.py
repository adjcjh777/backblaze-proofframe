import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_submission_checklist.py"
SPEC = importlib.util.spec_from_file_location("devpost_submission_checklist", SCRIPT_PATH)
devpost_submission_checklist = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_submission_checklist)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def form_fields(*, final: bool = False) -> list[dict]:
    values = {
        "project_name": "ProofFrame",
        "tagline": "B2-ready provenance desk for GenAI media.",
        "one_liner": "ProofFrame turns generated media into approved evidence packets.",
        "short_description": "A review desk for generated media evidence packets.",
        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
        "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "video_url": "https://youtu.be/proofframe-demo" if final else "TBD after final proof.",
        "built_with": "Python, FastAPI, Backblaze B2, Genblaze",
        "tags": "AI, Generative media, Backblaze B2",
        "inspiration": "Generated media needs operational provenance.",
        "what_it_does": "- Create a campaign.\n- Review assets.\n- Export evidence.",
        "how_we_built_it": "FastAPI plus B2 and Genblaze adapters.",
        "backblaze_b2_usage": "B2 stores generated media and manifests.",
        "genblaze_usage": "Genblaze generates media and records model metadata.",
        "challenges": "Avoiding shallow sponsor integration.",
        "accomplishments": "- Working product.\n- Public demo.\n- Fail-closed gates.",
        "what_we_learned": "The useful unit is an evidence packet.",
        "whats_next": "- More providers.\n- Team workflows.",
        "judging_note": "Current packet mode: post_live_verified.",
    }
    return [
        {
            "id": field_id,
            "label": field_id.replace("_", " ").title(),
            "source": f"packet.{field_id}",
            "value": value,
            "chars": len(value),
            "max_chars": 2500,
            "ok_for_mock": True,
            "ok_for_final": final or field_id != "video_url",
        }
        for field_id, value in values.items()
    ]


def write_fixtures(root: Path, *, final: bool = False) -> None:
    statuses = {
        "T020": "done" if final else "doing",
        "T021": "done" if final else "doing",
        "T040": "done",
        "T041": "todo",
        "T041A": "done" if final else "todo",
        "T042": "todo",
    }
    write_json(
        root,
        "tasks.json",
        {"tasks": [{"id": task_id, "status": status} for task_id, status in statuses.items()]},
    )
    write_json(
        root,
        "docs/assets/devpost-form-kit.json",
        {
            "schema": "proofframe.devpost_form_kit.v1",
            "mode": "final_form_ready" if final else "pre_live_form_ready",
            "final_form_ready": final,
            "fields": form_fields(final=final),
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "schema": "proofframe.devpost_packet.v1",
            "mode": "post_live_verified" if final else "pre_live_safe",
            "video_url": "https://youtu.be/proofframe-demo" if final else "TBD after final proof.",
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "ready_to_submit" if final else "pre_live_control",
            "safe_to_submit": final,
        },
    )
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {
            "schema": "proofframe.submission_audit.v1",
            "mode": "pre_submit_audit_ready" if final else "pre_submit_audit_blocked",
            "ok": final,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-receipt.json",
        {
            "schema": "proofframe.devpost_submission_receipt.v1",
            "mode": "pending_submission",
            "ok": False,
        },
    )


def test_devpost_submission_checklist_blocks_pre_live_submit(tmp_path):
    write_fixtures(tmp_path)

    checklist = devpost_submission_checklist.build_checklist(tmp_path)

    assert checklist["mode"] == "pre_submit_blocked"
    assert checklist["ok"] is False
    assert checklist["safe_to_submit"] is False
    assert "video_url" in checklist["field_gate"]["final_pending_fields"]
    blocked = {item["id"] for item in checklist["preflight"] if not item["ok"]}
    assert "packet_post_live_verified" in blocked
    assert "prerequisite_tasks_done" in blocked
    assert "submission_audit_report_present" not in blocked
    assert "final_control_report_present" not in blocked


def test_devpost_submission_checklist_ready_after_final_gates(tmp_path):
    write_fixtures(tmp_path, final=True)

    checklist = devpost_submission_checklist.build_checklist(tmp_path)

    assert checklist["mode"] == "ready_to_submit_devpost"
    assert checklist["ok"] is True
    assert checklist["safe_to_submit"] is True
    assert checklist["field_gate"]["final_pending_fields"] == []
    assert [field["id"] for field in checklist["fields"][:3]] == [
        "project_name",
        "tagline",
        "one_liner",
    ]


def test_devpost_submission_checklist_writes_outputs(tmp_path):
    write_fixtures(tmp_path)
    checklist = devpost_submission_checklist.build_checklist(tmp_path)
    json_path = tmp_path / "out" / "checklist.json"
    markdown_path = tmp_path / "out" / "checklist.md"

    devpost_submission_checklist.write_outputs(checklist, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.devpost_submission_checklist.v1"
    assert "# ProofFrame Devpost Submission Checklist" in markdown
    assert "This checklist contains Devpost copy only" in markdown
