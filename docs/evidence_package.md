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
5. Read `docs/assets/judge-brief.md`, `docs/assets/judge-crosswalk.md`, `docs/assets/judge-evidence-index.md`, and `docs/assets/final-submission-control.md` for the safe claim boundary: B2 and Genblaze code paths are implemented, while live proof remains final-gated.

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
| Public HF Space screenshot verification | `scripts/public_demo_screenshot.py`, `docs/assets/public-demo-screenshot-report.json`, `docs/assets/public-demo-screenshot-report.md` | Public-ready; refreshes the public judge-mode screenshot and verifies visible judge/sponsor/final-gate markers plus nonblank image stats |
| Public HF Space API smoke | `python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space` | Passed in local/mock mode; verifies judge brief, judge crosswalk, recording runbook, Devpost kit, and submit checklist endpoints stay schema-valid and claim-safe |
| Public HF Space judge-mode sync | Latest HF Space commit/runtime sha is recorded in `docs/assets/public-space-sync-report.json`; `python scripts/public_space_sync.py` passes with no failed checks; public API smoke passes in local/mock mode; raw `docs/assets/devpost-event-snapshot.json` exposes the current observed participant count and submission-open status; raw `docs/assets/final-submission-control.json` exposes `control_health_ok=true` while `safe_to_submit=false`; raw `docs/assets/final-closeout-status.json` exposes `closeout_health_ok=true` while `safe_to_submit=false`; raw `docs/assets/judge-decision-brief.json` exposes a public-safe decision card with `safe_to_submit=false`; raw `docs/assets/judge-evidence-index.json` exposes `safe_to_submit=false` and public evidence links; raw `docs/assets/final-video-publish-kit.json` exposes final upload copy while keeping `safe_to_submit=false`; raw `docs/assets/public-video-check.json` is part of the Space sync gate and exposes `video_url_official_public_host` for YouTube/Vimeo/Youku-only final video URLs | Public-ready in local/mock mode |
| Public HF Space upload dry-run | `scripts/public_space_upload.py`, `docs/assets/public-space-upload-report.json`, `docs/assets/public-space-upload-report.md` | Internal-ready; excludes local env files, git state, virtualenvs, runtime output, caches, and `node_modules` before an explicit `--execute` upload, then checks raw public `.env.final.local` returns 404 after upload |
| Devpost submission preview | `scripts/devpost_submission_preview.py`, `docs/assets/devpost-submission-preview.json`, `docs/assets/devpost-submission-preview.md` | Public-ready; one-page copy/evidence/readiness preview that is safe to share before live proof but explicitly not safe to submit |
| Official Devpost event snapshot | `scripts/devpost_event_snapshot.py`, `docs/assets/devpost-event-snapshot.json`, `docs/assets/devpost-event-snapshot.md` | Public-ready; refreshes deadline, participant count, requirements, and judging criteria from official Devpost pages |
| Agent handoff consistency | `scripts/agent_handoff_check.py`, `docs/assets/agent-handoff-report.json`, `docs/assets/agent-handoff-report.md` | Public-ready; verifies AGENTS.md points future Codex and Agent Bus sessions at the current repo path |
| Public Space sync report | `scripts/public_space_sync.py`, `docs/assets/public-space-sync-report.json`, `docs/assets/public-space-sync-report.md` | Public-ready; verifies HF Space metadata/runtime sha, raw handoff report, raw Devpost event snapshot, raw final launch plan, raw B2 key scope checklist, raw Genblaze SDK contract report, raw judge brief, raw judge crosswalk, raw judge decision brief, raw judge evidence index, raw final closeout status, raw public screenshot report, raw recording assets, raw mock video draft report, public MP4 readability, raw public video check, raw Devpost kit, raw Devpost submission preview, raw submit checklist, raw post-credential live proof plan, raw submission bundle manifest, local/mock health, fail-closed submission gate, and judge HTML markers |
| Judge brief | `scripts/judge_brief.py`, `docs/assets/judge-brief.json`, `docs/assets/judge-brief.md` | Public-ready; 30-second judge framing with safe claims, current blockers, walkthrough, and evidence links |
| Judge crosswalk | `scripts/judge_crosswalk.py`, `GET /api/judge/crosswalk`, `docs/assets/judge-crosswalk.json`, `docs/assets/judge-crosswalk.md` | Public-ready; maps official judging criteria and submission requirements to evidence artifacts, safe claims, final gates, and demo shots, and powers the in-app Criteria Crosswalk panel |
| Judge decision brief | `scripts/judge_decision_brief.py`, `GET /api/judge/decision-brief`, `docs/assets/judge-decision-brief.json`, `docs/assets/judge-decision-brief.md` | Public-ready; one-page decision card with reasons to score high, public state, green checks, source health, and explicit final blockers |
| Judge evidence index | `scripts/judge_evidence_index.py`, `GET /api/judge/evidence-index`, `docs/assets/judge-evidence-index.json`, `docs/assets/judge-evidence-index.md` | Public-ready; one-stop evidence navigation with source health, public raw links, final blockers, and explicit `safe_to_submit=false` until live proof closes |
| Final rehearsal checklist | `scripts/final_rehearsal.py`, `docs/assets/final-rehearsal-checklist.json`, `docs/assets/final-rehearsal-checklist.md` | Internal-ready; no-secret sequence for credential entry, live proof, video, audit, Devpost receipt, and final green gate |
| Devpost registration | `tasks.json` T040 | Done; registered for the event |
| Downloadable evidence ZIP | `/api/campaigns/{id}/packet.zip` | Public-ready in local mode |
| One-click judge packet | `/api/demo/judge-packet` | Public-ready in local mode |
| Final live proof preflight | `scripts/live_proof.py --preflight-only` | Public-ready; reports missing env/packages without printing secrets |
| Live credential handoff | `.env.final.example`, `scripts/live_env_handoff.py`, `docs/assets/live-credential-handoff.json`, `docs/assets/live-credential-handoff.md` | Public-ready; reports required variable presence and next commands without credential values |
| Final env wizard | `scripts/final_env_wizard.py --output .env.final.local --missing-only --force` | Local-only helper; can fill only missing required values, writes git-ignored 0600 env files, and prints variable names only |
| Post-credential live proof sequence | `scripts/post_credential_live_proof.py --env-file .env.final.local --execute --update-tasks`, `docs/assets/post-credential-live-proof-plan.json`, `docs/assets/post-credential-live-proof-plan.md` | Public-safe plan plus explicit runner for the B2-only and final Genblaze proof sequence; validates each sanitized evidence JSON before any T020/T021 task update |
| B2 live setup record | `docs/assets/b2-live-setup.json`, `docs/assets/b2-live-setup.md` | Public-ready; records bucket name, endpoint, private status, and pending application key without secrets |
| B2 key scope checklist | `scripts/b2_key_scope_checklist.py`, `docs/assets/b2-key-scope-checklist.json`, `docs/assets/b2-key-scope-checklist.md` | Public-ready; no-secret checklist for creating a standard, single-bucket, `campaigns/`-prefixed B2 key with upload proof permissions, S3 SDK compatibility flag, forbidden admin/delete permissions, and stop conditions |
| Genblaze SDK contract check | `scripts/genblaze_contract_check.py`, `docs/assets/genblaze-contract-report.json`, `docs/assets/genblaze-contract-report.md` | Public-ready; verifies installed Genblaze/B2 package imports and callable signatures without reading environment variables or credential files, reducing final live-proof drift risk |
| B2 live proof runner | `scripts/run_b2_live_proof.py --env-file .env.final.local` | Public-ready; verifies B2 storage with mock generation and writes sanitized T020 evidence after B2 key is present |
| Final live proof runner | `scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only`, then `scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json` | Public-ready; starts and stops local app without committing logs or secrets |
| Evidence safety gate | `scripts/api_smoke.py --evidence-out` refuses secret-like keys and signed-token values before writing JSON | Public-ready |
| Secret scan report | `scripts/secret_scan.py`, `docs/assets/secret-scan-report.json`, `docs/assets/secret-scan-report.md` | Public-ready; scans public text/evidence/log files, inventories screenshots/media, excludes local credential files without reading values, and stores no matched line text |
| Public claim lint | `scripts/claim_lint.py` fails CI if active public copy claims completed B2/Genblaze proof before final evidence exists | Public-ready |
| Final submission control | `scripts/final_submission_control.py`, `docs/assets/final-submission-control.json`, `docs/assets/final-submission-control.md` aggregate the final gate, Devpost form, storyboard, credential handoff, award score, and next commands | Public-ready; `control_health_ok=true` means the control report is healthy, while `safe_to_submit=false` remains intentional until live proof/video/audit gates complete |
| Final closeout status | `scripts/final_closeout_status.py`, `docs/assets/final-closeout-status.json`, `docs/assets/final-closeout-status.md` summarize final proof, video, Devpost, secret scan, audit, bundle, and receipt gates | Public-ready; `closeout_health_ok=true` can coexist with `safe_to_submit=false` while the next command remains credential entry |
| Final closeout UI/API | `/api/judge/final-closeout`, judge-mode `Final Closeout` panel, and public Space HTML marker validation | Public-ready; exposes the no-secret blocker ledger in the product UI without requiring judges to inspect raw JSON |
| Final operator brief | `scripts/final_operator_brief.py`, `docs/assets/final-operator-brief.json`, `docs/assets/final-operator-brief.md` | Public-ready; no-secret handoff for user credential entry, Codex follow-up commands, and final safety policy |
| Final launch plan | `scripts/final_launch_plan.py`, `docs/assets/final-launch-plan.json`, `docs/assets/final-launch-plan.md` | Public-ready; no-secret phase checklist for credential entry, B2 proof, Genblaze proof, public video, final audit, and Devpost receipt |
| Final submission audit | `scripts/submission_audit.py --strict-final` checks pre-submit tasks, required artifacts, screenshots, live proof evidence, final video URL, and synchronized readiness reports | Public-ready; intentionally fails until T020/T021/T040/T041A, live proof, public video, and strict final reports are complete; T041/T042 are observer tasks |
| Devpost submission receipt | `scripts/devpost_submission_receipt.py`, `docs/assets/devpost-submission-receipt.json`, `docs/assets/devpost-submission-receipt.md` | Public-ready; pending before submit, final mode records only public Devpost `/software/<slug>` URL, timestamp, and confirmation note |
| Copy-ready Devpost packet | `docs/assets/devpost-submission-packet.json`, `docs/assets/devpost-submission-packet.md` | Public-ready in pre-live-safe mode |
| Public video check | `scripts/public_video_check.py`, `docs/assets/public-video-check.json`, `docs/assets/public-video-check.md` | Internal-ready; verifies final demo video URL is public, token-free, hosted on YouTube/Vimeo/Youku per event rules, under the event video constraint via storyboard, and reachable in strict final mode |
| Mock demo video draft | `scripts/demo_video_draft.py`, `docs/assets/demo-video-draft.json`, `docs/assets/demo-video-draft.md`, `docs/assets/proofframe-demo-draft.mp4` | Public-ready rehearsal asset; intentionally not final-safe until live B2/Genblaze proof and final video URL replace it |
| Final video publish kit | `scripts/final_video_publish_kit.py`, `GET /api/judge/video-publish-kit`, `docs/assets/final-video-publish-kit.json`, `docs/assets/final-video-publish-kit.md` | Public-ready; prepares final upload title, description, chapters, official host requirements, and Devpost video field copy while keeping `safe_to_submit=false` until the final public URL passes |
| Devpost form kit | `scripts/devpost_form_kit.py`, `GET /api/judge/devpost`, `docs/assets/devpost-form-kit.json`, `docs/assets/devpost-form-kit.md` | Public-ready for field-by-field copy; powers the in-app Devpost Kit, and strict final mode waits for live proof and a public video URL |
| Devpost submission checklist | `scripts/devpost_submission_checklist.py`, `GET /api/judge/submission-checklist`, `docs/assets/devpost-submission-checklist.json`, `docs/assets/devpost-submission-checklist.md` | Internal-ready; powers the in-app Submit Checklist and provides ordered final Devpost web copy checklist with preflight gates, stop rules, and receipt commands |
| Safe submission bundle manifest | `docs/assets/submission-bundle-manifest.json`, `docs/assets/submission-bundle-manifest.md` | Public-ready in pre-live-safe mode; `safe_to_share=true` can coexist with `safe_to_submit=false` until final live proof, video, audit, and Devpost receipt gates pass |
| Demo readiness report | `scripts/demo_readiness.py`, `docs/assets/demo-readiness-report.json`, `docs/assets/demo-readiness-report.md` | Public-ready for mock recording; strict final mode intentionally waits for T020/T021/T041A |
| Demo storyboard | `scripts/demo_storyboard.py`, `docs/assets/demo-storyboard.json`, `docs/assets/demo-storyboard.md` | Public-ready for mock recording; strict final mode waits for live proof and a public video URL |
| Recording assets report | `scripts/recording_assets.py`, `GET /api/judge/recording`, `docs/assets/recording-assets.json`, `docs/assets/recording-assets.md` | Public-ready; powers the in-app Recording Runbook, verifies committed screenshots, and can run GET-only checks against the public mock demo |
| Sponsor fit matrix | `docs/sponsor_fit_matrix.md` | Public-ready; maps official judging angles to current evidence, safe claims, final gates, and demo shots |
| Sponsor fit audit | `scripts/sponsor_fit_audit.py`, `docs/assets/sponsor-fit-audit.json`, `docs/assets/sponsor-fit-audit.md` | Public-ready; checks Devpost B2/Genblaze specificity, early demo coverage, and claim-safe final gates |
| Award readiness report | `scripts/award_readiness.py`, `docs/assets/award-readiness-report.json`, `docs/assets/award-readiness-report.md` | Public-ready; scores sponsor fit, provenance depth, demo readiness, claim safety, and final closure |
| Devpost draft | `docs/devpost_draft.md` | Public-ready after final claim check |
| Deployment runbook | `docs/deployment.md` | Public-ready |
| Docker smoke report | `scripts/docker_smoke.py`, `.dockerignore`, `docs/assets/docker-smoke-report.json`, `docs/assets/docker-smoke-report.md` | Public-ready; verifies Docker build/run/API smoke in local/mock mode and confirms local env files are excluded from the build context |
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
