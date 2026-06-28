# ProofFrame Submission Audit

Mode: `pre_submit_audit_blocked`
OK: `false`
Created: `2026-06-28T10:59:52Z`
Final evidence: `docs/assets/final-live-proof-evidence.json`

## Task Statuses

- T020: `doing`
- T021: `doing`
- T040: `done`
- T041A: `todo`
- T041: `todo`
- T042: `todo`

## Section Findings

- tasks: 3 finding(s)
- files: OK
- schemas: OK
- final_evidence: 1 finding(s)
- devpost_packet: 5 finding(s)
- event_snapshot: OK
- final_reports: 7 finding(s)
- final_control: 1 finding(s)

## Findings

- `T020` [doing]: Integrate Backblaze B2-compatible storage is not done. Evidence: `tasks.json`
- `T021` [doing]: Integrate Genblaze-compatible generation is not done. Evidence: `tasks.json`
- `T041A` [todo]: Run final secret scan is not done. Evidence: `tasks.json`
- `final-live-proof-evidence` [missing]: docs/assets/final-live-proof-evidence.json is missing or invalid JSON. Evidence: `docs/assets/final-live-proof-evidence.json`
- `devpost_packet.mode` [mismatch]: Expected 'post_live_verified', got 'pre_live_safe'. Evidence: `docs/assets/devpost-submission-packet.json`
- `devpost_packet.video_url` [missing]: Final packet must include a public http(s) demo video URL, not a placeholder. Evidence: `docs/assets/devpost-submission-packet.json`
- `devpost_packet.T020` [doing]: Devpost packet checklist is not synchronized with required pre-submit task status. Evidence: `docs/assets/devpost-submission-packet.json`
- `devpost_packet.T021` [doing]: Devpost packet checklist is not synchronized with required pre-submit task status. Evidence: `docs/assets/devpost-submission-packet.json`
- `devpost_packet.T041A` [todo]: Devpost packet checklist is not synchronized with required pre-submit task status. Evidence: `docs/assets/devpost-submission-packet.json`
- `devpost_form_kit.final_form_ready` [incomplete]: Final Devpost form kit is not ready. Evidence: `docs/assets/devpost-form-kit.json`
- `devpost_submission_checklist.safe_to_submit` [incomplete]: Final Devpost submission checklist is not ready. Evidence: `docs/assets/devpost-submission-checklist.json`
- `demo_storyboard.public_video_ready` [incomplete]: Storyboard does not have a public video URL ready. Evidence: `docs/assets/demo-storyboard.json`
- `public_video_check.safe_to_submit` [incomplete]: Public demo video URL is not verified. Evidence: `docs/assets/public-video-check.json`
- `demo_readiness.final_recording_ready` [incomplete]: Final recording readiness gate is not ready. Evidence: `docs/assets/demo-readiness-report.json`
- `recording_assets.final_video_ready` [incomplete]: Recording assets do not verify the final public video. Evidence: `docs/assets/recording-assets.json`
- `live_credential_handoff.ready_for_live_proof` [incomplete]: Live credential handoff is not ready. Evidence: `docs/assets/live-credential-handoff.json`
- `final_submission_control.blocking_items` [blocked]: Unexpected blockers remain before audit sign-off: b2_live_proof, credential_handoff, devpost_submission_checklist, final_recording, final_secret_scan, genblaze_live_proof, public_video, public_video_check Evidence: `docs/assets/final-submission-control.json`

## Next Commands

- `python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json`
- `python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json`
- `python scripts/demo_storyboard.py --strict-final`
- `python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final`
- `python scripts/demo_readiness.py --strict-final`
- `python scripts/recording_assets.py --verify-public --strict-final`
- `python scripts/secret_scan.py`
- `python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"`
- `python scripts/devpost_form_kit.py --strict-final`
- `python scripts/devpost_submission_checklist.py --strict-final`
- `python scripts/final_submission_control.py --strict-final`
- `python scripts/submission_audit.py --strict-final`
- `python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."`

## Signoff

When this report is ok, mark T041 done, submit Devpost, generate the public submission receipt, then mark T042 done and rerun final_submission_control.py --strict-final.
