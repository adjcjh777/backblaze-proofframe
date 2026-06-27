# ProofFrame Submission Bundle

Created: `2026-06-27T17:49:06Z`
Repository: https://github.com/adjcjh777/backblaze-proofframe
Public mock demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Devpost packet mode: `pre_live_safe`
Final gate mode: `pre_live_safe`
Final gate ready: `false`

## Current Gate

- Tasks: 1 done / 6 required; 2 doing, 0 blocked, 3 todo.
- Live evidence: `missing`
- Devpost copy packet: `ready`

## Next Actions

- Run a live Backblaze B2 asset and manifest proof.
- Run a live Genblaze generation proof and capture provider metadata.
- Run the final submission audit after live proofs are captured.
- Run the final secret scan before recording or submitting.
- Submit the Devpost project after every preceding gate is done.

## Artifacts

- `README.md` (9129 bytes, sha256 `ee77ef246a365bc2...`) - Core public project overview
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (4874 bytes, sha256 `8320ef186af34075...`) - Implementation specification
- `docs/devpost_draft.md` (5621 bytes, sha256 `85588ba9e7178774...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6278 bytes, sha256 `fe9d64550737a5d7...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (5167 bytes, sha256 `5de4e82e0f3038c2...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `29fa3f02ce7720ae...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `74c8c2e8e85c2695...`) - Human-readable Devpost event snapshot
- `scripts/devpost_form_kit.py` (12830 bytes, sha256 `b0173e698f4c3629...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (12491 bytes, sha256 `4b9e0a7e8284e7a9...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (7504 bytes, sha256 `f0af423732a0613e...`) - Human-readable Devpost form kit
- `apps/web/index.html` (41224 bytes, sha256 `a22eeb7f79fbd372...`) - Browser proof ledger UI
- `docs/demo_script.md` (5690 bytes, sha256 `1a3128155b57c677...`) - Video shot list and narration
- `scripts/demo_storyboard.py` (11007 bytes, sha256 `dadfe2907f2c1ca5...`) - Machine-checked demo video storyboard
- `docs/assets/demo-storyboard.json` (4496 bytes, sha256 `04d655aa20ace836...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2686 bytes, sha256 `b5a03a0bd468630b...`) - Human-readable demo storyboard
- `docs/sponsor_fit_matrix.md` (3054 bytes, sha256 `cfa25f30bc5d2051...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (22811 bytes, sha256 `06ce9eb0b788dfee...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (10844 bytes, sha256 `303549ad89478b17...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4153 bytes, sha256 `fb635cd20fb0b791...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (22599 bytes, sha256 `aacce75156e06c77...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (14924 bytes, sha256 `c090b7179883f781...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (4496 bytes, sha256 `e4c877adf38192b4...`) - Human-readable final control report
- `scripts/final_operator_brief.py` (12395 bytes, sha256 `7c0f74b82fb8a162...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (5798 bytes, sha256 `cda13b8ab34e7d33...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (2917 bytes, sha256 `0e02a4ceb1b842e7...`) - Human-readable final operator brief
- `scripts/submission_audit.py` (18458 bytes, sha256 `a07f81dba7d89139...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (4960 bytes, sha256 `079ce7afa90da730...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (3651 bytes, sha256 `f5762e50434c881d...`) - Human-readable submission audit report
- `docs/evidence_package.md` (12044 bytes, sha256 `357afb039f0e4cf7...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4089 bytes, sha256 `735b9188feae74ea...`) - Verified-claim boundary
- `docs/verification.md` (7483 bytes, sha256 `bd0364f5a32a81fe...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (352 bytes, sha256 `d250e97bb0a653fa...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (7670 bytes, sha256 `7780ecdcfe222479...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `047dfb610c8b1559...`) - Human-readable secret scan report
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (9278 bytes, sha256 `a10bddfc1048122d...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (4269 bytes, sha256 `6a6a62634cde12cd...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2158 bytes, sha256 `75481d5d095709a3...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (11654 bytes, sha256 `9cd606a2cbca1a93...`) - Local final credential env wizard
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8540 bytes, sha256 `283410fe3daef374...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3552 bytes, sha256 `54d474741550660c...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1647 bytes, sha256 `742c02b42b2dd717...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (15950 bytes, sha256 `d07f957b639398dd...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (5935 bytes, sha256 `6c3d77c9d19614d0...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (2872 bytes, sha256 `0ebc1e1108e9a0ed...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (4938 bytes, sha256 `21e83a6213cd5f13...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (3428 bytes, sha256 `9d6eb3492adea765...`) - Registration and submission plan
- `tasks.json` (26009 bytes, sha256 `058988678b5ecc8b...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (369328 bytes, sha256 `8f7dc32d520f8391...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
