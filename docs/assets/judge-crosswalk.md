# ProofFrame Judge Crosswalk

Created: `2026-07-03T10:38:00Z`
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
| B2 Storage + Data Orchestration<br>`live_verified` | `src/proofframe/storage.py`<br>`docs/assets/b2-live-setup.md`<br>`scripts/run_b2_live_proof.py`<br>`docs/assets/live-credential-handoff.md`<br>`docs/assets/final-submission-control.md` | ProofFrame has captured live B2 media and manifest evidence with sanitized object keys and checksums. | B2 proof is done; final submission still needs public video, audit, scan, and Devpost receipt. | B2 Object Route and manifest checksum fields in the first-screen evidence model. |
| Use of Genblaze<br>`live_verified` | `src/proofframe/providers.py`<br>`scripts/run_final_live_proof.py`<br>.env.final.example<br>`docs/assets/live-credential-handoff.md`<br>`docs/assets/devpost-submission-packet.md` | ProofFrame has captured Genblaze Pipeline proof with provider/model metadata and B2-backed manifest output. | Genblaze proof is done; final submission still needs public video, audit, scan, and Devpost receipt. | Genblaze Step, provider/model metadata, and prompt lineage in the manifest preview. |

## Blocking Items

- `devpost_submission_checklist`: Devpost submission checklist mode is pre_submit_blocked; safe_to_submit is False. Evidence: `docs/assets/devpost-submission-checklist.json`
- `public_video`: Storyboard mode is mock_storyboard_ready; public video ready is False. Evidence: `docs/assets/demo-storyboard.json`
- `public_video_check`: Public video check mode is pending_video_url; safe_to_submit is False. Evidence: `docs/assets/public-video-check.json`
- `final_recording`: Demo readiness mode is pre_live_mock_ready; final recording ready is False. Evidence: `docs/assets/demo-readiness-report.json`
- `final_secret_scan`: T041A is blocked; secret scan mode is clear; secret scan ok is True. Evidence: `tasks.json and docs/assets/secret-scan-report.json`
- `final_submission_audit`: T041 is blocked; audit mode is pre_submit_audit_blocked; audit ok is False. Evidence: `tasks.json and docs/assets/submission-audit-report.json`
- `devpost_submitted`: T042 is blocked; receipt mode is pending_submission; receipt ok is False. Evidence: `tasks.json and docs/assets/devpost-submission-receipt.json`

## Claim Boundaries

- B2 live storage proof may be claimed with sanitized evidence.
- Genblaze Pipeline proof may be claimed with sanitized provider/model evidence.
- Do not mark safe_to_submit true until public video, strict audit, final secret scan, and Devpost receipt are complete.

## Next Actions

- Use this crosswalk as the judge-facing map while recording the final video and filling Devpost.
- After the public video URL is ready, rerun final reports and regenerate this crosswalk.
- Submit only after final_submission_control.py --strict-final and submission_audit.py --strict-final pass.
