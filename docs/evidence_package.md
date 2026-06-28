# Submission Evidence Package

This file is the internal source of truth for Devpost submission assets. Anything marked "public-ready" can be copied into Devpost or the public README. Anything marked "final gate" must not be claimed as completed until the linked task is done.

## Contest Metadata

| Field | Value |
| --- | --- |
| Event | Backblaze Generative Media Hackathon |
| Official page | https://backblaze-generative-media.devpost.com/ |
| Rules page | https://backblaze-generative-media.devpost.com/rules |
| Deadline | 2026-08-03 17:00 EDT |
| Beijing deadline | 2026-08-04 05:00 Asia/Shanghai |
| Sponsor tech | Backblaze B2 and Genblaze |

## Public Links

| Asset | Link | Status |
| --- | --- | --- |
| GitHub repo | https://github.com/adjcjh777/backblaze-proofframe | Public-ready |
| Public mock demo | https://adjcjh-backblaze-proofframe.hf.space/?judge=1 | Public-ready in local/mock mode; auto-loads judge packet |
| Hugging Face Space repo | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe | Public-ready in local/mock mode |
| Local app | `http://127.0.0.1:8088/` | Internal demo only |
| B2/Genblaze-backed deployed app URL | TBD | Final gate after T020/T021 |
| Demo video | TBD | Final gate |
| Devpost project page | TBD | Final gate |
| Devpost draft | `docs/devpost_draft.md` | Public-ready after final claim check |
| Deployment runbook | `docs/deployment.md` | Public-ready |

## Judge Quickstart

1. Open https://adjcjh-backblaze-proofframe.hf.space/?judge=1.
2. Confirm the first screen shows the Sponsor Evidence Model and the fail-closed final gate.
3. Use Judge Demo to create a local/mock media packet.
4. Inspect the asset ledger, manifest preview, approval state, checksum, and downloadable evidence ZIP.
5. Read `docs/assets/judge-brief.md`, `docs/assets/judge-crosswalk.md`, and `docs/assets/final-submission-control.md` for the safe claim boundary: B2 and Genblaze code paths are implemented, while live proof remains final-gated.

## Current Verified Evidence

