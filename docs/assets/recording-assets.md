# ProofFrame Recording Assets

Mode: `mock_recording_ready`
Mock recording ready: `true`
Public mock verified: `false`
Final video ready: `false`
Public judge URL: https://adjcjh-backblaze-proofframe.hf.space/?judge=1

## Source Reports

- OK `storyboard`: `docs/assets/demo-storyboard.json` mode `mock_storyboard_ready`
- OK `readiness`: `docs/assets/demo-readiness-report.json` mode `pre_live_mock_ready`
- OK `public_video_check`: `docs/assets/public-video-check.json` mode `pending_video_url`
- OK `demo_video_draft`: `docs/assets/demo-video-draft.json` mode `mock_video_draft_ready`
- OK `devpost_form`: `docs/assets/devpost-form-kit.json` mode `pre_live_form_ready`
- OK `final_control`: `docs/assets/final-submission-control.json` mode `pre_live_control`

## Required Assets

- OK `README.md`
- OK `docs/demo_script.md`
- OK `docs/assets/demo-storyboard.json`
- OK `docs/assets/demo-storyboard.md`
- OK `docs/assets/demo-video-draft.json`
- OK `docs/assets/demo-video-draft.md`
- OK `docs/assets/proofframe-demo-draft.mp4`
- OK `docs/assets/public-video-check.json`
- OK `docs/assets/public-video-check.md`
- OK `docs/assets/demo-readiness-report.json`
- OK `docs/assets/demo-readiness-report.md`
- OK `docs/assets/devpost-form-kit.json`
- OK `docs/assets/devpost-form-kit.md`
- OK `docs/assets/final-submission-control.json`
- OK `docs/assets/final-submission-control.md`
- OK `docs/assets/proofframe-local-ui-smoke.png`
- OK `docs/assets/proofframe-review-console-smoke.png`
- OK `docs/assets/proofframe-hf-public-smoke.png`
- OK `docs/assets/proofframe-sponsor-model-smoke.png`
- OK `docs/assets/proofframe-sponsor-model-mobile-smoke.png`

## Public GET-only Verification

- Not checked in this run. Use `python scripts/recording_assets.py --verify-public`.

## Shot Plan

- `judge_slate` - Public judge URL: First viewport with judge recording slate and claim boundary.
- `sponsor_model` - Public judge URL: Sponsor Evidence Model showing Genblaze step, B2 route, manifest, and claim mode.
- `creative_brief` - Local or public mock demo: Campaign brief with audience, tone, and prompt context.
- `asset_ledger` - Local or public mock demo: Generated asset ledger with provider/model/checksum/storage fields.
- `review_console` - Committed screenshot or live UI: Review console filters, approval state, and copy-safe summary.
- `final_gate` - Final submission control report: Fail-closed final gate with remaining B2/Genblaze/video blockers.

## Commands

```bash
uvicorn proofframe.app:app --host 127.0.0.1 --port 8088
python scripts/recording_assets.py --verify-public
python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space
python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json
python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json
python scripts/demo_storyboard.py --strict-final
python scripts/demo_video_draft.py --build-video
python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final
python scripts/demo_readiness.py --strict-final
python scripts/final_submission_control.py --strict-final
```

## Next Actions

- Run python scripts/recording_assets.py --verify-public before recording.
- After live B2/Genblaze proof, record and upload the final public video.
- Run python scripts/final_submission_control.py --strict-final before Devpost submit.
