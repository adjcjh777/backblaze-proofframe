# ProofFrame Submission Bundle

Created: `2026-06-27T17:20:08Z`
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

- `README.md` (8746 bytes, sha256 `3a853951cea516c5...`) - Core public project overview
- `docs/prd.md` (3918 bytes, sha256 `ada7e9161b86483c...`) - Product requirements
- `docs/spec.md` (4874 bytes, sha256 `8320ef186af34075...`) - Implementation specification
- `docs/devpost_draft.md` (5621 bytes, sha256 `85588ba9e7178774...`) - Copy-ready Devpost fields
- `docs/assets/devpost-submission-packet.json` (6234 bytes, sha256 `333fc3ce900e7059...`) - Machine-readable Devpost copy
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
- `docs/assets/demo-storyboard.json` (4496 bytes, sha256 `68cddae91116f11d...`) - Machine-readable demo storyboard
- `docs/assets/demo-storyboard.md` (2686 bytes, sha256 `b5a03a0bd468630b...`) - Human-readable demo storyboard
- `docs/sponsor_fit_matrix.md` (3054 bytes, sha256 `cfa25f30bc5d2051...`) - Sponsor judging matrix and claim boundary
- `scripts/sponsor_fit_audit.py` (7965 bytes, sha256 `ef53a82d7e1b1426...`) - Sponsor-fit clarity audit
- `docs/assets/sponsor-fit-audit.json` (1599 bytes, sha256 `234a2eb7b09ae02e...`) - Machine-readable sponsor-fit audit
- `docs/assets/sponsor-fit-audit.md` (1088 bytes, sha256 `867d356985612279...`) - Human-readable sponsor-fit audit
- `scripts/award_readiness.py` (22750 bytes, sha256 `6dbc17e3a19b3cbc...`) - Judge-facing award readiness scorecard
- `docs/assets/award-readiness-report.json` (10805 bytes, sha256 `bc14dffeeebf21c5...`) - Machine-readable award readiness report
- `docs/assets/award-readiness-report.md` (4114 bytes, sha256 `1fd4a628ab1c178c...`) - Human-readable award readiness report
- `scripts/final_submission_control.py` (21293 bytes, sha256 `0d17e6912bbb63e4...`) - Final submission control tower
- `docs/assets/final-submission-control.json` (13666 bytes, sha256 `eac880d46bdbfa8f...`) - Machine-readable final control report
- `docs/assets/final-submission-control.md` (4345 bytes, sha256 `2429a5245d006fd3...`) - Human-readable final control report
- `scripts/final_operator_brief.py` (12047 bytes, sha256 `32dad2c9e0c815e8...`) - No-secret final operator brief
- `docs/assets/final-operator-brief.json` (5061 bytes, sha256 `ed78dedc272cfb18...`) - Machine-readable final operator brief
- `docs/assets/final-operator-brief.md` (2902 bytes, sha256 `f3f3ca6c18fd82e3...`) - Human-readable final operator brief
- `docs/evidence_package.md` (11609 bytes, sha256 `3c637c38f02d91dd...`) - Evidence package plan
- `docs/public_claim_freeze.md` (4089 bytes, sha256 `735b9188feae74ea...`) - Verified-claim boundary
- `docs/verification.md` (7394 bytes, sha256 `bdb4167376985942...`) - Local, CI, Docker, and live proof runbook
- `.env.final.example` (352 bytes, sha256 `d250e97bb0a653fa...`) - Redacted final B2 plus Genblaze env template
- `docs/assets/b2-live-setup.json` (719 bytes, sha256 `a377923f48e112b1...`) - Non-secret B2 bucket setup record
- `docs/assets/b2-live-setup.md` (864 bytes, sha256 `863b2a02e3d2824f...`) - Human-readable B2 bucket setup record
- `scripts/run_b2_live_proof.py` (5781 bytes, sha256 `9678c0292a70cc0b...`) - One-command B2 storage proof runner
- `scripts/live_env_handoff.py` (9180 bytes, sha256 `1192c443de7ab889...`) - Redacted live credential handoff gate
- `docs/assets/live-credential-handoff.json` (4171 bytes, sha256 `6d7622c1b99bd1aa...`) - Machine-readable live credential handoff
- `docs/assets/live-credential-handoff.md` (2055 bytes, sha256 `3c5c4b1ed2de426b...`) - Human-readable live credential handoff
- `scripts/final_env_wizard.py` (11654 bytes, sha256 `9cd606a2cbca1a93...`) - Local final credential env wizard
- `scripts/claim_lint.py` (5190 bytes, sha256 `d8e9f53dfee772a1...`) - Fail-closed public claim lint
- `scripts/demo_readiness.py` (8540 bytes, sha256 `283410fe3daef374...`) - Demo recording readiness gate
- `docs/assets/demo-readiness-report.json` (3552 bytes, sha256 `27d81c06daf68f56...`) - Machine-readable demo readiness report
- `docs/assets/demo-readiness-report.md` (1647 bytes, sha256 `742c02b42b2dd717...`) - Human-readable demo readiness report
- `scripts/recording_assets.py` (15950 bytes, sha256 `d07f957b639398dd...`) - Public-safe recording asset gate
- `docs/assets/recording-assets.json` (5935 bytes, sha256 `7dd8eb3ff4a5d8fc...`) - Machine-readable recording asset report
- `docs/assets/recording-assets.md` (2872 bytes, sha256 `0ebc1e1108e9a0ed...`) - Human-readable recording asset report
- `scripts/run_final_live_proof.py` (4938 bytes, sha256 `21e83a6213cd5f13...`) - One-command final B2 plus Genblaze proof runner
- `docs/submission.md` (3353 bytes, sha256 `2e819bd8d2a6cd4d...`) - Registration and submission plan
- `tasks.json` (24962 bytes, sha256 `61957049eb401ad1...`) - Machine-readable task board
- `docs/assets/proofframe-local-ui-smoke.png` (364927 bytes, sha256 `cca671ad38bda4dc...`) - Local UI screenshot
- `docs/assets/proofframe-review-console-smoke.png` (343618 bytes, sha256 `30620a33e3c7ab28...`) - Review console screenshot
- `docs/assets/proofframe-hf-public-smoke.png` (369328 bytes, sha256 `8f7dc32d520f8391...`) - Public mock demo screenshot

No credentials, browser cookies, signed URLs, or raw provider keys are included.
