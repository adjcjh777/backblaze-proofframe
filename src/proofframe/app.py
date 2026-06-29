"""FastAPI app for ProofFrame."""

from __future__ import annotations

import os
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import ConfigurationError, Settings
from .models import Asset, AssetStatus, AssetStatusUpdate, Campaign, CampaignCreate, CampaignManifest
from .providers import create_media_provider
from .repository import MemoryRepository
from .storage import create_storage_backend, manifest_to_plain_json
from .submission_gate import build_submission_gate


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


def public_artifact_path(filename: str) -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[2] / "docs" / "assets" / filename,
        Path.cwd() / "docs" / "assets" / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_public_artifact(filename: str, expected_schema: str, label: str) -> dict[str, object]:
    path = public_artifact_path(filename)
    if path is None:
        raise HTTPException(status_code=404, detail=f"{label} artifact not found")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=503, detail=f"{label} artifact is invalid") from exc
    if payload.get("schema") != expected_schema:
        raise HTTPException(status_code=503, detail=f"{label} schema mismatch")
    return payload


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

    def persist_generated_assets(campaign: Campaign, count: int) -> list[Asset]:
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

    @app.get("/api/submission/gate")
    def submission_gate() -> dict[str, object]:
        return build_submission_gate()

    @app.get("/api/judge/brief")
    def judge_brief() -> dict[str, object]:
        return load_public_artifact("judge-brief.json", "proofframe.judge_brief.v1", "Judge brief")

    @app.get("/api/judge/crosswalk")
    def judge_crosswalk() -> dict[str, object]:
        return load_public_artifact(
            "judge-crosswalk.json",
            "proofframe.judge_crosswalk.v1",
            "Judge crosswalk",
        )

    @app.get("/api/judge/evidence-index")
    def judge_evidence_index() -> dict[str, object]:
        return load_public_artifact(
            "judge-evidence-index.json",
            "proofframe.judge_evidence_index.v1",
            "Judge evidence index",
        )

    @app.get("/api/judge/recording")
    def judge_recording() -> dict[str, object]:
        return load_public_artifact(
            "recording-assets.json",
            "proofframe.recording_assets.v1",
            "Recording assets",
        )

    @app.get("/api/judge/devpost")
    def judge_devpost() -> dict[str, object]:
        return load_public_artifact(
            "devpost-form-kit.json",
            "proofframe.devpost_form_kit.v1",
            "Devpost form kit",
        )

    @app.get("/api/judge/submission-checklist")
    def judge_submission_checklist() -> dict[str, object]:
        return load_public_artifact(
            "devpost-submission-checklist.json",
            "proofframe.devpost_submission_checklist.v1",
            "Devpost submission checklist",
        )

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
        return persist_generated_assets(campaign, count)

    @app.post("/api/demo/judge-packet")
    def create_judge_packet() -> dict[str, object]:
        campaign = repo.add_campaign(
            Campaign(
                title="Judge Ready Provenance Packet",
                audience="hackathon judges, creative leads, and storage reviewers",
                tone="credible, warm, production-minded",
                brief=(
                    "Create a public-safe launch visual packet for an arts nonprofit. "
                    "The packet should prove prompt, provider, model, storage key, checksum, "
                    "and approval state without exposing secrets."
                ),
            )
        )
        assets = persist_generated_assets(campaign, count=3)
        if assets:
            assets[0].status = AssetStatus.approved
            assets[0].risk_note = "Approved demo asset: provenance, checksum, and storage route verified."
        manifest = CampaignManifest(campaign=campaign, assets=repo.list_assets(campaign.id))
        return {
            "campaign": campaign.model_dump(mode="json"),
            "assets": [asset.model_dump(mode="json") for asset in repo.list_assets(campaign.id)],
            "manifest": manifest_to_plain_json(manifest),
        }

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

    @app.get("/api/campaigns/{campaign_id}/packet.zip")
    def download_packet(campaign_id: str) -> Response:
        campaign = repo.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        assets = repo.list_assets(campaign_id)
        manifest = CampaignManifest(campaign=campaign, assets=assets)
        manifest_json = manifest.model_dump_json(indent=2)
        read_bytes = getattr(storage, "read_bytes", None)

        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as packet:
            packet.writestr("manifest.json", manifest_json)
            packet.writestr(
                "README.txt",
                "\n".join(
                    [
                        "ProofFrame Evidence Packet",
                        f"Campaign: {campaign.title}",
                        f"Campaign ID: {campaign.id}",
                        f"Storage backend: {storage.name}",
                        "",
                        "manifest.json contains prompts, providers, models, storage keys, checksums, and approval states.",
                        "Local media files are included when available. Remote B2 objects are referenced in the manifest only.",
                    ]
                ),
            )
            if callable(read_bytes):
                for asset in assets:
                    try:
                        data = read_bytes(asset.storage_key)
                    except OSError:
                        continue
                    filename = Path(asset.storage_key).name
                    packet.writestr(f"media/{filename}", data)

        return Response(
            content=buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{campaign_id}-proofframe-packet.zip"'
            },
        )

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
