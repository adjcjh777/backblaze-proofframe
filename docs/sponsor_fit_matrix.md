# ProofFrame Sponsor Fit Matrix

This matrix keeps the Backblaze B2 and Genblaze story central without claiming live proof before the final evidence exists.

| Official judging angle | ProofFrame evidence | Current safe claim | Final live gate | Demo shot |
| --- | --- | --- | --- | --- |
| Working generative media application | `apps/web/index.html`, `/api/demo/judge-packet`, public Space judge mode | ProofFrame is a working local/mock product for reviewing generated media packets. | T021 verifies the generation path with Genblaze-backed provider metadata. | Product hook and Generate variants |
| Meaningful Backblaze B2 use | `src/proofframe/storage.py`, `docs/assets/b2-live-setup.json`, `scripts/run_b2_live_proof.py` | The storage model is B2-shaped today: manifest fields include storage backend, storage key, checksum, byte size, and review state; a private B2 bucket is prepared; live upload is the final gate. | T020 uploads one asset and one manifest to the dedicated B2 bucket and records sanitized keys and checksums. | Sponsor evidence model, Manifest preview, Export packet |
| Meaningful Genblaze use | `src/proofframe/providers.py`, `scripts/run_final_live_proof.py`, `.env.final.example` | The provider adapter uses the official Genblaze Pipeline API shape; public demo uses mock generation until credentials are present. | T021 captures provider/model/run metadata from a live Genblaze-compatible generation. | Generate variants and final live proof terminal cut |
| Durable media and metadata management | `CampaignManifest`, downloadable ZIP, review console, safe summary copy | ProofFrame treats the useful unit as an evidence packet: media, prompt, provider/model, storage reference, checksum, approval state, and risk note. | Final evidence confirms the same packet flow with B2 plus Genblaze. | Review and approve, Manifest preview |
| Production-minded trust and safety | `scripts/secret_scan.py`, `scripts/claim_lint.py`, `scripts/api_smoke.py`, `docs/public_claim_freeze.md` | Public claims stay in pre-live-safe mode and generated evidence refuses secret-like values or signed URLs. | T041A final secret scan and T041 final submission audit pass after live artifacts are generated. | Close and gate status |
| Judge-friendly submission | `docs/assets/devpost-form-kit.md`, `docs/assets/submission-bundle-manifest.md`, `docs/assets/demo-storyboard.md` | Devpost copy, demo URL, screenshots, storyboard, and evidence package are ready for the mock public demo. | T042 submits the Devpost project after final proof and audit. | Close |

## Claim Boundary

Safe before T020/T021:

- "ProofFrame has a B2-compatible storage backend and a prepared live proof runner."
- "ProofFrame records B2-ready object metadata fields in the manifest."
- "The public demo uses local/mock mode while final B2 and Genblaze proof remains gated."

Unsafe before T020/T021:

- "ProofFrame stores generated media in Backblaze B2."
- "ProofFrame generates media through Genblaze."
- "Every asset is B2-backed."

Safe after T020/T021 and final evidence:

- "ProofFrame stores media and manifests through Backblaze B2."
- "ProofFrame generates media through Genblaze/GMICloud and records provider/model metadata."
