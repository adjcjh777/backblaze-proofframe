# ProofFrame Devpost Submission Preview

Mode: `pre_live_preview_ready`
Safe to share: `true`
Safe to submit: `false`

## Project

- Name: ProofFrame
- Tagline: B2-ready provenance desk for GenAI media.
- Repository: https://github.com/adjcjh777/backblaze-proofframe
- Demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
- Video: TBD after final public video upload.

## Copy Blocks

### 30-Second Pitch

ProofFrame is not another image generator. It is a media operations desk that turns each generated asset into a reviewable packet: prompt, provider/model metadata, storage reference, checksum, approval state, risk note, manifest, and exportable evidence.

### Short Description

ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. Each packet includes prompt history, provider/model metadata, B2 storage references, checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, or retire generated media.

### Backblaze B2 Usage

ProofFrame stores generated media and exported manifests in Backblaze B2 using environment-only credentials. The final proof evidence records sanitized B2 storage keys, byte sizes, and checksums without exposing credentials or signed URLs. B2 is the durable evidence layer: the media asset and manifest are separate objects under the ProofFrame campaign prefix, and the app uses those hashes to make later review, export, and audit steps reproducible.

### Genblaze Usage

ProofFrame generates media through Genblaze's official Pipeline. The final proof uses the credential-free local image provider, records provider/model metadata, and carries the resulting asset through Genblaze's B2 sink into the ProofFrame storage and approval manifest.

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

- `packet_mode`: `post_live_verified`
- `form_mode`: `pre_live_form_ready`
- `final_control_mode`: `pre_live_control`
- `submit_checklist_mode`: `pre_submit_blocked`
- `submission_audit_mode`: `pre_submit_audit_blocked`
- `secret_scan_mode`: `clear`
- `public_space_mode`: `public_space_synced`
- `public_screenshot_mode`: `public_judge_screenshot_ready`

## Final Blockers

- `devpost_submission_checklist`: Final Devpost web submission checklist is ready - Devpost submission checklist mode is pre_submit_blocked; safe_to_submit is False.
- `public_video`: final public video - Storyboard mode is mock_storyboard_ready; public video ready is False.
- `public_video_check`: public video URL check - Public video check mode is pending_video_url; safe_to_submit is False.
- `final_recording`: Final recording gate is ready - Demo readiness mode is pre_live_mock_ready; final recording ready is False.
- `final_secret_scan`: final secret scan task completion - T041A is blocked; secret scan mode is clear; secret scan ok is True.
- `final_submission_audit`: strict final submission audit - T041 is blocked; audit mode is pre_submit_audit_blocked; audit ok is False.
- `devpost_submitted`: Devpost submission receipt - T042 is blocked; receipt mode is pending_submission; receipt ok is False.

## Claim Boundary

- Public demo evidence proves only the credential-free local/mock judge flow.
- Do not claim completed live Backblaze B2 storage until T020 has sanitized live evidence.
- Do not claim completed live Genblaze generation until T021 has sanitized live evidence.
- Do not submit this packet as final until safe_to_submit is true.

## Next Actions

- Finalize Devpost fields: Demo video URL.
- Resolve final blocker: Final Devpost web submission checklist is ready.
- Resolve final blocker: final public video.
- Resolve final blocker: public video URL check.
- Resolve final blocker: Final recording gate is ready.
- Resolve final blocker: final secret scan task completion.
- Resolve final blocker: strict final submission audit.
- Resolve final blocker: Devpost submission receipt.
