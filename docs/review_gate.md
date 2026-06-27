# ProofFrame Review Gate

Date: 2026-06-27 Asia/Shanghai  
Reviewer: proofframe-hackathon-reviewer  
Scope: security, compliance, submission risk, Devpost/B2/Genblaze blockers, and public claim boundaries.

## Verdict

**HOLD for final Devpost submission.**

The repo is directionally safe for continued MVP work: no obvious committed secrets were found, `.env.example` is blank, `.gitignore` excludes local secrets and generated runtime folders, and the current implementation is honest local/mock infrastructure.

It is **not ready for final submission** because the mandatory Backblaze B2 and Genblaze paths are not implemented or verified yet, Devpost registration/submission remains manual and incomplete, and the working app/video/evidence package is not ready.

## Blocking Risks

1. **Backblaze B2 requirement is not satisfied yet.** Current code uses `LocalStorageBackend` only. `tasks.json` still lists `T020` as todo. Do not claim a working B2-backed run until an asset and manifest are stored in a dedicated B2 bucket using environment-only credentials.

2. **Genblaze requirement is not satisfied yet.** Current code uses `MockMediaProvider` only. `tasks.json` still lists `T021` as todo. The final submission must demonstrate real Genblaze or Genblaze-compatible orchestration, not only a planned adapter or local mock.

3. **Devpost access and submission are not complete.** `T040` is blocked on manual registration/login/terms acceptance, and `T042` is todo. A representative must join the event and confirm the submission form requirements before freeze.

4. **Submission assets are missing.** The final package still needs a functioning app URL or judge-accessible deployment, public demo video under the event limit, screenshots, repo URL, setup README evidence, AI provider/model list, and clear B2/Genblaze usage explanation.

5. **Draft pitch overclaims if submitted as-is before integrations.** `docs/submission.md` says ProofFrame "creates media through a Genblaze-compatible pipeline" and "stores every asset and manifest through Backblaze B2." This is acceptable as target copy only after B2 and Genblaze evidence exists. Until then, public copy must say "planned", "local mock mode", or "B2/Genblaze integration in progress."

## Non-Blocking Risks

1. **Deadline and prize facts were recently corrected.** Current docs align with the scout report's Eastern Time / Beijing 05:00 deadline and $7,000 / $2,000 / $1,000 prize split. Recheck the official Devpost rules before final submission because these are public factual claims.

2. **Participant count is dynamic.** Avoid using an exact participant count as a current competitive claim unless it is freshly checked on Devpost.

3. **System Python is not a valid verification environment.** `python3 -m pytest` failed because the system interpreter has no `pytest` module, while the project venv passed. Final gates should use the project venv or Docker image.

4. **Public repo vs private repo remains a tradeoff.** Public repo reduces judge friction but increases secret/media exposure risk. If private, Backblaze/Devpost judge access must be granted exactly as required by the rules.

5. **Generated sample media needs IP review.** Demo assets should avoid trademarks, copyrighted characters, private likenesses, copyrighted music, or brand-confusing prompts unless rights are explicit.

## Recommended Gates

1. **Gate A: B2 proof.** Create a dedicated B2 bucket and least-privilege application key. Run one end-to-end storage flow that uploads media and manifest, records sanitized object keys/checksums, and fails closed when B2 env vars are absent.

2. **Gate B: Genblaze proof.** Run one real Genblaze or Genblaze-compatible generation flow, capture provider/model/request metadata in the manifest, and document the fallback path when credits or remote provider access are unavailable.

3. **Gate C: Claim freeze.** Before recording the video or publishing Devpost text, grep all public docs for future-tense integration claims and update them to match verified behavior only.

4. **Gate D: Submission evidence.** Prepare English Devpost text, public demo video, screenshots, working app URL or Docker instructions, repo URL, AI provider/model list, and explicit "How we use Backblaze B2 and Genblaze" section.

5. **Gate E: Verification.** Run unit tests, API smoke, browser happy-path smoke, Docker build/run, secret scan, and final `git status --short --branch` before submission.

6. **Gate F: Manual Devpost check.** Confirm registration, eligibility, team representative, final deadline timezone, rules language, app access requirements, and repo access requirements in the official Devpost UI.

## Secret Hygiene Checklist

- [x] `.env.example` contains placeholder keys only.
- [x] `.gitignore` excludes `.env`, `.env.*`, `.venv/`, cache directories, `var/`, build outputs, and `node_modules/`.
- [x] Repo scan found no obvious committed API keys, B2 credentials, Devpost cookies, bearer tokens, or application keys.
- [ ] Use only least-privilege B2 application keys for demo/deployment.
- [ ] Keep B2, Genblaze, provider, Devpost, and judge-account credentials in environment variables or the hosting secret store only.
- [ ] Do not print full signed URLs, application keys, access keys, bearer tokens, cookies, or private bucket paths in logs, screenshots, demo video, or exported manifests.
- [ ] Redact or hash sensitive object identifiers if public screenshots show storage details.
- [ ] Ensure `var/`, generated private media, downloaded credentials, local SQLite files, and browser session artifacts are never force-added.
- [ ] Rotate demo credentials after public judging if they were exposed to a deployment, test account, or shared judge environment.
- [ ] Run a final secret scan immediately before the submission/release commit.

## Checks Performed

- Confirmed working directory with `pwd`.
- Confirmed branch/status with `git status --short --branch`.
- Ran `git pull --ff-only`; repository was already up to date.
- Read `AGENTS.md`, `README.md`, `docs/research.md`, `docs/prd.md`, `docs/spec.md`, `docs/submission.md`, and `tasks.json`.
- Also read `docs/scout_report.md`, `.env.example`, `.gitignore`, and current implementation files relevant to B2/Genblaze/storage claims.
- Ran repository file listing and secret-pattern search.
- Attempted `python3 -m pytest`; it failed because `pytest` is not installed for the system Python.
- Ran `.venv/bin/python -m pytest`; result: 2 passed, 1 warning.
