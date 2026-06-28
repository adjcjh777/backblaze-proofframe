# ProofFrame Final Rehearsal Checklist

Mode: `ready_for_credential_rehearsal`
OK: `true`
Safe to submit: `false`
Current phase: `credential_entry`
Next command: `python scripts/final_env_wizard.py --output .env.final.local --missing-only --force`

## Preconditions

- OK `operator_ready`: Operator brief mode is credential_entry_ready. Evidence: `docs/assets/final-operator-brief.json`
- OK `only_expected_secrets_missing`: Missing ids: b2_application_key, b2_key_id, genblaze_api_key. Evidence: `docs/assets/final-operator-brief.json`
- OK `launch_plan_at_credential_entry`: Current phase is credential_entry. Evidence: `docs/assets/final-launch-plan.json`
- OK `public_space_synced`: Runtime sha: ff91f45b5e6598cf2163efdc6a217373f56dac0b. Evidence: `docs/assets/public-space-sync-report.json`
- OK `mock_form_ready`: Devpost form mode is pre_live_form_ready. Evidence: `docs/assets/devpost-form-kit.json`
- OK `mock_recording_ready`: Recording assets mode is public_mock_verified. Evidence: `docs/assets/recording-assets.json`
- OK `secret_scan_currently_clear`: Secret scan mode is clear. Evidence: `docs/assets/secret-scan-report.json`
- OK `final_gate_fail_closed`: Final control mode is pre_live_control. Evidence: `docs/assets/final-submission-control.json`
- OK `live_tasks_not_overclaimed`: T020=doing; T021=doing. Evidence: `tasks.json`

## Required Secret IDs

- `b2_key_id`
- `b2_application_key`
- `genblaze_api_key`

## Rehearsal Steps

### 1. enter_credentials (operator)
```bash
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
```
- Success signal: docs/assets/live-credential-handoff.json reports no missing ids after live_env_handoff.py --strict.

### 2. b2_live_proof (codex)
```bash
python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json
```
- Success signal: B2 evidence JSON has ok=true, storage_backend=b2, asset and manifest checksums, and sanitized object keys.
- Safe to commit after a clean secret scan:
  - `docs/assets/b2-live-proof-evidence.json`
- Task update after success: `python3 scripts/task.py done T020 --note "B2 live proof evidence captured in docs/assets/b2-live-proof-evidence.json."`

### 3. final_live_proof (codex)
```bash
python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json
```
- Success signal: Final evidence JSON has storage_backend=b2, generation_backend=genblaze, provider/model metadata, checksums, and no raw provider URLs.
- Safe to commit after a clean secret scan:
  - `docs/assets/final-live-proof-evidence.json`
- Task update after success: `python3 scripts/task.py done T021 --note "Final B2 plus Genblaze live proof evidence captured in docs/assets/final-live-proof-evidence.json."`

### 4. seed_public_video_packet (codex)
```bash
python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" && python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final
```
- Success signal: Devpost packet includes the public video URL and public-video-check reports safe_to_submit=true.
- Safe to commit after a clean secret scan:
  - `docs/assets/devpost-submission-packet.json`
  - `docs/assets/public-video-check.json`

### 5. final_secret_scan (codex)
```bash
python scripts/secret_scan.py
```
- Success signal: Secret scan is clear after live proof and public video URL are present.
- Safe to commit after a clean secret scan:
  - `docs/assets/secret-scan-report.json`
- Task update after success: `python3 scripts/task.py done T041A --note "Final secret scan clear after live proof and public video."`

### 6. final_video_reports (codex)
```bash
python scripts/devpost_form_kit.py --strict-final && python scripts/demo_storyboard.py --strict-final && python scripts/demo_readiness.py --strict-final && python scripts/recording_assets.py --verify-public --strict-final
```
- Success signal: Devpost form kit, storyboard, demo readiness, and recording assets all report final video readiness.
- Safe to commit after a clean secret scan:
  - `docs/assets/devpost-form-kit.json`
  - `docs/assets/demo-storyboard.json`
  - `docs/assets/demo-readiness-report.json`
  - `docs/assets/recording-assets.json`

### 7. devpost_submission_checklist (codex)
```bash
python scripts/devpost_submission_checklist.py --strict-final
```
- Success signal: Devpost submission checklist is ready_to_submit_devpost.
- Safe to commit after a clean secret scan:
  - `docs/assets/devpost-submission-checklist.json`

### 8. devpost_submission_preview (codex)
```bash
python scripts/devpost_submission_preview.py
```
- Success signal: Devpost submission preview is regenerated with current copy, evidence links, and remaining final blockers.
- Safe to commit after a clean secret scan:
  - `docs/assets/devpost-submission-preview.json`

### 9. final_submission_audit (codex)
```bash
python scripts/submission_audit.py --strict-final
```
- Success signal: Submission audit is pre_submit_audit_ready after live proof, final video, final scan, and Devpost checklist.
- Safe to commit after a clean secret scan:
  - `docs/assets/submission-audit-report.json`
- Task update after success: `python3 scripts/task.py done T041 --note "Final submission audit passed after live proof, public video, secret scan, and Devpost checklist."`

### 10. devpost_receipt (operator)
```bash
python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."
```
- Success signal: Devpost receipt JSON is ok=true, uses a devpost.com project URL, and contains no cookies or session data.
- Safe to commit after a clean secret scan:
  - `docs/assets/devpost-submission-receipt.json`
- Task update after success: `python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."`

### 11. final_green_gate (codex)
```bash
python scripts/secret_scan.py && python scripts/final_submission_control.py --strict-final && python scripts/final_launch_plan.py --strict-final && python scripts/devpost_submission_preview.py --strict-final && python scripts/submission_bundle.py --strict-final
```
- Success signal: Final scan is clear; final control, launch plan, Devpost preview, and submission bundle all report final submit readiness.
- Safe to commit after a clean secret scan:
  - `docs/assets/secret-scan-report.json`
  - `docs/assets/final-submission-control.json`
  - `docs/assets/final-launch-plan.json`
  - `docs/assets/devpost-submission-preview.json`
  - `docs/assets/submission-bundle-manifest.json`

## Stop Rules

- Stop immediately if a command prints or writes a value that looks like a B2 key, Genblaze/GMI key, browser cookie, authorization header, or signed URL.
- Do not mark T020 or T021 done unless the corresponding sanitized evidence JSON exists and passes the expected backend/provider checks.
- Do not run Devpost submission until final_submission_control.py --strict-final passes after live proof, public video, final scan, and final audit.
- Do not update public copy from pre-live to completed sponsor proof until both B2 and Genblaze evidence are committed after a clean secret scan.

This checklist contains secret names only, never secret values.
