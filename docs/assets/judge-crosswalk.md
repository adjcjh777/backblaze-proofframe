# ProofFrame Judge Crosswalk

Created: `2026-06-28T16:53:29Z`
Mode: `pre_live_crosswalk_ready`
OK: `true`
Safe to submit: `false`
Event: Backblaze Generative Media Hackathon
Deadline: `2026-08-03T21:00:00Z` / `2026-08-04 05:00 Asia/Shanghai`

## Source Health

- OK `docs/assets/devpost-event-snapshot.json` schema `proofframe.devpost_event_snapshot.v1` (expected `proofframe.devpost_event_snapshot.v1`)
- OK `docs/assets/judge-brief.json` schema `proofframe.judge_brief.v1` (expected `proofframe.judge_brief.v1`)
- OK `docs/assets/sponsor-fit-audit.json` schema `proofframe.sponsor_fit_audit.v1` (expected `proofframe.sponsor_fit_audit.v1`)
- OK `docs/assets/award-readiness-report.json` schema `proofframe.award_readiness.v1` (expected `proofframe.award_readiness.v1`)
- OK `docs/assets/final-submission-control.json` schema `proofframe.final_submission_control.v1` (expected `proofframe.final_submission_control.v1`)

## Official Requirements

| Requirement | Official Marker | Evidence |
| --- | --- | --- |
| Working application URL | `yes` | Public mock demo URL in README and Devpost form kit |
| GitHub repository URL | `yes` | Public GitHub repository and submission bundle manifest |
| Demonstration video | `yes` | Public video check and storyboard reports; final URL still gated |
| Video under three minutes | `yes` | Demo storyboard duration gate |
| Public video host | `yes` | Public video check URL rules |
| Backblaze B2 usage | `yes` | B2 adapter, B2 live setup record, and T020 live proof runner |
| Genblaze usage | `yes` | Genblaze provider adapter and T021 final live proof runner |

## Judging Crosswalk

| Official angle | Current evidence | Safe claim | Final gate | Demo shot |
| --- | --- | --- | --- | --- |
| Real-world Utility<br>`public_mock_ready` | `docs/prd.md`<br>`docs/spec.md`<br>`apps/web/index.html`<br>`docs/assets/judge-brief.md`<br>Downloadable evidence ZIP from /api/campaigns/{id}/packet.zip | ProofFrame is a working provenance and review desk for generated media, with the public demo running in credential-free local/mock mode. | Final video must show one creator workflow end-to-end with live proof context. | Judge Demo packet, asset review, approval state, manifest preview, evidence ZIP. |
| Production Readiness<br>`pre_live_fail_closed` | `.github/workflows/ci.yml`<br>`scripts/secret_scan.py`<br>`scripts/claim_lint.py`<br>`scripts/final_submission_control.py`<br>`scripts/submission_audit.py` | The repo has fail-closed readiness gates, CI checks, secret scanning, claim linting, and generated submission reports. | T041A secret scan, T041 strict audit, and T042 receipt must close before submit. | Final gate dashboard and judge recording slate showing current safe-to-submit state. |
| B2 Storage + Data Orchestration<br>`code_ready_live_proof_pending` | `src/proofframe/storage.py`<br>`docs/assets/b2-live-setup.md`<br>`scripts/run_b2_live_proof.py`<br>`docs/assets/live-credential-handoff.md`<br>`docs/assets/final-submission-control.md` | ProofFrame includes B2-compatible storage paths and B2-ready manifests; completed live B2 proof is not claimed until T020 is done. | T020 must capture sanitized B2 asset and manifest object keys plus checksums. | B2 Object Route and manifest checksum fields in the first-screen evidence model. |
| Use of Genblaze<br>`adapter_ready_live_proof_pending` | `src/proofframe/providers.py`<br>`scripts/run_final_live_proof.py`<br>.env.final.example<br>`docs/assets/live-credential-handoff.md`<br>`docs/assets/devpost-submission-packet.md` | ProofFrame includes a Genblaze-compatible provider path and manifest fields; completed live Genblaze proof is not claimed until T021 is done. | T021 must capture live provider/model metadata from the final Genblaze path. | Genblaze Step, provider/model metadata, and prompt lineage in the manifest preview. |

## Blocking Items

- `devpost_submission_checklist`: Devpost submission checklist mode is pre_submit_blocked; safe_to_submit is False. Evidence: `docs/assets/devpost-submission-checklist.json`
- `b2_live_proof`: T020 is doing; B2 evidence status is missing; final evidence status is missing. Evidence: `tasks.json, docs/assets/b2-live-proof-evidence.json, and docs/assets/final-live-proof-evidence.json`
- `genblaze_live_proof`: T021 is doing; final evidence status is missing. Evidence: `tasks.json and docs/assets/final-live-proof-evidence.json`
- `credential_handoff`: Credential handoff mode is missing_live_env; missing ids: b2_key_id, b2_application_key, genblaze_api_key. Evidence: `docs/assets/live-credential-handoff.json`
- `public_video`: Storyboard mode is mock_storyboard_ready; public video ready is False. Evidence: `docs/assets/demo-storyboard.json`
- `public_video_check`: Public video check mode is pending_video_url; safe_to_submit is False. Evidence: `docs/assets/public-video-check.json`
- `final_recording`: Demo readiness mode is pre_live_mock_ready; final recording ready is False. Evidence: `docs/assets/demo-readiness-report.json`
- `final_secret_scan`: T041A is todo; secret scan mode is clear; secret scan ok is True. Evidence: `tasks.json and docs/assets/secret-scan-report.json`
- `final_submission_audit`: T041 is todo; audit mode is pre_submit_audit_blocked; audit ok is False. Evidence: `tasks.json and docs/assets/submission-audit-report.json`
- `devpost_submitted`: T042 is todo; receipt mode is pending_submission; receipt ok is False. Evidence: `tasks.json and docs/assets/devpost-submission-receipt.json`

## Claim Boundaries

- Do not claim completed B2 live storage until T020 is done and evidence is sanitized.
- Do not claim completed Genblaze live generation until T021 is done and provider/model metadata is captured.
- Do not mark safe_to_submit true until public video, strict audit, final secret scan, and Devpost receipt are complete.

## Next Actions

- Use this crosswalk as the judge-facing map while recording the final video and filling Devpost.
- After T020/T021 and the public video URL are ready, rerun final reports and regenerate this crosswalk.
- Submit only after final_submission_control.py --strict-final and submission_audit.py --strict-final pass.
