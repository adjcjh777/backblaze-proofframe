# ProofFrame Submission Bundle

Created: `2026-07-03T05:02:40Z`
Repository: https://github.com/adjcjh777/backblaze-proofframe
Public mock demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Devpost packet mode: `pre_live_safe`
Final gate mode: `pre_live_safe`
Final gate ready: `false`

## Current Gate

- Tasks: 2 done / 6 required; 0 doing, 1 blocked, 3 todo.
- Live evidence: `missing`
- Devpost copy packet: `pre_live_packet_pending`
- Final reports: `incomplete`
- Post-Devpost closeout: `incomplete`

## Next Actions

- Run a live Genblaze generation proof and capture provider metadata.
- Run the final submission audit after live proofs are captured.
- Run the final secret scan before recording or submitting.
- Submit the Devpost project after every preceding gate is done.
- Capture final live proof evidence JSON.

## Artifacts

- `README.md` (16154 bytes, sha256 `942591160b27b28d...`) - Core public project overview
- `Dockerfile` (522 bytes, sha256 `6764f101746a802d...`) - Docker deployment image contract
- `.dockerignore` (214 bytes, sha256 `29e12906fc6e9af3...`) - Docker build context secret exclusion policy
- `scripts/docker_smoke.py` (13273 bytes, sha256 `4e900d7da53d329c...`) - Docker build and API smoke verifier
- `docs/assets/docker-smoke-report.json` (11194 bytes, sha256 `c62c9e2ca07acaee...`) - Machine-readable Docker smoke report
- `docs/assets/docker-smoke-report.md` (1421 bytes, sha256 `b985393e5d0961db...`) - Human-readable Docker smoke report
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (6177 bytes, sha256 `d0d24f751da92adc...`) - Implementation specification
- `docs/deployment.md` (5387 bytes, sha256 `6586ed6a5038d882...`) - Public demo deployment runbook
- `docs/devpost_draft.md` (5661 bytes, sha256 `8b1c3d412edaa055...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6325 bytes, sha256 `229e74455cb34371...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (5203 bytes, sha256 `1420be897b97f51c...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `5b7c1f2277d121b8...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `cc2e49b18ae1776d...`) - Human-readable Devpost event snapshot
- `scripts/agent_handoff_check.py` (14559 bytes, sha256 `3ef180b6a92eb987...`) - Agent Bus and Codex handoff path checker
- `docs/assets/agent-handoff-report.json` (2253 bytes, sha256 `d4912010b69b8a18...`) - Machine-readable Agent handoff report
- `docs/assets/agent-handoff-report.md` (1571 bytes, sha256 `04348bf2d799f2f0...`) - Human-readable Agent handoff report
- `scripts/public_space_sync.py` (85191 bytes, sha256 `dc578f8483e01432...`) - Public Hugging Face Space sync verifier
- `docs/assets/public-space-sync-report.json` (20605 bytes, sha256 `027085e3585e9c00...`) - Machine-readable public Space sync report
- `docs/assets/public-space-sync-report.md` (8682 bytes, sha256 `d22b8803304c209d...`) - Human-readable public Space sync report
- `scripts/public_space_upload.py` (12920 bytes, sha256 `38e4c3e665478e0b...`) - No-secret public Hugging Face Space upload helper
- `docs/assets/public-space-upload-report.json` (4164 bytes, sha256 `201ef783d30a9af2...`) - Machine-readable public Space upload report
- `docs/assets/public-space-upload-report.md` (1372 bytes, sha256 `86f01f36e2a1e708...`) - Human-readable public Space upload report
- `scripts/public_demo_screenshot.py` (8926 bytes, sha256 `3eb5b0a003e383dd...`) - Public judge-mode screenshot verifier
- `docs/assets/public-demo-screenshot-report.json` (2421 bytes, sha256 `e8ce08735a86a920...`) - Machine-readable public screenshot report
- `docs/assets/public-demo-screenshot-report.md` (1418 bytes, sha256 `dce44c3bc2188131...`) - Human-readable public screenshot report
- `scripts/devpost_form_kit.py` (12821 bytes, sha256 `7ec65aed60da6f9d...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (12511 bytes, sha256 `dd10841a80033623...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (7524 bytes, sha256 `96ffdfcb212f4041...`) - Human-readable Devpost form kit
- `scripts/devpost_submission_preview.py` (17329 bytes, sha256 `28ed8703ca6479fc...`) - One-page claim-safe Devpost preview
- `docs/assets/devpost-submission-preview.json` (11037 bytes, sha256 `a2b0918ea5dd5473...`) - Machine-readable Devpost preview
- `docs/assets/devpost-submission-preview.md` (5139 bytes, sha256 `737654b10b4cc6c8...`) - Human-readable Devpost preview
- `scripts/devpost_submission_checklist.py` (11257 bytes, sha256 `32be583ec76fe1b0...`) - No-secret final Devpost web submission checklist
- `docs/assets/devpost-submission-checklist.json` (16468 bytes, sha256 `ee81e96f5cc3f31d...`) - Machine-readable final Devpost submission checklist
- `docs/assets/devpost-submission-checklist.md` (9358 bytes, sha256 `294d1a36fbd029e3...`) - Human-readable final Devpost submission checklist
- `scripts/judge_brief.py` (9983 bytes, sha256 `9b62f07ba6a5f987...`) - Public-safe 30-second judge brief
- `docs/assets/judge-brief.json` (3748 bytes, sha256 `2ac946ff0bd4b8f2...`) - Machine-readable judge brief
- `docs/assets/judge-brief.md` (3015 bytes, sha256 `b6315d9786e2e1c8...`) - Human-readable judge brief
- `scripts/judge_crosswalk.py` (17642 bytes, sha256 `d9153174e330fd53...`) - Official criteria to evidence crosswalk
- `docs/assets/judge-crosswalk.json` (9610 bytes, sha256 `ed9d9e3b783d86f9...`) - Machine-readable judge crosswalk
- `docs/assets/judge-crosswalk.md` (5748 bytes, sha256 `a5fd6cc58bbd5c2d...`) - Human-readable judge crosswalk
- `scripts/judge_decision_brief.py` (15000 bytes, sha256 `b24d679416d1c743...`) - Public-safe judge decision brief builder
- `docs/assets/judge-decision-brief.json` (8103 bytes, sha256 `67a6c303908a828e...`) - Machine-readable judge decision brief
- `docs/assets/judge-decision-brief.md` (3782 bytes, sha256 `59b9604a77605013...`) - Human-readable judge decision brief
- `scripts/judge_evidence_index.py` (13831 bytes, sha256 `efbf5dee17eab7f8...`) - Public-safe judge evidence index builder
- `docs/assets/judge-evidence-index.json` (10406 bytes, sha256 `745f687682cd3546...`) - Machine-readable judge evidence index
- `docs/assets/judge-evidence-index.md` (4432 bytes, sha256 `ead603365df75bfb...`) - Human-readable judge evidence index
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
- `docs/assets/final-video-publish-kit.json` (5366 bytes, sha256 `058abdac1fb9919c...`) - Machine-readable final video publish kit
- `docs/assets/final-video-publish-kit.md` (2727 bytes, sha256 `0ac4b78c3e1daa51...`) - Human-readable final video publish kit
- `scripts/public_video_check.py` (14919 bytes, sha256 `ca4e127967c6b81d...`) - Public demo video URL verifier
- `docs/assets/public-video-check.json` (2977 bytes, sha256 `7a03b5ebf3c56060...`) - Machine-readable public video check
- `docs/assets/public-video-check.md` (1701 bytes, sha256 `990cd0e1a0bd4814...`) - Human-readable public video check
- `docs/sponsor_fit_matrix.md` (3072 bytes, sha256 `88511a028afa98ae...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (24703 bytes, sha256 `216032966d48421c...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (11400 bytes, sha256 `71c84d75efaf66e1...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4416 bytes, sha256 `74bb2693fe711802...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (32820 bytes, sha256 `a329dfe6c8baf86e...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (23559 bytes, sha256 `324a5a2ee297ccba...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (7093 bytes, sha256 `9c1b6f9d4359a103...`) - Human-readable final control report
- `scripts/final_closeout_status.py` (20225 bytes, sha256 `4def3f76374999ca...`) - No-secret final closeout status report
- `docs/assets/final-closeout-status.json` (16314 bytes, sha256 `b7fad9dc17b56f17...`) - Machine-readable final closeout status
- `docs/assets/final-closeout-status.md` (2457 bytes, sha256 `f98ed29fc97c7352...`) - Human-readable final closeout status
- `scripts/final_operator_brief.py` (16925 bytes, sha256 `c5fbbdaa91046469...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (9681 bytes, sha256 `e7e577a626d289ee...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (4112 bytes, sha256 `1bd01020bf0bb901...`) - Human-readable final operator brief
- `scripts/final_launch_plan.py` (17629 bytes, sha256 `65548b4aa20d01f6...`) - No-secret final launch phase plan
- `docs/assets/final-launch-plan.json` (5945 bytes, sha256 `9f87b9c73fb442fc...`) - Machine-readable final launch plan
- `docs/assets/final-launch-plan.md` (4850 bytes, sha256 `698597015095c4fa...`) - Human-readable final launch plan
- `scripts/final_rehearsal.py` (18402 bytes, sha256 `1a5040ec43f1e7d3...`) - No-secret final submission rehearsal checklist
- `docs/assets/final-rehearsal-checklist.json` (16576 bytes, sha256 `eb44cdcf4fa9c980...`) - Machine-readable final rehearsal checklist
- `docs/assets/final-rehearsal-checklist.md` (7541 bytes, sha256 `a4bfb5a89729158c...`) - Human-readable final rehearsal checklist
- `scripts/submission_audit.py` (21101 bytes, sha256 `26bc52718e9b4ceb...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (5490 bytes, sha256 `987e09a1962f49d7...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (4162 bytes, sha256 `81aac7af98cc058d...`) - Human-readable submission audit report
- `scripts/devpost_submission_receipt.py` (9209 bytes, sha256 `76c55e8ff1aeaa52...`) - Public-safe Devpost submission receipt generator
- `docs/assets/devpost-submission-receipt.json` (1298 bytes, sha256 `bf646cf968665c8c...`) - Machine-readable Devpost submission receipt
- `docs/assets/devpost-submission-receipt.md` (996 bytes, sha256 `af2fa18349d5c017...`) - Human-readable Devpost submission receipt
- `docs/evidence_package.md` (21792 bytes, sha256 `4b174479858245b1...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4092 bytes, sha256 `82671cee60b14437...`) - Verified-claim boundary
- `docs/verification.md` (13317 bytes, sha256 `7ead904f085f516e...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (438 bytes, sha256 `4151766ec63bb19c...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (12039 bytes, sha256 `2e45551e690e9f5f...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `f53459a851e83068...`) - Human-readable secret scan report
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/b2_key_scope_checklist.py` (17240 bytes, sha256 `bb1e6140f10aa3ac...`) - No-secret Backblaze B2 application key scope checklist
- `docs/assets/b2-key-scope-checklist.json` (8235 bytes, sha256 `b72f6e8b2cc55e1f...`) - Machine-readable B2 key scope checklist
- `docs/assets/b2-key-scope-checklist.md` (4527 bytes, sha256 `2fa660a7e0e19d0e...`) - Human-readable B2 key scope checklist
- `scripts/genblaze_contract_check.py` (12868 bytes, sha256 `71a670029756c3d9...`) - No-secret Genblaze/B2 SDK contract checker
- `docs/assets/genblaze-contract-report.json` (6720 bytes, sha256 `a7a9f76144112ff1...`) - Machine-readable Genblaze SDK contract report
- `docs/assets/genblaze-contract-report.md` (3555 bytes, sha256 `6f47c4adfda40849...`) - Human-readable Genblaze SDK contract report
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (10611 bytes, sha256 `9c928d118f3981af...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (4892 bytes, sha256 `47891ba90e70fc02...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2361 bytes, sha256 `6242dff9129b6016...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (19463 bytes, sha256 `2652addc82b9531f...`) - Local final credential env wizard
- `scripts/post_credential_live_proof.py` (18183 bytes, sha256 `69c506304ff37f99...`) - Post-credential live proof sequence runner
- `docs/assets/post-credential-live-proof-plan.json` (8440 bytes, sha256 `93045ca354625be6...`) - Machine-readable post-credential live proof plan
- `docs/assets/post-credential-live-proof-plan.md` (2785 bytes, sha256 `8c53e6044ba05028...`) - Human-readable post-credential live proof plan
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8661 bytes, sha256 `d38ad138a2ca0d78...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3893 bytes, sha256 `ebd13ea05535dba2...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1768 bytes, sha256 `39fcc67011a5eaa9...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (18340 bytes, sha256 `8c15f362298fa92c...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (7826 bytes, sha256 `568ec3fed5266f57...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (3867 bytes, sha256 `e3d2ef5dd86dfe33...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (6535 bytes, sha256 `412a8f0bde3cb919...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (4000 bytes, sha256 `b702417f1345fe39...`) - Registration and submission plan
- `tasks.json` (73153 bytes, sha256 `006a47a6d4679d8c...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (741074 bytes, sha256 `5d6f68f7a4a2fdee...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
