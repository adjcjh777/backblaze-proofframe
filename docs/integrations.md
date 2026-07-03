# Integration Readiness

## Current Truth

- Local demo path: implemented and tested.
- B2 code path: implemented as an S3-compatible backend with fake-client tests.
- B2 key scope checklist: generated as a no-secret pre-creation gate for the dedicated bucket, `campaigns/` prefix, required upload/S3 compatibility permissions, and forbidden admin/delete permissions.
- B2 live proof: not complete until a dedicated Backblaze bucket and least-privilege key are configured and one media object plus one manifest are uploaded.
- Genblaze code path: implemented with the official Genblaze `Pipeline` API and provider adapters for `GMICloudImageProvider` and OpenAI `DalleProvider`.
- Genblaze+B2 sink path: in final B2 mode, the provider builds an official `ObjectStorageSink` with `S3StorageBackend.for_backblaze`, so Genblaze output and provenance can land in B2 before ProofFrame records its own packet manifest.
- Genblaze SDK contract check: implemented as a no-secret import/signature report so package/API drift is caught before live keys are entered.
- Genblaze live proof: not complete until official Genblaze packages/provider credentials generate media, the B2 sink is active, and the manifest records provider/model/run metadata.

## Readiness Command

```bash
. .venv/bin/activate
python scripts/check_integrations.py
python scripts/genblaze_contract_check.py
```

These commands report booleans, package versions, and callable signatures only. They do not print secrets or read local credential files.

## Live Proof Gate

When B2 and Genblaze credentials are available, first run the preflight without printing secret values:

```bash
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/b2_key_scope_checklist.py
python scripts/genblaze_contract_check.py
python scripts/live_proof.py --preflight-only
python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only
python scripts/run_final_live_proof.py \
  --env-file .env.final.local \
  --genblaze-provider openai \
  --genblaze-image-model gpt-image-1 \
  --preflight-only
```

Use `.env.final.example` as the copy source for `.env.final.local`. The handoff report records only variable names, presence, expected modes, and next commands; it never prints, hashes, stores, or commits credential values.

Then use the one-command runner:

```bash
python scripts/run_final_live_proof.py \
  --env-file .env.final.local \
  --evidence-out docs/assets/final-live-proof-evidence.json
```

If the GMI Cloud path is blocked by provider credits, use the same runner with non-secret OpenAI provider/model overrides after a real `OPENAI_API_KEY` is available in the process environment:

```bash
python scripts/run_final_live_proof.py \
  --env-file .env.final.local \
  --genblaze-provider openai \
  --genblaze-image-model gpt-image-1 \
  --evidence-out docs/assets/final-live-proof-evidence.json
```

The runner starts the app with inherited environment variables, waits until health reports `storage_backend=b2` and `generation_backend=genblaze`, delegates to the safe API smoke test, writes `docs/assets/final-live-proof-evidence.json`, and stops the server. Server logs go to `var/live-proof/uvicorn.log`, which is ignored by git.

If the app is already running with those environment variables, require the expected backends directly:

```bash
python scripts/live_proof.py \
  --base-url http://127.0.0.1:8088 \
  --evidence-out docs/assets/final-live-proof-evidence.json
```

The wrapper checks required backend modes, env presence, integration packages, and then delegates the end-to-end smoke test to `scripts/api_smoke.py`. The evidence JSON is intentionally limited to campaign ids, provider/model names, sanitized storage keys, checksums, byte counts, and backend names. It must not contain raw API keys, cookies, signed URLs, or account dashboards.

During the final B2 plus Genblaze run, ProofFrame enables the Genblaze B2 sink automatically when `PROOFFRAME_STORAGE_BACKEND=b2` and `PROOFFRAME_GENERATION_BACKEND=genblaze`. The app passes B2 bucket, region, key id, application key, and optional public URL base to Genblaze's official B2/S3 storage backend. If the bucket is private, ProofFrame reads the generated object back with a separate authenticated B2 client rather than storing signed URLs in the manifest or smoke evidence.

## B2 Environment

Required for `PROOFFRAME_STORAGE_BACKEND=b2`:

```bash
PROOFFRAME_STORAGE_BACKEND=b2
B2_ENDPOINT_URL=
B2_BUCKET=
B2_KEY_ID=
B2_APPLICATION_KEY=
```

Accepted aliases:

- `B2_S3_ENDPOINT_URL` for `B2_ENDPOINT_URL`
- `B2_APP_KEY` for `B2_APPLICATION_KEY`

Optional:

```bash
B2_REGION=
B2_PUBLIC_BASE_URL=
```

`B2_REGION` can be omitted when `B2_ENDPOINT_URL` is a standard Backblaze S3 endpoint such as `https://s3.us-west-004.backblazeb2.com`; the preflight derives `us-west-004`. Set `B2_REGION` explicitly for unusual endpoint formats.

## Genblaze Environment

Required for `PROOFFRAME_GENERATION_BACKEND=genblaze`:

```bash
PROOFFRAME_GENERATION_BACKEND=genblaze
GENBLAZE_BASE_URL=
GENBLAZE_PROVIDER=gmicloud
GENBLAZE_API_KEY=
GENBLAZE_IMAGE_MODEL=
GENBLAZE_ASPECT_RATIO=16:9
GENBLAZE_TIMEOUT_SECONDS=180
```

Provider selection:

- `GENBLAZE_PROVIDER=gmicloud` uses `genblaze-gmicloud` and accepts `GENBLAZE_API_KEY` or `GMI_API_KEY`.
- `GENBLAZE_PROVIDER=openai` uses `genblaze-openai` and accepts `OPENAI_API_KEY`.
- `GMI_BASE_URL` can satisfy `GENBLAZE_BASE_URL` when an override is required.

Leave `GENBLAZE_BASE_URL` blank for the official GMICloud default. Set it only for a custom GMI request-queue endpoint. The OpenAI provider path uses its provider package defaults.

## Claim Rules

- Until live B2 proof exists, public copy must say "B2-compatible backend implemented" or "B2 integration pending verification", not "stored in Backblaze B2".
- Until live Genblaze proof exists, public copy must say "Genblaze provider path implemented" or "Genblaze route pending verification", not "generated through Genblaze".
- After proof exists, add evidence paths, sanitized object keys, model/provider names, and screenshots to the final submission package.
