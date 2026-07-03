# ProofFrame Sponsor Fit Matrix

This matrix keeps the Backblaze B2 and Genblaze story central without claiming live proof before the final evidence exists.

| Official judging angle / requirement | ProofFrame evidence | Current safe claim | Final live gate | Demo shot |
| --- | --- | --- | --- | --- |
| Real-world Utility | `docs/prd.md`, `apps/web/index.html`, review console, downloadable evidence ZIP | ProofFrame solves the post-generation operations problem: teams can inspect, approve, package, and trust generated media instead of treating it as loose files. | Final video must show one creator workflow end to end with live evidence attached. | Product hook, Review and approve |
| Production Readiness | `scripts/secret_scan.py`, `scripts/claim_lint.py`, `scripts/api_smoke.py`, CI, final control report | Public claims stay in pre-live-safe mode, evidence refuses secret-like values, and submission is blocked until proof/video/audit gates pass. | T041A final secret scan and T041 final submission audit pass after live artifacts are generated. | Close and gate status |
| B2 Storage + Data Orchestration | `src/proofframe/storage.py`, `apps/web/index.html`, `docs/assets/b2-live-setup.json`, `scripts/run_b2_live_proof.py` | The storage model is B2-shaped today: manifest fields include storage backend, storage key, checksum, byte size, and review state; a private B2 bucket is prepared; live upload is the final gate. | T020 uploads one asset and one manifest to the dedicated B2 bucket and records sanitized keys and checksums. | Sponsor evidence model, Manifest preview, Export packet |
| Use of Genblaze | `src/proofframe/providers.py`, `apps/web/index.html`, `scripts/run_final_live_proof.py`, `.env.final.example` | The provider adapter uses the official Genblaze Pipeline API shape; public demo uses mock generation until credentials are present. | T021 captures provider/model/run metadata from a live Genblaze-compatible generation. | Sponsor evidence model, Generate variants, final live proof terminal cut |
| Official submission requirements | `docs/assets/devpost-event-snapshot.md`, `docs/assets/devpost-form-kit.md`, `docs/assets/demo-storyboard.md` | Working app URL, GitHub URL, sub-3-minute public video plan, B2 use, and Genblaze use are tracked as explicit gates. | T042 submits the Devpost project after final proof, public video, secret scan, and audit. | Close |

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
- "ProofFrame generates media through Genblaze with the verified provider and records provider/model metadata."
