# ProofFrame Public Space Sync Report

Mode: `public_space_synced`
OK: `true`
Created: `2026-06-28T02:56:31Z`
Space: `ADJCJH/backblaze-proofframe`
Public host: https://adjcjh-backblaze-proofframe.hf.space
Expected sha: `a0418b6da52376ca3984294c850e368552920404`
Runtime sha: `a0418b6da52376ca3984294c850e368552920404`
Runtime stage: `RUNNING`

## Checks

| Status | Check | Detail | Evidence |
| --- | --- | --- | --- |
| OK | Space metadata points at the expected commit | Space sha is a0418b6da52376ca3984294c850e368552920404; expected a0418b6da52376ca3984294c850e368552920404. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe |
| OK | Space runtime is running the expected commit | Runtime stage is RUNNING; runtime sha is a0418b6da52376ca3984294c850e368552920404; domain ready is True. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe/runtime |
| OK | Raw handoff report is public and ready | Handoff schema is proofframe.agent_handoff.v1; mode is handoff_ready. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/agent-handoff-report.json |
| OK | Public demo health is local/mock and ready | Health storage=local, generation=mock, ready=True. | https://adjcjh-backblaze-proofframe.hf.space/api/health |
| OK | Public submission gate is fail-closed with repo-relative paths | Gate mode is pre_live_safe; report gate is incomplete; relative paths=True. | https://adjcjh-backblaze-proofframe.hf.space/api/submission/gate |
| OK | Judge-mode HTML contains recording and sponsor markers | Markers: judge_recording_slate=True, sponsor_evidence_model=True, auto_load_judge_demo=True, final_reports_pending=True. | https://adjcjh-backblaze-proofframe.hf.space/?judge=1 |

## Next Actions

- Public Space sync evidence is ready for the pre-live Devpost demo.
