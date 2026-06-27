# Integration Readiness

## Current Truth

- Local demo path: implemented and tested.
- B2 code path: implemented as an S3-compatible backend with fake-client tests.
- B2 live proof: not complete until a dedicated Backblaze bucket and least-privilege key are configured and one media object plus one manifest are uploaded.
- Genblaze code path: implemented with the official Genblaze `Pipeline` API and `GMICloudImageProvider`.
- Genblaze live proof: not complete until official Genblaze packages/provider credentials generate media and the manifest records provider/model/run metadata.

## Readiness Command

```bash
. .venv/bin/activate
python scripts/check_integrations.py
```

This command reports booleans only and does not print secrets.

## Live Proof Gate

When B2 and Genblaze credentials are available, first run the preflight without printing secret values:

```bash
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/live_proof.py --preflight-only
python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only
```

Use `.env.final.example` as the copy source for `.env.final.local`. The handoff report records only variable names, presence, expected modes, and next commands; it never prints, hashes, stores, or commits credential values.

Then use the one-command runner:

```bash
python scripts/run_final_live_proof.py \
  --env-file .env.final.local \
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
B2_PUBLIC_BASE_URL=
```

## Genblaze Environment

Required for `PROOFFRAME_GENERATION_BACKEND=genblaze`:

```bash
PROOFFRAME_GENERATION_BACKEND=genblaze
GENBLAZE_BASE_URL=
GENBLAZE_API_KEY=
GENBLAZE_IMAGE_MODEL=
GENBLAZE_ASPECT_RATIO=16:9
GENBLAZE_TIMEOUT_SECONDS=180
```

Accepted alias:

- `GMI_API_KEY` can satisfy the API-key presence check when using the GMI Cloud-backed Genblaze path.
- `GMI_BASE_URL` can satisfy `GENBLAZE_BASE_URL` when an override is required.

Leave `GENBLAZE_BASE_URL` blank for the official GMICloud default. Set it only for a custom request-queue endpoint.

## Claim Rules

- Until live B2 proof exists, public copy must say "B2-compatible backend implemented" or "B2 integration pending verification", not "stored in Backblaze B2".
- Until live Genblaze proof exists, public copy must say "Genblaze provider path implemented" or "Genblaze route pending verification", not "generated through Genblaze".
- After proof exists, add evidence paths, sanitized object keys, model/provider names, and screenshots to the final submission package.
