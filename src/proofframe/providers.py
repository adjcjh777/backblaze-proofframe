"""Media generation providers."""

from __future__ import annotations

import html
from dataclasses import dataclass

from .checksum import sha256_hex
from .models import Campaign, GeneratedMedia


@dataclass(frozen=True)
class MockMediaProvider:
    """Deterministic media provider for tests and credential-free demos."""

    model: str = "mock-svg-v1"
    provider: str = "mock"

    def generate(self, campaign: Campaign, count: int = 3) -> list[GeneratedMedia]:
        return [self._generate_one(campaign, index) for index in range(1, count + 1)]

    def _generate_one(self, campaign: Campaign, index: int) -> GeneratedMedia:
        prompt = (
            f"Create a {campaign.tone} campaign image for {campaign.audience}. "
            f"Brief: {campaign.brief}. Variant {index}."
        )
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
        )

