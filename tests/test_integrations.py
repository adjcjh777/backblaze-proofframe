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


def test_openai_genblaze_provider_fails_closed_without_package(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "genblaze_openai":
            raise ModuleNotFoundError(name)
        return real_import(name, globals, locals, fromlist, level)

    provider = GenblazeMediaProvider(
        api_key="test-key",
        image_model="gpt-image-1",
        genblaze_provider="openai",
    )
    campaign = Campaign(title="Launch", brief="Generate one safe image.")

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ConfigurationError, match="GENBLAZE_PROVIDER=openai requires"):
        provider.generate(campaign)


def test_genblaze_settings_parse_official_defaults():
    settings = Settings.from_env(
        {
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "PROOFFRAME_STORAGE_BACKEND": "b2",
            "B2_ENDPOINT_URL": "https://s3.us-west-004.backblazeb2.com",
            "B2_BUCKET": "proof-bucket",
            "B2_KEY_ID": "key-id",
            "B2_APPLICATION_KEY": "application-key",
            "GMI_API_KEY": "test-key",
            "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
            "GENBLAZE_TIMEOUT_SECONDS": "240",
        }
    )
    assert settings.genblaze_base_url == ""
    assert settings.genblaze_aspect_ratio == "16:9"
    assert settings.genblaze_timeout_seconds == 240
    assert settings.b2_region_for_backblaze() == "us-west-004"

    provider = create_media_provider(settings)

    assert isinstance(provider, GenblazeMediaProvider)
    assert provider.b2_sink_enabled is True
    assert provider.b2_region == "us-west-004"


def test_genblaze_settings_parse_openai_provider():
    settings = Settings.from_env(
        {
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "GENBLAZE_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "GENBLAZE_IMAGE_MODEL": "gpt-image-1",
        }
    )

    assert settings.genblaze_provider == "openai"
    assert settings.genblaze_provider_key() == "test-key"

    provider = create_media_provider(settings)

    assert isinstance(provider, GenblazeMediaProvider)
    assert provider.genblaze_provider == "openai"
    assert provider.api_key == "test-key"


def test_openai_provider_does_not_accept_non_openai_aliases_as_key():
    settings = Settings.from_env(
        {
            "PROOFFRAME_GENERATION_BACKEND": "genblaze",
            "GENBLAZE_PROVIDER": "openai",
            "GENBLAZE_API_KEY": "wrong-provider-key",
            "GMI_API_KEY": "wrong-provider-key",
            "GENBLAZE_IMAGE_MODEL": "gpt-image-1",
        }
    )

    assert settings.genblaze_provider_key() == ""
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        create_media_provider(settings)


def test_genblaze_b2_sink_builds_from_official_packages_without_network():
    provider = GenblazeMediaProvider(
        api_key="test-key",
        image_model="seedream-5.0-lite",
        b2_sink_enabled=True,
        b2_bucket="proof-bucket",
        b2_key_id="key-id",
        b2_application_key="application-key",
        b2_region="us-west-004",
    )

    sink, read_backend = provider._build_genblaze_b2_sink("cmp_test", preflight=False)

    assert sink is not None
    assert read_backend is not None
    provider._close_if_possible(read_backend)
    provider._close_if_possible(sink)


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


def test_genblaze_fetch_asset_uses_b2_backend_for_private_sink_url():
    class FakeReadBackend:
        def __init__(self):
            self.keys = []

        def key_from_url(self, url):
            assert url == "https://s3.us-west-004.backblazeb2.com/proof-bucket/genblaze/a.png"
            return "genblaze/a.png"

        def get(self, key):
            self.keys.append(key)
            return b"private-b2-image"

    backend = FakeReadBackend()

    data, content_type, filename = GenblazeMediaProvider._fetch_asset(
        "https://s3.us-west-004.backblazeb2.com/proof-bucket/genblaze/a.png",
        "cmp_test",
        3,
        storage_backend=backend,
    )

    assert data == b"private-b2-image"
    assert content_type == "image/png"
    assert filename == "cmp_test-genblaze-3.png"
    assert backend.keys == ["genblaze/a.png"]


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


def test_b2_backend_normalizes_endpoint_without_scheme():
    backend = B2StorageBackend(
        endpoint_url="s3.us-west-004.backblazeb2.com",
        bucket="proof-bucket",
        key_id="key-id",
        application_key="application-key",
        client=FakeS3Client(),
    )

    assert backend.endpoint_url == "https://s3.us-west-004.backblazeb2.com"
