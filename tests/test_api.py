from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from proofframe.app import create_app, frontend_index_path, load_public_artifact, public_artifact_path


def test_frontend_index_path_can_use_explicit_web_root(tmp_path, monkeypatch):
    web_root = tmp_path / "web"
    web_root.mkdir()
    index_path = web_root / "index.html"
    index_path.write_text("<html>ProofFrame</html>", encoding="utf-8")

    monkeypatch.setenv("PROOFFRAME_WEB_ROOT", str(web_root))

    assert frontend_index_path() == index_path


def test_public_artifact_path_finds_judge_brief():
    path = public_artifact_path("judge-brief.json")

    assert path is not None
    assert path.name == "judge-brief.json"


def test_public_artifact_loader_rejects_schema_mismatch(tmp_path, monkeypatch):
    artifact = tmp_path / "docs" / "assets"
    artifact.mkdir(parents=True)
    path = artifact / "bad.json"
    path.write_text('{"schema": "wrong"}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(HTTPException) as exc_info:
        load_public_artifact("bad.json", "proofframe.expected.v1", "Bad")

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Bad schema mismatch"


def test_health_and_campaign_flow(tmp_path):
    client = TestClient(create_app(storage_root=tmp_path))

    index_response = client.get("/")
    assert index_response.status_code == 200
    assert "Generated Media Ledger" in index_response.text
    assert "Search Evidence" in index_response.text
    assert "Judge recording slate" in index_response.text
    assert "Sponsor Evidence Model" in index_response.text
    assert "30-Second Judge Brief" in index_response.text
    assert "Criteria Crosswalk" in index_response.text
    assert "Decision brief" in index_response.text
    assert "Evidence index" in index_response.text
    assert "Video publish kit" in index_response.text
    assert "crosswalkRows" in index_response.text
    assert "Recording Runbook" in index_response.text
    assert "recordingRows" in index_response.text
    assert "Devpost Kit" in index_response.text
    assert "devpostRows" in index_response.text
    assert "Submit Checklist" in index_response.text
    assert "submitRows" in index_response.text
    assert "Final Closeout" in index_response.text
    assert "closeoutRows" in index_response.text
    assert "B2/Genblaze final proof gated" in index_response.text
    assert "Claim Boundary" in index_response.text
    assert "Submission readiness gate" in index_response.text
    assert "shouldAutoLoadJudgeDemo" in index_response.text

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["ready"] is True

    gate_response = client.get("/api/submission/gate")
    assert gate_response.status_code == 200
    gate = gate_response.json()
    assert gate["mode"] in {"pre_live_safe", "final_ready"}
    assert "task_gates" in gate
    assert "evidence_gate" in gate
    assert "report_gate" in gate

    brief_response = client.get("/api/judge/brief")
    assert brief_response.status_code == 200
    brief = brief_response.json()
    assert brief["schema"] == "proofframe.judge_brief.v1"
    assert brief["status"]["safe_to_submit"] is False
    assert "Genblaze" in " ".join(brief["not_yet_claimed"] + brief["safe_claims"])

    crosswalk_response = client.get("/api/judge/crosswalk")
    assert crosswalk_response.status_code == 200
    crosswalk = crosswalk_response.json()
    assert crosswalk["schema"] == "proofframe.judge_crosswalk.v1"
    assert crosswalk["safe_to_submit"] is False
    row_ids = {row["id"] for row in crosswalk["rows"]}
    assert {"real_world_utility", "production_readiness"} <= row_ids

    decision_brief_response = client.get("/api/judge/decision-brief")
    assert decision_brief_response.status_code == 200
    decision_brief = decision_brief_response.json()
    assert decision_brief["schema"] == "proofframe.judge_decision_brief.v1"
    assert decision_brief["ok"] is True
    assert decision_brief["safe_to_share"] is True
    assert decision_brief["safe_to_submit"] is False
    assert len(decision_brief["decision_checks"]) >= 6

    evidence_index_response = client.get("/api/judge/evidence-index")
    assert evidence_index_response.status_code == 200
    evidence_index = evidence_index_response.json()
    assert evidence_index["schema"] == "proofframe.judge_evidence_index.v1"
    assert evidence_index["safe_to_submit"] is False
    assert len(evidence_index["links"]) >= 10
    assert {"genblaze_live_proof", "public_video"} & set(evidence_index["status"]["final_blockers"])

    video_kit_response = client.get("/api/judge/video-publish-kit")
    assert video_kit_response.status_code == 200
    video_kit = video_kit_response.json()
    assert video_kit["schema"] == "proofframe.final_video_publish_kit.v1"
    assert video_kit["safe_to_submit"] is False
    assert video_kit["final_video_ready"] is False
    assert len(video_kit["upload_checklist"]) >= 4
    assert "YouTube" in video_kit["allowed_hosts"]

    recording_response = client.get("/api/judge/recording")
    assert recording_response.status_code == 200
    recording = recording_response.json()
    assert recording["schema"] == "proofframe.recording_assets.v1"
    assert recording["final_video_ready"] is False
    assert len(recording["shot_plan"]) >= 3
    assert recording["source_reports"]["storyboard"]["schema_ok"] is True
    assert recording["source_reports"]["final_video_publish_kit"]["schema_ok"] is True
    assert recording["source_reports"]["final_video_publish_kit"]["safe_to_submit"] is False

    devpost_response = client.get("/api/judge/devpost")
    assert devpost_response.status_code == 200
    devpost = devpost_response.json()
    assert devpost["schema"] == "proofframe.devpost_form_kit.v1"
    assert devpost["mode"] == "pre_live_form_ready"
    assert devpost["final_form_ready"] is False
    field_ids = {field["id"] for field in devpost["fields"]}
    assert {"project_name", "tagline", "video_url"} <= field_ids

    checklist_response = client.get("/api/judge/submission-checklist")
    assert checklist_response.status_code == 200
    checklist = checklist_response.json()
    assert checklist["schema"] == "proofframe.devpost_submission_checklist.v1"
    assert checklist["mode"] == "pre_submit_blocked"
    assert checklist["safe_to_submit"] is False
    assert len(checklist["preflight"]) >= 3
    assert checklist["field_gate"]["final_pending_fields"] == ["video_url"]

    closeout_response = client.get("/api/judge/final-closeout")
    assert closeout_response.status_code == 200
    closeout = closeout_response.json()
    assert closeout["schema"] == "proofframe.final_closeout_status.v1"
    assert closeout["closeout_health_ok"] is True
    assert closeout["safe_to_submit"] is False
    assert any(gate["id"] == "b2_live_proof" for gate in closeout["gates"])

    campaign_response = client.post(
        "/api/campaigns",
        json={
            "title": "Library Night",
            "brief": "Invite teens to a late-night zine and music event.",
            "audience": "teen creators",
            "tone": "bold but trustworthy",
        },
    )
    assert campaign_response.status_code == 200
    campaign = campaign_response.json()

    assets_response = client.post(f"/api/campaigns/{campaign['id']}/generate?count=2")
    assert assets_response.status_code == 200
    assets = assets_response.json()
    assert len(assets) == 2
    assert assets[0]["sha256"]

    status_response = client.post(
        f"/api/assets/{assets[0]['id']}/status",
        json={"status": "approved", "risk_note": "Approved for demo use."},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "approved"

    manifest_response = client.get(f"/api/campaigns/{campaign['id']}/manifest")
    assert manifest_response.status_code == 200
    manifest = manifest_response.json()
    assert manifest["campaign"]["id"] == campaign["id"]
    assert len(manifest["assets"]) == 2

    export_response = client.post(f"/api/campaigns/{campaign['id']}/export")
    assert export_response.status_code == 200
    export_payload = export_response.json()
    assert export_payload["stored_manifest"]["storage_key"].endswith("-manifest.json")
    assert (tmp_path / export_payload["stored_manifest"]["storage_key"]).exists()

    packet_response = client.get(f"/api/campaigns/{campaign['id']}/packet.zip")
    assert packet_response.status_code == 200
    assert packet_response.headers["content-type"] == "application/zip"
    with ZipFile(BytesIO(packet_response.content)) as packet:
        names = set(packet.namelist())
        assert "manifest.json" in names
        assert "README.txt" in names
        assert any(name.startswith("media/") and name.endswith(".svg") for name in names)
        assert campaign["id"] in packet.read("manifest.json").decode("utf-8")


def test_judge_demo_packet_flow(tmp_path):
    client = TestClient(create_app(storage_root=tmp_path))

    demo_response = client.post("/api/demo/judge-packet")
    assert demo_response.status_code == 200
    demo = demo_response.json()
    campaign = demo["campaign"]
    assets = demo["assets"]

    assert campaign["title"] == "Judge Ready Provenance Packet"
    assert len(assets) == 3
    assert assets[0]["status"] == "approved"
    assert demo["manifest"]["campaign"]["id"] == campaign["id"]

    packet_response = client.get(f"/api/campaigns/{campaign['id']}/packet.zip")
    assert packet_response.status_code == 200
    with ZipFile(BytesIO(packet_response.content)) as packet:
        assert "manifest.json" in packet.namelist()
        assert "README.txt" in packet.namelist()