| Evidence | Location | Status |
| --- | --- | --- |
| PRD | `docs/prd.md` | Public-ready |
| Technical spec | `docs/spec.md` | Public-ready |
| Submission plan | `docs/submission.md` | Public-ready after final claim check |
| Local Proof Ledger UI | `apps/web/index.html` | Public-ready |
| Judge recording slate | First viewport in `apps/web/index.html` showing demo mode, evidence packet state, and claim boundary | Public-ready in local/mock mode |
| Sponsor evidence model | First viewport in `apps/web/index.html` showing Genblaze step, B2 object route, manifest proof, and claim mode | Public-ready in local/mock mode |
| Review console | scorecard, status filter, search, safe summary copy in `apps/web/index.html` | Public-ready in local/mock mode |
| Review console smoke screenshot | `docs/assets/proofframe-review-console-smoke.png` | Public-ready in local/mock mode |
| UI smoke screenshot | `docs/assets/proofframe-local-ui-smoke.png` | Public-ready |
| Public HF Space smoke screenshot | `docs/assets/proofframe-hf-public-smoke.png` | Public-ready in local/mock mode |
| Public HF Space API smoke | `python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space` | Passed in local/mock mode; verifies judge brief, judge crosswalk, recording runbook, Devpost kit, and submit checklist endpoints stay schema-valid and claim-safe |
| Public HF Space judge-mode sync | HF Space commit `3115d66`; runtime sha `3115d6631f6e8d994da8c41a922fab20a0f9b1ba`; public HTML contains `Judge recording slate`, `Sponsor Evidence Model`, `30-Second Judge Brief`, `Criteria Crosswalk`, `Recording Runbook`, `Devpost Kit`, `Submit Checklist`, `shouldAutoLoadJudgeDemo`, and `Final reports pending`; `/api/submission/gate` returns `pre_live_safe` with `pre_live_packet_pending` and `report_gate`; `/api/judge/crosswalk` returns `proofframe.judge_crosswalk.v1` with four rows and `safe_to_submit=false`; `/api/judge/recording` returns `proofframe.recording_assets.v1` with six shots and `final_video_ready=false`; `/api/judge/devpost` returns `proofframe.devpost_form_kit.v1` with 19 fields and `final_form_ready=false`; `/api/judge/submission-checklist` returns `proofframe.devpost_submission_checklist.v1` with preflight rows and `safe_to_submit=false`; raw Space `docs/assets/agent-handoff-report.json` returns `handoff_ready`; raw Space `docs/assets/final-launch-plan.json` returns `ready_for_credential_entry`; raw Space `docs/assets/judge-brief.json` returns `safe_to_submit=false`; raw Space `docs/assets/judge-crosswalk.json` returns `pre_live_crosswalk_ready` with `safe_to_submit=false`; raw Space `docs/assets/recording-assets.json` returns `public_mock_verified` with `final_video_ready=false`; raw Space `docs/assets/devpost-form-kit.json` returns `pre_live_form_ready` with `final_form_ready=false`; raw Space `docs/assets/devpost-submission-checklist.json` returns `pre_submit_blocked` with `safe_to_submit=false`; API smoke passes | Public-ready in local/mock mode |
| Official Devpost event snapshot | `scripts/devpost_event_snapshot.py`, `docs/assets/devpost-event-snapshot.json`, `docs/assets/devpost-event-snapshot.md` | Public-ready; refreshes deadline, participant count, requirements, and judging criteria from official Devpost pages |
| Agent handoff consistency | `scripts/agent_handoff_check.py`, `docs/assets/agent-handoff-report.json`, `docs/assets/agent-handoff-report.md` | Public-ready; verifies AGENTS.md points future Codex and Agent Bus sessions at the current repo path |
| Public Space sync report | `scripts/public_space_sync.py`, `docs/assets/public-space-sync-report.json`, `docs/assets/public-space-sync-report.md` | Public-ready; verifies HF Space metadata/runtime sha, raw handoff report, raw final launch plan, raw judge brief, raw judge crosswalk, local/mock health, fail-closed submission gate, and judge HTML markers |
| Judge brief | `scripts/judge_brief.py`, `docs/assets/judge-brief.json`, `docs/assets/judge-brief.md` | Public-ready; 30-second judge framing with safe claims, current blockers, walkthrough, and evidence links |
| Judge crosswalk | `scripts/judge_crosswalk.py`, `GET /api/judge/crosswalk`, `docs/assets/judge-crosswalk.json`, `docs/assets/judge-crosswalk.md` | Public-ready; maps official judging criteria and submission requirements to evidence artifacts, safe claims, final gates, and demo shots, and powers the in-app Criteria Crosswalk panel |
| Final rehearsal checklist | `scripts/final_rehearsal.py`, `docs/assets/final-rehearsal-checklist.json`, `docs/assets/final-rehearsal-checklist.md` | Internal-ready; no-secret sequence for credential entry, live proof, video, audit, Devpost receipt, and final green gate |
| Devpost registration | `tasks.json` T040 | Done; registered for the event |
| Downloadable evidence ZIP | `/api/campaigns/{id}/packet.zip` | Public-ready in local mode |
| One-click judge packet | `/api/demo/judge-packet` | Public-ready in local mode |
| Final live proof preflight | `scripts/live_proof.py --preflight-only` | Public-ready; reports missing env/packages without printing secrets |
| Live credential handoff | `.env.final.example`, `scripts/live_env_handoff.py`, `docs/assets/live-credential-handoff.json`, `docs/assets/live-credential-handoff.md` | Public-ready; reports required variable presence and next commands without credential values |
| Final env wizard | `scripts/final_env_wizard.py --output .env.final.local` | Local-only helper; writes git-ignored 0600 env files and prints variable names only |
| B2 live setup record | `docs/assets/b2-live-setup.json`, `docs/assets/b2-live-setup.md` | Public-ready; records bucket name, endpoint, private status, and pending application key without secrets |
| B2 live proof runner | `scripts/run_b2_live_proof.py --env-file .env.final.local` | Public-ready; verifies B2 storage with mock generation and writes sanitized T020 evidence after B2 key is present |
| Final live proof runner | `scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only`, then `scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json` | Public-ready; starts and stops local app without committing logs or secrets |
| Evidence safety gate | `scripts/api_smoke.py --evidence-out` refuses secret-like keys and signed-token values before writing JSON | Public-ready |
| Secret scan report | `scripts/secret_scan.py`, `docs/assets/secret-scan-report.json`, `docs/assets/secret-scan-report.md` | Public-ready; scans public text/evidence/log files, inventories screenshots/media, excludes local credential files without reading values, and stores no matched line text |
| Public claim lint | `scripts/claim_lint.py` fails CI if active public copy claims completed B2/Genblaze proof before final evidence exists | Public-ready |
| Final submission control | `scripts/final_submission_control.py`, `docs/assets/final-submission-control.json`, `docs/assets/final-submission-control.md` aggregate the final gate, Devpost form, storyboard, credential handoff, award score, and next commands | Public-ready; intentionally not safe-to-submit until live proof/video/audit gates complete |
| Final operator brief | `scripts/final_operator_brief.py`, `docs/assets/final-operator-brief.json`, `docs/assets/final-operator-brief.md` | Public-ready; no-secret handoff for user credential entry, Codex follow-up commands, and final safety policy |
| Final launch plan | `scripts/final_launch_plan.py`, `docs/assets/final-launch-plan.json`, `docs/assets/final-launch-plan.md` | Public-ready; no-secret phase checklist for credential entry, B2 proof, Genblaze proof, public video, final audit, and Devpost receipt |
| Final submission audit | `scripts/submission_audit.py --strict-final` checks pre-submit tasks, required artifacts, screenshots, live proof evidence, final video URL, and synchronized readiness reports | Public-ready; intentionally fails until T020/T021/T040/T041A, live proof, public video, and strict final reports are complete; T041/T042 are observer tasks |
| Devpost submission receipt | `scripts/devpost_submission_receipt.py`, `docs/assets/devpost-submission-receipt.json`, `docs/assets/devpost-submission-receipt.md` | Public-ready; pending before submit, final mode records only public Devpost `/software/<slug>` URL, timestamp, and confirmation note |
| Copy-ready Devpost packet | `docs/assets/devpost-submission-packet.json`, `docs/assets/devpost-submission-packet.md` | Public-ready in pre-live-safe mode |
| Public video check | `scripts/public_video_check.py`, `docs/assets/public-video-check.json`, `docs/assets/public-video-check.md` | Internal-ready; verifies final demo video URL is public, token-free, under the event video constraint via storyboard, and reachable in strict final mode |
| Devpost form kit | `scripts/devpost_form_kit.py`, `GET /api/judge/devpost`, `docs/assets/devpost-form-kit.json`, `docs/assets/devpost-form-kit.md` | Public-ready for field-by-field copy; powers the in-app Devpost Kit, and strict final mode waits for live proof and a public video URL |
| Devpost submission checklist | `scripts/devpost_submission_checklist.py`, `GET /api/judge/submission-checklist`, `docs/assets/devpost-submission-checklist.json`, `docs/assets/devpost-submission-checklist.md` | Internal-ready; powers the in-app Submit Checklist and provides ordered final Devpost web copy checklist with preflight gates, stop rules, and receipt commands |
| Safe submission bundle manifest | `docs/assets/submission-bundle-manifest.json`, `docs/assets/submission-bundle-manifest.md` | Public-ready in pre-live-safe mode |
| Demo readiness report | `scripts/demo_readiness.py`, `docs/assets/demo-readiness-report.json`, `docs/assets/demo-readiness-report.md` | Public-ready for mock recording; strict final mode intentionally waits for T020/T021/T041A |
| Demo storyboard | `scripts/demo_storyboard.py`, `docs/assets/demo-storyboard.json`, `docs/assets/demo-storyboard.md` | Public-ready for mock recording; strict final mode waits for live proof and a public video URL |
| Recording assets report | `scripts/recording_assets.py`, `GET /api/judge/recording`, `docs/assets/recording-assets.json`, `docs/assets/recording-assets.md` | Public-ready; powers the in-app Recording Runbook, verifies committed screenshots, and can run GET-only checks against the public mock demo |
| Sponsor fit matrix | `docs/sponsor_fit_matrix.md` | Public-ready; maps official judging angles to current evidence, safe claims, final gates, and demo shots |
| Sponsor fit audit | `scripts/sponsor_fit_audit.py`, `docs/assets/sponsor-fit-audit.json`, `docs/assets/sponsor-fit-audit.md` | Public-ready; checks Devpost B2/Genblaze specificity, early demo coverage, and claim-safe final gates |
| Award readiness report | `scripts/award_readiness.py`, `docs/assets/award-readiness-report.json`, `docs/assets/award-readiness-report.md` | Public-ready; scores sponsor fit, provenance depth, demo readiness, claim safety, and final closure |
| Devpost draft | `docs/devpost_draft.md` | Public-ready after final claim check |
| Deployment runbook | `docs/deployment.md` | Public-ready |
| Task ledger | `tasks.json`, `scripts/task.py` | Public-ready |
| Task ledger add/search | `python3 scripts/task.py add ...`, `python3 scripts/task.py search ...` | Public-ready |
| Local API tests | `.venv` verification: `pytest` | Public-ready |
| Integration readiness check | `scripts/check_integrations.py` | Public-ready |
| B2 storage adapter code | `src/proofframe/storage.py` | Code-ready, final live proof pending T020 |
| Genblaze provider path | `src/proofframe/providers.py` | Code-ready, final live proof pending T021 |

