---
title: Backblaze ProofFrame
sdk: docker
app_port: 8088
---

# ProofFrame

ProofFrame is a provenance-first generative media vault for the Backblaze Generative Media Hackathon.

It turns a creative brief into a reviewable asset packet: generated media, prompt history, model/provider metadata, hashes, approval state, and a shareable manifest. The local demo uses deterministic generation and local storage; the final hackathon gate is to verify the same packet flow through Genblaze-backed generation and Backblaze B2-compatible storage. The product goal is not "yet another image generator"; it is the missing operations desk for teams that need to know where an AI asset came from, whether it is approved, and how to reproduce or retire it.

## Hackathon Choice

Selected competition: [Backblaze Generative Media Hackathon](https://backblaze-generative-media.devpost.com/)

Public mock demo: [Hugging Face Space Judge Mode](https://adjcjh-backblaze-proofframe.hf.space/?judge=1) (credential-free local/mock mode; final B2 and Genblaze live proof remains gated).

Why this one:

- Online Devpost format with a clear August 3, 2026 5:00 PM EDT deadline, which is August 4, 2026 05:00 in Beijing.
- Cash prizes, including a $7,000 grand prize.
- Moderate visible participant count compared with larger AI agent events.
- Sponsor requirements are specific enough to reward meaningful integration: Genblaze plus Backblaze B2.
- A polished, useful product can beat a raw model demo here.

## Judge Quickstart

For a 60-second review path:

1. Open the [public judge-mode demo](https://adjcjh-backblaze-proofframe.hf.space/?judge=1).
2. Read the first-screen Sponsor Evidence Model and fail-closed gate status.
3. Use the one-click Judge Demo packet if it does not auto-load.
4. Inspect the generated asset ledger, manifest preview, approval state, checksum, and evidence ZIP.
5. Treat the public run as local/mock mode: B2 and Genblaze integration code paths are present, but live B2/Genblaze proof remains the final gate before sponsor-complete claims.

Copy-ready judge brief: `docs/assets/judge-brief.md`.
Official criteria crosswalk: `docs/assets/judge-crosswalk.md`.

## Core Documents

- `docs/research.md`: competition search, candidate comparison, selected-event evidence.
- `docs/prd.md`: product PRD.
- `docs/spec.md`: technical specification.
- `docs/integrations.md`: B2 and Genblaze readiness gates.
- `docs/deployment.md`: public demo deployment runbook.
- `docs/devpost_draft.md`: copy-ready Devpost draft with claim gates.
- `docs/demo_script.md`: demo video script and shot list.
- `docs/evidence_package.md`: Devpost evidence package and copy bank.
- `docs/public_claim_freeze.md`: public claim boundaries before final submission.
- `docs/verification.md`: local, Docker, live proof, and secret-scan runbook.
- `docs/submission.md`: registration and submission plan.
- `docs/todo.md`: human task board.
- `tasks.json`: queryable task ledger.

## Local Task Commands

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py search Genblaze --status doing
python3 scripts/task.py show T001
python3 scripts/task.py add T099 "Record final demo" --phase "P4 Submit" --owner controller --after T041
python3 scripts/task.py done T001
python3 scripts/task.py blocked T010 --note "Requires account setup"
```

## Planned Stack

- Backend: Python, FastAPI, SQLite.
- Storage: local storage for offline demo, Backblaze B2 S3-compatible storage for submission.
- Generation: deterministic mock provider for local tests, Genblaze/OpenAI-compatible media provider adapter for real runs.
- Frontend: production-grade browser UI with `apps/web/index.html` as entry point.
- Packaging: Dockerfile and release checklist.

## Current Status

Stage 0 is complete: selected competition, repo, PRD/spec/todo, Agent Bus team, official-rule scout report, and GitHub setup.

Stage 1 is complete enough for local demo iteration: FastAPI MVP skeleton, mock generation, local storage, manifest export, downloadable evidence packets, one-click Judge Demo packets, and the Proof Ledger browser UI.

Stage 2 is in progress: B2-compatible storage code and a Genblaze/GMICloud image provider path exist. In final B2 mode, the Genblaze path now uses the official `ObjectStorageSink` plus `S3StorageBackend.for_backblaze` so Genblaze provenance output can land in B2 before ProofFrame records its own packet manifest. Live B2 and Genblaze runs still need credentials/provider verification before final submission claims.

Stage 3 preparation is active: the public mock demo is deployed, Review Console polish is captured, Devpost/evidence/claim-freeze docs are ready for the final sponsor-integration pass, API evidence exports fail closed if secret-like values appear, and the app now displays a fail-closed submission gate dashboard, judge recording slate, criteria crosswalk, recording runbook, Devpost kit, and submit checklist for final task/live-proof status.

![ProofFrame local UI smoke](docs/assets/proofframe-local-ui-smoke.png)

![ProofFrame review console smoke](docs/assets/proofframe-review-console-smoke.png)

## Run Locally

```bash
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,integrations]"
pytest
uvicorn proofframe.app:app --reload --port 8088
```

Then open `http://127.0.0.1:8088/`.

## Integration Readiness

```bash
. .venv/bin/activate
python scripts/check_integrations.py
python scripts/genblaze_contract_check.py
python scripts/docker_smoke.py
python scripts/live_proof.py --preflight-only
python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only
python scripts/live_env_handoff.py
python scripts/final_env_wizard.py --check-only
python scripts/b2_key_scope_checklist.py
python scripts/devpost_form_kit.py
python scripts/devpost_submission_checklist.py
python scripts/judge_brief.py
python scripts/judge_crosswalk.py
python scripts/judge_decision_brief.py
python scripts/devpost_event_snapshot.py --validate-committed
python scripts/agent_handoff_check.py
python scripts/public_space_upload.py
python scripts/public_space_sync.py --wait-attempts 5 --wait-seconds 30
python scripts/claim_lint.py
python scripts/demo_storyboard.py
python scripts/demo_video_draft.py --build-video
python scripts/public_video_check.py
python scripts/sponsor_fit_audit.py
python scripts/demo_readiness.py
python scripts/recording_assets.py
python scripts/award_readiness.py --min-score 75
python scripts/final_submission_control.py
python scripts/final_closeout_status.py
python scripts/final_operator_brief.py
python scripts/final_launch_plan.py
python scripts/submission_audit.py
python scripts/devpost_submission_receipt.py
python scripts/devpost_packet.py
python scripts/submission_bundle.py
```

The browser UI and `GET /api/submission/gate` expose the same fail-closed final gate: required task status, Devpost packet presence, final B2/Genblaze evidence readiness, and the final secret scan, submission audit, and Devpost receipt reports.
`scripts/submission_bundle.py` creates a safe manifest of public submission artifacts, screenshots, checksums, Devpost copy mode, and remaining gate blockers.
`scripts/live_env_handoff.py` creates a redacted B2/Genblaze credential handoff report so final proof setup can be checked without printing keys.
`scripts/public_space_upload.py` dry-runs the Hugging Face Space upload plan by default, excludes local env files and runtime folders, and can execute the upload only after the no-secret preflight passes.
`scripts/genblaze_contract_check.py` verifies the installed Genblaze/B2 SDK import and signature contract without reading environment variables or credential files, catching package/API drift before live keys are entered.
`scripts/docker_smoke.py` verifies the Docker image builds, starts in local/mock mode, passes API smoke, and uses `.dockerignore` to keep local env files out of the build context.
`scripts/final_env_wizard.py` creates a local git-ignored `.env.final.local` with 0600 permissions, can prefill non-secret B2/default values, reads existing local values as defaults, and uses hidden prompts for credential values. Its `--check-only` mode is a no-secret readiness preflight for git-ignore status, `.env.final.local` presence, chmod `0600`, missing or placeholder variable names, and B2 region derivation.
`scripts/b2_key_scope_checklist.py` creates a no-secret B2 app-key scope checklist for the dedicated bucket, prefix, required upload capability, S3 SDK compatibility flag, forbidden permissions, and stop conditions before a key is created.
`scripts/run_b2_live_proof.py` verifies the Backblaze B2 storage path independently with mock generation, so T020 can close before Genblaze credentials are ready.
`scripts/devpost_form_kit.py` turns the safe packet into field-by-field Devpost copy with length checks, a strict final gate, and an in-app Devpost Kit through `GET /api/judge/devpost`.
`scripts/devpost_submission_checklist.py` turns the final form kit into an ordered, no-secret Devpost web submission checklist with preflight gates, copy order, stop rules, post-submit receipt commands, and an in-app Submit Checklist through `GET /api/judge/submission-checklist`.
`scripts/judge_brief.py` condenses the current public demo, award posture, safe claims, and final blockers into a 30-second judge brief.
`scripts/judge_crosswalk.py` maps official judging criteria and submission requirements to current evidence, safe claims, final gates, and demo shots; the browser UI exposes the same map through `GET /api/judge/crosswalk`.
`scripts/judge_decision_brief.py` builds the one-page judge decision card behind `GET /api/judge/decision-brief`, summarizing why to score ProofFrame highly, what public evidence is green, and which final gates remain without overclaiming.
`scripts/judge_evidence_index.py` builds the public-safe evidence index behind `GET /api/judge/evidence-index`, collecting the judge brief, criteria crosswalk, decision brief, final gate, Devpost preview, recording assets, and live-proof gates without changing `safe_to_submit=false`.
`scripts/final_rehearsal.py` turns the final operator brief, launch plan, public sync, and gates into a no-secret final-submission rehearsal checklist.
`scripts/devpost_event_snapshot.py` keeps official Devpost deadline, participants, submission requirements, and judging criteria as a refreshable evidence report.
`scripts/agent_handoff_check.py` keeps AGENTS.md, Codex, and Agent Bus handoff paths aligned with the current repo so future role sessions do not follow stale project metadata.
`scripts/public_space_sync.py` verifies the public Hugging Face Space runtime sha, raw handoff, Devpost event snapshot, final launch plan, B2 key scope checklist, Genblaze SDK contract report, judge brief, judge crosswalk, judge decision brief, judge evidence index, final closeout status, final video publish kit, mock video draft, public video check, health/gate APIs, and judge-mode HTML markers.
`scripts/run_final_live_proof.py` is the final one-command live runner: once B2 and Genblaze env vars are present, it starts the app, verifies `/api/health` reports `b2` plus `genblaze`, routes Genblaze output through the B2 sink, writes sanitized final evidence, and stops the server.
`scripts/claim_lint.py` keeps pre-live public copy from claiming completed Backblaze B2 or Genblaze proof before evidence exists.
`scripts/secret_scan.py` writes a no-value secret scan report for public files, generated evidence, local logs, and media inventory while excluding local credential files without reading them.
`scripts/demo_storyboard.py` keeps the demo video timeline under 3 minutes and tracks the public video URL as a final gate.
`scripts/demo_video_draft.py` builds a public-safe mock MP4 draft from committed screenshots for rehearsal, while explicitly keeping `safe_to_submit=false` and `final_video_ready=false`.
`scripts/final_video_publish_kit.py` prepares final upload title, description, chapters, allowed hosts, and the Devpost video field gate without marking the video ready before the public URL passes.
`scripts/public_video_check.py` verifies the final public demo video URL is non-placeholder, token-free, hosted on an allowed Devpost public video family (YouTube, Vimeo, or Youku), and reachable before final submission.
`scripts/sponsor_fit_audit.py` checks that Backblaze B2 and Genblaze are explained as product-critical sponsor paths without overclaiming live proof.
`scripts/demo_readiness.py` keeps the mock demo recording package ready while failing strict final mode until live B2/Genblaze proof and the final secret scan are complete.
`scripts/recording_assets.py` checks committed recording assets, powers the in-app Recording Runbook through `GET /api/judge/recording`, and can run GET-only public demo verification without creating data or using secrets.
`scripts/award_readiness.py` scores sponsor fit, provenance depth, demo readiness, claim safety, and final closure so polish work stays aligned with judge expectations.
`scripts/final_submission_control.py` aggregates the gate, form kit, storyboard, credential handoff, and award reports into one final Devpost control tower.
`scripts/final_closeout_status.py` summarizes final live proof, public video, Devpost, secret scan, audit, bundle, and receipt gates into one no-secret closeout report with the next command to run.
`scripts/final_operator_brief.py` turns the remaining live-proof blockers into a no-secret handoff: user actions, Codex follow-up commands, and safety policy.
`scripts/final_launch_plan.py` turns the final operator brief and gate reports into a no-secret phased launch checklist from credential entry through Devpost receipt.
`scripts/submission_audit.py` writes a schema-stamped pre-submit audit report and only passes strict mode after live proof, final scan, public video, and submit-ready copy are synchronized.
`scripts/devpost_submission_receipt.py` records the final public Devpost `/software/<slug>` URL and confirmation note after submission, without cookies or private form data.

B2 mode intentionally fails closed unless `B2_ENDPOINT_URL`, `B2_BUCKET`, `B2_KEY_ID`, and `B2_APPLICATION_KEY` are set. Final Genblaze+B2 proof also requires a B2 region, either via `B2_REGION` or a standard Backblaze S3 endpoint such as `https://s3.us-west-004.backblazeb2.com`. Genblaze mode intentionally fails closed unless a Genblaze/GMI key and `GENBLAZE_IMAGE_MODEL` are set, and the official `genblaze-core`, `genblaze-gmicloud`, and `genblaze-s3` packages are installed.

## Submission Verification

The repository also runs the same core checks in GitHub Actions on `main`, `feature/**`, and pull requests.

```bash
. .venv/bin/activate
python scripts/check_integrations.py
python scripts/genblaze_contract_check.py
ruff check .
pytest
python scripts/api_smoke.py --base-url http://127.0.0.1:8088
python scripts/secret_scan.py
python scripts/claim_lint.py
python scripts/live_env_handoff.py
python scripts/final_env_wizard.py --check-only
python scripts/b2_key_scope_checklist.py
python scripts/devpost_form_kit.py
python scripts/devpost_submission_checklist.py
python scripts/judge_brief.py
python scripts/judge_crosswalk.py
python scripts/judge_decision_brief.py
python scripts/devpost_event_snapshot.py --validate-committed
python scripts/agent_handoff_check.py
python scripts/public_space_sync.py
python scripts/demo_storyboard.py
python scripts/demo_video_draft.py
python scripts/public_video_check.py
python scripts/demo_readiness.py
python scripts/recording_assets.py
python scripts/final_operator_brief.py
python scripts/final_launch_plan.py
```

See `docs/verification.md` for Docker and live B2/Genblaze proof commands.
