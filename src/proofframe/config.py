"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class ConfigurationError(RuntimeError):
    """Raised when an explicitly requested integration is not configured."""


def _env(env: Mapping[str, str], key: str, default: str = "") -> str:
    return env.get(key, default).strip()


def _env_int(env: Mapping[str, str], key: str, default: int) -> int:
    value = env.get(key, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{key} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    storage_backend: str = "local"
    generation_backend: str = "mock"
    storage_root: str = "var/storage"
    b2_endpoint_url: str = ""
    b2_bucket: str = ""
    b2_key_id: str = ""
    b2_application_key: str = ""
    b2_public_base_url: str = ""
    genblaze_base_url: str = ""
    genblaze_api_key: str = ""
    genblaze_image_model: str = ""
    genblaze_aspect_ratio: str = "16:9"
    genblaze_timeout_seconds: int = 180
    gmi_api_key: str = ""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        return cls(
            storage_backend=_env(source, "PROOFFRAME_STORAGE_BACKEND", "local").lower(),
            generation_backend=_env(source, "PROOFFRAME_GENERATION_BACKEND", "mock").lower(),
            storage_root=_env(source, "PROOFFRAME_STORAGE_ROOT", "var/storage"),
            b2_endpoint_url=_env(source, "B2_ENDPOINT_URL") or _env(source, "B2_S3_ENDPOINT_URL"),
            b2_bucket=_env(source, "B2_BUCKET"),
            b2_key_id=_env(source, "B2_KEY_ID"),
            b2_application_key=_env(source, "B2_APPLICATION_KEY") or _env(source, "B2_APP_KEY"),
            b2_public_base_url=_env(source, "B2_PUBLIC_BASE_URL"),
            genblaze_base_url=_env(source, "GENBLAZE_BASE_URL") or _env(source, "GMI_BASE_URL"),
            genblaze_api_key=_env(source, "GENBLAZE_API_KEY"),
            genblaze_image_model=_env(source, "GENBLAZE_IMAGE_MODEL"),
            genblaze_aspect_ratio=_env(source, "GENBLAZE_ASPECT_RATIO", "16:9"),
            genblaze_timeout_seconds=_env_int(source, "GENBLAZE_TIMEOUT_SECONDS", 180),
            gmi_api_key=_env(source, "GMI_API_KEY"),
        )

    def require_b2(self) -> None:
        missing = [
            key
            for key, value in {
                "B2_ENDPOINT_URL": self.b2_endpoint_url,
                "B2_BUCKET": self.b2_bucket,
                "B2_KEY_ID": self.b2_key_id,
                "B2_APPLICATION_KEY or B2_APP_KEY": self.b2_application_key,
            }.items()
            if not value
        ]
        if missing:
            raise ConfigurationError(
                "B2 storage was requested but required environment variables are missing: "
                + ", ".join(missing)
            )

    def require_genblaze(self) -> None:
        missing = [
            key
            for key, value in {
                "GENBLAZE_API_KEY or GMI_API_KEY": self.genblaze_api_key or self.gmi_api_key,
                "GENBLAZE_IMAGE_MODEL": self.genblaze_image_model,
            }.items()
            if not value
        ]
        if missing:
            raise ConfigurationError(
                "Genblaze generation was requested but required environment variables are missing: "
                + ", ".join(missing)
            )
