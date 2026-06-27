# Devpost Submission Packet

Mode: `pre_live_safe`
Claim warning: Safe for public mock demo only. Do not submit as final sponsor proof.

## Project Name

ProofFrame

## Tagline

A provenance-first vault for generated media.

## One-Liner

ProofFrame turns generated media into reviewable evidence packets with prompts, provider/model metadata, storage references, hashes, approval state, and a downloadable manifest bundle.

## Repository

https://github.com/adjcjh777/backblaze-proofframe

## Demo URL

https://adjcjh-backblaze-proofframe.hf.space/?judge=1

## Short Description

ProofFrame is a review desk for generated media. The local demo creates a campaign, generates mock variants, approves or rejects assets, exports a manifest, and downloads an evidence ZIP with prompts, provider/model fields, storage references, hashes, and approval status. The final hackathon submission gate is to verify the same flow with Genblaze-backed generation and Backblaze B2-backed storage.

## Inspiration

Generated media is easy to make and hard to govern. Teams often lose the prompt, model, provider, approval status, and durable storage evidence for the files that eventually ship. ProofFrame treats provenance as the product, not a footer.

## What It Does

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

## How We Built It

ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and a Genblaze/GMICloud provider adapter built around the official Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for judge-friendly product inspection while the final sponsor-backed proof remains gated.

## Backblaze B2 Usage

ProofFrame includes a Backblaze B2-compatible storage backend and live B2 proof is a final submission gate.

## Genblaze Usage

ProofFrame includes a Genblaze/GMICloud image provider path and live Genblaze proof is a final submission gate.

## Challenges

The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to make storage and provenance central: B2 should be the durable evidence layer, and Genblaze should be the generation orchestration path. Another challenge is public claim hygiene, so the repo separates local demo behavior from final live sponsor proof.

## Accomplishments

- Built a working local product, not just a pitch.
- Deployed a credential-free public mock demo.
- Added a one-click Judge Demo path.
- Added a review console with evidence search, status filtering, decision coverage, and safe summary copy.
- Added downloadable evidence ZIPs.
- Added B2-compatible storage and Genblaze/GMICloud provider code paths.
- Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.
- Added fail-closed gates for evidence JSON exports and final submission audits.
- Kept public claims gated until live sponsor proof exists.

## What We Learned

The useful unit for generated media teams is not a single image. It is a packet: asset, prompt, provider, model, storage object, checksum, approval state, and risk note.

## What's Next

- Live B2 proof with a dedicated bucket and least-privilege key.
- Live Genblaze proof with provider/model/run metadata.
- Demo video under the event limit.
- Final Devpost submission.
