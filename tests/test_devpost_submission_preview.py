import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_submission_preview.py"
SPEC = importlib.util.spec_from_file_location("devpost_submission_preview", SCRIPT_PATH)
devpost_submission_preview = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_submission_preview)


def write_json(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def packet(*, live: bool = False) -> dict:
    return {
        "schema": "proofframe.devpost_packet.v1",
        "mode": "post_live_verified" if live else "pre_live_safe",
        "project_name": "ProofFrame",
        "tagline": "B2-ready provenance desk for GenAI media.",
        "one_liner": "ProofFrame turns generated media into evidence packets.",
        "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
        "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "video_url": "https://youtu.be/final-proof" if live else "TBD after final B2 and Genblaze proof.",
        "short_description": "A review desk for generated media evidence packets.",
        "b2_usage": "B2 live proof is a final submission gate.",
        "genblaze_usage": "Genblaze live proof is a final submission gate.",
        "accomplishments": ["Working product.", "Public mock demo."],
        "whats_next": ["Live B2 proof.", "Live Genblaze proof."],
    }


def form_kit(*, live: bool = False) -> dict:
    return {
        "schema": "proofframe.devpost_form_kit.v1",
        "mode": "final_form_ready" if live else "pre_live_form_ready",
        "mock_form_ready": True,
        "final_form_ready": live,
        "public_video_ready": live,
        "fields": [
            {
                "id": "project_name",
                "label": "Project name",
                "ok_for_mock": True,
                "ok_for_final": True,
            },
            {
                "id": "video_url",
                "label": "Demo video URL",
                "ok_for_mock": True,
                "ok_for_final": live,
            },
        ],
    }


def screenshot_report(*, ok: bool = True) -> dict:
    return {
        "schema": "proofframe.public_demo_screenshot.v1",
        "mode": "public_judge_screenshot_ready" if ok else "public_judge_screenshot_blocked",
        "ok": ok,
        "safe_to_commit": True,
        "screenshot": {
            "path": "docs/assets/proofframe-hf-public-smoke.png",
            "bytes": 741074 if ok else 100,
            "width": 1440,
            "height": 2692,
        },
        "markers": {"visible_ok": ok, "html_ok": ok},
    }


def public_space_sync(*, ok: bool = True) -> dict:
    return {
        "schema": "proofframe.public_space_sync.v1",
        "mode": "public_space_synced" if ok else "public_space_mismatch",
        "ok": ok,
        "observed": {
            "public_demo_screenshot": {
                "ok": ok,
                "visible_ok": ok,
                "html_ok": ok,
            }
        },
    }


def final_control(*, live: bool = False) -> dict:
    return {
        "schema": "proofframe.final_submission_control.v1",
        "mode": "final_ready" if live else "pre_live_control",
        "safe_to_submit": live,
        "blocking_items": []
        if live
        else [
            {
                "id": "b2_live_proof",
                "label": "Backblaze B2 live proof captured",
                "detail": "T020 is doing.",
                "evidence": "tasks.json",
            },
            {
                "id": "genblaze_live_proof",
                "label": "Genblaze live proof captured",
                "detail": "T021 is doing.",
                "evidence": "tasks.json",
            },
        ],
    }


def write_fixtures(root: Path, *, live: bool = False, screenshot_ok: bool = True) -> None:
    write_json(root, "docs/assets/devpost-submission-packet.json", packet(live=live))
    write_json(root, "docs/assets/devpost-form-kit.json", form_kit(live=live))
    write_json(
        root,
        "docs/assets/judge-brief.json",
        {
            "schema": "proofframe.judge_brief.v1",
            "judge_opening_30s": "ProofFrame is a media operations desk.",
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
            "mode": "final_crosswalk_ready" if live else "pre_live_crosswalk_ready",
            "safe_to_submit": live,
            "official_criteria": [{"name": "Production Readiness", "present": True}],
            "rows": [{"id": "production"}],
        },
    )
    write_json(root, "docs/assets/public-demo-screenshot-report.json", screenshot_report(ok=screenshot_ok))
    write_json(root, "docs/assets/public-space-sync-report.json", public_space_sync(ok=screenshot_ok))
    write_json(root, "docs/assets/final-submission-control.json", final_control(live=live))
    write_json(
        root,
        "docs/assets/devpost-submission-checklist.json",
        {
            "schema": "proofframe.devpost_submission_checklist.v1",
            "mode": "ready" if live else "pre_submit_blocked",
            "safe_to_submit": live,
        },
    )
    write_json(
        root,
        "docs/assets/submission-audit-report.json",
        {
            "schema": "proofframe.submission_audit.v1",
            "mode": "final_submit_ready" if live else "pre_submit_audit_blocked",
            "ok": live,
        },
    )
    write_json(
        root,
        "docs/assets/secret-scan-report.json",
        {"schema": "proofframe.secret_scan.v1", "mode": "clear", "ok": True},
    )


def test_devpost_submission_preview_is_shareable_but_not_submittable_before_live_proof(tmp_path):
    write_fixtures(tmp_path)

    preview = devpost_submission_preview.build_preview(tmp_path)

    assert preview["schema"] == "proofframe.devpost_submission_preview.v1"
    assert preview["mode"] == "pre_live_preview_ready"
    assert preview["safe_to_share"] is True
    assert preview["safe_to_submit"] is False
    assert preview["field_rollup"]["mock_ready"] is True
    assert preview["field_rollup"]["final_ready"] is False
    assert {item["id"] for item in preview["submission_readiness"]["final_blockers"]} == {
        "b2_live_proof",
        "genblaze_live_proof",
    }
    assert "Do not claim completed live Backblaze B2 storage" in preview["claim_boundary"][1]


def test_devpost_submission_preview_blocks_when_public_screenshot_is_not_verified(tmp_path):
    write_fixtures(tmp_path, screenshot_ok=False)

    preview = devpost_submission_preview.build_preview(tmp_path)

    assert preview["mode"] == "preview_blocked"
    assert preview["safe_to_share"] is False
    assert "Regenerate the public judge-mode screenshot report." in preview["next_actions"]


def test_devpost_submission_preview_can_be_final_ready_after_live_gates(tmp_path):
    write_fixtures(tmp_path, live=True)

    preview = devpost_submission_preview.build_preview(tmp_path)

    assert preview["mode"] == "final_preview_ready"
    assert preview["safe_to_share"] is True
    assert preview["safe_to_submit"] is True
    assert preview["submission_readiness"]["final_blockers"] == []


def test_devpost_submission_preview_writes_outputs(tmp_path):
    write_fixtures(tmp_path)
    preview = devpost_submission_preview.build_preview(tmp_path)
    json_path = tmp_path / "out" / "preview.json"
    markdown_path = tmp_path / "out" / "preview.md"

    devpost_submission_preview.write_outputs(preview, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.devpost_submission_preview.v1"
    assert "# ProofFrame Devpost Submission Preview" in markdown
    assert "## Final Blockers" in markdown
