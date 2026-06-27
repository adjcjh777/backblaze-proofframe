"""FastAPI app for ProofFrame."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import __version__
from .models import Asset, AssetStatusUpdate, Campaign, CampaignCreate, CampaignManifest
from .providers import MockMediaProvider
from .repository import MemoryRepository
from .storage import LocalStorageBackend


def create_app(storage_root: Path | str = "var/storage") -> FastAPI:
    app = FastAPI(title="ProofFrame", version=__version__)
    repo = MemoryRepository()
    generator = MockMediaProvider()
    storage = LocalStorageBackend(storage_root)

    app.state.repo = repo
    app.state.generator = generator
    app.state.storage = storage

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "app": "ProofFrame",
            "version": __version__,
            "generation_backend": generator.provider,
            "storage_backend": storage.name,
            "ready": True,
        }

    @app.post("/api/campaigns", response_model=Campaign)
    def create_campaign(payload: CampaignCreate) -> Campaign:
        return repo.add_campaign(Campaign(**payload.model_dump()))

    @app.get("/api/campaigns", response_model=list[Campaign])
    def list_campaigns() -> list[Campaign]:
        return repo.list_campaigns()

    @app.post("/api/campaigns/{campaign_id}/generate", response_model=list[Asset])
    def generate_assets(campaign_id: str, count: int = 3) -> list[Asset]:
        campaign = repo.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        generated = generator.generate(campaign, count=max(1, min(count, 6)))
        assets: list[Asset] = []
        for media in generated:
            stored = storage.put_media(campaign.id, media)
            asset = Asset(
                campaign_id=campaign.id,
                prompt=media.prompt,
                provider=media.provider,
                model=media.model,
                storage_backend=stored.storage_backend,
                storage_key=stored.storage_key,
                public_url=stored.public_url,
                sha256=stored.sha256,
                bytes_size=stored.bytes_size,
            )
            assets.append(repo.add_asset(asset))
        return assets

    @app.post("/api/assets/{asset_id}/status", response_model=Asset)
    def update_asset_status(asset_id: str, payload: AssetStatusUpdate) -> Asset:
        asset = repo.get_asset(asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        asset.status = payload.status
        if payload.risk_note is not None:
            asset.risk_note = payload.risk_note
        return asset

    @app.get("/api/campaigns/{campaign_id}/manifest", response_model=CampaignManifest)
    def campaign_manifest(campaign_id: str) -> CampaignManifest:
        campaign = repo.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return CampaignManifest(campaign=campaign, assets=repo.list_assets(campaign_id))

    storage_path = Path(storage_root)
    storage_path.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

    return app


app = create_app()


def main() -> None:
    uvicorn.run("proofframe.app:app", host="127.0.0.1", port=8088, reload=True)


if __name__ == "__main__":
    main()

