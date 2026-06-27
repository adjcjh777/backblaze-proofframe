"""Storage backends."""

from __future__ import annotations

from pathlib import Path

from .checksum import sha256_hex
from .models import GeneratedMedia, StoredObject


class LocalStorageBackend:
    """Filesystem storage used for tests and credential-free demos."""

    name = "local"

    def __init__(self, root: Path | str = "var/storage") -> None:
        self.root = Path(root)

    def put_media(self, campaign_id: str, media: GeneratedMedia) -> StoredObject:
        folder = self.root / campaign_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / media.filename
        path.write_bytes(media.data)
        relative = path.relative_to(self.root)
        return StoredObject(
            storage_backend=self.name,
            storage_key=str(relative),
            public_url=f"/storage/{relative.as_posix()}",
            sha256=sha256_hex(media.data),
            bytes_size=len(media.data),
        )

