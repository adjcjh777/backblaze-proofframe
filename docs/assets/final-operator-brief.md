# ProofFrame Final Operator Brief

Mode: `needs_operator_setup`
Ready for secret entry: `false`
Ready for Genblaze live proof: `false`
Safe to submit: `false`

## Current Blockers

- T020: `done`
- T021: `done`
- T040: `done`
- T041: `blocked`
- T041A: `blocked`
- T042: `blocked`

## Credential Handoff

- Source: `.env.final.local`
- Mode: `live_env_ready`
- Missing ids: `none`
- Missing only expected secrets: `false`

## B2 Setup

- status: `bucket_created_key_pending`
- bucket_name: `proofframe-demo-a6b4e49`
- endpoint: `s3.us-west-004.backblazeb2.com`
- bucket_type: `private`
- prepared_application_key_name: `proofframe-demo-live-proof`
- application_key_status: `form_prepared_not_created`

## User Actions

- Run `python scripts/live_env_handoff.py --env-file .env.final.local --strict` and confirm it reports no missing ids.
- Run the post-credential live proof runner once; it validates B2-only and final evidence before any task updates.
- Record and upload the public demo video only after live proof evidence exists.
- Run final secret scan and final submission audit, submit Devpost, then generate the public Devpost submission receipt.

## Codex Actions After Credentials

```bash
python scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks
python scripts/public_space_upload.py --execute --commit-message "Sync ProofFrame public Space after live proof"
python scripts/public_space_sync.py --wait-attempts 5 --wait-seconds 30
python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space
python scripts/demo_storyboard.py --strict-final
python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final
python scripts/demo_readiness.py --strict-final
python scripts/recording_assets.py --verify-public --strict-final
python scripts/secret_scan.py
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"
python scripts/devpost_form_kit.py --strict-final
python scripts/devpost_submission_checklist.py --strict-final
python scripts/submission_audit.py --strict-final
python scripts/devpost_submission_preview.py
python scripts/secret_scan.py
python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."
python scripts/secret_scan.py
python scripts/final_submission_control.py --strict-final
python scripts/final_launch_plan.py --strict-final
python scripts/devpost_submission_preview.py --strict-final
python scripts/submission_bundle.py --strict-final
python scripts/public_space_upload.py --execute --commit-message "Sync ProofFrame public Space after final receipt"
python scripts/public_space_sync.py --wait-attempts 5 --wait-seconds 30
python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space
```

## Safety Policy

- `.env.final.local` ignored: `true`
- Never commit:
  - .env.final.local
  - Backblaze key IDs or application keys
  - Genblaze provider keys
  - Devpost cookies or browser session files
  - raw signed URLs or provider temporary URLs
  - screen recordings that visibly expose secrets
- Safe to commit only after scan:
  - `docs/assets/b2-live-proof-evidence.json`
  - `docs/assets/final-live-proof-evidence.json`
  - `docs/assets/public-video-check.json`
  - `docs/assets/devpost-submission-packet.json`
  - `docs/assets/devpost-form-kit.json`
  - `docs/assets/devpost-submission-preview.json`
  - `docs/assets/devpost-submission-checklist.json`
  - `docs/assets/submission-bundle-manifest.json`

## Claim Boundary

Do not claim completed B2 or Genblaze proof until sanitized live evidence is generated and final gates pass.
