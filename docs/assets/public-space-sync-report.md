# ProofFrame Public Space Sync Report

Mode: `public_space_synced`
OK: `true`
Created: `2026-06-28T05:07:03Z`
Space: `ADJCJH/backblaze-proofframe`
Public host: https://adjcjh-backblaze-proofframe.hf.space
Expected sha: `cbb686640283a157a6ab93a68ff5b0b5d7848977`
Runtime sha: `cbb686640283a157a6ab93a68ff5b0b5d7848977`
Runtime stage: `RUNNING`

## Checks

| Status | Check | Detail | Evidence |
| --- | --- | --- | --- |
| OK | Space metadata points at the expected commit | Space sha is cbb686640283a157a6ab93a68ff5b0b5d7848977; expected cbb686640283a157a6ab93a68ff5b0b5d7848977. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe |
| OK | Space runtime is running the expected commit | Runtime stage is RUNNING; runtime sha is cbb686640283a157a6ab93a68ff5b0b5d7848977; domain ready is True. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe/runtime |
| OK | Raw handoff report is public and ready | Handoff schema is proofframe.agent_handoff.v1; mode is handoff_ready. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/agent-handoff-report.json |
| OK | Raw final launch plan is public and phase-aware | Launch plan schema is proofframe.final_launch_plan.v1; mode is ready_for_credential_entry; current phase is credential_entry. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/final-launch-plan.json |
| OK | Raw judge brief is public and claim-safe | Judge brief schema is proofframe.judge_brief.v1; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/judge-brief.json |
| OK | Public demo health is local/mock and ready | Health storage=local, generation=mock, ready=True. | https://adjcjh-backblaze-proofframe.hf.space/api/health |
| OK | Public submission gate is fail-closed with repo-relative paths | Gate mode is pre_live_safe; report gate is incomplete; relative paths=True. | https://adjcjh-backblaze-proofframe.hf.space/api/submission/gate |
| OK | Judge-mode HTML contains recording and sponsor markers | Markers: judge_recording_slate=True, sponsor_evidence_model=True, judge_brief_panel=True, auto_load_judge_demo=True, final_reports_pending=True. | https://adjcjh-backblaze-proofframe.hf.space/?judge=1 |

## Next Actions

- Public Space sync evidence is ready for the pre-live Devpost demo.
