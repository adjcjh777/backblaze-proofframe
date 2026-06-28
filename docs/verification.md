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
python scripts/final_env_wizard.py --check-only
python scripts/b2_key_scope_checklist.py
python scripts/devpost_form_kit.py
python scripts/devpost_submission_checklist.py
python scripts/judge_brief.py
python scripts/judge_crosswalk.py
python scripts/devpost_event_snapshot.py --validate-committed
python scripts/agent_handoff_check.py
python scripts/public_space_sync.py
python scripts/demo_storyboard.py
python scripts/demo_video_draft.py
python scripts/public_video_check.py
python scripts/sponsor_fit_audit.py
python scripts/demo_readiness.py
python scripts/recording_assets.py
python scripts/award_readiness.py --min-score 75
python scripts/final_submission_control.py
python scripts/final_operator_brief.py
python scripts/final_launch_plan.py
python scripts/submission_audit.py
python scripts/devpost_submission_receipt.py
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
- `python scripts/final_env_wizard.py --check-only`
- `python scripts/b2_key_scope_checklist.py`
- `python scripts/devpost_form_kit.py`
- `python scripts/devpost_submission_checklist.py`
- `python scripts/judge_brief.py`
- `python scripts/judge_crosswalk.py`
- `python scripts/devpost_event_snapshot.py --validate-committed`
- `python scripts/agent_handoff_check.py`
- `python scripts/public_space_sync.py`
- `python scripts/demo_storyboard.py`
- `python scripts/demo_video_draft.py`
- `python scripts/public_video_check.py`
- `python scripts/sponsor_fit_audit.py`
- `python scripts/demo_readiness.py`
- `python scripts/recording_assets.py`
- `python scripts/award_readiness.py --min-score 75`
- `python scripts/final_submission_control.py`
- `python scripts/final_operator_brief.py`
- `python scripts/final_launch_plan.py`
- `python scripts/submission_audit.py`
- `python scripts/devpost_submission_receipt.py`
- `python scripts/submission_bundle.py`

Use the CI result as public repo evidence for the non-secret local gate. It does not replace T020/T021 live sponsor proof because those require private credentials.

Evidence files written by `scripts/api_smoke.py --evidence-out` are checked before writing and fail closed if they contain secret-like field names, bearer tokens, signed URL parameters, or GMI-style key values.

The final sponsor proof has a preflight wrapper:

```bash
. .venv/bin/activate
python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local
python scripts/b2_key_scope_checklist.py
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/post_credential_live_proof.py
python scripts/live_proof.py --preflight-only
python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only
```

When B2 and Genblaze env/packages are complete, use the post-credential runner:

```bash
. .venv/bin/activate
python scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks
```

The runner first runs the B2-only proof with mock generation, validates `docs/assets/b2-live-proof-evidence.json`, and only then marks T020 when `--update-tasks` is set. It then runs the final B2 plus Genblaze proof, validates `docs/assets/final-live-proof-evidence.json`, and only then marks T021. Both validators require the expected backend/provider fields, nonempty checksum/object-key fields, and no secret-like keys, bearer tokens, signed URL parameters, or GMI-style key values. Server logs stay under `var/live-proof/`, which is ignored by git.

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

The default Docker image is optimized for the credential-free public mock demo and installs the core app only. For a B2/Genblaze-capable image, build with:

```bash
docker build --build-arg INSTALL_EXTRAS=integrations -t proofframe:integrations .
```

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
python scripts/run_b2_live_proof.py --env-file .env.final.local --preflight-only
uvicorn proofframe.app:app --host 127.0.0.1 --port 8088
python scripts/live_proof.py \
  --base-url http://127.0.0.1:8088 \
  --require-storage-backend b2 \
  --require-generation-backend mock \
  --evidence-out docs/assets/b2-live-proof-evidence.json
```

Fallback command:

```bash
python scripts/run_b2_live_proof.py --env-file .env.final.local \
  --evidence-out docs/assets/b2-live-proof-evidence.json
```

Fallback against an already running app:

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
python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local
python scripts/b2_key_scope_checklist.py
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks
python scripts/agent_handoff_check.py --check-bus
python scripts/public_space_sync.py
python scripts/devpost_event_snapshot.py --fetch-live
export PROOFFRAME_PUBLIC_VIDEO_URL="https://..."
python scripts/demo_storyboard.py --strict-final
python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final
python scripts/demo_readiness.py --strict-final
python scripts/recording_assets.py --verify-public --strict-final
python scripts/secret_scan.py
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"
python scripts/devpost_form_kit.py --strict-final
python scripts/devpost_submission_checklist.py --strict-final
python scripts/judge_brief.py
python scripts/judge_crosswalk.py
python scripts/submission_bundle.py
python scripts/final_operator_brief.py
python scripts/final_launch_plan.py
python scripts/final_submission_control.py --strict-final
python scripts/submission_audit.py --strict-final
# After Devpost accepts the project:
export PROOFFRAME_DEVPOST_PROJECT_URL="https://devpost.com/software/..."
export PROOFFRAME_DEVPOST_SUBMITTED_AT="2026-08-03T21:00:00Z"
python scripts/devpost_submission_receipt.py \
  --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" \
  --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" \
  --confirmation-note "Devpost accepted/submitted the ProofFrame project."
python scripts/task.py list --status doing
python scripts/task.py list --status blocked
python scripts/task.py list --status todo
git status --short --branch
```

Final submission remains blocked until T020, T021, T040, T041, T041A, and T042 are complete.