## Final Evidence Still Needed

| Task | Evidence Required | Public Claim Allowed After |
| --- | --- | --- |
| T020 | One asset and one manifest uploaded to a dedicated Backblaze B2 bucket using env-only credentials, with sanitized object keys and checksums captured. | "ProofFrame stores media and manifests through Backblaze B2." |
| T021 | One live Genblaze-backed generation run, with provider/model metadata captured in exported manifest. | "ProofFrame generates media through Genblaze." |
| T041A | Secret scan covering repo, screenshots, logs, manifests, and demo artifacts. | "Public package contains no exposed secrets." |
| T042 | Accepted Devpost project submission. | "Submitted." |

## Safe Devpost Draft

Project name: ProofFrame

Tagline:

> B2-ready provenance desk for GenAI media.

One-liner:

> ProofFrame turns generated media into approved evidence packets with B2-ready manifests, Genblaze-gated provider metadata, checksums, review status, and an exportable proof bundle.

Short description, safe before final live integrations:

> ProofFrame turns generated media into reviewable asset packets. The current app lets a team create a campaign, generate variants in local demo mode, approve or reject assets, and export a manifest with prompts, provider/model fields, storage references, checksums, and review status. The final hackathon submission gate is to verify the same flow with Genblaze-backed generation and Backblaze B2-backed storage.

