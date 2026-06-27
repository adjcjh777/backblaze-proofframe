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
