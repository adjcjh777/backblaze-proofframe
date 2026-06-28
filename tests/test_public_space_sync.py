import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "public_space_sync.py"
SPEC = importlib.util.spec_from_file_location("public_space_sync", SCRIPT_PATH)
public_space_sync = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_space_sync)


EXPECTED_SHA = "abc123"


def bundle_artifact(artifact_id: str) -> dict:
    return {
        "id": artifact_id,
        "path": f"docs/assets/{artifact_id}.json",
        "label": artifact_id,
        "present": True,
        "bytes": 128,
        "sha256": "a" * 64,
    }


def valid_submission_bundle() -> dict:
    return {
        "schema": "proofframe.submission_bundle.v1",
        "safe_to_share": True,
        "safe_to_submit": False,
        "devpost_packet": {
            "present": True,
            "mode": "pre_live_safe",
            "claim_warning": "Safe for public mock demo only. Do not submit as final sponsor proof.",
        },
        "submission_gate": {
            "ok": False,
            "mode": "pre_live_safe",
            "packet_gate": {"status": "pre_live_packet_pending"},
            "evidence_gate": {"status": "missing"},
            "report_gate": {
                "status": "incomplete",
                "reports": [
                    {"id": "secret_scan", "ok": True, "status": "verified"},
                    {"id": "submission_audit", "ok": False, "status": "incomplete"},
                ],
            },
            "next_actions": [
                "Run a live Backblaze B2 asset and manifest proof.",
                "Run a live Genblaze generation proof and capture provider metadata.",
            ],
        },
        "artifacts": [
            bundle_artifact(artifact_id)
            for artifact_id in sorted(public_space_sync.REQUIRED_BUNDLE_ARTIFACT_IDS)
        ],
        "missing_artifacts": [],
    }


def fake_fetcher(url: str, timeout: int) -> dict:
    assert timeout == public_space_sync.TIMEOUT_SECONDS
    if url.endswith("/api/spaces/ADJCJH/backblaze-proofframe"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "id": "ADJCJH/backblaze-proofframe",
                    "sdk": "docker",
                    "private": False,
                    "disabled": False,
                    "sha": EXPECTED_SHA,
                    "lastModified": "2026-06-27T19:05:08.000Z",
                }
            ),
            "error": None,
        }
    if url.endswith("/runtime"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "stage": "RUNNING",
                    "sha": EXPECTED_SHA,
                    "domains": [{"domain": "example.hf.space", "stage": "READY"}],
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/agent-handoff-report.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.agent_handoff.v1",
                    "ok": True,
                    "mode": "handoff_ready",
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/final-launch-plan.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.final_launch_plan.v1",
                    "ok": False,
                    "mode": "ready_for_credential_entry",
                    "current_phase": "credential_entry",
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/judge-brief.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.judge_brief.v1",
                    "status": {"safe_to_submit": False},
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/judge-crosswalk.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.judge_crosswalk.v1",
                    "ok": True,
                    "mode": "pre_live_crosswalk_ready",
                    "safe_to_submit": False,
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/recording-assets.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.recording_assets.v1",
                    "mode": "public_mock_verified",
                    "mock_recording_ready": True,
                    "final_video_ready": False,
                    "shot_plan": [
                        {"id": "judge_slate"},
                        {"id": "sponsor_model"},
                        {"id": "creative_brief"},
                    ],
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/demo-video-draft.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.demo_video_draft.v1",
                    "mode": "mock_video_draft_ready",
                    "ok": True,
                    "safe_to_submit": False,
                    "final_video_ready": False,
                    "video_path": "docs/assets/proofframe-demo-draft.mp4",
                    "video_probe": {"bytes": 761356, "duration_seconds": 65.97},
                }
            ),
            "bytes": 300,
            "content_type": "application/json",
            "error": None,
        }
    if url.endswith("/docs/assets/proofframe-demo-draft.mp4"):
        return {
            "ok": True,
            "status": 200,
            "body": "mp4",
            "bytes": 761356,
            "content_type": "video/mp4",
            "error": None,
        }
    if url.endswith("/docs/assets/devpost-form-kit.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.devpost_form_kit.v1",
                    "mode": "pre_live_form_ready",
                    "mock_form_ready": True,
                    "final_form_ready": False,
                    "fields": [{"id": f"field_{index}"} for index in range(10)],
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/devpost-submission-checklist.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.devpost_submission_checklist.v1",
                    "mode": "pre_submit_blocked",
                    "safe_to_submit": False,
                    "preflight": [
                        {"id": "final_form_ready", "ok": False},
                        {"id": "packet_post_live_verified", "ok": False},
                        {"id": "prerequisite_tasks_done", "ok": False},
                    ],
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "schema": "proofframe.post_credential_live_proof.v1",
                    "ok": True,
                    "mode": "plan_only",
                    "execute": False,
                    "update_tasks": False,
                    "commands": [
                        {"id": "credential_handoff"},
                        {"id": "b2_live_proof"},
                        {"id": "validate_b2_evidence"},
                        {"id": "final_live_proof"},
                        {"id": "validate_final_evidence"},
                    ],
                    "secret_policy": (
                        "This report stores command strings, statuses, and artifact paths only. "
                        "It never stores Backblaze keys, Genblaze/GMI keys, Devpost cookies, "
                        "provider responses, or signed URLs."
                    ),
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/submission-bundle-manifest.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_submission_bundle()),
            "error": None,
        }
    if url.endswith("/?judge=1"):
        return {
            "ok": True,
            "status": 200,
            "body": (
                "Judge recording slate Sponsor Evidence Model shouldAutoLoadJudgeDemo "
                "30-Second Judge Brief Criteria crosswalk Recording Runbook Devpost Kit Submit Checklist Final reports pending"
            ),
            "error": None,
        }
    if url.endswith("/api/health"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "ready": True,
                    "storage_backend": "local",
                    "generation_backend": "mock",
                    "b2_configured": False,
                    "genblaze_configured": False,
                }
            ),
            "error": None,
        }
    if url.endswith("/api/submission/gate"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(
                {
                    "mode": "pre_live_safe",
                    "tasks_path": "tasks.json",
                    "summary": {"done": 1, "required": 6},
                    "evidence_gate": {"path": "docs/assets/final-live-proof-evidence.json"},
                    "packet_gate": {"path": "docs/assets/devpost-submission-packet.json"},
                    "report_gate": {"status": "incomplete"},
                }
            ),
            "error": None,
        }
    raise AssertionError(f"Unexpected URL: {url}")


