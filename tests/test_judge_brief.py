import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "judge_brief.py"
SPEC = importlib.util.spec_from_file_location("judge_brief", SCRIPT_PATH)
judge_brief = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(judge_brief)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_brief_fixtures(root: Path) -> None:
    write_json(
        root,
        "tasks.json",
        {
            "tasks": [
                {"id": "T020", "status": "doing"},
                {"id": "T021", "status": "doing"},
                {"id": "T040", "status": "done"},
                {"id": "T041", "status": "todo"},
                {"id": "T041A", "status": "todo"},
                {"id": "T042", "status": "todo"},
            ]
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-packet.json",
        {
            "project_name": "ProofFrame",
            "tagline": "A provenance-first vault for generated media.",
            "one_liner": "ProofFrame turns generated media into evidence packets.",
            "mode": "pre_live_safe",
            "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
            "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
            "video_url": "TBD after final B2 and Genblaze proof.",
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {
            "mode": "pre_live_competitive",
            "score": 97,
            "max_score": 115,
            "readiness_interpretation": {
                "final_closure_score": 0,
                "final_closure_max_score": 10,
            },
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {"safe_to_submit": False},
    )
    write_json(
        root,
        "docs/assets/final-launch-plan.json",
        {
            "mode": "ready_for_credential_entry",
            "current_phase": "credential_entry",
            "next_command": "python scripts/final_env_wizard.py --output .env.final.local --force",
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {
            "mode": "public_space_synced",
            "observed": {"runtime_sha": "abc123"},
        },
    )
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {"validation": {"submission_open": True}},
    )


def test_judge_brief_summarizes_pre_live_boundary(tmp_path):
    write_brief_fixtures(tmp_path)

    brief = judge_brief.build_brief(tmp_path)

    assert brief["schema"] == judge_brief.SCHEMA
    assert brief["status"]["safe_to_submit"] is False
    assert brief["status"]["current_phase"] == "credential_entry"
    assert brief["status"]["award_score"] == 97
    assert brief["status"]["award_max_score"] == 115
    assert brief["status"]["final_closure_score"] == 0
    assert brief["status"]["final_closure_max_score"] == 10
    assert "Completed Backblaze B2 live storage proof." in brief["not_yet_claimed"]
    assert "Completed Genblaze live generation proof." in brief["not_yet_claimed"]
    assert all("completed backblaze b2" not in item.lower() for item in brief["safe_claims"])
    assert all("completed genblaze" not in item.lower() for item in brief["safe_claims"])
    assert any("integration code paths are implemented and gated" in item for item in brief["why_it_can_win"])


def test_judge_brief_writes_json_and_markdown(tmp_path):
    write_brief_fixtures(tmp_path)
    brief = judge_brief.build_brief(tmp_path)
    json_path = tmp_path / "out" / "judge-brief.json"
    markdown_path = tmp_path / "out" / "judge-brief.md"

    judge_brief.write_outputs(brief, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.judge_brief.v1"
    assert "# ProofFrame Judge Brief" in markdown
    assert "30-Second Opening" in markdown
    assert "Not Yet Claimed" in markdown
    assert "Final closure: `0/10`" in markdown
