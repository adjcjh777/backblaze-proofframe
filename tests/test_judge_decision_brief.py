import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "judge_decision_brief.py"
SPEC = importlib.util.spec_from_file_location("judge_decision_brief", SCRIPT_PATH)
judge_decision_brief = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(judge_decision_brief)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_tasks(root: Path, *, final_done: bool = False) -> None:
    write_json(
        root,
        "tasks.json",
        {
            "tasks": [
                {"id": "T020", "status": "done" if final_done else "doing"},
                {"id": "T021", "status": "done" if final_done else "doing"},
                {"id": "T040", "status": "done"},
                {"id": "T041", "status": "done" if final_done else "todo"},
                {"id": "T041A", "status": "done" if final_done else "todo"},
                {"id": "T042", "status": "done" if final_done else "todo"},
            ]
        },
    )


def write_decision_fixtures(root: Path, *, final_ready: bool = False) -> None:
    write_tasks(root, final_done=final_ready)
    write_json(
        root,
        "docs/assets/judge-brief.json",
        {
            "schema": "proofframe.judge_brief.v1",
            "status": {"safe_to_submit": final_ready},
            "links": {
                "public_demo": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "repository": "https://github.com/adjcjh777/backblaze-proofframe",
            },
        },
    )
    write_json(
        root,
        "docs/assets/judge-crosswalk.json",
        {
            "schema": "proofframe.judge_crosswalk.v1",
            "mode": "final_crosswalk_ready" if final_ready else "pre_live_crosswalk_ready",
            "ok": True,
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/judge-evidence-index.json",
        {
            "schema": "proofframe.judge_evidence_index.v1",
            "mode": "final_evidence_index_ready" if final_ready else "pre_live_evidence_index_ready",
            "ok": True,
            "safe_to_share": True,
            "safe_to_submit": final_ready,
            "links": [
                {"id": "public_space_sync", "raw_url": "https://example.test/public-space-sync.md"},
                {"id": "judge_crosswalk", "raw_url": "https://example.test/judge-crosswalk.md"},
                {"id": "award_readiness", "raw_url": "https://example.test/award-readiness.md"},
                {"id": "final_submission_control", "raw_url": "https://example.test/final-control.md"},
                {"id": "final_video_publish_kit", "raw_url": "https://example.test/video-kit.md"},
            ],
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {
            "schema": "proofframe.award_readiness.v1",
            "mode": "final_award_ready" if final_ready else "pre_live_competitive",
            "score": 115 if final_ready else 97,
            "max_score": 115,
            "readiness_interpretation": {
                "final_closure_score": 10 if final_ready else 0,
                "final_closure_max_score": 10,
            },
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "final_submit_ready" if final_ready else "pre_live_control",
            "ok": True,
            "control_health_ok": True,
            "safe_to_submit": final_ready,
            "blocking_items": [] if final_ready else [{"id": "b2_live_proof"}, {"id": "genblaze_live_proof"}],
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {
            "schema": "proofframe.public_space_sync.v1",
            "mode": "public_space_synced",
            "ok": True,
            "observed": {"runtime_sha": "a" * 40},
        },
    )
    write_json(
        root,
        "docs/assets/devpost-submission-preview.json",
        {
            "schema": "proofframe.devpost_submission_preview.v1",
            "mode": "final_preview_ready" if final_ready else "pre_live_preview_ready",
            "safe_to_share": True,
            "safe_to_submit": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/final-video-publish-kit.json",
        {
            "schema": "proofframe.final_video_publish_kit.v1",
            "mode": "public_video_ready" if final_ready else "ready_for_final_upload",
            "ok": True,
            "safe_to_share": True,
            "safe_to_submit": final_ready,
            "final_video_ready": final_ready,
        },
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {
            "schema": "proofframe.secret_scan.v1",
            "mode": "clear",
            "ok": True,
        },
    )
    write_json(
        root,
        "docs/assets/devpost-event-snapshot.json",
        {
            "schema": "proofframe.devpost_event_snapshot.v1",
            "mode": "live_official_snapshot",
            "validation": {"ok": True, "submission_open": True},
            "event": {"participant_count_observed": 372},
        },
    )


def test_judge_decision_brief_is_public_safe_pre_live(tmp_path):
    write_decision_fixtures(tmp_path)

    brief = judge_decision_brief.build_decision_brief(tmp_path)

    assert brief["schema"] == judge_decision_brief.SCHEMA
    assert brief["ok"] is True
    assert brief["mode"] == "pre_live_decision_ready"
    assert brief["safe_to_share"] is True
    assert brief["safe_to_submit"] is False
    assert "b2_live_proof" in brief["final_blockers"]
    assert len(brief["decision_checks"]) >= 6
    assert all(item["ok"] for item in brief["decision_checks"])
    assert brief["links"]["evidence_index"].endswith("/docs/assets/judge-evidence-index.md")
    assert "does not claim completed Backblaze B2" in brief["claim_boundary"]


def test_judge_decision_brief_fails_closed_on_bad_source_schema(tmp_path):
    write_decision_fixtures(tmp_path)
    write_json(tmp_path, "docs/assets/public-space-sync-report.json", {"schema": "wrong", "ok": True})

    brief = judge_decision_brief.build_decision_brief(tmp_path)

    assert brief["ok"] is False
    assert brief["safe_to_share"] is False
    assert brief["source_reports"]["public_space_sync"]["schema_ok"] is False


def test_judge_decision_brief_uses_final_mode_only_when_control_is_final(tmp_path):
    write_decision_fixtures(tmp_path, final_ready=True)

    brief = judge_decision_brief.build_decision_brief(tmp_path)

    assert brief["ok"] is True
    assert brief["mode"] == "final_decision_ready"
    assert brief["safe_to_submit"] is True
    assert brief["final_blockers"] == []
    assert brief["current_scores"]["final_closure_score"] == 10


def test_judge_decision_brief_writes_json_and_markdown(tmp_path):
    write_decision_fixtures(tmp_path)
    brief = judge_decision_brief.build_decision_brief(tmp_path)
    json_path = tmp_path / "out" / "brief.json"
    markdown_path = tmp_path / "out" / "brief.md"

    judge_decision_brief.write_outputs(brief, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.judge_decision_brief.v1"
    assert "# ProofFrame Judge Decision Brief" in markdown
    assert "Top Reasons To Score High" in markdown
    assert "Safe to submit: `false`" in markdown
