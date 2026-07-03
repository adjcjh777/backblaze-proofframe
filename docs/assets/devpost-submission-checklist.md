# ProofFrame Devpost Submission Checklist

Mode: `pre_submit_blocked`
OK: `false`
Safe to submit: `false`

## Preflight

- BLOCKED `final_form_ready`: Devpost form kit mode is pre_live_form_ready. Evidence: `docs/assets/devpost-form-kit.json`
- OK `packet_post_live_verified`: Devpost packet mode is post_live_verified. Evidence: `docs/assets/devpost-submission-packet.json`
- BLOCKED `prerequisite_tasks_done`: T020=done, T021=done, T040=done, T041A=blocked Evidence: `tasks.json`
- OK `submission_audit_report_present`: Submission audit mode is pre_submit_audit_blocked. Evidence: `docs/assets/submission-audit-report.json`
- OK `final_control_report_present`: Final control mode is pre_live_control; safe_to_submit=False. Evidence: `docs/assets/final-submission-control.json`
- OK `receipt_not_already_done`: T042=blocked; receipt mode=pending_submission. Evidence: `docs/assets/devpost-submission-receipt.json`

## Copy Order

### 1. Project name

- Field id: `project_name`
- Source: `packet.project_name`
- Status: `FINAL OK`
- Length: `10 / 80`

```text
ProofFrame
```

### 2. Tagline

- Field id: `tagline`
- Source: `packet.tagline`
- Status: `FINAL OK`
- Length: `41 / 140`

```text
B2-ready provenance desk for GenAI media.
```

### 3. One-liner

- Field id: `one_liner`
- Source: `packet.one_liner`
- Status: `FINAL OK`
- Length: `180 / 280`

```text
ProofFrame turns generated media into approved evidence packets with B2-ready manifests, Genblaze-gated provider metadata, checksums, review status, and an exportable proof bundle.
```

### 4. Short description

- Field id: `short_description`
- Source: `packet.short_description`
- Status: `FINAL OK`
- Length: `285 / 2000`

```text
ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. Each packet includes prompt history, provider/model metadata, B2 storage references, checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, or retire generated media.
```

### 5. Repository URL

- Field id: `repository_url`
- Source: `packet.repository_url`
- Status: `FINAL OK`
- Length: `49 / 300`

```text
https://github.com/adjcjh777/backblaze-proofframe
```

### 6. Demo URL

- Field id: `demo_url`
- Source: `packet.demo_url`
- Status: `FINAL OK`
- Length: `53 / 300`

```text
https://adjcjh-backblaze-proofframe.hf.space/?judge=1
```

### 7. Demo video URL

- Field id: `video_url`
- Source: `packet.video_url`
- Status: `FINAL PENDING`
- Length: `36 / 300`

```text
TBD after final public video upload.
```

### 8. Built with

- Field id: `built_with`
- Source: `form.built_with`
- Status: `FINAL OK`
- Length: `94 / 800`

```text
Python, FastAPI, Backblaze B2 S3-compatible API, Genblaze, Hugging Face Spaces, GitHub Actions
```

### 9. Suggested tags

- Field id: `tags`
- Source: `form.tags`
- Status: `FINAL OK`
- Length: `74 / 500`

```text
AI, Generative media, Backblaze B2, Genblaze, Provenance, Media operations
```

### 10. Inspiration

- Field id: `inspiration`
- Source: `packet.inspiration`
- Status: `FINAL OK`
- Length: `238 / 2000`

```text
Generated media is easy to make and hard to govern. Teams often lose the prompt, model, provider, approval status, and durable storage evidence for the files that eventually ship. ProofFrame treats provenance as the product, not a footer.
```

### 11. What it does

- Field id: `what_it_does`
- Source: `packet.what_it_does`
- Status: `FINAL OK`
- Length: `595 / 2500`

```text
- Create a campaign brief.
- Generate candidate media assets.
- Review, approve, or reject assets.
- Search and filter evidence by prompt, model, storage key, checksum, and status.
- Track decision coverage across approved, draft, and rejected assets.
- Inspect prompt, provider, model, storage backend, storage key, checksum, and risk note.
- Copy a safe evidence summary without credentials, cookies, signed URLs, or raw secrets.
- Export a manifest.
- Download an evidence ZIP containing the manifest, README, and available media.
- Use Judge Demo to create a complete local packet instantly.
```

