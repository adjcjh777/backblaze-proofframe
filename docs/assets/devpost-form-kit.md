# ProofFrame Devpost Form Kit

Mode: `pre_live_form_ready`
Packet mode: `post_live_verified`
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
- Length: `41 / 140`

```text
B2-ready provenance desk for GenAI media.
```

### One-liner

- Status: `OK` / `FINAL OK`
- Source: `packet.one_liner`
- Length: `180 / 280`

```text
ProofFrame turns generated media into approved evidence packets with B2-ready manifests, Genblaze-gated provider metadata, checksums, review status, and an exportable proof bundle.
```

### Short description

- Status: `OK` / `FINAL OK`
- Source: `packet.short_description`
- Length: `285 / 2000`

```text
ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. Each packet includes prompt history, provider/model metadata, B2 storage references, checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, or retire generated media.
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
- Length: `36 / 300`

```text
TBD after final public video upload.
```

### Built with

- Status: `OK` / `FINAL OK`
- Source: `form.built_with`
- Length: `94 / 800`

```text
Python, FastAPI, Backblaze B2 S3-compatible API, Genblaze, Hugging Face Spaces, GitHub Actions
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
- Length: `495 / 2500`

```text
ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and Genblaze provider adapters for GMICloud, OpenAI, and a credential-free local Pipeline provider built around the official Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for judge-friendly product inspection while final reports separate live proof, video, audit, and Devpost receipt gates.
```

### Backblaze B2 usage

- Status: `OK` / `FINAL OK`
- Source: `packet.b2_usage`
- Length: `451 / 1500`

```text
ProofFrame stores generated media and exported manifests in Backblaze B2 using environment-only credentials. The final proof evidence records sanitized B2 storage keys, byte sizes, and checksums without exposing credentials or signed URLs. B2 is the durable evidence layer: the media asset and manifest are separate objects under the ProofFrame campaign prefix, and the app uses those hashes to make later review, export, and audit steps reproducible.
```

### Genblaze usage

- Status: `OK` / `FINAL OK`
- Source: `packet.genblaze_usage`
- Length: `270 / 1500`

```text
ProofFrame generates media through Genblaze's official Pipeline. The final proof uses the credential-free local image provider, records provider/model metadata, and carries the resulting asset through Genblaze's B2 sink into the ProofFrame storage and approval manifest.
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
- Length: `193 / 1800`

```text
- Upload the final demo video under the event limit.
- Run the final secret scan and submission audit after video artifacts are ready.
- Submit the Devpost project and preserve the receipt URL.
```

### Judging note

- Status: `OK` / `FINAL OK`
- Source: `form.judging_note`
- Length: `106 / 1000`

```text
Current packet mode: post_live_verified. Use only after T020 and T021 are verified by live proof evidence.
```

## Final Prerequisite Tasks

- `T020`: `done`
- `T021`: `done`
- `T040`: `done`
- `T041A`: `blocked`

## Next Actions

- Finish final form prerequisite tasks: T041A.
- Finalize Devpost field: Demo video URL.
- Run final secret scan, final audit, then submit Devpost.
