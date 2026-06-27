# ProofFrame Submission Bundle

Created: `2026-06-27T18:42:13Z`
Repository: https://github.com/adjcjh777/backblaze-proofframe
Public mock demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Devpost packet mode: `pre_live_safe`
Final gate mode: `pre_live_safe`
Final gate ready: `false`

## Current Gate

- Tasks: 1 done / 6 required; 2 doing, 0 blocked, 3 todo.
- Live evidence: `missing`
- Devpost copy packet: `ready`
- Final reports: `incomplete`

## Next Actions

- Run a live Backblaze B2 asset and manifest proof.
- Run a live Genblaze generation proof and capture provider metadata.
- Run the final submission audit after live proofs are captured.
- Run the final secret scan before recording or submitting.
- Submit the Devpost project after every preceding gate is done.

## Artifacts

- `README.md` (9418 bytes, sha256 `a724d2eced70c79c...`) - Core public project overview
- `Dockerfile` (522 bytes, sha256 `6764f101746a802d...`) - Docker deployment image contract
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (5107 bytes, sha256 `d6be8b19cd14624e...`) - Implementation specification
- `docs/deployment.md` (3883 bytes, sha256 `1d9e5187ffe8b4a6...`) - Public demo deployment runbook
- `docs/devpost_draft.md` (5621 bytes, sha256 `85588ba9e7178774...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6278 bytes, sha256 `fe9d64550737a5d7...`) - Machine-readable Devpost copy
- `docs/assets/devpost-submission-packet.md` (5167 bytes, sha256 `5de4e82e0f3038c2...`) - Human-readable Devpost copy
- `scripts/devpost_event_snapshot.py` (19728 bytes, sha256 `1389e03af0d481ea...`) - Official Devpost event snapshot checker
- `docs/assets/devpost-event-snapshot.json` (2492 bytes, sha256 `29fa3f02ce7720ae...`) - Machine-readable Devpost event snapshot
- `docs/assets/devpost-event-snapshot.md` (1443 bytes, sha256 `74c8c2e8e85c2695...`) - Human-readable Devpost event snapshot
- `scripts/devpost_form_kit.py` (12830 bytes, sha256 `b0173e698f4c3629...`) - Field-by-field Devpost form kit
- `docs/assets/devpost-form-kit.json` (12491 bytes, sha256 `4b9e0a7e8284e7a9...`) - Machine-readable Devpost form kit
- `docs/assets/devpost-form-kit.md` (7504 bytes, sha256 `f0af423732a0613e...`) - Human-readable Devpost form kit
- `apps/web/index.html` (41336 bytes, sha256 `52508e553ace7d7d...`) - Browser proof ledger UI
- `docs/demo_script.md` (5690 bytes, sha256 `1a3128155b57c677...`) - Video shot list and narration
- `scripts/demo_storyboard.py` (11007 bytes, sha256 `dadfe2907f2c1ca5...`) - Machine-checked demo video storyboard
- `docs/assets/demo-storyboard.json` (4496 bytes, sha256 `04d655aa20ace836...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2686 bytes, sha256 `b5a03a0bd468630b...`) - Human-readable demo storyboard
- `docs/sponsor_fit_matrix.md` (3054 bytes, sha256 `cfa25f30bc5d2051...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (22984 bytes, sha256 `b6d425284f4d56fa...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (10894 bytes, sha256 `1c6fd347710d969d...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4198 bytes, sha256 `15954ff53b6f109c...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (23578 bytes, sha256 `2dbe5df35a95b5b9...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (15895 bytes, sha256 `ee9e1cd29eed7610...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (4833 bytes, sha256 `8a47f292b4e32dae...`) - Human-readable final control report
- `scripts/final_operator_brief.py` (12812 bytes, sha256 `95151e1210c1ea91...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (6397 bytes, sha256 `a0992a5109dd82fb...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (3124 bytes, sha256 `38d79c1dc13660c4...`) - Human-readable final operator brief
- `scripts/submission_audit.py` (18802 bytes, sha256 `5786c2acd1c6159f...`) - Pre-submit audit gate
- `docs/assets/submission-audit-report.json` (5201 bytes, sha256 `57b50e33c50c073a...`) - Machine-readable submission audit report
- `docs/assets/submission-audit-report.md` (3887 bytes, sha256 `e818a17407f5ab19...`) - Human-readable submission audit report
- `scripts/devpost_submission_receipt.py` (9187 bytes, sha256 `0fd53dda995a854e...`) - Public-safe Devpost submission receipt generator
- `docs/assets/devpost-submission-receipt.json` (1270 bytes, sha256 `f9a44878665ecdf1...`) - Machine-readable Devpost submission receipt
- `docs/assets/devpost-submission-receipt.md` (972 bytes, sha256 `2f203cf768ea5517...`) - Human-readable Devpost submission receipt
- `docs/evidence_package.md` (12397 bytes, sha256 `efbcd4059832bff4...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4089 bytes, sha256 `735b9188feae74ea...`) - Verified-claim boundary
- `docs/verification.md` (7933 bytes, sha256 `5fae592330a79cd2...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (352 bytes, sha256 `d250e97bb0a653fa...`) - Redacted final B2 plus Genblaze env template
- `scripts/secret_scan.py` (11105 bytes, sha256 `02aec3a4a6e9fd47...`) - Final secret scanner
- `docs/assets/secret-scan-report.json` (7904 bytes, sha256 `e24182e65053e8ca...`) - Machine-readable secret scan report
- `docs/assets/secret-scan-report.md` (846 bytes, sha256 `ad53c936e464119e...`) - Human-readable secret scan report
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
- `scripts/recording_assets.py` (16842 bytes, sha256 `b304d1b1724fb9d5...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (6080 bytes, sha256 `fa4bb045738aa3d1...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (2872 bytes, sha256 `0ebc1e1108e9a0ed...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (4938 bytes, sha256 `21e83a6213cd5f13...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (3492 bytes, sha256 `9b550c884cdfa24e...`) - Registration and submission plan
- `tasks.json` (27518 bytes, sha256 `2cd3b555d1ca8e25...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (369328 bytes, sha256 `8f7dc32d520f8391...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
