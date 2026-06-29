# ProofFrame Demo Video Draft

Mode: `mock_video_draft_ready`
OK: `true`
Safe to submit: `false`
Final video ready: `false`
Draft URL: https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/resolve/main/docs/assets/proofframe-demo-draft.mp4
Expected duration: `54s / 180s max`

## Claim Boundary

This MP4 is a mock recording draft for rehearsal and public review. It is not the final Devpost video and does not prove live B2 or Genblaze execution.

## Slides

- OK `docs/assets/proofframe-hf-public-smoke.png` (10s): Judge-mode public demo
- OK `docs/assets/proofframe-sponsor-model-smoke.png` (12s): Sponsor evidence model
- OK `docs/assets/proofframe-local-ui-smoke.png` (12s): Campaign and asset ledger
- OK `docs/assets/proofframe-review-console-smoke.png` (12s): Review console
- OK `docs/assets/proofframe-sponsor-model-mobile-smoke.png` (8s): Mobile-safe judge proof

## Video Probe

- Checked: `true`
- OK: `true`
- Duration: `65.97`
- Bytes: `747727`
- Size: `1280x720`
- Error: `None`

## Checks

- OK `draft_inputs_present`: 5 / 5 slide inputs present.
- OK `draft_video_present`: Video path is /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/docs/assets/proofframe-demo-draft.mp4.
- OK `draft_under_time_limit`: Duration is 65.97; max is 180.

## Next Actions

- Upload or sync this draft only as a mock video reference.
- After B2 and Genblaze live proof, record the final narrated video and set PROOFFRAME_PUBLIC_VIDEO_URL.
- Run scripts/public_video_check.py with --verify-url --strict-final on the final public video URL.