### 12. How we built it

- Field id: `how_we_built_it`
- Source: `packet.how_we_built_it`
- Status: `FINAL OK`
- Length: `495 / 2500`

```text
ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and Genblaze provider adapters for GMICloud, OpenAI, and a credential-free local Pipeline provider built around the official Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for judge-friendly product inspection while final reports separate live proof, video, audit, and Devpost receipt gates.
```

### 13. Backblaze B2 usage

- Field id: `backblaze_b2_usage`
- Source: `packet.b2_usage`
- Status: `FINAL OK`
- Length: `451 / 1500`

```text
ProofFrame stores generated media and exported manifests in Backblaze B2 using environment-only credentials. The final proof evidence records sanitized B2 storage keys, byte sizes, and checksums without exposing credentials or signed URLs. B2 is the durable evidence layer: the media asset and manifest are separate objects under the ProofFrame campaign prefix, and the app uses those hashes to make later review, export, and audit steps reproducible.
```

### 14. Genblaze usage

- Field id: `genblaze_usage`
- Source: `packet.genblaze_usage`
- Status: `FINAL OK`
- Length: `270 / 1500`

```text
ProofFrame generates media through Genblaze's official Pipeline. The final proof uses the credential-free local image provider, records provider/model metadata, and carries the resulting asset through Genblaze's B2 sink into the ProofFrame storage and approval manifest.
```

### 15. Challenges

- Field id: `challenges`
- Source: `packet.challenges`
- Status: `FINAL OK`
- Length: `332 / 2000`

```text
The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to make storage and provenance central: B2 should be the durable evidence layer, and Genblaze should be the generation orchestration path. Another challenge is public claim hygiene, so the repo separates local demo behavior from final live sponsor proof.
```

### 16. Accomplishments

- Field id: `accomplishments`
- Source: `packet.accomplishments`
- Status: `FINAL OK`
- Length: `649 / 2500`

```text
- Built a working local product, not just a pitch.
- Deployed a credential-free public mock demo.
- Added a one-click Judge Demo path.
- Added a review console with evidence search, status filtering, decision coverage, and safe summary copy.
- Added downloadable evidence ZIPs.
- Added B2-compatible storage and Genblaze provider code paths for GMICloud, OpenAI, and a credential-free local Pipeline provider.
- Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.
- Added fail-closed gates for evidence JSON exports and final submission audits.
- Kept public claims gated by reports, task status, and secret-scan artifacts.
```

### 17. What we learned

- Field id: `what_we_learned`
- Source: `packet.what_we_learned`
- Status: `FINAL OK`
- Length: `169 / 2000`

```text
The useful unit for generated media teams is not a single image. It is a packet: asset, prompt, provider, model, storage object, checksum, approval state, and risk note.
```

### 18. What's next

- Field id: `whats_next`
- Source: `packet.whats_next`
- Status: `FINAL OK`
- Length: `193 / 1800`

```text
- Upload the final demo video under the event limit.
- Run the final secret scan and submission audit after video artifacts are ready.
- Submit the Devpost project and preserve the receipt URL.
```

### 19. Judging note

- Field id: `judging_note`
- Source: `form.judging_note`
- Status: `FINAL OK`
- Length: `106 / 1000`

```text
Current packet mode: post_live_verified. Use only after T020 and T021 are verified by live proof evidence.
```

## Stop Rules

- Do not paste Backblaze keys, Genblaze provider keys, Devpost cookies, authorization headers, or signed URLs into Devpost.
- Do not press Submit unless every preflight item is OK and final_submission_control.py --strict-final passes.
- If Devpost changes field labels or requirements, stop and update this checklist before submitting.
- After Devpost accepts the project, record only the public project URL and submitted timestamp; never capture cookies or private browser state.

## Post-submit Commands

```bash
python scripts/devpost_submission_receipt.py --project-url "$PROOFFRAME_DEVPOST_PROJECT_URL" --submitted-at "$PROOFFRAME_DEVPOST_SUBMITTED_AT" --confirmation-note "Devpost accepted/submitted the ProofFrame project."
python3 scripts/task.py done T042 --note "Devpost project submitted and public receipt captured."
PYTHONPATH=src python scripts/final_submission_control.py --strict-final
PYTHONPATH=src python scripts/submission_bundle.py
```

This checklist contains Devpost copy only, never credentials or browser session data.
