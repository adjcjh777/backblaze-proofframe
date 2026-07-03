"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


class ConfigurationError(RuntimeError):
    """Raised when an explicitly requested integration is not configured."""


GENBLAZE_PROVIDER_ALIASES = {
    "gmi": "gmicloud",
    "gmicloud": "gmicloud",
    "gmi-cloud": "gmicloud",
    "openai": "openai",
    "dalle": "openai",
    "dall-e": "openai",
}
GENBLAZE_PROVIDER_MODULES = {
    "gmicloud": ("genblaze_gmicloud",),
    "openai": ("genblaze_openai",),
}


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


def normalize_genblaze_provider(value: str) -> str:
    provider = (value or "gmicloud").strip().lower().replace("_", "-")
    return GENBLAZE_PROVIDER_ALIASES.get(provider, provider)


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
    b2_region: str = ""
    genblaze_provider: str = "gmicloud"
    genblaze_base_url: str = ""
    genblaze_api_key: str = ""
    genblaze_image_model: str = ""
    genblaze_aspect_ratio: str = "16:9"
    genblaze_timeout_seconds: int = 180
    gmi_api_key: str = ""
    openai_api_key: str = ""

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
            b2_region=_env(source, "B2_REGION")
            or _region_from_b2_endpoint(
                _env(source, "B2_ENDPOINT_URL") or _env(source, "B2_S3_ENDPOINT_URL")
            ),
            genblaze_provider=normalize_genblaze_provider(
                _env(source, "GENBLAZE_PROVIDER", "gmicloud")
            ),
            genblaze_base_url=_env(source, "GENBLAZE_BASE_URL") or _env(source, "GMI_BASE_URL"),
            genblaze_api_key=_env(source, "GENBLAZE_API_KEY"),
            genblaze_image_model=_env(source, "GENBLAZE_IMAGE_MODEL"),
            genblaze_aspect_ratio=_env(source, "GENBLAZE_ASPECT_RATIO", "16:9"),
            genblaze_timeout_seconds=_env_int(source, "GENBLAZE_TIMEOUT_SECONDS", 180),
            gmi_api_key=_env(source, "GMI_API_KEY"),
            openai_api_key=_env(source, "OPENAI_API_KEY"),
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

    def b2_region_for_backblaze(self) -> str:
        return self.b2_region or _region_from_b2_endpoint(self.b2_endpoint_url)

    def genblaze_provider_modules(self) -> tuple[str, ...]:
        return GENBLAZE_PROVIDER_MODULES.get(self.genblaze_provider, ())

    def genblaze_provider_key(self) -> str:
        if self.genblaze_provider == "gmicloud":
            return self.genblaze_api_key or self.gmi_api_key
        if self.genblaze_provider == "openai":
            return self.openai_api_key
        return ""

    def genblaze_key_remediation(self) -> str:
        if self.genblaze_provider == "openai":
            return "Set OPENAI_API_KEY for GENBLAZE_PROVIDER=openai."
        return "Set GENBLAZE_API_KEY or GMI_API_KEY for GENBLAZE_PROVIDER=gmicloud."

    def require_genblaze(self) -> None:
        if self.genblaze_provider not in GENBLAZE_PROVIDER_MODULES:
            raise ConfigurationError(
                "Unsupported Genblaze provider: "
                f"{self.genblaze_provider}. Use GENBLAZE_PROVIDER=gmicloud or openai."
            )
        missing = [
            key
            for key, value in {
                self.genblaze_key_remediation(): self.genblaze_provider_key(),
                "GENBLAZE_IMAGE_MODEL": self.genblaze_image_model,
            }.items()
            if not value
        ]
        if missing:
            raise ConfigurationError(
                "Genblaze generation was requested but required environment variables are missing: "
                + ", ".join(missing)
            )


def _region_from_b2_endpoint(endpoint_url: str) -> str:
    if not endpoint_url:
        return ""
    parsed = urlparse(endpoint_url if "://" in endpoint_url else f"https://{endpoint_url}")
    host = parsed.netloc or parsed.path
    match = re.match(r"^s3[.-]([a-z0-9-]+)\.backblazeb2\.com$", host)
    return match.group(1) if match else ""
