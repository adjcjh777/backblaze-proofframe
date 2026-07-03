# ProofFrame Post-Credential Live Proof Plan

Mode: `plan_only`
OK: `true`
Created: `2026-07-03T05:02:40Z`
Env file: `.env.final.local`
Update tasks: `false`

This report stores command strings, statuses, and artifact paths only. It never stores Backblaze keys, Genblaze provider keys, Devpost cookies, provider responses, or signed URLs.

## Commands

| Status | ID | Command |
| --- | --- | --- |
| PLANNED | `credential_handoff` | `python scripts/live_env_handoff.py --env-file .env.final.local --strict` |
| PLANNED | `b2_live_proof` | `python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json` |
| PLANNED | `validate_b2_evidence` | `python scripts/post_credential_live_proof.py --validate-evidence b2 --evidence-path docs/assets/b2-live-proof-evidence.json` |
| PLANNED | `final_live_proof` | `python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json` |
| PLANNED | `validate_final_evidence` | `python scripts/post_credential_live_proof.py --validate-evidence final --evidence-path docs/assets/final-live-proof-evidence.json` |
| PLANNED | `live_env_handoff_report` | `python scripts/live_env_handoff.py --env-file .env.final.local` |
| PLANNED | `devpost_form_kit` | `python scripts/devpost_form_kit.py` |
| PLANNED | `devpost_submission_checklist` | `python scripts/devpost_submission_checklist.py` |
| PLANNED | `judge_brief` | `python scripts/judge_brief.py` |
| PLANNED | `judge_crosswalk` | `python scripts/judge_crosswalk.py` |
| PLANNED | `demo_storyboard` | `python scripts/demo_storyboard.py` |
| PLANNED | `demo_readiness` | `python scripts/demo_readiness.py` |
| PLANNED | `recording_assets` | `python scripts/recording_assets.py --verify-public` |
| PLANNED | `award_readiness` | `python scripts/award_readiness.py --min-score 75` |
| PLANNED | `final_operator_brief` | `python scripts/final_operator_brief.py` |
| PLANNED | `final_launch_plan` | `python scripts/final_launch_plan.py` |
| PLANNED | `final_rehearsal` | `python scripts/final_rehearsal.py` |
| PLANNED | `final_submission_control` | `python scripts/final_submission_control.py` |
| PLANNED | `submission_audit` | `python scripts/submission_audit.py` |
| PLANNED | `devpost_submission_preview` | `python scripts/devpost_submission_preview.py` |
| PLANNED | `secret_scan` | `python scripts/secret_scan.py` |
| PLANNED | `submission_bundle` | `python scripts/submission_bundle.py` |

## Next Actions

- If mode is plan_only, rerun with --execute after credentials are entered locally.
- If live proof succeeds, record and upload the final public demo video.
- After the public video is verified, run the final secret scan, strict audit, Devpost submit, and receipt capture.
