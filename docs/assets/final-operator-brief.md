# ProofFrame Final Operator Brief

Mode: `credential_entry_ready`
Ready for secret entry: `true`
Safe to submit: `false`

## Current Blockers

- T020: `doing`
- T021: `doing`
- T040: `done`
- T041: `todo`
- T041A: `todo`
- T042: `todo`

## Credential Handoff

- Source: `.env.final.local`
- Mode: `missing_live_env`
- Missing ids: `b2_key_id, b2_application_key, genblaze_api_key`
- Missing only expected secrets: `true`

## B2 Setup

- status: `bucket_created_key_pending`
- bucket_name: `proofframe-demo-a6b4e49`
- endpoint: `s3.us-west-004.backblazeb2.com`
- bucket_type: `private`
- prepared_application_key_name: `proofframe-demo-live-proof`
- application_key_status: `form_prepared_not_created`

## User Actions

- Review `docs/assets/b2-key-scope-checklist.md`, then create a least-privilege Backblaze B2 application key named `proofframe-demo-live-proof` scoped to `proofframe-demo-a6b4e49`, then enter only the key id and application key into `.env.final.local` via `python scripts/final_env_wizard.py --output .env.final.local --missing-only --force`.
- Enter a Genblaze/GMI API key into `.env.final.local` with the same wizard; do not paste it into chat, docs, screenshots, or git.
- Run `python scripts/live_env_handoff.py --env-file .env.final.local --strict` and confirm it reports no missing ids.
- Run the post-credential live proof runner once; it validates B2-only and final evidence before any task updates.
- Record and upload the public demo video only after live proof evidence exists.
- Run final secret scan and final submission audit, submit Devpost, then generate the public Devpost submission receipt.

## Codex Actions After Credentials

```bash
python scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks
python scripts/demo_storyboard.py --strict-final
python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final
python scripts/demo_readiness.py --strict-final
python scripts/recording_assets.py --verify-public --strict-final
python scripts/secret_scan.py
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"
python scripts/devpost_form_kit.py --strict-final
python scripts/devpost_submission_checklist.py --strict-final
python scripts/submission_audit.py --strict-final
python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."
python scripts/final_submission_control.py --strict-final
```

## Safety Policy

- `.env.final.local` ignored: `true`
- Never commit:
  - .env.final.local
  - Backblaze key IDs or application keys
  - Genblaze/GMI provider keys
  - Devpost cookies or browser session files
  - raw signed URLs or provider temporary URLs
  - screen recordings that visibly expose secrets
- Safe to commit only after scan:
  - `docs/assets/b2-live-proof-evidence.json`
  - `docs/assets/final-live-proof-evidence.json`
  - `docs/assets/public-video-check.json`
  - `docs/assets/devpost-submission-packet.json`
  - `docs/assets/devpost-form-kit.json`
  - `docs/assets/devpost-submission-checklist.json`

## Claim Boundary

Do not claim completed B2 or Genblaze proof until sanitized live evidence is generated and final gates pass.