def test_public_space_sync_report_passes_when_space_is_current():
    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=fake_fetcher)

    assert report["schema"] == "proofframe.public_space_sync.v1"
    assert report["ok"] is True
    assert report["mode"] == "public_space_synced"
    assert report["observed"]["runtime_sha"] == EXPECTED_SHA
    assert report["observed"]["handoff_mode"] == "handoff_ready"
    assert report["observed"]["launch_plan_mode"] == "ready_for_credential_entry"
    assert report["observed"]["launch_plan_phase"] == "credential_entry"
    assert report["observed"]["judge_brief_schema"] == "proofframe.judge_brief.v1"
    assert report["observed"]["judge_brief_safe_to_submit"] is False
    assert report["observed"]["judge_crosswalk_schema"] == "proofframe.judge_crosswalk.v1"
    assert report["observed"]["judge_crosswalk_mode"] == "pre_live_crosswalk_ready"
    assert report["observed"]["judge_crosswalk_safe_to_submit"] is False
    assert report["observed"]["post_credential_plan_mode"] == "plan_only"
    assert report["observed"]["post_credential_plan_validators"] == {
        "validate_b2_evidence": True,
        "validate_final_evidence": True,
    }
    assert report["observed"]["post_credential_plan_required_sequence"] is True
    assert report["observed"]["post_credential_plan_secret_policy_safe"] is True
    assert report["observed"]["submission_bundle"]["safe_to_share"] is True
    assert report["observed"]["submission_bundle"]["safe_to_submit"] is False
    assert report["observed"]["submission_bundle"]["required_artifacts_present"] is True
    assert all(item["ok"] for item in report["checks"])


