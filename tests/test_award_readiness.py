import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "award_readiness.py"
SPEC = importlib.util.spec_from_file_location("award_readiness", SCRIPT_PATH)
award_readiness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(award_readiness)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def write_tasks(root: Path, *, live_done: bool = False, final_done: bool = False) -> None:
    statuses = {
        "T020": "done" if live_done else "doing",
        "T021": "done" if live_done else "doing",
        "T040": "done",
        "T041": "done" if final_done else "todo",
        "T041A": "done" if live_done else "todo",
        "T042": "done" if final_done else "todo",
    }
    write_file(
        root,
        "tasks.json",
        json.dumps(
            {
                "project": "ProofFrame",
                "tasks": [
                    {"id": task_id, "status": status, "title": task_id}
                    for task_id, status in statuses.items()
                ],
            }
        ),
    )


def write_common_fixtures(root: Path, *, live_done: bool = False, final_done: bool = False) -> None:
    write_tasks(root, live_done=live_done, final_done=final_done)
    write_file(root, ".gitignore", ".env.*\n!.env.final.example\n.env.final.local\nvar/\n")
    write_file(root, "README.md", "ProofFrame local demo; final gate verifies B2.\n")
    write_file(root, "docs/submission.md", "Final submission target uses B2 after proof.\n")
    write_file(root, "docs/prd.md", "# PRD\n")
    write_file(root, "docs/spec.md", "# Spec\n")
    write_file(root, "docs/demo_script.md", "# Demo\n")
    write_file(root, "docs/public_claim_freeze.md", "# Claim Freeze\n")
    write_file(root, "docs/verification.md", "# Verification\n")
    write_file(root, "docs/evidence_package.md", "# Evidence\n")
    write_file(root, "docs/devpost_draft.md", "# Draft\n")
    write_file(root, "docs/sponsor_fit_matrix.md", "# Matrix\n")
    write_file(root, "docs/assets/sponsor-fit-audit.json", json.dumps({"ok": True, "mode": "sponsor_fit_ready"}))
    write_file(root, "docs/assets/sponsor-fit-audit.md", "# Sponsor Fit Audit\n")
    write_file(root, "src/proofframe/storage.py", "class B2StorageBackend:\n    pass\n")
    write_file(root, "src/proofframe/providers.py", "class GenblazeMediaProvider:\n    pass\n")
    write_file(root, "src/proofframe/models.py", "class CampaignManifest:\n    pass\n")
    write_file(root, "src/proofframe/app.py", '"/api/demo/judge-packet"\n"packet.zip"\n')
    write_file(root, "apps/web/index.html", '<main class="review-console">Sponsor Evidence Model</main>\n')
    write_file(root, "scripts/run_b2_live_proof.py", "# b2 runner\n")
    write_file(root, "scripts/run_final_live_proof.py", "# final runner\n")
    write_file(root, "scripts/api_smoke.py", "def assert_safe_evidence():\n    pass\n")
    write_file(root, "scripts/claim_lint.py", "# claim lint\n")
    write_file(root, "scripts/devpost_form_kit.py", "# form kit\n")
    write_file(root, "scripts/demo_storyboard.py", "# storyboard\n")
    write_file(root, "scripts/live_env_handoff.py", "# handoff\n")
    write_file(root, "scripts/secret_scan.py", "# secret scan\n")
    write_file(root, ".env.final.example", "PROOFFRAME_STORAGE_BACKEND=b2\n")
    write_file(
        root,
        "docs/assets/b2-live-setup.json",
        json.dumps(
            {
                "bucket_name": "proofframe-demo",
                "endpoint": "s3.us-west-004.backblazeb2.com",
                "bucket_type": "private",
            }
        ),
    )
    write_file(root, "docs/assets/b2-live-setup.md", "# B2 setup\n")
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps(
            {
                "mode": "post_live_verified" if live_done else "pre_live_safe",
                "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
                "claim_warning": "safe",
            }
        ),
    )
    write_file(root, "docs/assets/devpost-submission-packet.md", "Final B2 proof target.\n")
    write_file(root, "docs/assets/devpost-form-kit.json", "{}\n")
    write_file(root, "docs/assets/devpost-form-kit.md", "# Form Kit\n")
    write_file(
        root,
        "docs/assets/devpost-event-snapshot.json",
        json.dumps(
            {
                "schema": "proofframe.devpost_event_snapshot.v1",
                "validation": {"ok": True, "submission_open": True},
                "rules": {
                    "requirements": {
                        "working_app_url": True,
                        "github_repo_url": True,
                        "demo_video": True,
                    },
                    "judging_criteria": [
                        {"name": "Real-world Utility", "present": True},
                        {"name": "Production Readiness", "present": True},
                        {"name": "B2 Storage + Data Orchestration", "present": True},
                        {"name": "Use of Genblaze", "present": True},
                    ],
                },
            }
        ),
    )
    write_file(root, "docs/assets/devpost-event-snapshot.md", "# Event Snapshot\n")
    write_file(root, "docs/assets/submission-bundle-manifest.json", "{}\n")
    write_file(root, "docs/assets/submission-bundle-manifest.md", "# Bundle\n")
    write_file(root, "docs/assets/live-credential-handoff.json", "{}\n")
    write_file(root, "docs/assets/live-credential-handoff.md", "# Handoff\n")
    write_file(root, "docs/assets/demo-storyboard.json", "{}\n")
    write_file(root, "docs/assets/demo-storyboard.md", "# Storyboard\n")
    for screenshot in [
        "docs/assets/proofframe-local-ui-smoke.png",
        "docs/assets/proofframe-review-console-smoke.png",
        "docs/assets/proofframe-hf-public-smoke.png",
    ]:
        write_file(root, screenshot, b"\x89PNG\r\n\x1a\nfixture")
    if live_done:
        live_evidence = {
            "ok": True,
            "storage_backend": "b2",
            "generation_backend": "genblaze",
            "asset_storage_backend": "b2",
            "asset_provider": "genblaze/gmicloud-image",
            "asset_sha256": "a" * 64,
            "manifest_sha256": "b" * 64,
            "asset_storage_key": "campaigns/cmp/media/asset.png",
            "manifest_key": "campaigns/cmp/manifests/manifest.json",
        }
        write_file(root, "docs/assets/b2-live-proof-evidence.json", json.dumps(live_evidence))
        write_file(root, "docs/assets/final-live-proof-evidence.json", json.dumps(live_evidence))


