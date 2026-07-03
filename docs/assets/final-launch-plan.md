# ProofFrame Final Launch Plan

Mode: `ready_for_genblaze_live_proof`
Current phase: `genblaze_live_proof`
Complete: `false`
Progress: `2 / 6` done; `1` ready, `3` blocked.

## Next Command

```bash
python scripts/run_final_live_proof.py --env-file .env.final.local --genblaze-provider openai --genblaze-image-model gpt-image-1 --evidence-out docs/assets/final-live-proof-evidence.json
```
Run after the B2-only proof passes so final evidence has storage and generation proof.

## Phases

### credential_entry - Enter final credentials locally
- Status: `done`
- Detail: Live credential handoff is complete; no missing ids remain.
- Command:
```bash
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
```
- Expected artifacts:
  - `docs/assets/b2-key-scope-checklist.md reviewed before key creation`
  - `B2 pre-key confirmation phrase recorded without secrets: I confirm ProofFrame B2 key scope: standard key, bucket proofframe-demo-a6b4e49, prefix campaigns/, no all-bucket access, no delete/admin permissions, and no secrets in chat/docs/git.`
  - `.env.final.local (git-ignored, never committed)`

### b2_live_proof - Capture Backblaze B2 live proof
- Status: `done`
- Detail: Sanitized B2 evidence is present and T020 is done.
- Command:
```bash
python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json
```
- Expected artifacts:
  - `docs/assets/b2-live-proof-evidence.json`
- Safe to commit after scan:
  - `docs/assets/b2-live-proof-evidence.json`
- Task ledger updates after success:
  - `python3 scripts/task.py done T020 --note "B2 live proof evidence captured in docs/assets/b2-live-proof-evidence.json."`

### genblaze_live_proof - Capture final B2 plus Genblaze proof
- Status: `ready`
- Detail: Run after the B2-only proof passes so final evidence has storage and generation proof.
- Command:
```bash
python scripts/run_final_live_proof.py --env-file .env.final.local --genblaze-provider openai --genblaze-image-model gpt-image-1 --evidence-out docs/assets/final-live-proof-evidence.json
```
- Expected artifacts:
  - `docs/assets/final-live-proof-evidence.json`
- Safe to commit after scan:
  - `docs/assets/final-live-proof-evidence.json`
- Task ledger updates after success:
  - `python3 scripts/task.py done T021 --note "Final B2 plus Genblaze live proof evidence captured in docs/assets/final-live-proof-evidence.json."`

### public_video - Record and verify public demo video
- Status: `blocked`
- Detail: Waiting on live B2 plus Genblaze evidence.
- Command:
```bash
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"
```
- Expected artifacts:
  - `public demo video URL`
  - `docs/assets/devpost-submission-packet.json`
  - `docs/assets/devpost-form-kit.json`
  - `docs/assets/demo-storyboard.json`
  - `docs/assets/recording-assets.json`
- Safe to commit after scan:
  - `docs/assets/devpost-submission-packet.json`
  - `docs/assets/devpost-form-kit.json`
  - `docs/assets/demo-storyboard.json`
  - `docs/assets/recording-assets.json`

### final_safety_audit - Run final secret scan and submission audit
- Status: `blocked`
- Detail: Waiting on final public video.
- Command:
```bash
python scripts/secret_scan.py && python scripts/submission_audit.py --strict-final
```
- Expected artifacts:
  - `docs/assets/secret-scan-report.json`
  - `docs/assets/submission-audit-report.json`
- Safe to commit after scan:
  - `docs/assets/secret-scan-report.json`
  - `docs/assets/submission-audit-report.json`
- Task ledger updates after success:
  - `python3 scripts/task.py done T041A --note "Final secret scan clear after live proof and public video."`
  - `python3 scripts/task.py done T041 --note "Final submission audit passed after live proof and public video."`

### devpost_submit - Submit Devpost and capture receipt
- Status: `blocked`
- Detail: Waiting on all pre-submit gates.
- Command:
```bash
python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."
```
- Expected artifacts:
  - `docs/assets/devpost-submission-receipt.json`
- Safe to commit after scan:
  - `docs/assets/devpost-submission-receipt.json`
- Task ledger updates after success:
  - `python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."`

## Safety Policy

- This report contains command strings and artifact paths only; no secret values.
- Do not commit:
  - .env.final.local
  - Backblaze key IDs or application keys
  - Genblaze provider API keys
  - Devpost cookies or browser session files
  - raw signed URLs or provider temporary URLs
- Do not source `.env.final.local`; use the parser-based `--env-file` commands.