Short description, safe after T020 and T021:

> ProofFrame turns Genblaze-generated media into Backblaze B2-backed asset packets. Each packet includes prompt history, provider/model metadata, storage references, checksums, approval state, and an exportable manifest so creative teams can reuse generated media with confidence.

## Suggested Devpost Sections

### Inspiration

Generated media is easy to create but hard to govern. Teams often lose the exact prompt, model, approval status, and storage evidence for the assets they end up using.

### What It Does

ProofFrame provides a browser-based review desk for generated media. It creates a campaign, generates candidate assets, lets reviewers approve or reject them, and exports a manifest that ties each asset to its prompt, provider, model, storage backend, object reference, hash, and review status.

### How We Built It

FastAPI powers the API and manifest flow. The browser UI is a single-file `index.html` proof ledger. Storage is abstracted behind local and Backblaze B2-compatible backends. Generation is abstracted behind local mock and Genblaze-backed provider paths.

### Challenges

The main challenge is keeping public claims aligned with verified sponsor integrations. ProofFrame is built with fail-closed adapters so missing B2 or Genblaze configuration is visible instead of silently falling back.

### What Is Next

Add team roles, signed judge access links, richer asset types, and a release dashboard for retiring or reproducing approved media packets.

## Evidence Hygiene

- Never upload `.env`, credentials, cookies, browser session files, or raw signed URLs.
- Do not include private Backblaze bucket names or account ids in public screenshots unless they are dedicated demo resources.
- Prefer sanitized object references plus checksums in screenshots and manifests.
- Keep public copy aligned with `docs/public_claim_freeze.md`.
