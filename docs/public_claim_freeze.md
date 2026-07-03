# Public Claim Freeze

Status: active until final submission.

This document controls what ProofFrame can safely say in the README, Devpost submission, demo video, screenshots, and social copy.

## Rule

Use present tense only for behavior that has been verified in the current repo or final deployment. Use "target", "planned", "final gate", or "in progress" for B2 and Genblaze behavior until live evidence exists.

## Verified Claims Allowed Now

- ProofFrame is a provenance-first generative media vault for the Backblaze Generative Media Hackathon.
- The local app provides campaign creation, generated asset review, approval state changes, manifest preview, and manifest export.
- The local demo can run without secrets using a deterministic mock media provider and local storage.
- The app records prompt, provider, model, storage backend, storage key, checksum, risk note, created time, and approval state in exported manifests.
- The Review Console supports evidence search, status filtering, decision coverage, and safe evidence-summary copy in local/mock mode.
- A credential-free public mock demo is deployed at `https://adjcjh-backblaze-proofframe.hf.space/`; the Devpost-friendly judge link is `https://adjcjh-backblaze-proofframe.hf.space/?judge=1`.
- The repo includes a Backblaze B2-compatible storage adapter boundary and tests that exercise the storage contract without real secrets.
- The repo includes Genblaze image provider paths for GMICloud, OpenAI, and a credential-free local Pipeline provider. Final B2 plus local Genblaze Pipeline proof is captured in sanitized evidence; public video, final audit, and Devpost receipt remain gated.
- `scripts/api_smoke.py --evidence-out` refuses to write evidence JSON when secret-like keys, bearer tokens, signed URL parameters, or GMI-style key values are detected.
- The selected UI direction is Proof Ledger.
- The public repo is available at `https://github.com/adjcjh777/backblaze-proofframe`.

## Claims Blocked Until T020

Do not say:

- "ProofFrame stores assets in Backblaze B2."
- "Every asset and manifest is backed by B2."
- "Judges can inspect the live B2 object packet."
- "The final app uses B2 storage end to end."

Allowed replacement before T020:

- "ProofFrame includes a B2-compatible storage adapter and requires one live B2 upload proof before final submission."

Release criteria:

- A dedicated B2 bucket exists.
- One media asset and one manifest are uploaded through the app/storage backend.
- `scripts/check_integrations.py` reports B2 configured and available.
- Sanitized object keys and checksums are captured in `docs/evidence_package.md` or a final evidence appendix.
- No B2 secret appears in repo, logs, screenshots, or manifests.

## Claims Blocked Until T021

Do not say:

- "ProofFrame generates media with Genblaze."
- "This demo uses Genblaze to produce all assets."
- "The manifest records live Genblaze output."

Allowed replacement before T021:

- "ProofFrame includes Genblaze provider paths and final submission requires one live Genblaze-backed generation proof."

Release criteria:

- A live Genblaze-backed run completes.
- Provider, model, request metadata, prompt, checksum, and resulting storage reference appear in the manifest.
- Fallback behavior is documented and fail-closed when required config is missing.
- No provider key or raw request secret appears in repo, logs, screenshots, or manifests.

## README And Devpost Copy Gate

Before recording the final video or submitting Devpost, run:

```bash
python scripts/claim_lint.py
rg -n "stores|stored|Backblaze B2|B2|Genblaze|generates|generated through|end to end|every asset" README.md docs apps src
```

Use `scripts/claim_lint.py` as the fail-closed gate for active public copy. Then manually classify any remaining grep result as:

- verified present-tense claim
- future/target claim
- implementation detail
- unsafe overclaim that must be edited

## Final Release Checklist

- [ ] T020 complete.
- [ ] T021 complete.
- [ ] T041 final submission audit complete.
- [ ] T041A secret scan complete.
- [ ] README checked.
- [ ] Devpost text checked.
- [ ] Demo script checked.
- [ ] Screenshots checked.
- [ ] Exported manifests checked.
