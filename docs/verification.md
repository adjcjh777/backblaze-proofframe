# Verification Runbook

Use this runbook before recording the final demo and again before Devpost submission.

## Local Checks

```bash
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,integrations]"
python scripts/check_integrations.py
ruff check .
pytest
python scripts/secret_scan.py
```

## Local App Smoke

In one terminal:

```bash
. .venv/bin/activate
uvicorn proofframe.app:app --host 127.0.0.1 --port 8088
```

In another terminal:

```bash
. .venv/bin/activate
python scripts/api_smoke.py --base-url http://127.0.0.1:8088
```

The JSON output should include `ok: true`, one generated asset checksum, and one exported manifest checksum.

## Docker Smoke

```bash
docker build -t proofframe:local .
docker run --rm -p 8089:8088 proofframe:local
python3 scripts/api_smoke.py --base-url http://127.0.0.1:8089
```

The Docker image installs integration packages so the same image can be run with B2 and Genblaze environment variables for final proof.

## B2 Live Proof

Required environment:

```bash
PROOFFRAME_STORAGE_BACKEND=b2
B2_ENDPOINT_URL=
B2_BUCKET=
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_PUBLIC_BASE_URL=
```

Run:

```bash
. .venv/bin/activate
python scripts/check_integrations.py
uvicorn proofframe.app:app --host 127.0.0.1 --port 8088
python scripts/api_smoke.py --base-url http://127.0.0.1:8088
```

Evidence to save after T020:

- sanitized B2 object key for the generated asset
- sanitized B2 object key for the manifest
- asset checksum
- manifest checksum
- no raw keys, cookies, signed URLs, or private account ids

## Genblaze Live Proof

Required environment:

```bash
PROOFFRAME_GENERATION_BACKEND=genblaze
GMI_API_KEY=
GENBLAZE_IMAGE_MODEL=seedream-5.0-lite
GENBLAZE_ASPECT_RATIO=16:9
GENBLAZE_TIMEOUT_SECONDS=180
```

Run the same app smoke command. Evidence to save after T021:

- provider `genblaze/gmicloud-image`
- model name
- Genblaze run id
- Genblaze manifest hash
- ProofFrame asset checksum
- no provider key or raw temporary provider URL

## Final Submission Gate

Before Devpost submit:

```bash
python scripts/secret_scan.py
python scripts/task.py list --status doing
python scripts/task.py list --status blocked
python scripts/task.py list --status todo
git status --short --branch
```

Final submission remains blocked until T020, T021, T040, T041, T041A, and T042 are complete.
