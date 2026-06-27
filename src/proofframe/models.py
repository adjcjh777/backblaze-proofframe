"""Domain models for ProofFrame."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


class AssetStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"


class CampaignCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    brief: str = Field(min_length=1, max_length=2000)
    audience: str = Field(default="general audience", max_length=240)
    tone: str = Field(default="clear and trustworthy", max_length=160)


class Campaign(CampaignCreate):
    id: str = Field(default_factory=lambda: f"cmp_{uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=utc_now)


class GeneratedMedia(BaseModel):
    kind: Literal["image"] = "image"
    prompt: str
    provider: str
    model: str
    filename: str
    content_type: str
    data: bytes
    generation_metadata: dict[str, str] = Field(default_factory=dict)


class StoredObject(BaseModel):
    storage_backend: str
    storage_key: str
    public_url: str | None = None
    sha256: str
    bytes_size: int


class Asset(BaseModel):
    id: str = Field(default_factory=lambda: f"ast_{uuid4().hex[:12]}")
    campaign_id: str
    kind: Literal["image"] = "image"
    status: AssetStatus = AssetStatus.draft
    prompt: str
    provider: str
    model: str
    storage_backend: str
    storage_key: str
    public_url: str | None = None
    sha256: str
    bytes_size: int
    generation_metadata: dict[str, str] = Field(default_factory=dict)
    risk_note: str = "Draft asset. Review provenance, rights, and brand fit before publishing."
    created_at: datetime = Field(default_factory=utc_now)


class AssetStatusUpdate(BaseModel):
    status: AssetStatus
    risk_note: str | None = Field(default=None, max_length=500)


class CampaignManifest(BaseModel):
    manifest_version: str = "proofframe.v1"
    campaign: Campaign
    assets: list[Asset]
    exported_at: datetime = Field(default_factory=utc_now)
    app_version: str = "0.1.0"
