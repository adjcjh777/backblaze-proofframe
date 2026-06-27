# ProofFrame Award Readiness

Mode: `pre_live_competitive`
Score: `97/115` (84.3%)
Public demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1

## Gate Snapshot

- Submission gate: `pre_live_safe`
- Live evidence: `missing`
- Mock recording ready: `true`
- Final recording ready: `false`
- Claim lint: `true`
- Secret scan: `true`

## Criteria

### Sponsor integration fit - 30/38 (78.9%)
- OK `b2_backend_code` (5/5): Backblaze B2 has a dedicated S3-compatible storage adapter.
- OK `b2_bucket_setup` (4/4): The non-secret B2 bucket setup record exists for final proof.
- OK `b2_live_runner` (4/4): B2 storage can be verified independently before Genblaze is ready.
- OK `genblaze_provider_code` (5/5): The app has a real Genblaze/GMICloud provider adapter.
- OK `final_live_runner` (4/4): A one-command runner can produce sanitized final evidence once keys are present.
- OK `sponsor_fit_matrix` (4/4): Judging angles are mapped to current evidence, safe claims, final gates, and demo shots.
- OK `sponsor_fit_audit` (4/4): Devpost B2/Genblaze copy is specific and the demo introduces B2 early.
- TODO `b2_live_evidence` (0/4): T020 requires a real B2 media and manifest proof.
- TODO `genblaze_live_evidence` (0/4): T021 requires provider/model metadata from a live Genblaze run.

### Provenance product depth - 23/23 (100.0%)
- OK `manifest_model` (4/4): Assets, prompts, provider/model metadata, hashes, and review state are modeled.
- OK `packet_zip` (4/4): Judges can inspect a packaged manifest and local media evidence.
- OK `judge_packet` (4/4): The demo can be loaded quickly into a believable reviewer workflow.
- OK `review_console` (4/4): The app is positioned as an operations desk, not a generic generator.
- OK `sponsor_model_ui` (3/3): Judge mode foregrounds Genblaze, B2 object route, manifest proof, and claim mode.
- OK `prd_spec` (4/4): The product and implementation story are documented for judges and maintainers.

### Demo and Devpost readiness - 29/29 (100.0%)
- OK `public_judge_demo` (5/5): The Devpost packet points judges to a credential-free public demo.
- OK `devpost_form_kit` (4/4): Field-by-field copy is ready and length checked.
- OK `official_event_snapshot` (4/4): Deadline, participants, requirements, and judging criteria are refreshed from Devpost.
- OK `storyboard` (4/4): The video can be recorded around a clear judge story.
- OK `mock_recording_ready` (4/4): The current public demo can be recorded safely before live proof.
- OK `screenshots` (4/4): Local, review-console, and public demo screenshots are available.
- OK `devpost_registered` (4/4): The project is through the registration gate.

### Trust, safety, and claim discipline - 15/15 (100.0%)
- OK `secret_scan` (4/4): No obvious API keys, cookies, signed URLs, or tokens were found in public files.
- OK `claim_lint` (4/4): Pre-live copy avoids claiming unverified B2 or Genblaze runs.
- OK `env_ignored` (3/3): Credential-bearing local env files stay out of Git.
- OK `safe_evidence_writer` (2/2): Live evidence cannot silently include key-like fields or signed URLs.
- OK `claim_freeze_doc` (2/2): The team has a written boundary for what can be said before final proof.

### Final submission closure - 0/10 (0.0%)
- TODO `final_gate` (0/6): Requires T020, T021, T040, T041, T041A, T042, and final live evidence.
- TODO `final_audit_done` (0/2): The reviewer audit must pass after live evidence exists.
- TODO `final_secret_scan_done` (0/1): The final scan should run after live proof artifacts are generated.
- TODO `devpost_submitted` (0/1): The submission is not complete until the project page is submitted.

## Next Actions

- After explicit key-creation confirmation, create the scoped B2 key and run python scripts/run_b2_live_proof.py --env-file .env.final.local.
- Configure Genblaze/GMI credentials and run python scripts/run_final_live_proof.py --env-file .env.final.local.
- Run python scripts/secret_scan.py after live evidence is generated.
- Run python scripts/submission_audit.py after T020/T021/T041A are done.
- Submit the Devpost project only after the final gate turns green.
