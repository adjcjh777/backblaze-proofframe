import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "public_space_sync.py"
SPEC = importlib.util.spec_from_file_location("public_space_sync", SCRIPT_PATH)
public_space_sync = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_space_sync)


EXPECTED_SHA = "abc123"


def test_fetch_text_handles_incomplete_read(monkeypatch):
    class BrokenResponse:
        status = 200
        headers = {"content-type": "video/mp4"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            raise public_space_sync.IncompleteRead(b"", 747727)

    monkeypatch.setattr(public_space_sync, "urlopen", lambda request, timeout: BrokenResponse())

    result = public_space_sync.fetch_text("https://example.test/video.mp4", timeout=1)

    assert result["ok"] is False
    assert result["bytes"] == 0
    assert "IncompleteRead" in result["error"]


def test_fetch_text_retries_transient_incomplete_read(monkeypatch):
    calls = []

    class HealthyResponse:
        status = 200
        headers = {"content-type": "application/json"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"ok": true}'

    class BrokenResponse(HealthyResponse):
        def read(self):
            raise public_space_sync.IncompleteRead(b"", 10)

    def flaky_urlopen(request, timeout):
        calls.append(request.full_url)
        return BrokenResponse() if len(calls) == 1 else HealthyResponse()

    monkeypatch.setattr(public_space_sync, "urlopen", flaky_urlopen)

    result = public_space_sync.fetch_text("https://example.test/report.json", timeout=1, retries=2)

    assert result["ok"] is True
    assert result["body"] == '{"ok": true}'
    assert len(calls) == 2


def valid_post_credential_commands() -> list[dict]:
    return [
        {"id": "credential_handoff"},
        {"id": "b2_live_proof"},
        {"id": "validate_b2_evidence"},
        {"id": "final_live_proof"},
        {"id": "validate_final_evidence"},
        {"id": "live_env_handoff_report"},
        {"id": "devpost_form_kit"},
        {"id": "devpost_submission_checklist"},
        {"id": "judge_brief"},
        {"id": "judge_crosswalk"},
        {"id": "demo_storyboard"},
        {"id": "demo_readiness"},
        {"id": "recording_assets"},
        {"id": "award_readiness"},
        {"id": "final_operator_brief"},
        {"id": "final_launch_plan"},
        {"id": "final_rehearsal"},
        {"id": "final_submission_control"},
        {"id": "submission_audit"},
        {"id": "devpost_submission_preview"},
        {"id": "secret_scan"},
        {"id": "submission_bundle"},
    ]


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


def valid_genblaze_contract_report() -> dict:
    return {
        "schema": "proofframe.genblaze_contract_check.v1",
        "ok": True,
        "mode": "sdk_contract_ready",
        "failed_checks": [],
        "secret_policy": (
            "This report reads Python package metadata and callable signatures only. "
            "It does not read environment variables, credential files, provider responses, "
            "Backblaze keys, Genblaze/GMI keys, cookies, or signed URLs."
        ),
    }


def valid_docker_smoke_report() -> dict:
    check_ids = [
        "dockerignore_secret_exclusions",
        "docker_daemon",
        "docker_build",
        "docker_run",
        "docker_health",
        "api_smoke",
        "docker_cleanup",
    ]
    return {
        "schema": "proofframe.docker_smoke.v1",
        "ok": True,
        "mode": "docker_smoke_ready",
        "dockerignore": {
            "missing_required_patterns": [],
            "missing_allow_patterns": [],
        },
        "health": {
            "ok": True,
            "json": {
                "ready": True,
                "storage_backend": "local",
                "generation_backend": "mock",
                "b2_configured": False,
                "genblaze_configured": False,
            }
        },
        "checks": [{"id": check_id, "ok": True} for check_id in check_ids],
    }


def valid_event_snapshot() -> dict:
    return {
        "schema": "proofframe.devpost_event_snapshot.v1",
        "checked_at": "2026-06-28T16:00:00Z",
        "mode": "live_official_snapshot",
        "event": {
            "participant_count_observed": 365,
            "deadline_utc": "2026-08-03T21:00:00Z",
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
        "sources": [
            {"id": "overview", "ok": True, "status": 200},
            {"id": "rules", "ok": True, "status": 200},
        ],
        "validation": {"ok": True, "submission_open": True},
    }


def valid_b2_key_scope_checklist() -> dict:
    return {
        "schema": "proofframe.b2_key_scope_checklist.v1",
        "mode": "scope_ready_key_not_created",
        "ok": True,
        "safe_to_commit": True,
        "requires_user_confirmation_before_key_creation": True,
        "pre_key_creation_confirmation": {
            "status": "required_before_key_creation",
            "required_phrase": (
                "I confirm ProofFrame B2 key scope: standard key, bucket "
                "proofframe-demo-a6b4e49, prefix campaigns/, no all-bucket access, "
                "no delete/admin permissions, and no secrets in chat/docs/git."
            ),
            "safe_to_store": True,
        },
        "expected_key": {
            "bucket_scope": {
                "mode": "single_bucket",
                "bucket_name": "proofframe-demo-a6b4e49",
                "forbidden": "all_buckets",
            },
            "file_name_prefix": {
                "value": "campaigns/",
                "required": True,
            },
            "required_capabilities": [
                {"capability": "writeFiles"},
                {"capability": "listAllBucketNames"},
            ],
            "conditional_capabilities": [
                {"capability": "readFiles", "required_now": "false"},
                {"capability": "listFiles", "required_now": "false"},
            ],
            "forbidden_capabilities": [
                {"capability": "deleteFiles"},
                {"capability": "writeBuckets/deleteBuckets"},
            ],
        },
        "secret_policy": {"forbidden_setup_fields": []},
    }


def valid_public_demo_screenshot() -> dict:
    return {
        "schema": "proofframe.public_demo_screenshot.v1",
        "mode": "public_judge_screenshot_ready",
        "ok": True,
        "safe_to_commit": True,
        "url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
        "screenshot": {
            "present": True,
            "path": "docs/assets/proofframe-hf-public-smoke.png",
            "ok": True,
            "bytes": 717007,
            "width": 1440,
            "height": 2692,
            "luma_mean": 236.6,
            "luma_stddev": 47.11,
        },
        "markers": {
            "visible_ok": True,
            "html_ok": True,
            "visible": {
                "sponsor_evidence_model": {
                    "needle": "Sponsor Evidence Model",
                    "present": True,
                },
                "final_reports_pending": {
                    "needle": "Final reports pending",
                    "present": True,
                },
            },
            "html": {
                "judge_recording_slate": {
                    "needle": "Judge recording slate",
                    "present": True,
                },
                "auto_load_judge_demo": {
                    "needle": "shouldAutoLoadJudgeDemo",
                    "present": True,
                },
            },
        },
    }


def valid_devpost_preview() -> dict:
    return {
        "schema": "proofframe.devpost_submission_preview.v1",
        "mode": "pre_live_preview_ready",
        "ok": True,
        "safe_to_share": True,
        "safe_to_submit": False,
        "submission_readiness": {
            "packet_mode": "pre_live_safe",
            "public_space_mode": "public_space_synced",
            "public_screenshot_mode": "public_judge_screenshot_ready",
            "final_blockers": [
                {"id": "b2_live_proof"},
                {"id": "genblaze_live_proof"},
            ],
        },
        "field_rollup": {
            "mock_ready": True,
            "final_ready": False,
        },
        "evidence_links": {
            "public_demo": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
            "public_screenshot": "docs/assets/proofframe-hf-public-smoke.png",
        },
    }


def valid_public_video_check() -> dict:
    return {
        "schema": "proofframe.public_video_check.v1",
        "mode": "pending_video_url",
        "ok": False,
        "safe_to_submit": False,
        "video_url": "TBD after final B2 and Genblaze proof.",
        "url_analysis": {
            "present": False,
            "official_host": False,
            "official_host_family": None,
            "reason": "missing_or_placeholder",
        },
        "checks": [
            {"id": "video_url_present", "ok": False},
            {
                "id": "video_url_official_public_host",
                "ok": False,
                "detail": "host=None; official_host_family=None; allowed families are YouTube, Vimeo, and Youku.",
            },
            {"id": "video_url_accessible", "ok": False},
        ],
        "next_actions": [
            "Upload the final demo video to YouTube, Vimeo, or Youku before strict final submission.",
        ],
    }


def valid_judge_evidence_index() -> dict:
    return {
        "schema": "proofframe.judge_evidence_index.v1",
        "ok": True,
        "mode": "pre_live_evidence_index_ready",
        "safe_to_share": True,
        "safe_to_submit": False,
        "status": {
            "control_health_ok": True,
            "final_blockers": ["b2_live_proof", "genblaze_live_proof", "public_video"],
        },
        "links": [
            {"id": "public_demo", "present": True},
            {"id": "judge_brief", "present": True},
            {"id": "judge_crosswalk", "present": True},
            {"id": "judge_decision_brief", "present": True},
            {"id": "final_submission_control", "present": True},
            {"id": "final_closeout_status", "present": True},
            {"id": "devpost_preview", "present": True},
            {"id": "submission_checklist", "present": True},
            {"id": "submission_bundle", "present": True},
            {"id": "award_readiness", "present": True},
            {"id": "public_space_sync", "present": True},
            {"id": "recording_assets", "present": True},
        ],
        "sections": [
            {"id": "start_here", "ready": True},
            {"id": "submission_controls", "ready": True},
            {"id": "award_case", "ready": True},
            {"id": "recording", "ready": True},
            {"id": "live_proof_gates", "ready": True},
        ],
        "claim_boundary": (
            "This index is public-safe evidence navigation. It does not claim completed B2 or "
            "Genblaze live proof until final_submission_control.safe_to_submit is true."
        ),
    }


def valid_final_closeout_status() -> dict:
    return {
        "schema": "proofframe.final_closeout_status.v1",
        "ok": True,
        "mode": "waiting_for_credentials",
        "phase": "credential_entry",
        "safe_to_submit": False,
        "closeout_health_ok": True,
        "next_command": "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
        "gates": [
            {"id": "report_inventory", "ok": True},
            {"id": "credential_handoff", "ok": False},
            {"id": "b2_live_proof", "ok": False},
            {"id": "genblaze_live_proof", "ok": False},
            {"id": "public_video", "ok": False},
            {"id": "devpost_receipt", "ok": False},
            {"id": "final_control", "ok": False},
        ],
        "secret_policy": (
            "This closeout report stores only task statuses, report metadata, public URLs, and artifact paths; "
            "it never stores Backblaze keys, Genblaze/GMI keys, Devpost cookies, browser sessions, or signed URLs."
        ),
    }


def valid_final_ready_closeout_status() -> dict:
    closeout = valid_final_closeout_status()
    closeout["mode"] = "final_closeout_ready"
    closeout["phase"] = "submit_receipt_captured"
    closeout["safe_to_submit"] = True
    closeout["next_command"] = "python scripts/submission_bundle.py --strict-final"
    closeout["gates"] = [{**gate, "ok": True} for gate in closeout["gates"]]
    return closeout


def valid_judge_decision_brief() -> dict:
    source_reports = {
        "judge_brief": {"schema_ok": True},
        "judge_crosswalk": {
            "schema_ok": True,
            "ok": True,
            "mode": "pre_live_crosswalk_ready",
            "safe_to_submit": False,
        },
        "judge_evidence_index": {
            "schema_ok": True,
            "ok": True,
            "mode": "pre_live_evidence_index_ready",
            "safe_to_share": True,
            "safe_to_submit": False,
        },
        "award_readiness": {"schema_ok": True},
        "final_control": {
            "schema_ok": True,
            "ok": True,
            "mode": "pre_live_control",
            "safe_to_submit": False,
        },
        "public_space_sync": {
            "schema_ok": True,
            "ok": True,
            "mode": "public_space_synced",
        },
        "devpost_preview": {
            "schema_ok": True,
            "mode": "pre_live_preview_ready",
            "safe_to_share": True,
            "safe_to_submit": False,
        },
        "video_publish_kit": {
            "schema_ok": True,
            "ok": True,
            "mode": "ready_for_final_upload",
            "safe_to_share": True,
            "safe_to_submit": False,
        },
        "secret_scan": {"schema_ok": True, "ok": True, "mode": "clear"},
        "event_snapshot": {"schema_ok": True, "mode": "live_official_snapshot"},
    }
    return {
        "schema": "proofframe.judge_decision_brief.v1",
        "created_at": public_space_sync.utc_now(),
        "ok": True,
        "mode": "pre_live_decision_ready",
        "safe_to_share": True,
        "safe_to_submit": False,
        "public_state": {
            "space_sync_ok": True,
            "space_mode": "public_space_synced",
            "space_sync_checked_at": public_space_sync.utc_now(),
        },
        "decision_checks": [
            {"id": "public_demo_runs", "ok": True},
            {"id": "criteria_are_mapped", "ok": True},
            {"id": "award_case_is_competitive", "ok": True},
            {"id": "claims_are_fail_closed", "ok": True},
            {"id": "video_submission_is_gated", "ok": True},
            {"id": "no_secret_exposure", "ok": True},
        ],
        "source_reports": source_reports,
        "links": {
            "evidence_index": (
                "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/"
                "docs/assets/judge-evidence-index.md"
            )
        },
        "claim_boundary": (
            "This brief is public-safe and decision-oriented. It does not claim completed Backblaze B2 "
            "or Genblaze live proof until final_submission_control.safe_to_submit is true."
        ),
    }


def valid_video_publish_kit() -> dict:
    return {
        "schema": "proofframe.final_video_publish_kit.v1",
        "ok": True,
        "mode": "ready_for_final_upload",
        "safe_to_share": True,
        "safe_to_submit": False,
        "final_video_ready": False,
        "allowed_hosts": ["YouTube", "Vimeo", "Youku"],
        "devpost_field": {
            "field_id": "video_url",
            "value": "TBD after final upload.",
            "ready": False,
        },
        "upload_checklist": [
            {"id": "host_family", "ok": False},
            {"id": "public_visibility", "ok": False},
            {"id": "duration", "ok": True},
            {"id": "devpost_field", "ok": False},
        ],
        "source_reports": {
            "storyboard": {"schema_ok": True},
            "draft_video": {"schema_ok": True},
            "public_video_check": {
                "schema_ok": True,
                "ok": False,
                "safe_to_submit": False,
            },
            "final_control": {
                "schema_ok": True,
                "ok": True,
                "safe_to_submit": False,
            },
            "evidence_index": {"schema_ok": True},
        },
        "claim_boundary": (
            "Use this title and description for final upload only after live B2 and Genblaze proof "
            "are recorded; until then, the public demo remains local/mock and safe_to_submit=false."
        ),
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
    if url.endswith("/docs/assets/devpost-event-snapshot.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_event_snapshot()),
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
                    "mode": "blocked_at_credential_entry",
                    "current_phase": "credential_entry",
                }
            ),
            "error": None,
        }
    if url.endswith("/docs/assets/b2-key-scope-checklist.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_b2_key_scope_checklist()),
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
    if url.endswith("/docs/assets/judge-decision-brief.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_judge_decision_brief()),
            "error": None,
        }
    if url.endswith("/docs/assets/judge-evidence-index.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_judge_evidence_index()),
            "error": None,
        }
    if url.endswith("/docs/assets/final-closeout-status.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_final_closeout_status()),
            "error": None,
        }
    if url.endswith("/api/judge/final-closeout"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_final_closeout_status()),
            "error": None,
        }
    if url.endswith("/docs/assets/final-video-publish-kit.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_video_publish_kit()),
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
    if url.endswith("/docs/assets/public-demo-screenshot-report.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_public_demo_screenshot()),
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
    if url.endswith("/docs/assets/public-video-check.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_public_video_check()),
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
    if url.endswith("/docs/assets/devpost-submission-preview.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_devpost_preview()),
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
                    "commands": valid_post_credential_commands(),
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
    if url.endswith("/docs/assets/genblaze-contract-report.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_genblaze_contract_report()),
            "error": None,
        }
    if url.endswith("/docs/assets/docker-smoke-report.json"):
        return {
            "ok": True,
            "status": 200,
            "body": json.dumps(valid_docker_smoke_report()),
            "error": None,
        }
    if url.endswith("/?judge=1"):
        return {
            "ok": True,
            "status": 200,
            "body": (
                "Judge recording slate Sponsor Evidence Model shouldAutoLoadJudgeDemo "
                "30-Second Judge Brief Criteria crosswalk Decision brief Evidence index Video publish kit "
                "Final closeout Recording Runbook Devpost Kit Submit Checklist Final Closeout Final reports pending"
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
    assert report["observed"]["event_snapshot"]["participant_count_observed"] == 365
    assert report["observed"]["event_snapshot"]["submission_open"] is True
    assert report["observed"]["event_snapshot"]["requirements_ok"] is True
    assert report["observed"]["launch_plan_mode"] == "blocked_at_credential_entry"
    assert report["observed"]["launch_plan_phase"] == "credential_entry"
    assert report["observed"]["genblaze_contract"] == {
        "schema": "proofframe.genblaze_contract_check.v1",
        "mode": "sdk_contract_ready",
        "ok": True,
        "failed_checks": 0,
    }
    assert report["observed"]["docker_smoke"] == {
        "schema": "proofframe.docker_smoke.v1",
        "mode": "docker_smoke_ready",
        "ok": True,
        "storage_backend": "local",
        "generation_backend": "mock",
    }
    assert report["observed"]["b2_key_scope_checklist"]["safe_to_commit"] is True
    assert report["observed"]["b2_key_scope_checklist"]["confirmation_status"] == "required_before_key_creation"
    assert report["observed"]["b2_key_scope_checklist"]["confirmation_phrase_safe"] is True
    assert report["observed"]["b2_key_scope_checklist"]["bucket_name"] == "proofframe-demo-a6b4e49"
    assert report["observed"]["b2_key_scope_checklist"]["prefix"] == "campaigns/"
    assert {"writeFiles", "listAllBucketNames"} <= set(
        report["observed"]["b2_key_scope_checklist"]["required_capabilities"]
    )
    assert report["observed"]["judge_brief_schema"] == "proofframe.judge_brief.v1"
    assert report["observed"]["judge_brief_safe_to_submit"] is False
    assert report["observed"]["judge_crosswalk_schema"] == "proofframe.judge_crosswalk.v1"
    assert report["observed"]["judge_crosswalk_mode"] == "pre_live_crosswalk_ready"
    assert report["observed"]["judge_crosswalk_safe_to_submit"] is False
    decision_observed = report["observed"]["judge_decision_brief"]
    assert decision_observed["schema"] == "proofframe.judge_decision_brief.v1"
    assert decision_observed["mode"] == "pre_live_decision_ready"
    assert decision_observed["safe_to_share"] is True
    assert decision_observed["safe_to_submit"] is False
    assert decision_observed["check_count"] == 6
    assert decision_observed["space_mode"] == "public_space_synced"
    assert decision_observed["space_sync_checked_at"]
    assert decision_observed["fresh"] is True
    assert decision_observed["source_state_ok"] is True
    assert "judge-evidence-index.md" in decision_observed["evidence_index_link"]
    assert report["observed"]["judge_evidence_index"] == {
        "schema": "proofframe.judge_evidence_index.v1",
        "mode": "pre_live_evidence_index_ready",
        "safe_to_share": True,
        "safe_to_submit": False,
        "link_count": 12,
        "section_count": 5,
        "blocker_count": 3,
    }

    assert report["observed"]["final_closeout_status"] == {
        "schema": "proofframe.final_closeout_status.v1",
        "mode": "waiting_for_credentials",
        "closeout_health_ok": True,
        "safe_to_submit": False,
        "gate_count": 7,
    }
    assert report["observed"]["final_closeout_api"] == {
        "schema": "proofframe.final_closeout_status.v1",
        "mode": "waiting_for_credentials",
        "safe_to_submit": False,
        "gate_count": 7,
    }
    assert report["observed"]["video_publish_kit"] == {
        "schema": "proofframe.final_video_publish_kit.v1",
        "mode": "ready_for_final_upload",
        "safe_to_share": True,
        "safe_to_submit": False,
        "final_video_ready": False,
        "upload_check_count": 4,
    }
    assert report["observed"]["public_demo_screenshot"]["ok"] is True
    assert report["observed"]["public_demo_screenshot"]["visible_ok"] is True
    assert report["observed"]["public_demo_screenshot"]["html_ok"] is True
    assert report["observed"]["public_demo_screenshot"]["bytes"] == 717007
    assert report["observed"]["public_demo_screenshot"]["size"] == [1440, 2692]
    assert report["observed"]["public_video_check"] == {
        "mode": "pending_video_url",
        "safe_to_submit": False,
        "official_host_check_ok": False,
    }
    assert report["observed"]["devpost_preview"]["mode"] == "pre_live_preview_ready"
    assert report["observed"]["devpost_preview"]["safe_to_share"] is True
    assert report["observed"]["devpost_preview"]["safe_to_submit"] is False
    assert report["observed"]["devpost_preview"]["field_final_ready"] is False
    assert report["observed"]["devpost_preview"]["blocker_count"] == 2
    assert report["observed"]["post_credential_plan_mode"] == "plan_only"
    assert report["observed"]["post_credential_plan_validators"] == {
        "validate_b2_evidence": True,
        "validate_final_evidence": True,
        "devpost_submission_preview": True,
    }
    assert report["observed"]["post_credential_plan_required_sequence"] is True
    assert report["observed"]["post_credential_plan_report_sequence"] is True
    assert report["observed"]["post_credential_plan_secret_policy_safe"] is True
    assert report["observed"]["submission_bundle"]["safe_to_share"] is True
    assert report["observed"]["submission_bundle"]["safe_to_submit"] is False
    assert report["observed"]["submission_bundle"]["required_artifacts_present"] is True
    assert report["urls"]["raw_genblaze_contract_report"].endswith(
        "/docs/assets/genblaze-contract-report.json"
    )
    assert report["urls"]["raw_docker_smoke_report"].endswith("/docs/assets/docker-smoke-report.json")
    assert all(item["ok"] for item in report["checks"])


def test_public_space_sync_parser_accepts_wait_options():
    parser = public_space_sync.build_parser()

    args = parser.parse_args(["--wait-attempts", "5", "--wait-seconds", "1.5"])

    assert args.wait_attempts == 5
    assert args.wait_seconds == 1.5


def test_public_space_sync_required_bundle_artifacts_include_genblaze_contract():
    assert {
        "genblaze_contract_json",
        "genblaze_contract_script",
    } <= public_space_sync.REQUIRED_BUNDLE_ARTIFACT_IDS


def test_public_space_sync_required_bundle_artifacts_include_docker_smoke():
    assert {
        "dockerignore",
        "docker_smoke_json",
        "docker_smoke_script",
    } <= public_space_sync.REQUIRED_BUNDLE_ARTIFACT_IDS


def test_public_space_sync_required_bundle_artifacts_include_final_closeout_status():
    assert {
        "final_closeout_status_json",
        "final_closeout_status_md",
        "final_closeout_status_script",
    } <= public_space_sync.REQUIRED_BUNDLE_ARTIFACT_IDS


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


def test_public_space_sync_fails_on_broken_genblaze_contract_report():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/genblaze-contract-report.json"):
            contract = valid_genblaze_contract_report()
            contract["ok"] = False
            contract["mode"] = "sdk_contract_blocked"
            contract["failed_checks"] = ["pipeline_step_aspect_ratio"]
            result = {**result, "body": json.dumps(contract)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_genblaze_contract_report" in failed


def test_public_space_sync_fails_on_broken_docker_smoke_report():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/docker-smoke-report.json"):
            docker_report = valid_docker_smoke_report()
            docker_report["ok"] = False
            docker_report["mode"] = "docker_smoke_blocked"
            docker_report["dockerignore"]["missing_required_patterns"] = [".env.final.local"]
            result = {**result, "body": json.dumps(docker_report)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_docker_smoke_report" in failed


def test_public_space_sync_fails_on_truncated_docker_smoke_report():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/docker-smoke-report.json"):
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.docker_smoke.v1",
                        "ok": True,
                        "mode": "docker_smoke_ready",
                        "dockerignore": {
                            "missing_required_patterns": [],
                            "missing_allow_patterns": [],
                        },
                        "health": {
                            "json": {
                                "storage_backend": "local",
                                "generation_backend": "mock",
                            }
                        },
                    }
                ),
            }
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_docker_smoke_report" in failed


def test_public_space_sync_fails_when_docker_cleanup_check_is_missing():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/docker-smoke-report.json"):
            docker_report = valid_docker_smoke_report()
            docker_report["checks"] = [
                check for check in docker_report["checks"] if check["id"] != "docker_cleanup"
            ]
            result = {**result, "body": json.dumps(docker_report)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_docker_smoke_report" in failed


def test_public_space_sync_fails_when_docker_health_is_not_fail_closed():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/docker-smoke-report.json"):
            docker_report = valid_docker_smoke_report()
            docker_report["health"]["json"]["b2_configured"] = True
            result = {**result, "body": json.dumps(docker_report)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_docker_smoke_report" in failed


def test_public_space_sync_fails_when_bundle_omits_genblaze_contract_artifacts():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/submission-bundle-manifest.json"):
            bundle = valid_submission_bundle()
            bundle["artifacts"] = [
                artifact
                for artifact in bundle["artifacts"]
                if artifact["id"] not in {"genblaze_contract_json", "genblaze_contract_script"}
            ]
            result = {**result, "body": json.dumps(bundle)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_submission_bundle" in failed


def test_public_space_sync_fails_when_bundle_omits_docker_smoke_artifacts():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/submission-bundle-manifest.json"):
            bundle = valid_submission_bundle()
            bundle["artifacts"] = [
                artifact
                for artifact in bundle["artifacts"]
                if artifact["id"] not in {"dockerignore", "docker_smoke_json", "docker_smoke_script"}
            ]
            result = {**result, "body": json.dumps(bundle)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_submission_bundle" in failed


def test_public_space_sync_fails_on_unsafe_b2_key_scope_checklist():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/b2-key-scope-checklist.json"):
            checklist = valid_b2_key_scope_checklist()
            checklist["safe_to_commit"] = False
            checklist["pre_key_creation_confirmation"]["status"] = "missing"
            checklist["pre_key_creation_confirmation"]["required_phrase"] = "create the key"
            checklist["secret_policy"]["forbidden_setup_fields"] = ["$.application_key"]
            checklist["expected_key"]["bucket_scope"] = {
                "mode": "all_buckets",
                "bucket_name": None,
                "forbidden": None,
            }
            checklist["expected_key"]["file_name_prefix"]["value"] = ""
            checklist["expected_key"]["forbidden_capabilities"] = []
            result = {**result, "body": json.dumps(checklist)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_b2_key_scope_checklist" in failed
    assert (
        "Regenerate and upload docs/assets/b2-key-scope-checklist.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_unsafe_public_demo_screenshot_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/public-demo-screenshot-report.json"):
            screenshot = valid_public_demo_screenshot()
            screenshot["safe_to_commit"] = False
            screenshot["markers"]["html_ok"] = False
            screenshot["markers"]["html"]["judge_recording_slate"]["present"] = False
            screenshot["screenshot"]["bytes"] = 100
            result = {**result, "body": json.dumps(screenshot)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_public_demo_screenshot" in failed
    assert report["observed"]["public_demo_screenshot"]["html_ok"] is False
    assert (
        "Regenerate and upload docs/assets/public-demo-screenshot-report.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_missing_public_video_host_gate_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/public-video-check.json"):
            public_video_check = valid_public_video_check()
            public_video_check["checks"] = [
                item for item in public_video_check["checks"] if item["id"] != "video_url_official_public_host"
            ]
            public_video_check["next_actions"] = ["Upload a final demo video."]
            result = {**result, "body": json.dumps(public_video_check)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_public_video_check" in failed
    assert report["observed"]["public_video_check"]["official_host_check_ok"] is None
    assert (
        "Regenerate and upload docs/assets/public-video-check.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_unsafe_devpost_preview_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/devpost-submission-preview.json"):
            preview = valid_devpost_preview()
            preview["safe_to_share"] = False
            preview["submission_readiness"]["final_blockers"] = []
            result = {**result, "body": json.dumps(preview)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_devpost_preview" in failed
    assert report["observed"]["devpost_preview"]["safe_to_share"] is False
    assert (
        "Regenerate and upload docs/assets/devpost-submission-preview.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_stale_event_snapshot_with_action():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/devpost-event-snapshot.json"):
            snapshot = valid_event_snapshot()
            snapshot["checked_at"] = "2026-05-01T00:00:00Z"
            result = {**result, "body": json.dumps(snapshot)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_event_snapshot" in failed
    assert (
        "Regenerate and upload docs/assets/devpost-event-snapshot.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_missing_event_requirement():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/devpost-event-snapshot.json"):
            snapshot = valid_event_snapshot()
            snapshot["rules"]["requirements"]["genblaze_usage"] = False
            result = {**result, "body": json.dumps(snapshot)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_event_snapshot" in failed
    assert report["observed"]["event_snapshot"]["requirements_ok"] is False


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


def test_public_space_sync_fails_on_unsafe_judge_evidence_index():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-evidence-index.json"):
            index = valid_judge_evidence_index()
            index["safe_to_submit"] = True
            index["status"]["final_blockers"] = []
            index["claim_boundary"] = "Completed live B2 and Genblaze proof."
            result = {**result, "body": json.dumps(index)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_evidence_index" in failed
    assert (
        "Regenerate and upload docs/assets/judge-evidence-index.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_accepts_final_ready_closeout_status():
    def final_ready_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/final-closeout-status.json") or url.endswith("/api/judge/final-closeout"):
            result = {**result, "body": json.dumps(valid_final_ready_closeout_status())}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=final_ready_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert "raw_final_closeout_status" not in failed
    assert "api_final_closeout_status" not in failed
    assert report["observed"]["final_closeout_status"]["mode"] == "final_closeout_ready"
    assert report["observed"]["final_closeout_status"]["safe_to_submit"] is True


def test_public_space_sync_fails_on_inconsistent_final_closeout_status():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/final-closeout-status.json"):
            closeout = valid_final_closeout_status()
            closeout["safe_to_submit"] = True
            closeout["mode"] = "final_closeout_ready"
            result = {**result, "body": json.dumps(closeout)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_final_closeout_status" in failed
    assert (
        "Regenerate and upload docs/assets/final-closeout-status.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_unsafe_judge_decision_brief():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-decision-brief.json"):
            brief = valid_judge_decision_brief()
            brief["safe_to_submit"] = True
            brief["claim_boundary"] = "Completed Backblaze B2 and Genblaze live proof."
            result = {**result, "body": json.dumps(brief)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_decision_brief" in failed
    assert (
        "Regenerate and upload docs/assets/judge-decision-brief.json to the Space."
        in report["next_actions"]
    )


def test_public_space_sync_fails_on_stale_judge_decision_brief_created_at():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-decision-brief.json"):
            brief = valid_judge_decision_brief()
            brief["created_at"] = "2000-01-01T00:00:00Z"
            result = {**result, "body": json.dumps(brief)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_decision_brief" in failed
    assert report["observed"]["judge_decision_brief"]["fresh"] is False


def test_public_space_sync_fails_on_wrong_judge_decision_evidence_link():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-decision-brief.json"):
            brief = valid_judge_decision_brief()
            brief["links"]["evidence_index"] = (
                "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/"
                "docs/assets/public-space-sync-report.md"
            )
            result = {**result, "body": json.dumps(brief)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_decision_brief" in failed
    assert report["observed"]["judge_decision_brief"]["fresh"] is False


def test_public_space_sync_fails_on_bad_judge_decision_source_state():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/judge-decision-brief.json"):
            brief = valid_judge_decision_brief()
            brief["source_reports"]["public_space_sync"]["ok"] = False
            result = {**result, "body": json.dumps(brief)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_judge_decision_brief" in failed
    assert report["observed"]["judge_decision_brief"]["source_state_ok"] is False


def test_public_space_sync_accepts_final_ready_video_publish_kit():
    def final_ready_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/final-video-publish-kit.json"):
            kit = valid_video_publish_kit()
            kit["mode"] = "public_video_ready"
            kit["safe_to_submit"] = True
            kit["final_video_ready"] = True
            kit["devpost_field"]["ready"] = True
            kit["devpost_field"]["value"] = "https://youtu.be/proofframe-final"
            kit["source_reports"]["public_video_check"] = {
                "schema_ok": True,
                "ok": True,
                "safe_to_submit": True,
            }
            kit["source_reports"]["final_control"] = {
                "schema_ok": True,
                "ok": True,
                "safe_to_submit": True,
            }
            result = {**result, "body": json.dumps(kit)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=final_ready_fetcher)

    assert report["ok"] is True
    assert report["observed"]["video_publish_kit"]["mode"] == "public_video_ready"
    assert report["observed"]["video_publish_kit"]["safe_to_submit"] is True


def test_public_space_sync_fails_on_inconsistent_video_publish_kit():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/final-video-publish-kit.json"):
            kit = valid_video_publish_kit()
            kit["mode"] = "public_video_ready"
            kit["safe_to_submit"] = True
            kit["final_video_ready"] = True
            kit["devpost_field"]["ready"] = True
            kit["source_reports"]["public_video_check"] = {
                "schema_ok": True,
                "ok": True,
                "safe_to_submit": True,
            }
            kit["source_reports"]["final_control"] = {
                "schema_ok": True,
                "ok": False,
                "safe_to_submit": True,
            }
            result = {**result, "body": json.dumps(kit)}
        return result

    report = public_space_sync.build_report(expected_sha=EXPECTED_SHA, fetcher=broken_fetcher)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "raw_video_publish_kit" in failed
    assert (
        "Regenerate and upload docs/assets/final-video-publish-kit.json to the Space."
        in report["next_actions"]
    )


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
                        "commands": valid_post_credential_commands(),
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
        "devpost_submission_preview": False,
    }
    assert report["observed"]["post_credential_plan_required_sequence"] is False


def test_public_space_sync_fails_when_post_credential_preview_is_missing_from_valid_sequence():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            commands = [
                command
                for command in valid_post_credential_commands()
                if command["id"] != "devpost_submission_preview"
            ]
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": commands,
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
    assert report["observed"]["post_credential_plan_required_sequence"] is True
    assert report["observed"]["post_credential_plan_report_sequence"] is False
    assert report["observed"]["post_credential_plan_validators"]["devpost_submission_preview"] is False


def test_public_space_sync_fails_when_post_credential_preview_is_after_secret_scan():
    def broken_fetcher(url: str, timeout: int) -> dict:
        result = fake_fetcher(url, timeout)
        if url.endswith("/docs/assets/post-credential-live-proof-plan.json"):
            commands = valid_post_credential_commands()
            ids = [command["id"] for command in commands]
            preview_index = ids.index("devpost_submission_preview")
            secret_scan_index = ids.index("secret_scan")
            commands[preview_index], commands[secret_scan_index] = commands[secret_scan_index], commands[preview_index]
            result = {
                **result,
                "body": json.dumps(
                    {
                        "schema": "proofframe.post_credential_live_proof.v1",
                        "ok": True,
                        "mode": "plan_only",
                        "execute": False,
                        "update_tasks": False,
                        "commands": commands,
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
    assert report["observed"]["post_credential_plan_required_sequence"] is True
    assert report["observed"]["post_credential_plan_report_sequence"] is False
    assert report["observed"]["post_credential_plan_validators"]["devpost_submission_preview"] is True


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
