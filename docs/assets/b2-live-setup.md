# ProofFrame B2 Live Setup

Status: `bucket_created_key_pending`

The Backblaze account is registered and the private B2 bucket for the final live proof has been created.

## Non-Secret Values

- Bucket: `proofframe-demo-a6b4e49`
- Type: `private`
- Endpoint: `s3.us-west-004.backblazeb2.com`
- Prepared application key name: `proofframe-demo-live-proof`
- Application key status: `form_prepared_not_created`

## Secret Policy

This file intentionally excludes key IDs, application keys, cookies, hidden form tokens, signed URLs, account billing details, and provider secrets.

## Next Step

Create the scoped application key only after user confirmation, then write it to the local git-ignored `.env.final.local` file and run:

```bash
python scripts/run_b2_live_proof.py --env-file .env.final.local \
  --evidence-out docs/assets/b2-live-proof-evidence.json
```
