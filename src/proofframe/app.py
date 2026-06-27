"""FastAPI app for ProofFrame."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import ConfigurationError, Settings
from .models import Asset, AssetStatusUpdate, Campaign, CampaignCreate, CampaignManifest
from .providers import create_media_provider
from .repository import MemoryRepository
from .storage import create_storage_backend, manifest_to_plain_json


def frontend_index_path() -> Path | None:
    explicit_root = os.environ.get("PROOFFRAME_WEB_ROOT", "").strip()
    candidates: list[Path] = []
    if explicit_root:
        candidates.append(Path(explicit_root) / "index.html")
    candidates.extend(
        [
            Path(__file__).resolve().parents[2] / "apps" / "web" / "index.html",
            Path.cwd() / "apps" / "web" / "index.html",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def create_app(storage_root: Path | str | None = None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    if storage_root is not None:
        settings = Settings(
            **{
                **settings.__dict__,
                "storage_root": str(storage_root),
            }
        )
    app = FastAPI(title="ProofFrame", version=__version__)
    repo = MemoryRepository()
    generator = create_media_provider(settings)
    storage = create_storage_backend(settings)

    app.state.repo = repo
    app.state.generator = generator
    app.state.storage = storage
    app.state.settings = settings

    @app.get("/")
    def index() -> FileResponse:
        index_path = frontend_index_path()
        if index_path is None:
            raise HTTPException(status_code=404, detail="Frontend not built")
        return FileResponse(index_path)

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "app": "ProofFrame",
            "version": __version__,
            "generation_backend": generator.provider,
            "storage_backend": storage.name,
            "b2_configured": bool(settings.b2_bucket and settings.b2_endpoint_url),
            "genblaze_configured": bool(
                settings.genblaze_image_model and (settings.genblaze_api_key or settings.gmi_api_key)
            ),
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
                generation_metadata=media.generation_metadata,
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

    @app.post("/api/campaigns/{campaign_id}/export")
    def export_campaign(campaign_id: str) -> dict[str, object]:
        campaign = repo.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        manifest = CampaignManifest(campaign=campaign, assets=repo.list_assets(campaign_id))
        stored = storage.put_manifest(campaign_id, manifest)
        return {
            "manifest": manifest_to_plain_json(manifest),
            "stored_manifest": stored.model_dump(mode="json"),
        }

    if storage.name == "local":
        storage_path = Path(settings.storage_root)
        storage_path.mkdir(parents=True, exist_ok=True)
        app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

    return app


try:
    app = create_app()
except ConfigurationError as exc:
    # Uvicorn should fail clearly when an explicitly requested integration is misconfigured.
    raise RuntimeError(str(exc)) from exc


def main() -> None:
    uvicorn.run("proofframe.app:app", host="127.0.0.1", port=8088, reload=True)


if __name__ == "__main__":
    main()