def test_award_readiness_scores_pre_live_competitive_state(tmp_path):
    write_common_fixtures(tmp_path)

    report = award_readiness.build_report(tmp_path)

    assert report["mode"] == "pre_live_competitive"
    assert report["score"] >= 75
    assert report["submission_gate"]["mode"] == "pre_live_safe"
    assert report["task_statuses"]["T020"] == "doing"
    assert report["secret_scan"]["ok"] is True
    product_depth = next(item for item in report["criteria"] if item["id"] == "product_depth")
    trust = next(item for item in report["criteria"] if item["id"] == "trust_and_compliance")
    assert next(signal for signal in product_depth["signals"] if signal["id"] == "review_console")["ok"] is True
    assert next(signal for signal in trust["signals"] if signal["id"] == "env_ignored")["ok"] is True


def test_b2_setup_ready_accepts_legacy_bucket_field(tmp_path):
    write_file(
        tmp_path,
        "docs/assets/b2-live-setup.json",
        json.dumps(
            {
                "bucket": "proofframe-demo",
                "endpoint": "s3.us-west-004.backblazeb2.com",
                "bucket_type": "private",
            }
        ),
    )

    assert award_readiness.b2_setup_ready(tmp_path) is True


def test_award_readiness_reaches_final_mode_when_live_and_submit_tasks_done(tmp_path):
    write_common_fixtures(tmp_path, live_done=True, final_done=True)

    report = award_readiness.build_report(tmp_path)

    assert report["mode"] == "final_award_ready"
    assert report["score"] == report["max_score"]
    assert report["submission_gate"]["ok"] is True


def test_award_readiness_writes_markdown_and_json(tmp_path):
    write_common_fixtures(tmp_path)
    report = award_readiness.build_report(tmp_path)
    json_path = tmp_path / "out" / "award.json"
    markdown_path = tmp_path / "out" / "award.md"

    award_readiness.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.award_readiness.v1"
    assert "# ProofFrame Award Readiness" in markdown
    assert "Sponsor integration fit" in markdown
