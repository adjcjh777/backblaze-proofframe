# ProofFrame Submission Bundle

Created: `2026-07-03T10:57:05Z`
Repository: https://github.com/adjcjh777/backblaze-proofframe
Public mock demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Devpost packet mode: `post_live_verified`
Final gate mode: `pre_live_safe`
Final gate ready: `false`

## Current Gate

- Tasks: 3 done / 6 required; 0 doing, 3 blocked, 0 todo.
- Live evidence: `verified`
- Devpost copy packet: `post_live_packet_ready`
- Final reports: `incomplete`
- Post-Devpost closeout: `incomplete`

## Next Actions

- Run the final submission audit after live proofs are captured.
- Run the final secret scan before recording or submitting.
- Submit the Devpost project after every preceding gate is done.
- Run the final submission audit and capture a passing report.
- Capture the public-safe Devpost submission receipt after submitting.

## Artifacts

- `README.md` (16355 bytes, sha256 `3ef86d329740af0a...`) - Core public project overview
- `Dockerfile` (522 bytes, sha256 `6764f101746a802d...`) - Docker deployment image contract
- `.dockerignore` (214 bytes, sha256 `29e12906fc6e9af3...`) - Docker build context secret exclusion policy
- `scripts/docker_smoke.py` (13273 bytes, sha256 `4e900d7da53d329c...`) - Docker build and API smoke verifier
- `docs/assets/docker-smoke-report.json` (11194 bytes, sha256 `c62c9e2ca07acaee...`) - Machine-readable Docker smoke report
- `docs/assets/docker-smoke-report.md` (1421 bytes, sha256 `b985393e5d0961db...`) - Human-readable Docker smoke report
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (6177 bytes, sha256 `d0d24f751da92adc...`) - Implementation specification
- `docs/deployment.md` (5387 bytes, sha256 `6586ed6a5038d882...`) - Public demo deployment runbook
- `docs/devpost_draft.md` (5661 bytes, sha256 `8b1c3d412edaa055...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6002 bytes, sha256 `1c326d8aee272877...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (4771 bytes, sha256 `c54137893c728e9c...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `5b7c1f2277d121b8...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `cc2e49b18ae1776d...`) - Human-readable Devpost event snapshot
- `scripts/agent_handoff_check.py` (14559 bytes, sha256 `3ef180b6a92eb987...`) - Agent Bus and Codex handoff path checker
- `docs/assets/agent-handoff-report.json` (2253 bytes, sha256 `d4912010b69b8a18...`) - Machine-readable Agent handoff report
- `docs/assets/agent-handoff-report.md` (1571 bytes, sha256 `04348bf2d799f2f0...`) - Human-readable Agent handoff report
- `scripts/public_space_sync.py` (86276 bytes, sha256 `7e27db5e8c158e5a...`) - Public Hugging Face Space sync verifier
- `docs/assets/public-space-sync-report.json` (20577 bytes, sha256 `b1acbd77175e85fa...`) - Machine-readable public Space sync report
- `docs/assets/public-space-sync-report.md` (8668 bytes, sha256 `4200d3d31c1764e0...`) - Human-readable public Space sync report
- `scripts/public_space_upload.py` (12920 bytes, sha256 `38e4c3e665478e0b...`) - No-secret public Hugging Face Space upload helper
- `docs/assets/public-space-upload-report.json` (4136 bytes, sha256 `07bb9cd0a8c57a54...`) - Machine-readable public Space upload report
- `docs/assets/public-space-upload-report.md` (1372 bytes, sha256 `d36d78b8ba7df34f...`) - Human-readable public Space upload report
- `scripts/public_demo_screenshot.py` (8926 bytes, sha256 `3eb5b0a003e383dd...`) - Public judge-mode screenshot verifier
- `docs/assets/public-demo-screenshot-report.json` (2421 bytes, sha256 `e8ce08735a86a920...`) - Machine-readable public screenshot report
- `docs/assets/public-demo-screenshot-report.md` (1418 bytes, sha256 `dce44c3bc2188131...`) - Human-readable public screenshot report
- `scripts/devpost_form_kit.py` (12821 bytes, sha256 `7ec65aed60da6f9d...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (11927 bytes, sha256 `abd95b222afcfa63...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (6951 bytes, sha256 `b9734e0ccaee09fd...`) - Human-readable Devpost form kit
- `scripts/devpost_submission_preview.py` (17329 bytes, sha256 `28ed8703ca6479fc...`) - One-page claim-safe Devpost preview
- `docs/assets/devpost-submission-preview.json` (10306 bytes, sha256 `dfb2c54c3fc4be15...`) - Machine-readable Devpost preview
- `docs/assets/devpost-submission-preview.md` (4486 bytes, sha256 `777c62d66a904aa9...`) - Human-readable Devpost preview
- `scripts/devpost_submission_checklist.py` (11257 bytes, sha256 `32be583ec76fe1b0...`) - No-secret final Devpost web submission checklist
- `docs/assets/devpost-submission-checklist.json` (16051 bytes, sha256 `927b486ae9593604...`) - Machine-readable final Devpost submission checklist
- `docs/assets/devpost-submission-checklist.md` (8932 bytes, sha256 `067eec872ecd5359...`) - Human-readable final Devpost submission checklist
- `scripts/judge_brief.py` (10583 bytes, sha256 `d50c177f1bb8af81...`) - Public-safe 30-second judge brief
- `docs/assets/judge-brief.json` (3899 bytes, sha256 `034de9e6c5390ef2...`) - Machine-readable judge brief
- `docs/assets/judge-brief.md` (3162 bytes, sha256 `fc883adfa1d36455...`) - Human-readable judge brief
- `scripts/judge_crosswalk.py` (18865 bytes, sha256 `c70d6de303ee5229...`) - Official criteria to evidence crosswalk
- `docs/assets/judge-crosswalk.json` (9274 bytes, sha256 `e9dca3802f228c9a...`) - Machine-readable judge crosswalk
- `docs/assets/judge-crosswalk.md` (5503 bytes, sha256 `63eee290b7b0d5a1...`) - Human-readable judge crosswalk
- `scripts/judge_decision_brief.py` (15695 bytes, sha256 `9ad054c933e47481...`) - Public-safe judge decision brief builder
- `docs/assets/judge-decision-brief.json` (8118 bytes, sha256 `3572673cee7caa82...`) - Machine-readable judge decision brief
- `docs/assets/judge-decision-brief.md` (3786 bytes, sha256 `fcb9568f78395791...`) - Human-readable judge decision brief
- `scripts/judge_evidence_index.py` (14164 bytes, sha256 `286b4970bcfa5e36...`) - Public-safe judge evidence index builder
- `docs/assets/judge-evidence-index.json` (10445 bytes, sha256 `150904ffb5e6c8c8...`) - Machine-readable judge evidence index
- `docs/assets/judge-evidence-index.md` (4470 bytes, sha256 `a7745bae615def94...`) - Human-readable judge evidence index
- `apps/web/index.html` (69407 bytes, sha256 `9259d14a3b671a97...`) - Browser proof ledger UI
- `docs/demo_script.md` (5856 bytes, sha256 `fbabf38ff87cca9b...`) - Video shot list and narration
- `scripts/demo_storyboard.py` (11025 bytes, sha256 `e5d75956d6d4a20b...`) - Machine-checked demo video storyboard
- `docs/assets/demo-storyboard.json` (4349 bytes, sha256 `6aadb8e35eaaaeae...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2556 bytes, sha256 `c716de46e8c342e1...`) - Human-readable demo storyboard
- `scripts/demo_video_draft.py` (12209 bytes, sha256 `953f4b118ca2165f...`) - Mock demo video draft builder
- `docs/assets/demo-video-draft.json` (2459 bytes, sha256 `8b79f792ba877123...`) - Machine-readable demo video draft report
- `docs/assets/demo-video-draft.md` (1562 bytes, sha256 `1b041908b73020d6...`) - Human-readable demo video draft report
- `docs/assets/proofframe-demo-draft.mp4` (747727 bytes, sha256 `7c943ee37b96a865...`) - Public-safe mock demo video draft
- `scripts/final_video_publish_kit.py` (12256 bytes, sha256 `651a73d338ae1f4b...`) - Final public video upload copy and gate kit
- `docs/assets/final-video-publish-kit.json` (5364 bytes, sha256 `8fef093281f7f925...`) - Machine-readable final video publish kit
- `docs/assets/final-video-publish-kit.md` (2727 bytes, sha256 `817fd5151fa4f608...`) - Human-readable final video publish kit
- `scripts/public_video_check.py` (14919 bytes, sha256 `ca4e127967c6b81d...`) - Public demo video URL verifier
- `docs/assets/public-video-check.json` (2971 bytes, sha256 `d57a96c08899f558...`) - Machine-readable public video check
- `docs/assets/public-video-check.md` (1697 bytes, sha256 `4bddd566071706f5...`) - Human-readable public video check
- `docs/sponsor_fit_matrix.md` (3072 bytes, sha256 `88511a028afa98ae...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (8402 bytes, sha256 `694bab2253dbe040...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1604 bytes, sha256 `17a417abe85aa233...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1093 bytes, sha256 `d20d7fd6d0523cbf...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (25369 bytes, sha256 `f5929505ac848be4...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (11275 bytes, sha256 `9f1fe4537b73e543...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4275 bytes, sha256 `145cdbe2c4f506cf...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (32820 bytes, sha256 `609c37fdb8ee286c...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (23118 bytes, sha256 `3e94e0a41456ca2c...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (6956 bytes, sha256 `bdb063d64eb7fab4...`) - Human-readable final control report
- `scripts/final_closeout_status.py` (20820 bytes, sha256 `21b5ed7e5ca1d4c8...`) - No-secret final closeout status report
- `docs/assets/final-closeout-status.json` (17250 bytes, sha256 `945405d6f01a4c39...`) - Machine-readable final closeout status
- `docs/assets/final-closeout-status.md` (2405 bytes, sha256 `c9f5736cbb60ae56...`) - Human-readable final closeout status
- `scripts/final_operator_brief.py` (16863 bytes, sha256 `8c3c3296fe7b3d8a...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (9353 bytes, sha256 `36c41daf843cad43...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (3781 bytes, sha256 `ed8d6eef648772bf...`) - Human-readable final operator brief
- `scripts/final_launch_plan.py` (17629 bytes, sha256 `80b20a0eaad6af0c...`) - No-secret final launch phase plan
- `docs/assets/final-launch-plan.json` (5827 bytes, sha256 `1337b4416a94656f...`) - Machine-readable final launch plan
- `docs/assets/final-launch-plan.md` (4724 bytes, sha256 `743ccadac2efd2a5...`) - Human-readable final launch plan
- `scripts/final_rehearsal.py` (18402 bytes, sha256 `bda6d635c43825cb...`) - No-secret final submission rehearsal checklist
- `docs/assets/final-rehearsal-checklist.json` (16066 bytes, sha256 `738429e7996c8be9...`) - Machine-readable final rehearsal checklist
- `docs/assets/final-rehearsal-checklist.md` (7420 bytes, sha256 `b97bed749fe7982e...`) - Human-readable final rehearsal checklist
- `scripts/submission_audit.py` (21156 bytes, sha256 `3069fdbc34c595a1...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (4622 bytes, sha256 `24685e39d642daeb...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (3560 bytes, sha256 `4dace210a836a2f7...`) - Human-readable submission audit report
- `scripts/devpost_submission_receipt.py` (9209 bytes, sha256 `76c55e8ff1aeaa52...`) - Public-safe Devpost submission receipt generator
- `docs/assets/devpost-submission-receipt.json` (1298 bytes, sha256 `d4114b8de6fd9097...`) - Machine-readable Devpost submission receipt
- `docs/assets/devpost-submission-receipt.md` (996 bytes, sha256 `16d869190b5d872a...`) - Human-readable Devpost submission receipt
- `docs/evidence_package.md` (21768 bytes, sha256 `bfb1886c2787f1f4...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4211 bytes, sha256 `2330b8a47e183213...`) - Verified-claim boundary
- `docs/verification.md` (13318 bytes, sha256 `6cbc50930070d3e3...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (445 bytes, sha256 `3bc106fdc3d05ed3...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (12089 bytes, sha256 `0a39efa0493e835c...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `87d4637d03de15bc...`) - Human-readable secret scan report
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/b2_key_scope_checklist.py` (17240 bytes, sha256 `bb1e6140f10aa3ac...`) - No-secret Backblaze B2 application key scope checklist
- `docs/assets/b2-key-scope-checklist.json` (8235 bytes, sha256 `b72f6e8b2cc55e1f...`) - Machine-readable B2 key scope checklist
- `docs/assets/b2-key-scope-checklist.md` (4527 bytes, sha256 `2fa660a7e0e19d0e...`) - Human-readable B2 key scope checklist
- `scripts/genblaze_contract_check.py` (12868 bytes, sha256 `71a670029756c3d9...`) - No-secret Genblaze/B2 SDK contract checker
- `docs/assets/genblaze-contract-report.json` (6720 bytes, sha256 `cf8c3d3cf2a4cc9f...`) - Machine-readable Genblaze SDK contract report
- `docs/assets/genblaze-contract-report.md` (3555 bytes, sha256 `074df863c08566eb...`) - Human-readable Genblaze SDK contract report
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (11256 bytes, sha256 `d0451cd1140ed8bf...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (5045 bytes, sha256 `65647e4beff3436b...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2519 bytes, sha256 `96dc129f7421fcf0...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (19616 bytes, sha256 `08402ff430d0771a...`) - Local final credential env wizard
- `scripts/post_credential_live_proof.py` (18222 bytes, sha256 `5b565d0b4d9f1e2c...`) - Post-credential live proof sequence runner
- `docs/assets/post-credential-live-proof-plan.json` (8440 bytes, sha256 `93045ca354625be6...`) - Machine-readable post-credential live proof plan
- `docs/assets/post-credential-live-proof-plan.md` (2785 bytes, sha256 `8c53e6044ba05028...`) - Human-readable post-credential live proof plan
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8661 bytes, sha256 `d38ad138a2ca0d78...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3705 bytes, sha256 `ffdbe4385a652df3...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1590 bytes, sha256 `ec18b44ebea848cb...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (18340 bytes, sha256 `8c15f362298fa92c...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (7826 bytes, sha256 `b5d131035dbd114b...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (3867 bytes, sha256 `e3d2ef5dd86dfe33...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (7186 bytes, sha256 `8943e023f0136a13...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (4000 bytes, sha256 `b702417f1345fe39...`) - Registration and submission plan
- `tasks.json` (73132 bytes, sha256 `bacae2a51abbcc9a...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (741074 bytes, sha256 `5d6f68f7a4a2fdee...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
