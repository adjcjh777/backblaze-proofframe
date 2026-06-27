"""In-memory repository for the first MVP."""

from __future__ import annotations

from .models import Asset, Campaign


class MemoryRepository:
    def __init__(self) -> None:
        self.campaigns: dict[str, Campaign] = {}
        self.assets: dict[str, Asset] = {}

    def add_campaign(self, campaign: Campaign) -> Campaign:
        self.campaigns[campaign.id] = campaign
        return campaign

    def list_campaigns(self) -> list[Campaign]:
        return sorted(self.campaigns.values(), key=lambda item: item.created_at, reverse=True)

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        return self.campaigns.get(campaign_id)

    def add_asset(self, asset: Asset) -> Asset:
        self.assets[asset.id] = asset
        return asset

    def get_asset(self, asset_id: str) -> Asset | None:
        return self.assets.get(asset_id)

    def list_assets(self, campaign_id: str) -> list[Asset]:
        assets = [asset for asset in self.assets.values() if asset.campaign_id == campaign_id]
        return sorted(assets, key=lambda item: item.created_at)

