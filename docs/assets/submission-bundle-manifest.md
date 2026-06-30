# ProofFrame Submission Bundle

Created: `2026-06-30T10:37:46Z`
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

- `README.md` (15754 bytes, sha256 `363988b5191f54bf...`) - Core public project overview
- `Dockerfile` (522 bytes, sha256 `6764f101746a802d...`) - Docker deployment image contract
- `.dockerignore` (214 bytes, sha256 `29e12906fc6e9af3...`) - Docker build context secret exclusion policy
- `scripts/docker_smoke.py` (13273 bytes, sha256 `4e900d7da53d329c...`) - Docker build and API smoke verifier
- `docs/assets/docker-smoke-report.json` (11194 bytes, sha256 `c62c9e2ca07acaee...`) - Machine-readable Docker smoke report
- `docs/assets/docker-smoke-report.md` (1421 bytes, sha256 `b985393e5d0961db...`) - Human-readable Docker smoke report
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (6177 bytes, sha256 `d0d24f751da92adc...`) - Implementation specification
- `docs/deployment.md` (5387 bytes, sha256 `6586ed6a5038d882...`) - Public demo deployment runbook
- `docs/devpost_draft.md` (5613 bytes, sha256 `e08e3f25a04bab48...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6270 bytes, sha256 `92b06cc47f68c410...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (5159 bytes, sha256 `00e03e34b62dfdfc...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `626886a6fcee6199...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `b0389eded1537669...`) - Human-readable Devpost event snapshot
- `scripts/agent_handoff_check.py` (14559 bytes, sha256 `3ef180b6a92eb987...`) - Agent Bus and Codex handoff path checker
- `docs/assets/agent-handoff-report.json` (2253 bytes, sha256 `87711b3b8a5b1515...`) - Machine-readable Agent handoff report
- `docs/assets/agent-handoff-report.md` (1571 bytes, sha256 `b64f0c7769d5867c...`) - Human-readable Agent handoff report
- `scripts/public_space_sync.py` (84964 bytes, sha256 `52280330d9e7605b...`) - Public Hugging Face Space sync verifier
- `docs/assets/public-space-sync-report.json` (20606 bytes, sha256 `e315ee991f39586e...`) - Machine-readable public Space sync report
- `docs/assets/public-space-sync-report.md` (8673 bytes, sha256 `68fb795359bcfd69...`) - Human-readable public Space sync report
- `scripts/public_space_upload.py` (12920 bytes, sha256 `38e4c3e665478e0b...`) - No-secret public Hugging Face Space upload helper
- `docs/assets/public-space-upload-report.json` (4150 bytes, sha256 `588c3fb8d14733f4...`) - Machine-readable public Space upload report
- `docs/assets/public-space-upload-report.md` (1372 bytes, sha256 `0b35af876a813c9c...`) - Human-readable public Space upload report
- `scripts/public_demo_screenshot.py` (8926 bytes, sha256 `3eb5b0a003e383dd...`) - Public judge-mode screenshot verifier
- `docs/assets/public-demo-screenshot-report.json` (2421 bytes, sha256 `e8ce08735a86a920...`) - Machine-readable public screenshot report
- `docs/assets/public-demo-screenshot-report.md` (1418 bytes, sha256 `dce44c3bc2188131...`) - Human-readable public screenshot report
- `scripts/devpost_form_kit.py` (12830 bytes, sha256 `b0173e698f4c3629...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (12483 bytes, sha256 `96196519c036e0aa...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (7496 bytes, sha256 `f6beeb3fe9e7f94d...`) - Human-readable Devpost form kit
- `scripts/devpost_submission_preview.py` (17329 bytes, sha256 `28ed8703ca6479fc...`) - One-page claim-safe Devpost preview
- `docs/assets/devpost-submission-preview.json` (11611 bytes, sha256 `68a1f9fe85695031...`) - Machine-readable Devpost preview
- `docs/assets/devpost-submission-preview.md` (5407 bytes, sha256 `760d948b804fbe97...`) - Human-readable Devpost preview
- `scripts/devpost_submission_checklist.py` (11252 bytes, sha256 `78b8e1b70da428fd...`) - No-secret final Devpost web submission checklist
- `docs/assets/devpost-submission-checklist.json` (16428 bytes, sha256 `bea72137b1e7df2a...`) - Machine-readable final Devpost submission checklist
- `docs/assets/devpost-submission-checklist.md` (9319 bytes, sha256 `e45546c7334e78e3...`) - Human-readable final Devpost submission checklist
- `scripts/judge_brief.py` (9968 bytes, sha256 `605a72a56e24b330...`) - Public-safe 30-second judge brief
- `docs/assets/judge-brief.json` (3734 bytes, sha256 `257527084b2a6190...`) - Machine-readable judge brief
- `docs/assets/judge-brief.md` (3000 bytes, sha256 `e35af380276cc998...`) - Human-readable judge brief
- `scripts/judge_crosswalk.py` (17642 bytes, sha256 `d9153174e330fd53...`) - Official criteria to evidence crosswalk
- `docs/assets/judge-crosswalk.json` (10219 bytes, sha256 `26a13b2bb84cbb1f...`) - Machine-readable judge crosswalk
- `docs/assets/judge-crosswalk.md` (6157 bytes, sha256 `06ba78a107ac1b81...`) - Human-readable judge crosswalk
- `scripts/judge_decision_brief.py` (15000 bytes, sha256 `b24d679416d1c743...`) - Public-safe judge decision brief builder
- `docs/assets/judge-decision-brief.json` (8148 bytes, sha256 `d12065a387542430...`) - Machine-readable judge decision brief
- `docs/assets/judge-decision-brief.md` (3822 bytes, sha256 `21dd39e3c6c216e6...`) - Human-readable judge decision brief
- `scripts/judge_evidence_index.py` (13831 bytes, sha256 `efbf5dee17eab7f8...`) - Public-safe judge evidence index builder
- `docs/assets/judge-evidence-index.json` (10456 bytes, sha256 `bc40b8de678977d8...`) - Machine-readable judge evidence index
- `docs/assets/judge-evidence-index.md` (4473 bytes, sha256 `5d31c725d8910807...`) - Human-readable judge evidence index
- `apps/web/index.html` (69407 bytes, sha256 `9259d14a3b671a97...`) - Browser proof ledger UI
- `docs/demo_script.md` (5856 bytes, sha256 `fbabf38ff87cca9b...`) - Video shot list and narration
- `scripts/demo_storyboard.py` (11025 bytes, sha256 `e5d75956d6d4a20b...`) - Machine-checked demo video storyboard
- `docs/assets/demo-storyboard.json` (4514 bytes, sha256 `192f9dc7f55eaaa1...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2704 bytes, sha256 `3765ca34a5b53c7b...`) - Human-readable demo storyboard
- `scripts/demo_video_draft.py` (12209 bytes, sha256 `953f4b118ca2165f...`) - Mock demo video draft builder
- `docs/assets/demo-video-draft.json` (2459 bytes, sha256 `8b79f792ba877123...`) - Machine-readable demo video draft report
- `docs/assets/demo-video-draft.md` (1562 bytes, sha256 `1b041908b73020d6...`) - Human-readable demo video draft report
- `docs/assets/proofframe-demo-draft.mp4` (747727 bytes, sha256 `7c943ee37b96a865...`) - Public-safe mock demo video draft
- `scripts/final_video_publish_kit.py` (12256 bytes, sha256 `651a73d338ae1f4b...`) - Final public video upload copy and gate kit
- `docs/assets/final-video-publish-kit.json` (5366 bytes, sha256 `dee22bd22d1bef7f...`) - Machine-readable final video publish kit
- `docs/assets/final-video-publish-kit.md` (2727 bytes, sha256 `257da3cdc233f418...`) - Human-readable final video publish kit
- `scripts/public_video_check.py` (14919 bytes, sha256 `ca4e127967c6b81d...`) - Public demo video URL verifier
- `docs/assets/public-video-check.json` (2977 bytes, sha256 `7a03b5ebf3c56060...`) - Machine-readable public video check
- `docs/assets/public-video-check.md` (1701 bytes, sha256 `990cd0e1a0bd4814...`) - Human-readable public video check
- `docs/sponsor_fit_matrix.md` (3054 bytes, sha256 `cfa25f30bc5d2051...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (24519 bytes, sha256 `9cc121bb0fdc60ec...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (11377 bytes, sha256 `66417f6e0c2a15d9...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4390 bytes, sha256 `5be57ca5d9cab53d...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (32644 bytes, sha256 `6514cbdf2bfe8998...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (24359 bytes, sha256 `d2cf3949ba984a25...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (7087 bytes, sha256 `04a3aa516b2281bf...`) - Human-readable final control report
- `scripts/final_closeout_status.py` (19027 bytes, sha256 `fef94acd01449141...`) - No-secret final closeout status report
- `docs/assets/final-closeout-status.json` (12592 bytes, sha256 `ad81b91c1035a283...`) - Machine-readable final closeout status
- `docs/assets/final-closeout-status.md` (2467 bytes, sha256 `218ef848c482db51...`) - Human-readable final closeout status
- `scripts/final_operator_brief.py` (15912 bytes, sha256 `1e01afa36b48d9b8...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (10142 bytes, sha256 `4fb10abaa1f654cf...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (4526 bytes, sha256 `42f6a85163235033...`) - Human-readable final operator brief
- `scripts/final_launch_plan.py` (17492 bytes, sha256 `dc2766d5f424c1ac...`) - No-secret final launch phase plan
- `docs/assets/final-launch-plan.json` (5690 bytes, sha256 `2f74c7c3b603e512...`) - Machine-readable final launch plan
- `docs/assets/final-launch-plan.md` (4596 bytes, sha256 `7747b3177be9562a...`) - Human-readable final launch plan
- `scripts/final_rehearsal.py` (18265 bytes, sha256 `7b0b844fcce35158...`) - No-secret final submission rehearsal checklist
- `docs/assets/final-rehearsal-checklist.json` (17103 bytes, sha256 `ae398d43c900e40f...`) - Machine-readable final rehearsal checklist
- `docs/assets/final-rehearsal-checklist.md` (7404 bytes, sha256 `026e07a2a99bf616...`) - Human-readable final rehearsal checklist
- `scripts/submission_audit.py` (20684 bytes, sha256 `0f9a378c203bf7b6...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (5925 bytes, sha256 `cf1121ff24b443e8...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (4459 bytes, sha256 `dd3ed9a5c89591bf...`) - Human-readable submission audit report
- `scripts/devpost_submission_receipt.py` (9209 bytes, sha256 `76c55e8ff1aeaa52...`) - Public-safe Devpost submission receipt generator
- `docs/assets/devpost-submission-receipt.json` (1298 bytes, sha256 `bf646cf968665c8c...`) - Machine-readable Devpost submission receipt
- `docs/assets/devpost-submission-receipt.md` (996 bytes, sha256 `af2fa18349d5c017...`) - Human-readable Devpost submission receipt
- `docs/evidence_package.md` (21706 bytes, sha256 `82c45621486c175e...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4089 bytes, sha256 `735b9188feae74ea...`) - Verified-claim boundary
- `docs/verification.md` (12499 bytes, sha256 `c92fd26c877d5c5f...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (363 bytes, sha256 `fb5fad4f14e2b0ad...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (11871 bytes, sha256 `04215217a3a86930...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `4f93112233868372...`) - Human-readable secret scan report
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/b2_key_scope_checklist.py` (17240 bytes, sha256 `bb1e6140f10aa3ac...`) - No-secret Backblaze B2 application key scope checklist
- `docs/assets/b2-key-scope-checklist.json` (8235 bytes, sha256 `bd2b9e0e10706fe7...`) - Machine-readable B2 key scope checklist
- `docs/assets/b2-key-scope-checklist.md` (4527 bytes, sha256 `2fa660a7e0e19d0e...`) - Human-readable B2 key scope checklist
- `scripts/genblaze_contract_check.py` (12455 bytes, sha256 `58bf94bc7d994415...`) - No-secret Genblaze/B2 SDK contract checker
- `docs/assets/genblaze-contract-report.json` (5919 bytes, sha256 `0e30a126a206f946...`) - Machine-readable Genblaze SDK contract report
- `docs/assets/genblaze-contract-report.md` (3166 bytes, sha256 `6bb4bdb7c7a39915...`) - Human-readable Genblaze SDK contract report
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (9451 bytes, sha256 `39c8de0b58c132c3...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (4548 bytes, sha256 `08b0b09e257f6253...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2261 bytes, sha256 `17742c751ea63313...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (18690 bytes, sha256 `0fd664973da43311...`) - Local final credential env wizard
- `scripts/post_credential_live_proof.py` (17600 bytes, sha256 `244d2ecd9bb2f791...`) - Post-credential live proof sequence runner
- `docs/assets/post-credential-live-proof-plan.json` (8435 bytes, sha256 `30c716c29303c65a...`) - Machine-readable post-credential live proof plan
- `docs/assets/post-credential-live-proof-plan.md` (2780 bytes, sha256 `81ae854b8b7294a4...`) - Human-readable post-credential live proof plan
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8661 bytes, sha256 `d38ad138a2ca0d78...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3893 bytes, sha256 `ebd13ea05535dba2...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1768 bytes, sha256 `39fcc67011a5eaa9...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (18340 bytes, sha256 `8c15f362298fa92c...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (7826 bytes, sha256 `568ec3fed5266f57...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (3867 bytes, sha256 `e3d2ef5dd86dfe33...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (5814 bytes, sha256 `c6b9dc2fc9d7c670...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (4000 bytes, sha256 `b702417f1345fe39...`) - Registration and submission plan
- `tasks.json` (72478 bytes, sha256 `76c2bf237562c2ec...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (741074 bytes, sha256 `5d6f68f7a4a2fdee...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
