from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from proofframe.app import create_app, frontend_index_path


def test_frontend_index_path_can_use_explicit_web_root(tmp_path, monkeypatch):
    web_root = tmp_path / "web"
    web_root.mkdir()
    index_path = web_root / "index.html"
    index_path.write_text("<html>ProofFrame</html>", encoding="utf-8")

    monkeypatch.setenv("PROOFFRAME_WEB_ROOT", str(web_root))

    assert frontend_index_path() == index_path


def test_health_and_campaign_flow(tmp_path):
    client = TestClient(create_app(storage_root=tmp_path))

    index_response = client.get("/")
    assert index_response.status_code == 200
    assert "Generated Media Ledger" in index_response.text
    assert "Search Evidence" in index_response.text
    assert "Judge recording slate" in index_response.text
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
