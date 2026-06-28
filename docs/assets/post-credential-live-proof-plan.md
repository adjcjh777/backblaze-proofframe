# ProofFrame Post-Credential Live Proof Plan

Mode: `plan_only`
OK: `true`
Created: `2026-06-28T15:48:26Z`
Env file: `.env.final.local`
Update tasks: `false`

This report stores command strings, statuses, and artifact paths only. It never stores Backblaze keys, Genblaze/GMI keys, Devpost cookies, provider responses, or signed URLs.

## Commands

| Status | ID | Command |
| --- | --- | --- |
| PLANNED | `credential_handoff` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/live_env_handoff.py --env-file .env.final.local --strict` |
| PLANNED | `b2_live_proof` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json` |
| PLANNED | `validate_b2_evidence` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/post_credential_live_proof.py --validate-evidence b2 --evidence-path docs/assets/b2-live-proof-evidence.json` |
| PLANNED | `final_live_proof` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json` |
| PLANNED | `validate_final_evidence` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/post_credential_live_proof.py --validate-evidence final --evidence-path docs/assets/final-live-proof-evidence.json` |
| PLANNED | `live_env_handoff_report` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/live_env_handoff.py --env-file .env.final.local` |
| PLANNED | `devpost_form_kit` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/devpost_form_kit.py` |
| PLANNED | `devpost_submission_checklist` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/devpost_submission_checklist.py` |
| PLANNED | `judge_brief` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/judge_brief.py` |
| PLANNED | `judge_crosswalk` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/judge_crosswalk.py` |
| PLANNED | `demo_storyboard` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/demo_storyboard.py` |
| PLANNED | `demo_readiness` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/demo_readiness.py` |
| PLANNED | `recording_assets` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/recording_assets.py --verify-public` |
| PLANNED | `award_readiness` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/award_readiness.py --min-score 75` |
| PLANNED | `final_operator_brief` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/final_operator_brief.py` |
| PLANNED | `final_launch_plan` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/final_launch_plan.py` |
| PLANNED | `final_rehearsal` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/final_rehearsal.py` |
| PLANNED | `final_submission_control` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/final_submission_control.py` |
| PLANNED | `submission_audit` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/submission_audit.py` |
| PLANNED | `secret_scan` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/secret_scan.py` |
| PLANNED | `submission_bundle` | `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python /Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/scripts/submission_bundle.py` |

## Next Actions

- If mode is plan_only, rerun with --execute after credentials are entered locally.
- If live proof succeeds, record and upload the final public demo video.
- After the public video is verified, run the final secret scan, strict audit, Devpost submit, and receipt capture.
