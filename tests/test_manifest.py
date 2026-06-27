from proofframe.models import Campaign, CampaignManifest
from proofframe.providers import MockMediaProvider
from proofframe.storage import LocalStorageBackend


def test_mock_generation_and_manifest(tmp_path):
    campaign = Campaign(
        title="Tiny Museum Launch",
        brief="Announce a neighborhood museum opening with warm public-service energy.",
        audience="local families",
        tone="editorial",
    )
    provider = MockMediaProvider()
    storage = LocalStorageBackend(tmp_path)

    media = provider.generate(campaign, count=2)
    assert len(media) == 2
    assert media[0].data == provider.generate(campaign, count=1)[0].data

    stored = storage.put_media(campaign.id, media[0])
    assert stored.storage_backend == "local"
    assert stored.sha256
    assert (tmp_path / stored.storage_key).exists()

    manifest = CampaignManifest(campaign=campaign, assets=[])
    assert manifest.manifest_version == "proofframe.v1"

