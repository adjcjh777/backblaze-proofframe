# ProofFrame Task Board

Use `tasks.json` as the source of truth and `scripts/task.py` for machine-readable updates.

## Commands

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py search B2
python3 scripts/task.py search Devpost
python3 scripts/task.py show T001
python3 scripts/task.py add T099 "Record final demo" --phase "P4 Submit" --owner controller --after T041
python3 scripts/task.py done T001
python3 scripts/task.py doing T020 --note "Live B2 proof in progress"
```

## Phases

| Phase | Goal |
| --- | --- |
| P0 Foundation | Pick contest, create repo, write PRD/spec/todo, create team. |
| P1 MVP | Local app, manifest, mock generation, review UI. |
| P2 Integrations | B2 and Genblaze real paths, Docker, evidence. |
| P3 Polish | UI, samples, tests, demo video, public-claim freeze, evidence package. |
| P4 Submit | Devpost registration, final audit, submission. |

## Current Priority

1. Copy `.env.final.example` to `.env.final.local`, fill B2/Genblaze values outside git, confirm `B2_REGION` is set or derivable from `B2_ENDPOINT_URL`, then run `python scripts/live_env_handoff.py --env-file .env.final.local`.
2. Complete live Backblaze B2 upload proof for one asset and one manifest.
3. Complete live Genblaze-backed generation proof and capture provider/model metadata.
4. Record and upload the demo video to YouTube, Vimeo, or Youku using `docs/demo_script.md`, then regenerate `docs/assets/devpost-submission-packet.*` with `python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"`.
5. Run the final secret scan, strict form/storyboard/readiness gates, and `python scripts/submission_audit.py --strict-final`.
6. Keep public claims frozen with `docs/public_claim_freeze.md` until real B2 and Genblaze evidence exists and the strict audit is green.

## Recently Completed

| Task | Result |
| --- | --- |
| T082 | Judge decision brief generated, exposed in judge API/frontend, checked by public Space sync, and included in the submission bundle. |
| T083 | Official Devpost event snapshot refreshed from live overview/rules pages, downstream reports regenerated, and public Space sync passed. |
| T084 | Genblaze final path now uses the official B2 sink contract in B2 mode, with preflight coverage for `genblaze_s3` and B2 region readiness. |
| T085 | No-secret Genblaze/B2 SDK contract check added to CI, reports, submission bundle, and public sync required artifacts. |
| T086 | Docker build/run/API smoke report added with `.dockerignore` protection for local env files and submission checklist evidence. |
| T087 | Final closeout status report added so live proof, public video, Devpost, receipt, audit, bundle, and next command are visible in one no-secret gate. |
| T088 | Final closeout status exposed in judge evidence index and raw public Space sync validation as a fail-closed public blocker ledger. |
| T089 | Review findings hardened: real live credential handoff output, T020/T021 done checks, public raw closeout validation, and strict bundle closeout freshness are covered. |
| T090 | Final closeout status is now available through `/api/judge/final-closeout`, a judge-mode UI panel/link, API smoke, and public Space HTML marker validation. |
| T091 | Final closeout public sync now accepts both pre-final fail-closed and final-ready all-green states, validates the API against raw evidence, and keeps the UI next command visible. |
| T092 | No-secret live credential handoff regenerated from `.env.final.local`; remaining local credential blockers are narrowed to `b2_key_id`, `b2_application_key`, and `genblaze_api_key`. |
| T093 | Final env `--check-only` now performs no-secret readiness preflight for git-ignore, chmod `0600`, missing/placeholder names, B2 region derivation, and `B2_APP_KEY` alias handling. |
| T094 | Final rehearsal checklist regenerated from the current operator brief so the strict rehearsal gate is green and only the three expected secret blockers remain. |
| T095 | Public Space sync evidence refreshed against the live HF runtime, including final closeout raw/API checks, then downstream final reports were regenerated. |
| T096 | Official Devpost event snapshot refreshed from live overview/rules pages; submission remains open and observed participants are now `404` with dynamic-count warning preserved. |
| T097 | Public HF Space synced to the refreshed Devpost event snapshot at runtime `eab3ee62`; public Space sync and API smoke pass while remaining fail-closed. |
| T098 | No-secret public Space upload helper added with dry-run safety checks, explicit execute mode, raw `.env.final.local` public 404 probe, tests, docs, CI, and bundle coverage. |
| T099 | Public HF Space synced through the no-secret upload helper; raw `.env.final.local` public probe, public Space sync, and public API smoke all pass while final submission remains fail-closed. Current runtime sha is tracked in `docs/assets/public-space-sync-report.json`. |
| T100 | Post-credential live proof plan now renders portable `python scripts/...` commands without local absolute paths, while keeping execution argv semantics and public sync validation. |
| T101 | Final operator actions now include public Space upload, waited public sync, and public API smoke after live proof and after final receipt; `public_space_sync.py` supports rollout wait attempts. |
