"""Media generation providers."""

from __future__ import annotations

import html
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse
from urllib.request import urlopen

from .checksum import sha256_hex
from .config import ConfigurationError, Settings
from .models import Campaign, GeneratedMedia


class MediaProvider(Protocol):
    provider: str
    model: str

    def generate(self, campaign: Campaign, count: int = 3) -> list[GeneratedMedia]: ...


def build_campaign_prompt(campaign: Campaign, index: int) -> str:
    return (
        f"Create a {campaign.tone} campaign image for {campaign.audience}. "
        f"Brief: {campaign.brief}. Variant {index}."
    )


@dataclass(frozen=True)
class MockMediaProvider:
    """Deterministic media provider for tests and credential-free demos."""

    model: str = "mock-svg-v1"
    provider: str = "mock"

    def generate(self, campaign: Campaign, count: int = 3) -> list[GeneratedMedia]:
        return [self._generate_one(campaign, index) for index in range(1, count + 1)]

    def _generate_one(self, campaign: Campaign, index: int) -> GeneratedMedia:
        prompt = build_campaign_prompt(campaign, index)
        seed = sha256_hex(f"{campaign.id}:{prompt}".encode("utf-8"))[:8]
        colors = ["#F2C14E", "#4F7CAC", "#6FAE75", "#C45BAA", "#E4572E"]
        primary = colors[int(seed[:2], 16) % len(colors)]
        secondary = colors[int(seed[2:4], 16) % len(colors)]
        title = html.escape(campaign.title[:42])
        brief = html.escape(campaign.brief[:96])
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#101216"/>
  <rect x="80" y="76" width="1120" height="568" rx="28" fill="#F8F4EA"/>
  <circle cx="1080" cy="180" r="92" fill="{primary}" opacity="0.92"/>
  <rect x="140" y="142" width="420" height="28" fill="{secondary}"/>
  <text x="140" y="252" font-family="Georgia, serif" font-size="72" fill="#151515">{title}</text>
  <text x="144" y="326" font-family="Helvetica, Arial, sans-serif" font-size="28" fill="#333">{brief}</text>
  <text x="144" y="548" font-family="Helvetica, Arial, sans-serif" font-size="22" fill="#555">ProofFrame mock asset | seed {seed} | variant {index}</text>
</svg>
"""
        return GeneratedMedia(
            prompt=prompt,
            provider=self.provider,
            model=self.model,
            filename=f"{campaign.id}-variant-{index}.svg",
            content_type="image/svg+xml",
            data=svg.encode("utf-8"),
            generation_metadata={"mock_seed": seed, "variant": str(index)},
        )


@dataclass(frozen=True)
class GenblazeMediaProvider:
    """Genblaze image generation adapter using the official Pipeline API."""

    api_key: str
    image_model: str
    base_url: str = ""
    aspect_ratio: str = "16:9"
    timeout_seconds: int = 180
    provider: str = "genblaze"

    @property
    def model(self) -> str:
        return self.image_model

    @classmethod
    def from_settings(cls, settings: Settings) -> "GenblazeMediaProvider":
        settings.require_genblaze()
        return cls(
            api_key=settings.genblaze_api_key or settings.gmi_api_key,
            image_model=settings.genblaze_image_model,
            base_url=settings.genblaze_base_url,
            aspect_ratio=settings.genblaze_aspect_ratio,
            timeout_seconds=settings.genblaze_timeout_seconds,
        )

    def generate(self, campaign: Campaign, count: int = 3) -> list[GeneratedMedia]:
        try:
            from genblaze_core import Modality, Pipeline  # type: ignore[import-not-found]
            from genblaze_gmicloud import GMICloudImageProvider  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise ConfigurationError(
                "Genblaze generation requires the official Genblaze packages. "
                "Install with `pip install -e '.[integrations]'` and configure a live provider."
            ) from exc

        generated: list[GeneratedMedia] = []
        for index in range(1, count + 1):
            prompt = build_campaign_prompt(campaign, index)
            provider = GMICloudImageProvider(
                api_key=self.api_key,
                base_url=self.base_url or None,
                http_timeout=float(self.timeout_seconds),
            )
            try:
                result = (
                    Pipeline("proofframe-image", project_id=campaign.id)
                    .step(
                        provider,
                        model=self.image_model,
                        prompt=prompt,
                        modality=Modality.IMAGE,
                        aspect_ratio=self.aspect_ratio,
                    )
                    .run(
                        timeout=self.timeout_seconds,
                        max_retries=1,
                        raise_on_failure=True,
                    )
                )
            except Exception as exc:
                raise ConfigurationError(f"Genblaze generation failed: {exc}") from exc
            finally:
                close = getattr(provider, "close", None)
                if callable(close):
                    close()

            run = getattr(result, "run", None)
            manifest = getattr(result, "manifest", None)
            if run is None or manifest is None:
                run, manifest = result
            step = run.steps[0]
            if not step.assets:
                raise ConfigurationError("Genblaze generation completed without an image asset.")

            asset = step.assets[0]
            data, content_type, filename = self._fetch_asset(asset.url, campaign.id, index)
            generated.append(
                GeneratedMedia(
                    prompt=prompt,
                    provider=f"{self.provider}/gmicloud-image",
                    model=self.image_model,
                    filename=filename,
                    content_type=content_type or asset.media_type or "image/png",
                    data=data,
                    generation_metadata={
                        "genblaze_run_id": str(run.run_id),
                        "genblaze_manifest_hash": str(manifest.canonical_hash),
                        "genblaze_manifest_verified": str(manifest.verify()),
                        "genblaze_step_status": str(step.status),
                        "genblaze_asset_host": urlparse(asset.url).netloc or "local",
                        "genblaze_asset_sha256": str(asset.sha256 or ""),
                    },
                )
            )
        return generated

    @staticmethod
    def _fetch_asset(asset_url: str, campaign_id: str, index: int) -> tuple[bytes, str, str]:
        parsed = urlparse(asset_url)
        if parsed.scheme in {"http", "https"}:
            with urlopen(asset_url, timeout=60) as response:
                data = response.read()
                content_type = response.headers.get_content_type()
        else:
            path = Path(parsed.path if parsed.scheme == "file" else asset_url)
            data = path.read_bytes()
            content_type = mimetypes.guess_type(path.name)[0] or "image/png"

        extension = mimetypes.guess_extension(content_type) or ".png"
        return data, content_type, f"{campaign_id}-genblaze-{index}{extension}"


def create_media_provider(settings: Settings) -> MediaProvider:
    if settings.generation_backend == "mock":
        return MockMediaProvider()
    if settings.generation_backend == "genblaze":
        return GenblazeMediaProvider.from_settings(settings)
    raise ConfigurationError(f"Unknown generation backend: {settings.generation_backend}")
