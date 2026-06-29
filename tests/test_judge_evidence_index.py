import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "judge_evidence_index.py"
SPEC = importlib.util.spec_from_file_location("judge_evidence_index", SCRIPT_PATH)
judge_evidence_index = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(judge_evidence_index)


def write_file(root: Path, relative_path: str, content: str = "ready") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    write_file(root, relative_path, json.dumps(payload))


def write_index_fixtures(root: Path) -> None:
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
        "docs/assets/judge-brief.json",
        {
            "schema": "proofframe.judge_brief.v1",
            "project": "ProofFrame",
            "links": {
                "public_demo": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "repository": "https://github.com/adjcjh777/backblaze-proofframe",
            },
        },
    )
    write_json(
        root,
        "docs/assets/judge-crosswalk.json",
        {"schema": "proofframe.judge_crosswalk.v1", "safe_to_submit": False},
    )
    write_json(
        root,
        "docs/assets/final-submission-control.json",
        {
            "schema": "proofframe.final_submission_control.v1",
            "ok": True,
            "control_health_ok": True,
            "safe_to_submit": False,
            "blocking_items": [
                {"id": "b2_live_proof"},
                {"id": "genblaze_live_proof"},
                {"id": "public_video"},
            ],
        },
    )
    write_json(
        root,
        "docs/assets/public-space-sync-report.json",
        {
            "schema": "proofframe.public_space_sync.v1",
            "ok": True,
            "mode": "public_space_synced",
            "observed": {"runtime_sha": "abc123"},
        },
    )
    write_json(
        root,
        "docs/assets/award-readiness-report.json",
        {"schema": "proofframe.award_readiness.v1", "score": 97, "max_score": 115},
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {"schema": "proofframe.secret_scan.v1", "ok": True, "mode": "clear"},
    )
    write_json(
        root,
        "docs/assets/devpost-submission-preview.json",
        {"schema": "proofframe.devpost_submission_preview.v1", "safe_to_share": True},
    )
    for _, _, _, _, path, _ in judge_evidence_index.LINKS:
        if path:
            write_file(root, path)


def test_judge_evidence_index_is_public_safe_and_fail_closed(tmp_path):
    write_index_fixtures(tmp_path)

    index = judge_evidence_index.build_index(tmp_path)

    assert index["schema"] == judge_evidence_index.SCHEMA
    assert index["ok"] is True
    assert index["safe_to_share"] is True
    assert index["safe_to_submit"] is False
    assert index["status"]["control_health_ok"] is True
    assert index["status"]["final_blocker_count"] == 3
    assert {"b2_live_proof", "genblaze_live_proof"} <= set(index["status"]["final_blockers"])
    assert index["task_statuses"]["T020"] == "doing"
    assert {section["id"] for section in index["sections"]} == set(judge_evidence_index.SECTION_LINKS)
    assert all(link["present"] for link in index["links"])
    assert "final_closeout_status" in {link["id"] for link in index["links"]}
    submission_controls = next(section for section in index["sections"] if section["id"] == "submission_controls")
    assert "final_closeout_status" in submission_controls["links"]
    assert all(not str(link.get("path") or "").startswith("/") for link in index["links"])
    assert all("huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main" in link["raw_url"] for link in index["links"] if link.get("path"))
    assert "does not claim completed B2 or Genblaze live proof" in index["claim_boundary"]


def test_judge_evidence_index_writes_json_and_markdown(tmp_path):
    write_index_fixtures(tmp_path)
    index = judge_evidence_index.build_index(tmp_path)
    json_path = tmp_path / "out" / "judge-evidence-index.json"
    markdown_path = tmp_path / "out" / "judge-evidence-index.md"

    judge_evidence_index.write_outputs(index, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.judge_evidence_index.v1"
    assert "# ProofFrame Judge Evidence Index" in markdown
    assert "Safe to submit: `false`" in markdown
    assert "Submission Controls" in markdown
    assert "`b2_live_proof`" in markdown


def test_judge_evidence_index_fails_when_source_health_is_bad(tmp_path):
    write_index_fixtures(tmp_path)
    write_json(
        tmp_path,
        "docs/assets/public-space-sync-report.json",
        {"schema": "proofframe.public_space_sync.v1", "ok": False},
    )

    index = judge_evidence_index.build_index(tmp_path)

    assert index["ok"] is False
    assert index["source_health"]["public_space_sync"] is False
    assert index["safe_to_submit"] is False
