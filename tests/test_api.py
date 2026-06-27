from fastapi.testclient import TestClient

from proofframe.app import create_app


def test_health_and_campaign_flow(tmp_path):
    client = TestClient(create_app(storage_root=tmp_path))

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["ready"] is True

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

