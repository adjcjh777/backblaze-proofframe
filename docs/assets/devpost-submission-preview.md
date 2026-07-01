# ProofFrame Devpost Submission Preview

Mode: `pre_live_preview_ready`
Safe to share: `true`
Safe to submit: `false`

## Project

- Name: ProofFrame
- Tagline: B2-ready provenance desk for GenAI media.
- Repository: https://github.com/adjcjh777/backblaze-proofframe
- Demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
- Video: TBD after final B2 and Genblaze proof.

## Copy Blocks

### 30-Second Pitch

ProofFrame is not another image generator. It is a media operations desk that turns each generated asset into a reviewable packet: prompt, provider/model metadata, storage reference, checksum, approval state, risk note, manifest, and exportable evidence.

### Short Description

ProofFrame is a review desk for generated media. The local demo creates a campaign, generates mock variants, approves or rejects assets, exports a manifest, and downloads an evidence ZIP with prompts, provider/model fields, storage references, hashes, and approval status. The final hackathon submission gate is to verify the same flow with Genblaze-backed generation and Backblaze B2-backed storage.

### Backblaze B2 Usage

ProofFrame treats Backblaze B2 as the final durable evidence layer, not as a late file-upload checkbox. The public demo currently runs in local/mock mode, but every asset packet already carries the B2-ready object model: storage backend, storage key, checksum, byte size, prompt, provider/model metadata, approval state, and risk note. The repo includes a dedicated B2 S3-compatible storage adapter, a recorded private B2 bucket setup, and a one-command B2 proof runner that will upload one generated asset and one manifest with environment-only credentials. That live upload remains the final submission gate before any public claim is upgraded to completed B2 storage.

### Genblaze Usage

ProofFrame includes a Genblaze/GMICloud provider adapter built around the official Genblaze Pipeline API. In the public mock demo, deterministic generation keeps the workflow inspectable without secrets; the same manifest fields are reserved for the final provider, model, request/run metadata, prompt, and asset checksum. The final submission gate is a live Genblaze-compatible run that proves the provider path and then carries the resulting asset into the ProofFrame review and storage packet.

## Evidence Links

- `public_demo`: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
- `repository`: https://github.com/adjcjh777/backblaze-proofframe
- `public_screenshot`: docs/assets/proofframe-hf-public-smoke.png
- `screenshot_report`: docs/assets/public-demo-screenshot-report.json
- `public_space_sync`: docs/assets/public-space-sync-report.json
- `judge_brief`: docs/assets/judge-brief.json
- `judge_crosswalk`: docs/assets/judge-crosswalk.json
- `form_kit`: docs/assets/devpost-form-kit.json
- `final_control`: docs/assets/final-submission-control.json
- `submission_bundle`: docs/assets/submission-bundle-manifest.json

## Readiness

- `packet_mode`: `pre_live_safe`
- `form_mode`: `pre_live_form_ready`
- `final_control_mode`: `pre_live_control`
- `submit_checklist_mode`: `pre_submit_blocked`
- `submission_audit_mode`: `pre_submit_audit_blocked`
- `secret_scan_mode`: `clear`
- `public_space_mode`: `public_space_synced`
- `public_screenshot_mode`: `public_judge_screenshot_ready`

## Final Blockers

- `devpost_submission_checklist`: Final Devpost web submission checklist is ready - Devpost submission checklist mode is pre_submit_blocked; safe_to_submit is False.
- `genblaze_live_proof`: live Genblaze proof - T021 is blocked; final evidence status is missing.
- `public_video`: final public video - Storyboard mode is mock_storyboard_ready; public video ready is False.
- `public_video_check`: public video URL check - Public video check mode is pending_video_url; safe_to_submit is False.
- `final_recording`: Final recording gate is ready - Demo readiness mode is pre_live_mock_ready; final recording ready is False.
- `final_secret_scan`: final secret scan task completion - T041A is todo; secret scan mode is clear; secret scan ok is True.
- `final_submission_audit`: strict final submission audit - T041 is todo; audit mode is pre_submit_audit_blocked; audit ok is False.
- `devpost_submitted`: Devpost submission receipt - T042 is todo; receipt mode is pending_submission; receipt ok is False.

## Claim Boundary

- Public demo evidence proves only the credential-free local/mock judge flow.
- Do not claim completed live Backblaze B2 storage until T020 has sanitized live evidence.
- Do not claim completed live Genblaze generation until T021 has sanitized live evidence.
- Do not submit this packet as final until safe_to_submit is true.

## Next Actions

- Finalize Devpost fields: Demo video URL.
- Resolve final blocker: Final Devpost web submission checklist is ready.
- Resolve final blocker: live Genblaze proof.
- Resolve final blocker: final public video.
- Resolve final blocker: public video URL check.
- Resolve final blocker: Final recording gate is ready.
- Resolve final blocker: final secret scan task completion.
- Resolve final blocker: strict final submission audit.
