# ProofFrame Public Space Sync Report

Mode: `public_space_synced`
OK: `true`
Created: `2026-06-28T10:14:56Z`
Space: `ADJCJH/backblaze-proofframe`
Public host: https://adjcjh-backblaze-proofframe.hf.space
Expected sha: `52b556cc5935a2988ebb1c7ba30a5069f9eb887f`
Runtime sha: `52b556cc5935a2988ebb1c7ba30a5069f9eb887f`
Runtime stage: `RUNNING`

## Checks

| Status | Check | Detail | Evidence |
| --- | --- | --- | --- |
| OK | Space metadata points at the expected commit | Space sha is 52b556cc5935a2988ebb1c7ba30a5069f9eb887f; expected 52b556cc5935a2988ebb1c7ba30a5069f9eb887f. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe |
| OK | Space runtime is running the expected commit | Runtime stage is RUNNING; runtime sha is 52b556cc5935a2988ebb1c7ba30a5069f9eb887f; domain ready is True. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe/runtime |
| OK | Raw handoff report is public and ready | Handoff schema is proofframe.agent_handoff.v1; mode is handoff_ready. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/agent-handoff-report.json |
| OK | Raw final launch plan is public and phase-aware | Launch plan schema is proofframe.final_launch_plan.v1; mode is ready_for_credential_entry; current phase is credential_entry. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/final-launch-plan.json |
| OK | Raw judge brief is public and claim-safe | Judge brief schema is proofframe.judge_brief.v1; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/judge-brief.json |
| OK | Raw judge crosswalk is public and claim-safe | Judge crosswalk schema is proofframe.judge_crosswalk.v1; mode is pre_live_crosswalk_ready; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/judge-crosswalk.json |
| OK | Raw recording runbook is public and final-video gated | Recording schema is proofframe.recording_assets.v1; mode is public_mock_verified; final_video_ready is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/recording-assets.json |
| OK | Raw mock demo video draft report is public and fail-closed | Draft schema is proofframe.demo_video_draft.v1; mode is mock_video_draft_ready; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/demo-video-draft.json |
| OK | Mock demo video draft MP4 is publicly readable | status=200; bytes=761356; content_type=video/mp4. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/resolve/main/docs/assets/proofframe-demo-draft.mp4 |
| OK | Raw Devpost form kit is public and final-form gated | Devpost form schema is proofframe.devpost_form_kit.v1; mode is pre_live_form_ready; final_form_ready is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-form-kit.json |
| OK | Raw Devpost submit checklist is public and fail-closed | Submit checklist schema is proofframe.devpost_submission_checklist.v1; mode is pre_submit_blocked; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-submission-checklist.json |
| OK | Public demo health is local/mock and ready | Health storage=local, generation=mock, ready=True. | https://adjcjh-backblaze-proofframe.hf.space/api/health |
| OK | Public submission gate is fail-closed with repo-relative paths | Gate mode is pre_live_safe; report gate is incomplete; relative paths=True. | https://adjcjh-backblaze-proofframe.hf.space/api/submission/gate |
| OK | Judge-mode HTML contains recording and sponsor markers | Markers: judge_recording_slate=True, sponsor_evidence_model=True, judge_brief_panel=True, criteria_crosswalk_link=True, recording_runbook_panel=True, devpost_kit_panel=True, submit_checklist_panel=True, auto_load_judge_demo=True, final_reports_pending=True. | https://adjcjh-backblaze-proofframe.hf.space/?judge=1 |

## Next Actions

- Public Space sync evidence is ready for the pre-live Devpost demo.
