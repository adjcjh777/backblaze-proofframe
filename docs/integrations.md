# Integration Readiness

## Current Truth

- Local demo path: implemented and tested.
- B2 code path: implemented as an S3-compatible backend with fake-client tests.
- B2 live proof: not complete until a dedicated Backblaze bucket and least-privilege key are configured and one media object plus one manifest are uploaded.
- Genblaze code path: implemented as a fail-closed integration boundary.
- Genblaze live proof: not complete until official Genblaze packages/provider credentials generate media or orchestrate a provider route and the manifest records the provider/model metadata.

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
GENBLAZE_BASE_URL=http://localhost:8800/v1
GENBLAZE_API_KEY=
GENBLAZE_IMAGE_MODEL=
```

Accepted alias:

- `GMI_API_KEY` can satisfy the API-key presence check when using the GMI Cloud-backed Genblaze path.

## Claim Rules

- Until live B2 proof exists, public copy must say "B2-compatible backend implemented" or "B2 integration pending verification", not "stored in Backblaze B2".
- Until live Genblaze proof exists, public copy must say "Genblaze boundary implemented" or "Genblaze route pending verification", not "generated through Genblaze".
- After proof exists, add evidence paths, sanitized object keys, model/provider names, and screenshots to the final submission package.