def test_public_space_sync_fails_on_sha_mismatch():
    report = public_space_sync.build_report(expected_sha="different-sha", fetcher=fake_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert report["mode"] == "public_space_mismatch"
    assert "space_metadata" in failed
    assert "runtime_ready" in failed


def test_public_space_sync_fails_on_missing_judge_marker():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/?judge=1"):
            result = {**result, "body": "Judge recording slate"}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "judge_html_markers" in failed


def test_public_space_sync_fails_on_missing_launch_plan():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/final-launch-plan.json"):
            result = {**result, "body": json.dumps({"schema": "wrong"})}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_launch_plan" in failed


def test_public_space_sync_fails_on_unsafe_judge_brief():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-brief.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.judge_brief.v1",
                        "status": {"safe_to_submit": True},
                        "not_yet_claimed": [],
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_brief" in failed


def test_public_space_sync_fails_on_unsafe_judge_crosswalk():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-crosswalk.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.judge_crosswalk.v1",
                        "ok": True,
                        "mode": "final_crosswalk_ready",
                        "safe_to_submit": True,
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_crosswalk" in failed


def test_public_space_sync_fails_on_bad_submit_checklist_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/devpost-submission-checklist.json"):
            result = {**result, "body": json.dumps({"schema": "wrong"})}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_submit_checklist" in failed
    assert (
        "Regenerate and upload docs/assets/devpost-submission-checklist.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_missing_post_credential_validators():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": [{"id": "b2_live_proof"}, {"id": "final_live_proof"}],
                        "secret_policy": "No secrets are stored.",
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_post_credential_plan" in failed
    assert (
        "Regenerate and upload docs/assets/post-credential-live-proof-plan.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_unsafe_post_credential_secret_policy():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": [
                            {"id": "credential_handoff"},
                            {"id": "b2_live_proof"},
                            {"id": "validate_b2_evidence"},
                            {"id": "final_live_proof"},
                            {"id": "validate_final_evidence"},
                        ],
                        "secret_policy": "Store secrets and signed URLs in the public report.",
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_post_credential_plan" in failed
    assert report["observed"]["post_credential_plan_secret_policy_safe"] is False


def test_public_space_sync_fails_on_malformed_post_credential_commands():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": ["validate_b2_evidence", "validate_final_evidence"],
                        "secret_policy": (
                            "This report never stores Backblaze keys, Genblaze/GMI keys, "
                            "Devpost cookies, provider responses, or signed URLs."
                        ),
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_post_credential_plan" in failed
    assert report["observed"]["post_credential_plan_required_sequence"] is False


def test_public_space_sync_fails_when_post_credential_plan_only_has_validators():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": [
                            {"id": "validate_b2_evidence"},
                            {"id": "validate_final_evidence"},
                        ],
                        "secret_policy": (
                            "This report never stores Backblaze keys, Genblaze/GMI keys, "
                            "Devpost cookies, provider responses, or signed URLs."
                        ),
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_post_credential_plan" in failed
    assert report["observed"]["post_credential_plan_validators"] == {
        "validate_b2_evidence": True,
        "validate_final_evidence": True,
    }
    assert report["observed"]["post_credential_plan_required_sequence"] is False


def test_public_space_sync_fails_when_bundle_claims_submit_ready():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/submission-bundle-manifest.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.submission_bundle.v1",
                        "safe_to_share": True,
                        "safe_to_submit": True,
                        "submission_gate": {"ok": True, "mode": "final_ready"},
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_submission_bundle" in failed
    assert (
        "Regenerate and upload docs/assets/submission-bundle-manifest.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_truncated_submission_bundle():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/submission-bundle-manifest.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.submission_bundle.v1",
                        "safe_to_share": True,
                        "safe_to_submit": False,
                        "submission_gate": {"ok": False, "mode": "pre_live_safe"},
                        "missing_artifacts": [],
                        "artifacts": [],
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_submission_bundle" in failed
    assert report["observed"]["submission_bundle"]["required_artifacts_present"] is False


def test_public_space_sync_fails_on_missing_demo_video_mp4_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/proofframe-demo-draft.mp4"):
            result = {
                **result,
                "ok": False,
                "status": 404,
                "bytes": 0,
                "content_type": "text/plain",
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "public_demo_video_draft_mp4" in failed
    assert (
        "Regenerate and upload docs/assets/proofframe-demo-draft.mp4 to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_writes_reports(tmp_path):
    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=fake_fetcher)
    json_path = tmp_path / "public-space.json"
    markdown_path = tmp_path / "public-space.md"

    public_space_sync.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.public_space_sync.v1"
    assert "# ProofFrame Public Space Sync Report" in markdown
    assert "public_space_synced" in markdown
