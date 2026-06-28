# ProofFrame Public Space Sync Report

Mode: `public_space_synced`
OK: `true`
Created: `2026-06-28T18:54:05Z`
Space: `ADJCJH/backblaze-proofframe`
Public host: https://adjcjh-backblaze-proofframe.hf.space
Expected sha: `e9224d57a8ae90e20779f2c425b5dd465bfae355`
Runtime sha: `e9224d57a8ae90e20779f2c425b5dd465bfae355`
Runtime stage: `RUNNING`

## Checks

| Status | Check | Detail | Evidence |
| --- | --- | --- | --- |
| OK | Space metadata points at the expected commit | Space sha is e9224d57a8ae90e20779f2c425b5dd465bfae355; expected e9224d57a8ae90e20779f2c425b5dd465bfae355. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe |
| OK | Space runtime is running the expected commit | Runtime stage is RUNNING; runtime sha is e9224d57a8ae90e20779f2c425b5dd465bfae355; domain ready is True. | https://huggingface.co/api/spaces/ADJCJH/backblaze-proofframe/runtime |
| OK | Raw handoff report is public and ready | Handoff schema is proofframe.agent_handoff.v1; mode is handoff_ready. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/agent-handoff-report.json |
| OK | Raw Devpost event snapshot is public and fresh | Event snapshot schema is proofframe.devpost_event_snapshot.v1; submission_open=True; age_days=0; participants=369. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-event-snapshot.json |
| OK | Raw final launch plan is public and phase-aware | Launch plan schema is proofframe.final_launch_plan.v1; mode is ready_for_credential_entry; current phase is credential_entry. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/final-launch-plan.json |
| OK | Raw B2 key scope checklist is public and no-secret | Checklist schema is proofframe.b2_key_scope_checklist.v1; safe_to_commit=True; bucket=proofframe-demo-a6b4e49; prefix=campaigns/; confirmation=required_before_key_creation; required=['listAllBucketNames', 'writeFiles']. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/b2-key-scope-checklist.json |
| OK | Raw judge brief is public and claim-safe | Judge brief schema is proofframe.judge_brief.v1; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/judge-brief.json |
| OK | Raw judge crosswalk is public and claim-safe | Judge crosswalk schema is proofframe.judge_crosswalk.v1; mode is pre_live_crosswalk_ready; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/judge-crosswalk.json |
| OK | Raw recording runbook is public and final-video gated | Recording schema is proofframe.recording_assets.v1; mode is public_mock_verified; final_video_ready is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/recording-assets.json |
| OK | Raw public judge screenshot report is public and verified | Screenshot schema is proofframe.public_demo_screenshot.v1; mode is public_judge_screenshot_ready; visible_ok=True; html_ok=True; bytes=741074. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/public-demo-screenshot-report.json |
| OK | Raw mock demo video draft report is public and fail-closed | Draft schema is proofframe.demo_video_draft.v1; mode is mock_video_draft_ready; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/demo-video-draft.json |
| OK | Mock demo video draft MP4 is publicly readable | status=200; bytes=746805; content_type=video/mp4. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/resolve/main/docs/assets/proofframe-demo-draft.mp4 |
| OK | Raw Devpost form kit is public and final-form gated | Devpost form schema is proofframe.devpost_form_kit.v1; mode is pre_live_form_ready; final_form_ready is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-form-kit.json |
| OK | Raw Devpost submission preview is public and claim-safe | Preview schema is proofframe.devpost_submission_preview.v1; mode is pre_live_preview_ready; safe_to_share=True; safe_to_submit=False; blockers=10. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-submission-preview.json |
| OK | Raw Devpost submit checklist is public and fail-closed | Submit checklist schema is proofframe.devpost_submission_checklist.v1; mode is pre_submit_blocked; safe_to_submit is False. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/devpost-submission-checklist.json |
| OK | Raw post-credential live proof plan is public and task-safe | Post-credential schema is proofframe.post_credential_live_proof.v1; mode is plan_only; required sequence=True; report sequence=True; secret policy safe=True; devpost preview included=True. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/post-credential-live-proof-plan.json |
| OK | Raw submission bundle separates shareability from final submit readiness | Bundle schema is proofframe.submission_bundle.v1; safe_to_share=True; safe_to_submit=False; required artifacts=True. | https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/docs/assets/submission-bundle-manifest.json |
| OK | Public demo health is local/mock and ready | Health storage=local, generation=mock, ready=True. | https://adjcjh-backblaze-proofframe.hf.space/api/health |
| OK | Public submission gate is fail-closed with repo-relative paths | Gate mode is pre_live_safe; report gate is incomplete; relative paths=True. | https://adjcjh-backblaze-proofframe.hf.space/api/submission/gate |
| OK | Judge-mode HTML contains recording and sponsor markers | Markers: judge_recording_slate=True, sponsor_evidence_model=True, judge_brief_panel=True, criteria_crosswalk_link=True, recording_runbook_panel=True, devpost_kit_panel=True, submit_checklist_panel=True, auto_load_judge_demo=True, final_reports_pending=True. | https://adjcjh-backblaze-proofframe.hf.space/?judge=1 |

## Next Actions

- Public Space sync evidence is ready for the pre-live Devpost demo.
