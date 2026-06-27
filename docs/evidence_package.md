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

## Current Verified Evidence

| Evidence | Location | Status |
| --- | --- | --- |
| PRD | `docs/prd.md` | Public-ready |
| Technical spec | `docs/spec.md` | Public-ready |
| Submission plan | `docs/submission.md` | Public-ready after final claim check |
| Local Proof Ledger UI | `apps/web/index.html` | Public-ready |
| Review console | scorecard, status filter, search, safe summary copy in `apps/web/index.html` | Public-ready in local/mock mode |
| Review console smoke screenshot | `docs/assets/proofframe-review-console-smoke.png` | Public-ready in local/mock mode |
| UI smoke screenshot | `docs/assets/proofframe-local-ui-smoke.png` | Public-ready |
| Public HF Space smoke screenshot | `docs/assets/proofframe-hf-public-smoke.png` | Public-ready in local/mock mode |
| Public HF Space API smoke | `python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space` | Passed in local/mock mode |
| Public HF Space judge-mode sync | Public HTML contains `shouldAutoLoadJudgeDemo`; `/api/submission/gate` returns `pre_live_safe` | Public-ready in local/mock mode |
| Devpost registration | `tasks.json` T040 | Done; registered for the event |
| Downloadable evidence ZIP | `/api/campaigns/{id}/packet.zip` | Public-ready in local mode |
| One-click judge packet | `/api/demo/judge-packet` | Public-ready in local mode |
| Final live proof preflight | `scripts/live_proof.py --preflight-only` | Public-ready; reports missing env/packages without printing secrets |
| Evidence safety gate | `scripts/api_smoke.py --evidence-out` refuses secret-like keys and signed-token values before writing JSON | Public-ready |
| Final submission audit | `scripts/submission_audit.py` checks final task gates, required artifacts, screenshots, and live proof evidence | Public-ready; intentionally fails until T020/T021/T040/T041/T041A/T042 are complete |
| Copy-ready Devpost packet | `docs/assets/devpost-submission-packet.json`, `docs/assets/devpost-submission-packet.md` | Public-ready in pre-live-safe mode |
| Safe submission bundle manifest | `docs/assets/submission-bundle-manifest.json`, `docs/assets/submission-bundle-manifest.md` | Public-ready in pre-live-safe mode |
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

> A provenance-first vault for generated media.

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
