# ProofFrame Devpost Form Kit

Mode: `pre_live_form_ready`
Packet mode: `pre_live_safe`
Mock form ready: `true`
Final form ready: `false`
Public video ready: `false`

## Fields

### Project name

- Status: `OK` / `FINAL OK`
- Source: `packet.project_name`
- Length: `10 / 80`

```text
ProofFrame
```

### Tagline

- Status: `OK` / `FINAL OK`
- Source: `packet.tagline`
- Length: `45 / 140`

```text
A provenance-first vault for generated media.
```

### One-liner

- Status: `OK` / `FINAL OK`
- Source: `packet.one_liner`
- Length: `184 / 280`

```text
ProofFrame turns generated media into reviewable evidence packets with prompts, provider/model metadata, storage references, hashes, approval state, and a downloadable manifest bundle.
```

### Short description

- Status: `OK` / `FINAL OK`
- Source: `packet.short_description`
- Length: `400 / 2000`

```text
ProofFrame is a review desk for generated media. The local demo creates a campaign, generates mock variants, approves or rejects assets, exports a manifest, and downloads an evidence ZIP with prompts, provider/model fields, storage references, hashes, and approval status. The final hackathon submission gate is to verify the same flow with Genblaze-backed generation and Backblaze B2-backed storage.
```

### Repository URL

- Status: `OK` / `FINAL OK`
- Source: `packet.repository_url`
- Length: `49 / 300`

```text
https://github.com/adjcjh777/backblaze-proofframe
```

### Demo URL

- Status: `OK` / `FINAL OK`
- Source: `packet.demo_url`
- Length: `53 / 300`

```text
https://adjcjh-backblaze-proofframe.hf.space/?judge=1
```

### Demo video URL

- Status: `OK` / `FINAL PENDING`
- Source: `packet.video_url`
- Length: `38 / 300`

```text
TBD after final B2 and Genblaze proof.
```

### Built with

- Status: `OK` / `FINAL OK`
- Source: `form.built_with`
- Length: `103 / 800`

```text
Python, FastAPI, Backblaze B2 S3-compatible API, Genblaze/GMICloud, Hugging Face Spaces, GitHub Actions
```

### Suggested tags

- Status: `OK` / `FINAL OK`
- Source: `form.tags`
- Length: `74 / 500`

```text
AI, Generative media, Backblaze B2, Genblaze, Provenance, Media operations
```

### Inspiration

- Status: `OK` / `FINAL OK`
- Source: `packet.inspiration`
- Length: `238 / 2000`

```text
Generated media is easy to make and hard to govern. Teams often lose the prompt, model, provider, approval status, and durable storage evidence for the files that eventually ship. ProofFrame treats provenance as the product, not a footer.
```

### What it does

- Status: `OK` / `FINAL OK`
- Source: `packet.what_it_does`
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

### How we built it

- Status: `OK` / `FINAL OK`
- Source: `packet.how_we_built_it`
- Length: `407 / 2500`

```text
ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and a Genblaze/GMICloud provider adapter built around the official Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for judge-friendly product inspection while the final sponsor-backed proof remains gated.
```

### Backblaze B2 usage

- Status: `OK` / `FINAL OK`
- Source: `packet.b2_usage`
- Length: `107 / 1500`

```text
ProofFrame includes a Backblaze B2-compatible storage backend and live B2 proof is a final submission gate.
```

### Genblaze usage

- Status: `OK` / `FINAL OK`
- Source: `packet.genblaze_usage`
- Length: `111 / 1500`

```text
ProofFrame includes a Genblaze/GMICloud image provider path and live Genblaze proof is a final submission gate.
```

### Challenges

- Status: `OK` / `FINAL OK`
- Source: `packet.challenges`
- Length: `332 / 2000`

```text
The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to make storage and provenance central: B2 should be the durable evidence layer, and Genblaze should be the generation orchestration path. Another challenge is public claim hygiene, so the repo separates local demo behavior from final live sponsor proof.
```

### Accomplishments

- Status: `OK` / `FINAL OK`
- Source: `packet.accomplishments`
- Length: `571 / 2500`

```text
- Built a working local product, not just a pitch.
- Deployed a credential-free public mock demo.
- Added a one-click Judge Demo path.
- Added a review console with evidence search, status filtering, decision coverage, and safe summary copy.
- Added downloadable evidence ZIPs.
- Added B2-compatible storage and Genblaze/GMICloud provider code paths.
- Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.
- Added fail-closed gates for evidence JSON exports and final submission audits.
- Kept public claims gated until live sponsor proof exists.
```

### What we learned

- Status: `OK` / `FINAL OK`
- Source: `packet.what_we_learned`
- Length: `169 / 2000`

```text
The useful unit for generated media teams is not a single image. It is a packet: asset, prompt, provider, model, storage object, checksum, approval state, and risk note.
```

### What's next

- Status: `OK` / `FINAL OK`
- Source: `packet.whats_next`
- Length: `184 / 1800`

```text
- Live B2 proof with a dedicated bucket and least-privilege key.
- Live Genblaze proof with provider/model/run metadata.
- Demo video under the event limit.
- Final Devpost submission.
```

### Judging note

- Status: `OK` / `FINAL OK`
- Source: `form.judging_note`
- Length: `105 / 1000`

```text
Current packet mode: pre_live_safe. Safe for public mock demo only. Do not submit as final sponsor proof.
```

## Final Prerequisite Tasks

- `T020`: `doing`
- `T021`: `doing`
- `T040`: `done`
- `T041A`: `todo`

## Next Actions

- Regenerate the Devpost packet in post-live mode after B2 and Genblaze proof.
- Capture sanitized final B2 plus Genblaze live proof evidence.
- Finish final form prerequisite tasks: T020, T021, T041A.
- Finalize Devpost field: Demo video URL.
- Run final secret scan, final audit, then submit Devpost.
