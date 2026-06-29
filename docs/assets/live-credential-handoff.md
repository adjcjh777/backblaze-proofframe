# ProofFrame Live Credential Handoff

Mode: `missing_live_env`
Ready for live proof: `false`
Source: `process environment`

This report records only variable names and presence checks. It never prints, hashes, stores, or commits credential values.

## Required Values

- MISSING ProofFrame storage backend mode: `PROOFFRAME_STORAGE_BACKEND`; present none; expected `b2`.
  Remediation: Set PROOFFRAME_STORAGE_BACKEND=b2.
- MISSING ProofFrame generation backend mode: `PROOFFRAME_GENERATION_BACKEND`; present none; expected `genblaze`.
  Remediation: Set PROOFFRAME_GENERATION_BACKEND=genblaze.
- MISSING Backblaze B2 S3 endpoint: `B2_ENDPOINT_URL`, `B2_S3_ENDPOINT_URL`; present none.
  Remediation: Set B2_ENDPOINT_URL from the Backblaze bucket S3 endpoint.
- MISSING Backblaze B2 bucket: `B2_BUCKET`; present none.
  Remediation: Set B2_BUCKET to the dedicated demo bucket name.
- MISSING Backblaze B2 key id: `B2_KEY_ID`; present none.
  Remediation: Set B2_KEY_ID for a least-privilege application key.
- MISSING Backblaze B2 application key: `B2_APPLICATION_KEY`, `B2_APP_KEY`; present none.
  Remediation: Set B2_APPLICATION_KEY or B2_APP_KEY.
- MISSING Genblaze/GMI API key: `GENBLAZE_API_KEY`, `GMI_API_KEY`; present none.
  Remediation: Set GENBLAZE_API_KEY or GMI_API_KEY.
- MISSING Genblaze image model: `GENBLAZE_IMAGE_MODEL`; present none.
  Remediation: Set GENBLAZE_IMAGE_MODEL to the verified image model.

## Optional Values

- UNSET B2 public base URL: `B2_PUBLIC_BASE_URL`; present none.
- UNSET B2 region for Genblaze sink: `B2_REGION`; present none.
- UNSET Genblaze aspect ratio: `GENBLAZE_ASPECT_RATIO`; present none.
- UNSET Genblaze timeout seconds: `GENBLAZE_TIMEOUT_SECONDS`; present none.

## Next Commands

```bash
python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local
```
```bash
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
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
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"
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
