# ProofFrame Live Credential Handoff

Mode: `missing_live_env`
Ready for live proof: `false`
Source: `.env.final.local`

This report records only variable names and presence checks. It never prints, hashes, stores, or commits credential values.

## Required Values

- OK ProofFrame storage backend mode: `PROOFFRAME_STORAGE_BACKEND`; present `PROOFFRAME_STORAGE_BACKEND`; expected `b2`.
- OK ProofFrame generation backend mode: `PROOFFRAME_GENERATION_BACKEND`; present `PROOFFRAME_GENERATION_BACKEND`; expected `genblaze`.
- OK Backblaze B2 S3 endpoint: `B2_ENDPOINT_URL`, `B2_S3_ENDPOINT_URL`; present `B2_ENDPOINT_URL`.
- OK Backblaze B2 bucket: `B2_BUCKET`; present `B2_BUCKET`.
- MISSING Backblaze B2 key id: `B2_KEY_ID`; present none.
  Remediation: Set B2_KEY_ID for a least-privilege application key.
- MISSING Backblaze B2 application key: `B2_APPLICATION_KEY`, `B2_APP_KEY`; present none.
  Remediation: Set B2_APPLICATION_KEY or B2_APP_KEY.
- MISSING Genblaze/GMI API key: `GENBLAZE_API_KEY`, `GMI_API_KEY`; present none.
  Remediation: Set GENBLAZE_API_KEY or GMI_API_KEY.
- OK Genblaze image model: `GENBLAZE_IMAGE_MODEL`; present `GENBLAZE_IMAGE_MODEL`.

## Optional Values

- UNSET B2 public base URL: `B2_PUBLIC_BASE_URL`; present none.
- SET Genblaze aspect ratio: `GENBLAZE_ASPECT_RATIO`; present `GENBLAZE_ASPECT_RATIO`.
- SET Genblaze timeout seconds: `GENBLAZE_TIMEOUT_SECONDS`; present `GENBLAZE_TIMEOUT_SECONDS`.

## Next Commands

```bash
python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local
```
```bash
python scripts/final_env_wizard.py --output .env.final.local
```
```bash
set -a; source .env.final.local; set +a
```
```bash
python scripts/live_env_handoff.py --env-file .env.final.local
```
```bash
python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only
```
```bash
python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json
```
```bash
python scripts/devpost_packet.py --post-live --video-url <public video URL>
```
```bash
python scripts/secret_scan.py
```
```bash
python scripts/claim_lint.py
```
```bash
python scripts/submission_audit.py --strict-final
```
