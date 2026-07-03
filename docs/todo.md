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

1. Record and upload the final demo video to YouTube, Vimeo, or Youku using `docs/demo_script.md`, then verify it with `python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final`.
2. Regenerate `docs/assets/devpost-submission-packet.*` with `python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"`.
3. Run the final secret scan only after the public video and Devpost-safe artifacts are staged, then mark `T041A` done only if it remains clear.
4. Run strict form/storyboard/readiness gates and `python scripts/submission_audit.py --strict-final`, then mark `T041` done only if green.
5. Submit the Devpost project, capture the public-safe receipt URL/screenshot, run `scripts/devpost_submission_receipt.py`, then mark `T042` done.
6. Keep final `safe_to_submit=true` claims frozen until public video, final audit, final scan, and Devpost receipt are all complete.

## Current Final Gate Status

Last refreshed: `2026-07-03`.

| Task | True status | Evidence |
| --- | --- | --- |
| T020 | `done` | B2 live proof passed with scoped standard key against bucket `proofframe-demo-a6b4e49` and prefix `campaigns/`; sanitized evidence is saved at `docs/assets/b2-live-proof-evidence.json`. |
| T021 | `done` | Final B2 plus Genblaze live proof passed through the credential-free local Genblaze Pipeline provider; sanitized evidence is saved at `docs/assets/final-live-proof-evidence.json` with `asset_provider=genblaze/local-image`, `storage_backend=b2`, checksums, and B2 object keys. |
| T041 | `blocked` | Post-live audit is blocked by missing final public video URL, T041A final scan completion, and Devpost receipt; current non-strict audit remains `pre_submit_audit_blocked` in `docs/assets/submission-audit-report.json`. |
| T041A | `blocked` | Current secret scan is clear at `docs/assets/secret-scan-report.json`, but the final scan stays blocked until public video and Devpost-safe submission artifacts are staged. |
| T042 | `blocked` | Devpost submission is blocked by missing public video URL plus final audit/secret-scan gates; no Devpost receipt URL is present, and final submission control remains `phase=public_video`. |

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
