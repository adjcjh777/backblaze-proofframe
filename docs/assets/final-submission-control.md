# ProofFrame Final Submission Control

Mode: `pre_live_control`
Safe to submit: `false`
Created: `2026-06-28T17:50:00Z`
Public demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Repository: https://github.com/adjcjh777/backblaze-proofframe

## Event Snapshot

- Event: Backblaze Generative Media Hackathon
- Deadline: Aug 3, 2026 @ 5:00pm EDT / 2026-08-04 05:00 Asia/Shanghai
- Prize total: `$10000`
- Observed participants: `365` checked `2026-06-29 Asia/Shanghai`
- Source: https://backblaze-generative-media.devpost.com/
- Note: Dynamic Devpost count; recheck before final public claims.

## Submission Gate

- Mode: `pre_live_safe`
- Tasks: `1 / 6` done
- B2 evidence: `missing`
- Live evidence: `missing`
- Devpost packet: `pre_live_packet_pending`

## Launch Plan

- Mode: `ready_for_credential_entry`
- Current phase: `credential_entry`
- Next command: `python scripts/final_env_wizard.py --output .env.final.local --missing-only --force`
- Detail: Only expected secret ids are missing; operator can enter them locally.
- Source: `docs/assets/final-launch-plan.json`

## Warnings

- None.

## Requirements

| Status | Requirement | Detail | Evidence |
| --- | --- | --- | --- |
| OK | Devpost registration complete | T040 is done. | `tasks.json` |
| OK | Credential-free public demo is ready | Devpost form kit mode is pre_live_form_ready. | `docs/assets/devpost-form-kit.json` |
| PENDING | Final Devpost web submission checklist is ready | Devpost submission checklist mode is pre_submit_blocked; safe_to_submit is False. | `docs/assets/devpost-submission-checklist.json` |
| OK | Official Devpost event snapshot is fresh | Snapshot checked at 2026-06-28T16:30:54Z; submission open is True; age days is 0. | `docs/assets/devpost-event-snapshot.json` |
| OK | Agent handoff metadata points at the current repo | Agent handoff mode is handoff_ready; ok is True; bus status is skipped; active role cwd ok is None. | `docs/assets/agent-handoff-report.json` |
| OK | Public Space is synced to the current judge-facing demo | Public Space sync mode is public_space_synced; ok is True. | `docs/assets/public-space-sync-report.json` |
| OK | Final launch plan exposes the current operator step | Launch plan mode is ready_for_credential_entry; current phase is credential_entry; next command is python scripts/final_env_wizard.py --output .env.final.local --missing-only --force. | `docs/assets/final-launch-plan.json` |
| OK | Recording assets are ready | Recording assets mode is public_mock_verified; public mock verified is True. | `docs/assets/recording-assets.json` |
| OK | Control input reports match expected schemas | All input report schemas are current. | `docs/assets/*.json readiness reports` |
| PENDING | Backblaze B2 live proof captured | T020 is doing; B2 evidence status is missing; final evidence status is missing. | `tasks.json, docs/assets/b2-live-proof-evidence.json, and docs/assets/final-live-proof-evidence.json` |
| PENDING | Genblaze live proof captured | T021 is doing; final evidence status is missing. | `tasks.json and docs/assets/final-live-proof-evidence.json` |
| PENDING | Live credential handoff is ready | Credential handoff mode is missing_live_env; missing ids: b2_key_id, b2_application_key, genblaze_api_key. | `docs/assets/live-credential-handoff.json` |
| PENDING | Final public demo video URL is ready | Storyboard mode is mock_storyboard_ready; public video ready is False. | `docs/assets/demo-storyboard.json` |
| PENDING | Final public demo video URL is accessible and safe | Public video check mode is pending_video_url; safe_to_submit is False. | `docs/assets/public-video-check.json` |
| PENDING | Final recording gate is ready | Demo readiness mode is pre_live_mock_ready; final recording ready is False. | `docs/assets/demo-readiness-report.json` |
| OK | Award readiness score remains competitive | Award readiness score is 97/115. | `docs/assets/award-readiness-report.json` |
| PENDING | Final secret scan is complete | T041A is todo; secret scan mode is clear; secret scan ok is True. | `tasks.json and docs/assets/secret-scan-report.json` |
| PENDING | Final submission audit is complete | T041 is todo; audit mode is pre_submit_audit_blocked; audit ok is False. | `tasks.json and docs/assets/submission-audit-report.json` |
| PENDING | Devpost project submitted | T042 is todo; receipt mode is pending_submission; receipt ok is False. | `tasks.json and docs/assets/devpost-submission-receipt.json` |

## Next Actions

- Complete .env.final.local with B2_KEY_ID, B2_APPLICATION_KEY, and Genblaze/GMI API key values.
- Run the B2 live proof runner and save sanitized B2 evidence.
- Run the final B2 plus Genblaze proof runner and save sanitized final evidence.
- Record and upload the public demo video after live proof is captured.
- Verify the public video URL with python scripts/public_video_check.py --verify-url --strict-final.
- Regenerate the final Devpost submission checklist after the form kit and final control gates are current.
- Run and mark the final secret scan after live evidence/video assets are ready.
- Run final submission audit after proof, video, and secret scan pass.

## Operator Commands

```bash
python scripts/final_env_wizard.py --prefill-non-secret --output .env.final.local
python scripts/final_env_wizard.py --output .env.final.local --missing-only --force
python scripts/live_env_handoff.py --env-file .env.final.local
python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json
python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json
python scripts/agent_handoff_check.py
python scripts/public_space_sync.py
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
```

## Claim Boundary

Public demo remains local/mock and pre_live_safe until final live B2 plus Genblaze proof is captured.
