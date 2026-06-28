import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "judge_crosswalk.py"
SPEC = importlib.util.spec_from_file_location("judge_crosswalk", SCRIPT_PATH)
judge_crosswalk = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(judge_crosswalk)


def write_file(root: Path, relative_path: str, content: str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_file(root, relative_path, json.dumps(payload))


def write_crosswalk_fixtures(root: Path) -> None:
    for relative_path in judge_crosswalk.REQUIRED_EVIDENCE_FILES:
        write_file(root, relative_path, "ProofFrame evidence fixture\n")
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
        "docs/assets/devpost-event-snapshot.json",
        {
            "schema": "proofframe.devpost_event_snapshot.v1",
            "event": {
                "name": "Backblaze Generative Media Hackathon",
                "deadline_utc": "2026-08-03T21:00:00Z",
                "deadline_beijing": "2026-08-04 05:00 Asia/Shanghai",
                "devpost_url": "https://backblaze-generative-media.devpost.com/",
                "rules_url": "https://backblaze-generative-media.devpost.com/rules",
            },
            "rules": {
                "requirements": {
                    "working_app_url": True,
                    "github_repo_url": True,
                    "demo_video": True,
                    "video_under_three_minutes": True,
                    "public_video_host": True,
                    "b2_usage": True,
                    "genblaze_usage": True,
                },
                "judging_criteria": [
                    {"name": "Real-world Utility", "present": True},
                    {"name": "Production Readiness", "present": True},
                    {"name": "B2 Storage + Data Orchestration", "present": True},
                    {"name": "Use of Genblaze", "present": True},
                ],
            },
            "validation": {"ok": True, "submission_open": True},
        },
    )
    write_json(
        root,
        "docs/assets/judge-brief.json",
        {
            "schema": "proofframe.judge_brief.v1",
            "status": {"safe_to_submit": False},
        },
    )
    write_json(
        root,
        "docs/assets/sponsor-fit-audit.json",
        {
            "schema": "proofframe.sponsor_fit_audit.v1",
            "ok": True,
            "mode": "sponsor_fit_ready",
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {
            "schema": "proofframe.award_readiness.v1",
            "score": 97,
            "max_score": 115,
        },
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "mode": "pre_live_control",
            "safe_to_submit": False,
            "blocking_items": [
                {
                    "id": "b2_live_proof",
                    "label": "Backblaze B2 live proof captured",
                    "detail": "T020 is doing.",
                    "evidence": "tasks.json",
                }
            ],
        },
    )


def test_judge_crosswalk_maps_criteria_to_safe_claims(tmp_path):
    write_crosswalk_fixtures(tmp_path)

    report = judge_crosswalk.build_crosswalk(tmp_path)

    assert report["schema"] == judge_crosswalk.SCHEMA
    assert report["ok"] is True
    assert report["mode"] == "pre_live_crosswalk_ready"
    assert report["safe_to_submit"] is False
    rows = {row["id"]: row for row in report["rows"]}
    assert rows["b2_storage_data_orchestration"]["readiness"] == "code_ready_live_proof_pending"
    assert rows["use_of_genblaze"]["readiness"] == "adapter_ready_live_proof_pending"
    assert "completed live B2 proof is not claimed" in rows["b2_storage_data_orchestration"]["safe_claim"]
    assert "completed live Genblaze proof is not claimed" in rows["use_of_genblaze"]["safe_claim"]
    assert all(source["ok"] for source in report["source_reports"])
    assert report["missing_evidence_files"] == []


def test_judge_crosswalk_blocks_missing_source_schema(tmp_path):
    write_crosswalk_fixtures(tmp_path)
    path = tmp_path / "docs/assets/sponsor-fit-audit.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema"] = "wrong.schema"
    path.write_text(json.dumps(payload), encoding="utf-8")

    report = judge_crosswalk.build_crosswalk(tmp_path)

    assert report["ok"] is False
    assert report["mode"] == "needs_crosswalk_sources"
    sources = {source["path"]: source for source in report["source_reports"]}
    assert sources["docs/assets/sponsor-fit-audit.json"]["ok"] is False


def test_judge_crosswalk_writes_reports(tmp_path):
    write_crosswalk_fixtures(tmp_path)
    report = judge_crosswalk.build_crosswalk(tmp_path)
    json_path = tmp_path / "out" / "judge-crosswalk.json"
    markdown_path = tmp_path / "out" / "judge-crosswalk.md"

    judge_crosswalk.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.judge_crosswalk.v1"
    assert "# ProofFrame Judge Crosswalk" in markdown
    assert "B2 Storage + Data Orchestration" in markdown
    assert "Do not claim completed B2 live storage" in markdown
