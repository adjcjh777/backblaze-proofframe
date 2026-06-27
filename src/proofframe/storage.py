"""Storage backends."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .checksum import sha256_hex
from .config import ConfigurationError, Settings
from .models import CampaignManifest, GeneratedMedia, StoredObject


class StorageBackend(Protocol):
    name: str

    def put_media(self, campaign_id: str, media: GeneratedMedia) -> StoredObject: ...

    def put_manifest(self, campaign_id: str, manifest: CampaignManifest) -> StoredObject: ...


def _manifest_bytes(manifest: CampaignManifest) -> bytes:
    return manifest.model_dump_json(indent=2).encode("utf-8")


class LocalStorageBackend:
    """Filesystem storage used for tests and credential-free demos."""

    name = "local"

    def __init__(self, root: Path | str = "var/storage") -> None:
        self.root = Path(root)

    def put_media(self, campaign_id: str, media: GeneratedMedia) -> StoredObject:
        return self.put_bytes(
            campaign_id=campaign_id,
            filename=media.filename,
            data=media.data,
            content_type=media.content_type,
        )

    def put_manifest(self, campaign_id: str, manifest: CampaignManifest) -> StoredObject:
        return self.put_bytes(
            campaign_id=campaign_id,
            filename=f"{campaign_id}-manifest.json",
            data=_manifest_bytes(manifest),
            content_type="application/json",
        )

    def put_bytes(
        self, campaign_id: str, filename: str, data: bytes, content_type: str
    ) -> StoredObject:
        del content_type
        folder = self.root / campaign_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename
        path.write_bytes(data)
        relative = path.relative_to(self.root)
        return StoredObject(
            storage_backend=self.name,
            storage_key=str(relative),
            public_url=f"/storage/{relative.as_posix()}",
            sha256=sha256_hex(data),
            bytes_size=len(data),
        )

    def read_bytes(self, storage_key: str) -> bytes:
        path = (self.root / storage_key).resolve()
        root = self.root.resolve()
        if root not in path.parents:
            raise ConfigurationError(f"Refusing to read outside storage root: {storage_key}")
        return path.read_bytes()


@dataclass
class B2StorageBackend:
    """Backblaze B2 S3-compatible storage backend.

    The backend is intentionally explicit: if `PROOFFRAME_STORAGE_BACKEND=b2` is used,
    missing config raises before any silent local fallback can happen.
    """

    endpoint_url: str
    bucket: str
    key_id: str
    application_key: str
    public_base_url: str = ""
    client: Any | None = None

    name = "b2"

    @classmethod
    def from_settings(cls, settings: Settings) -> "B2StorageBackend":
        settings.require_b2()
        return cls(
            endpoint_url=settings.b2_endpoint_url,
            bucket=settings.b2_bucket,
            key_id=settings.b2_key_id,
            application_key=settings.b2_application_key,
            public_base_url=settings.b2_public_base_url,
        )

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        try:
            import boto3  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise ConfigurationError(
                "B2 storage requires boto3. Install with `pip install -e '.[integrations]'`."
            ) from exc
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.application_key,
        )
        return self.client

    def put_media(self, campaign_id: str, media: GeneratedMedia) -> StoredObject:
        return self.put_bytes(
            key=f"campaigns/{campaign_id}/media/{media.filename}",
            data=media.data,
            content_type=media.content_type,
            metadata={
                "campaign-id": campaign_id,
                "provider": media.provider,
                "model": media.model,
                "sha256": sha256_hex(media.data),
            },
        )

    def put_manifest(self, campaign_id: str, manifest: CampaignManifest) -> StoredObject:
        data = _manifest_bytes(manifest)
        return self.put_bytes(
            key=f"campaigns/{campaign_id}/manifests/{campaign_id}-manifest.json",
            data=data,
            content_type="application/json",
            metadata={"campaign-id": campaign_id, "sha256": sha256_hex(data)},
        )

    def put_bytes(
        self, key: str, data: bytes, content_type: str, metadata: dict[str, str] | None = None
    ) -> StoredObject:
        checksum = sha256_hex(data)
        self._client().put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            Metadata=metadata or {"sha256": checksum},
        )
        public_url = f"{self.public_base_url.rstrip('/')}/{key}" if self.public_base_url else None
        return StoredObject(
            storage_backend=self.name,
            storage_key=key,
            public_url=public_url,
            sha256=checksum,
            bytes_size=len(data),
        )


def create_storage_backend(settings: Settings) -> StorageBackend:
    if settings.storage_backend == "local":
        return LocalStorageBackend(settings.storage_root)
    if settings.storage_backend == "b2":
        return B2StorageBackend.from_settings(settings)
    raise ConfigurationError(f"Unknown storage backend: {settings.storage_backend}")


def manifest_to_plain_json(manifest: CampaignManifest) -> dict[str, Any]:
    return json.loads(manifest.model_dump_json())
