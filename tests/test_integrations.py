import builtins

import pytest

from proofframe.config import ConfigurationError, Settings
from proofframe.models import Campaign, CampaignManifest
from proofframe.providers import GenblazeMediaProvider, create_media_provider
from proofframe.storage import B2StorageBackend, create_storage_backend


def test_b2_backend_requires_explicit_config():
    settings = Settings(storage_backend="b2")
    with pytest.raises(ConfigurationError, match="B2 storage was requested"):
        create_storage_backend(settings)


def test_genblaze_backend_requires_explicit_config():
    settings = Settings(generation_backend="genblaze")
    with pytest.raises(ConfigurationError, match="Genblaze generation was requested"):
        create_media_provider(settings)


def test_genblaze_provider_fails_closed_without_package(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"genblaze_core", "genblaze_gmicloud"}:
            raise ModuleNotFoundError(name)
        return real_import(name, globals, locals, fromlist, level)

    provider = GenblazeMediaProvider(
        api_key="test-key",
        image_model="test-model",
        base_url="http://localhost:8800/v1",
    )
    campaign = Campaign(title="Launch", brief="Generate one safe image.")

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ConfigurationError, match="Genblaze generation requires"):
        provider.generate(campaign)


def test_genblaze_settings_parse_official_defaults():
    settings = Settings.from_env(
        {
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "GMI_API_KEY": "test-key",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
            "GENBLAZE_TIMEOUT_SECONDS": "240",
        }
    )
    assert settings.genblaze_base_url == ""
    assert settings.genblaze_aspect_ratio == "16:9"
    assert settings.genblaze_timeout_seconds == 240


def test_genblaze_fetch_asset_from_file_url(tmp_path):
    image_path = tmp_path / "asset.png"
    image_path.write_bytes(b"fake-png")

    data, content_type, filename = GenblazeMediaProvider._fetch_asset(
        image_path.as_uri(),
        "cmp_test",
        2,
    )

    assert data == b"fake-png"
    assert content_type == "image/png"
    assert filename == "cmp_test-genblaze-2.png"


class FakeS3Client:
    def __init__(self):
        self.puts = []

    def put_object(self, **kwargs):
        self.puts.append(kwargs)


def test_b2_backend_puts_media_and_manifest_with_fake_client():
    fake = FakeS3Client()
    backend = B2StorageBackend(
        endpoint_url="https://s3.us-west-004.backblazeb2.com",
        bucket="proof-bucket",
        key_id="key-id",
        application_key="application-key",
        public_base_url="https://cdn.example.test",
        client=fake,
    )
    campaign = Campaign(title="Launch", brief="Generate one safe image.")
    media = create_media_provider(Settings()).generate(campaign, count=1)[0]

    stored_media = backend.put_media(campaign.id, media)
    assert stored_media.storage_backend == "b2"
    assert stored_media.storage_key.startswith(f"campaigns/{campaign.id}/media/")
    assert stored_media.public_url == f"https://cdn.example.test/{stored_media.storage_key}"

    manifest = CampaignManifest(campaign=campaign, assets=[])
    stored_manifest = backend.put_manifest(campaign.id, manifest)
    assert stored_manifest.storage_key == (
        f"campaigns/{campaign.id}/manifests/{campaign.id}-manifest.json"
    )
    assert len(fake.puts) == 2
    assert fake.puts[0]["Bucket"] == "proof-bucket"
    assert fake.puts[0]["Metadata"]["sha256"] == stored_media.sha256
