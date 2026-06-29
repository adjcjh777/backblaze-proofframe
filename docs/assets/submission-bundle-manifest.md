# ProofFrame Submission Bundle

Created: `2026-06-29T11:27:36Z`
Repository: https://github.com/adjcjh777/backblaze-proofframe
Public mock demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Devpost packet mode: `pre_live_safe`
Final gate mode: `pre_live_safe`
Final gate ready: `false`

## Current Gate

- Tasks: 1 done / 6 required; 2 doing, 0 blocked, 3 todo.
- Live evidence: `missing`
- Devpost copy packet: `pre_live_packet_pending`
- Final reports: `incomplete`
- Post-Devpost closeout: `incomplete`

## Next Actions

- Run a live Backblaze B2 asset and manifest proof.
- Run a live Genblaze generation proof and capture provider metadata.
- Run the final submission audit after live proofs are captured.
- Run the final secret scan before recording or submitting.
- Submit the Devpost project after every preceding gate is done.

## Artifacts

- `README.md` (14049 bytes, sha256 `bd3c897bef754e5e...`) - Core public project overview
- `Dockerfile` (522 bytes, sha256 `6764f101746a802d...`) - Docker deployment image contract
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (6177 bytes, sha256 `d0d24f751da92adc...`) - Implementation specification
- `docs/deployment.md` (5202 bytes, sha256 `fdc41ebba3f4d496...`) - Public demo deployment runbook
- `docs/devpost_draft.md` (5613 bytes, sha256 `e08e3f25a04bab48...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6270 bytes, sha256 `92b06cc47f68c410...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (5159 bytes, sha256 `00e03e34b62dfdfc...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `37f41e7cbc113521...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `e8a43ea24e37e59a...`) - Human-readable Devpost event snapshot
- `scripts/agent_handoff_check.py` (14559 bytes, sha256 `3ef180b6a92eb987...`) - Agent Bus and Codex handoff path checker
- `docs/assets/agent-handoff-report.json` (2253 bytes, sha256 `adbfa254d223f248...`) - Machine-readable Agent handoff report
- `docs/assets/agent-handoff-report.md` (1571 bytes, sha256 `b19bc7bf51f52a8b...`) - Human-readable Agent handoff report
- `scripts/public_space_sync.py` (71771 bytes, sha256 `1c9b031e5dc6b61b...`) - Public Hugging Face Space sync verifier
- `docs/assets/public-space-sync-report.json` (17658 bytes, sha256 `6ed55a8a74012609...`) - Machine-readable public Space sync report
- `docs/assets/public-space-sync-report.md` (7497 bytes, sha256 `66f241f60248bee6...`) - Human-readable public Space sync report
- `scripts/public_demo_screenshot.py` (8926 bytes, sha256 `3eb5b0a003e383dd...`) - Public judge-mode screenshot verifier
- `docs/assets/public-demo-screenshot-report.json` (2421 bytes, sha256 `e8ce08735a86a920...`) - Machine-readable public screenshot report
- `docs/assets/public-demo-screenshot-report.md` (1418 bytes, sha256 `dce44c3bc2188131...`) - Human-readable public screenshot report
- `scripts/devpost_form_kit.py` (12830 bytes, sha256 `b0173e698f4c3629...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (12483 bytes, sha256 `96196519c036e0aa...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (7496 bytes, sha256 `f6beeb3fe9e7f94d...`) - Human-readable Devpost form kit
- `scripts/devpost_submission_preview.py` (17329 bytes, sha256 `28ed8703ca6479fc...`) - One-page claim-safe Devpost preview
- `docs/assets/devpost-submission-preview.json` (11611 bytes, sha256 `d6ca26367f7baf84...`) - Machine-readable Devpost preview
- `docs/assets/devpost-submission-preview.md` (5407 bytes, sha256 `760d948b804fbe97...`) - Human-readable Devpost preview
- `scripts/devpost_submission_checklist.py` (11252 bytes, sha256 `78b8e1b70da428fd...`) - No-secret final Devpost web submission checklist
- `docs/assets/devpost-submission-checklist.json` (16428 bytes, sha256 `27cb6f67c207ce86...`) - Machine-readable final Devpost submission checklist
- `docs/assets/devpost-submission-checklist.md` (9319 bytes, sha256 `e45546c7334e78e3...`) - Human-readable final Devpost submission checklist
- `scripts/judge_brief.py` (9968 bytes, sha256 `605a72a56e24b330...`) - Public-safe 30-second judge brief
- `docs/assets/judge-brief.json` (3734 bytes, sha256 `1770f84109bf715e...`) - Machine-readable judge brief
- `docs/assets/judge-brief.md` (3000 bytes, sha256 `eaa20f981d0f155b...`) - Human-readable judge brief
- `scripts/judge_crosswalk.py` (17642 bytes, sha256 `d9153174e330fd53...`) - Official criteria to evidence crosswalk
- `docs/assets/judge-crosswalk.json` (10219 bytes, sha256 `9a09f7d546f26294...`) - Machine-readable judge crosswalk
- `docs/assets/judge-crosswalk.md` (6157 bytes, sha256 `290b53dd0608d58d...`) - Human-readable judge crosswalk
- `scripts/judge_decision_brief.py` (14954 bytes, sha256 `8505d14ada46c7ac...`) - Public-safe judge decision brief builder
- `docs/assets/judge-decision-brief.json` (8137 bytes, sha256 `791198bc820f281d...`) - Machine-readable judge decision brief
- `docs/assets/judge-decision-brief.md` (3835 bytes, sha256 `eccfce4314d9b032...`) - Human-readable judge decision brief
- `scripts/judge_evidence_index.py` (13555 bytes, sha256 `db66a0c64d21723a...`) - Public-safe judge evidence index builder
- `docs/assets/judge-evidence-index.json` (9969 bytes, sha256 `c6401f8497770689...`) - Machine-readable judge evidence index
- `docs/assets/judge-evidence-index.md` (4262 bytes, sha256 `2423757dfbc785ee...`) - Human-readable judge evidence index
- `apps/web/index.html` (66300 bytes, sha256 `5ce547cddbec606f...`) - Browser proof ledger UI
- `docs/demo_script.md` (5856 bytes, sha256 `fbabf38ff87cca9b...`) - Video shot list and narration
- `scripts/demo_storyboard.py` (11025 bytes, sha256 `e5d75956d6d4a20b...`) - Machine-checked demo video storyboard
- `docs/assets/demo-storyboard.json` (4514 bytes, sha256 `d88c7c6c0b36433c...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2704 bytes, sha256 `3765ca34a5b53c7b...`) - Human-readable demo storyboard
- `scripts/demo_video_draft.py` (12209 bytes, sha256 `953f4b118ca2165f...`) - Mock demo video draft builder
- `docs/assets/demo-video-draft.json` (2459 bytes, sha256 `79cb37a997722de7...`) - Machine-readable demo video draft report
- `docs/assets/demo-video-draft.md` (1562 bytes, sha256 `4b6b4a0c7b9a501e...`) - Human-readable demo video draft report
- `docs/assets/proofframe-demo-draft.mp4` (746805 bytes, sha256 `4b36a50d5957575f...`) - Public-safe mock demo video draft
- `scripts/final_video_publish_kit.py` (12256 bytes, sha256 `651a73d338ae1f4b...`) - Final public video upload copy and gate kit
- `docs/assets/final-video-publish-kit.json` (5366 bytes, sha256 `a431d73d9fddaec6...`) - Machine-readable final video publish kit
- `docs/assets/final-video-publish-kit.md` (2727 bytes, sha256 `0b9f266ebec59dec...`) - Human-readable final video publish kit
- `scripts/public_video_check.py` (14919 bytes, sha256 `ca4e127967c6b81d...`) - Public demo video URL verifier
- `docs/assets/public-video-check.json` (2977 bytes, sha256 `f736e860d9301699...`) - Machine-readable public video check
- `docs/assets/public-video-check.md` (1701 bytes, sha256 `990cd0e1a0bd4814...`) - Human-readable public video check
- `docs/sponsor_fit_matrix.md` (3054 bytes, sha256 `cfa25f30bc5d2051...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (24519 bytes, sha256 `9cc121bb0fdc60ec...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (11377 bytes, sha256 `66417f6e0c2a15d9...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4390 bytes, sha256 `5be57ca5d9cab53d...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (32644 bytes, sha256 `6514cbdf2bfe8998...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (24359 bytes, sha256 `9a0bbbb4041da323...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (7087 bytes, sha256 `0beeb1d3fb95e529...`) - Human-readable final control report
- `scripts/final_operator_brief.py` (15305 bytes, sha256 `06367d7eddaf62ef...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (9555 bytes, sha256 `bdda68a06465e32c...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (3985 bytes, sha256 `4e035a35fea178fa...`) - Human-readable final operator brief
- `scripts/final_launch_plan.py` (17492 bytes, sha256 `dc2766d5f424c1ac...`) - No-secret final launch phase plan
- `docs/assets/final-launch-plan.json` (5690 bytes, sha256 `501171d2523f4e86...`) - Machine-readable final launch plan
- `docs/assets/final-launch-plan.md` (4596 bytes, sha256 `7747b3177be9562a...`) - Human-readable final launch plan
- `scripts/final_rehearsal.py` (18265 bytes, sha256 `7b0b844fcce35158...`) - No-secret final submission rehearsal checklist
- `docs/assets/final-rehearsal-checklist.json` (17103 bytes, sha256 `08c3a59bf876e65f...`) - Machine-readable final rehearsal checklist
- `docs/assets/final-rehearsal-checklist.md` (7404 bytes, sha256 `539ebdcfa16a58e6...`) - Human-readable final rehearsal checklist
- `scripts/submission_audit.py` (20524 bytes, sha256 `877f7e7c3e2f26d0...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (5925 bytes, sha256 `87dbf65125a12a80...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (4459 bytes, sha256 `8920524e7dcee197...`) - Human-readable submission audit report
- `scripts/devpost_submission_receipt.py` (9209 bytes, sha256 `76c55e8ff1aeaa52...`) - Public-safe Devpost submission receipt generator
- `docs/assets/devpost-submission-receipt.json` (1298 bytes, sha256 `bf646cf968665c8c...`) - Machine-readable Devpost submission receipt
- `docs/assets/devpost-submission-receipt.md` (996 bytes, sha256 `af2fa18349d5c017...`) - Human-readable Devpost submission receipt
- `docs/evidence_package.md` (19912 bytes, sha256 `2b1f38e28a063175...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4089 bytes, sha256 `735b9188feae74ea...`) - Verified-claim boundary
- `docs/verification.md` (9739 bytes, sha256 `07510fdc20821d14...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (352 bytes, sha256 `d250e97bb0a653fa...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (11051 bytes, sha256 `96f50d76bfd2fc1c...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `53223a9ab53f7a22...`) - Human-readable secret scan report
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/b2_key_scope_checklist.py` (17240 bytes, sha256 `bb1e6140f10aa3ac...`) - No-secret Backblaze B2 application key scope checklist
- `docs/assets/b2-key-scope-checklist.json` (8235 bytes, sha256 `2c8544973e7ea8f3...`) - Machine-readable B2 key scope checklist
- `docs/assets/b2-key-scope-checklist.md` (4527 bytes, sha256 `2fa660a7e0e19d0e...`) - Human-readable B2 key scope checklist
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (9322 bytes, sha256 `2c9aa63baa5f2640...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (4315 bytes, sha256 `5f025c40cb740383...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2197 bytes, sha256 `d254843a1e684df5...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (15789 bytes, sha256 `a885c927c1bb09ee...`) - Local final credential env wizard
- `scripts/post_credential_live_proof.py` (17108 bytes, sha256 `aec873007c4cb809...`) - Post-credential live proof sequence runner
- `docs/assets/post-credential-live-proof-plan.json` (9127 bytes, sha256 `c98417e979fac562...`) - Machine-readable post-credential live proof plan
- `docs/assets/post-credential-live-proof-plan.md` (5992 bytes, sha256 `4b7bd91cb02a170a...`) - Human-readable post-credential live proof plan
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8661 bytes, sha256 `d38ad138a2ca0d78...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3893 bytes, sha256 `19e0e6385337f6ee...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1768 bytes, sha256 `39fcc67011a5eaa9...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (18340 bytes, sha256 `8c15f362298fa92c...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (7826 bytes, sha256 `79debb92d62348ad...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (3867 bytes, sha256 `e3d2ef5dd86dfe33...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (5814 bytes, sha256 `c6b9dc2fc9d7c670...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (4000 bytes, sha256 `3800b9a0950779d0...`) - Registration and submission plan
- `tasks.json` (63266 bytes, sha256 `6ab8ae4d70e20b68...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (741074 bytes, sha256 `5d6f68f7a4a2fdee...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
