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
python scripts/claim_lint.py
python scripts/live_env_handoff.py
python scripts/demo_readiness.py
python scripts/submission_bundle.py
```

## GitHub CI

The `.github/workflows/ci.yml` workflow runs on `main`, `feature/**`, and pull requests:

- install `.[dev,integrations]`
- `python scripts/check_integrations.py`
- `ruff check .`
- `pytest`
- `python scripts/api_smoke.py --base-url http://127.0.0.1:8088`
- `python scripts/secret_scan.py`
- `python scripts/claim_lint.py`
- `python scripts/live_env_handoff.py`
- `python scripts/demo_readiness.py`

Use the CI result as public repo evidence for the non-secret local gate. It does not replace T020/T021 live sponsor proof because those require private credentials.

Evidence files written by `scripts/api_smoke.py --evidence-out` are checked before writing and fail closed if they contain secret-like field names, bearer tokens, signed URL parameters, or GMI-style key values.

The final sponsor proof has a preflight wrapper:

```bash
. .venv/bin/activate
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/live_proof.py --preflight-only
python scripts/run_final_live_proof.py --preflight-only
```

When B2 and Genblaze env/packages are complete, use the one-command runner:

```bash
. .venv/bin/activate
python scripts/run_final_live_proof.py \
  --evidence-out docs/assets/final-live-proof-evidence.json
```

The runner starts a local ProofFrame server with inherited environment variables, waits until `/api/health` reports `storage_backend=b2` and `generation_backend=genblaze`, runs the safe API smoke proof, writes sanitized evidence, and then stops the server. Server logs go to `var/live-proof/uvicorn.log`, which is ignored by git.

If the app is already running with those env vars, use:

```bash
python scripts/live_proof.py \
  --base-url http://127.0.0.1:8088 \
  --evidence-out docs/assets/final-live-proof-evidence.json
```

This wrapper does not print credential values. It checks required modes, env presence, package availability, and then delegates evidence writing to `scripts/api_smoke.py`.

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

The JSON output should include `ok: true`, one generated asset checksum, one exported manifest checksum, nonzero `packet_bytes`, and a `judge_demo_campaign_id`.

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
python scripts/live_proof.py \
  --base-url http://127.0.0.1:8088 \
  --require-storage-backend b2 \
  --require-generation-backend mock \
  --evidence-out docs/assets/b2-live-proof-evidence.json
```

Fallback command:

```bash
python scripts/api_smoke.py \
  --base-url http://127.0.0.1:8088 \
  --require-storage-backend b2 \
  --evidence-out docs/assets/b2-live-proof-evidence.json
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

```bash
python scripts/live_proof.py \
  --base-url http://127.0.0.1:8088 \
  --require-storage-backend local \
  --require-generation-backend genblaze \
  --evidence-out docs/assets/genblaze-live-proof-evidence.json
```

Fallback command:

```bash
python scripts/api_smoke.py \
  --base-url http://127.0.0.1:8088 \
  --require-generation-backend genblaze \
  --evidence-out docs/assets/genblaze-live-proof-evidence.json
```

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
python scripts/claim_lint.py
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/submission_bundle.py
python scripts/run_final_live_proof.py \
  --evidence-out docs/assets/final-live-proof-evidence.json
python scripts/demo_readiness.py --strict-final
python scripts/submission_audit.py
python scripts/task.py list --status doing
python scripts/task.py list --status blocked
python scripts/task.py list --status todo
git status --short --branch
```

Final submission remains blocked until T020, T021, T040, T041, T041A, and T042 are complete.
