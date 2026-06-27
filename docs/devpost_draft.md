# Devpost Submission Draft

Status: draft. Do not submit until T020, T021, T040, T041, T041A, and T042 are complete.

## Project Basics

Project name:

> ProofFrame

Tagline:

> A provenance-first vault for generated media.

One-liner:

> ProofFrame turns generated media into reviewable evidence packets with prompts, provider/model metadata, storage references, hashes, approval state, and a downloadable manifest bundle.

Repository:

> https://github.com/adjcjh777/backblaze-proofframe

Demo URL:

> Credential-free public mock demo: https://adjcjh-backblaze-proofframe.hf.space/

Final B2/Genblaze-backed demo URL:

> TBD after T020 and T021 live proof.

Video URL:

> TBD after final B2 and Genblaze proof.

## Short Description

Safe before live sponsor proof:

> ProofFrame is a review desk for generated media. The local demo creates a campaign, generates mock variants, approves or rejects assets, exports a manifest, and downloads an evidence ZIP with prompts, provider/model fields, storage references, hashes, and approval status. The final hackathon submission gate is to verify the same flow with Genblaze-backed generation and Backblaze B2-backed storage.

Safe after T020 and T021:

> ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. Each packet includes prompt history, provider/model metadata, B2 storage references, checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, or retire generated media.

## Inspiration

Generated media is easy to make and hard to govern. Teams often lose the prompt, model, provider, approval status, and durable storage evidence for the files that eventually ship. ProofFrame treats provenance as the product, not a footer.

## What It Does

ProofFrame provides a browser-based ledger for generated media approvals:

- Create a campaign brief.
- Generate candidate media assets.
- Review, approve, or reject assets.
- Inspect prompt, provider, model, storage backend, storage key, checksum, and risk note.
- Export a manifest.
- Download an evidence ZIP containing the manifest, README, and available media.
- Use Judge Demo to create a complete local packet instantly.

## How We Built It

ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and a Genblaze/GMICloud provider adapter built around the official Genblaze Pipeline API.

The local demo intentionally runs without secrets. The B2 and Genblaze adapters fail closed so missing credentials are visible instead of silently falling back.

## Backblaze B2 Usage

Current safe wording:

> ProofFrame includes a Backblaze B2-compatible storage backend and live B2 proof is a final submission gate.

After T020:

> ProofFrame stores generated media and exported manifests in Backblaze B2 using environment-only credentials. Each manifest records sanitized storage keys, byte sizes, and checksums.

## Genblaze Usage

Current safe wording:

> ProofFrame includes a Genblaze/GMICloud image provider path and live Genblaze proof is a final submission gate.

After T021:

> ProofFrame generates media through Genblaze/GMICloud, records provider/model/run metadata, and carries the resulting asset into the ProofFrame storage and approval manifest.

## AI Providers And Models

Current local demo:

- Provider: `mock`
- Model: `mock-svg-v1`

After T021:

- Provider: `genblaze/gmicloud-image`
- Model: `GENBLAZE_IMAGE_MODEL` value used for the verified run

## Challenges

The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to make storage and provenance central: B2 should be the durable evidence layer, and Genblaze should be the generation orchestration path. Another challenge is public claim hygiene, so the repo separates local demo behavior from final live sponsor proof.

## Accomplishments

- Built a working local product, not just a pitch.
- Added a one-click Judge Demo path.
- Added downloadable evidence ZIPs.
- Added B2-compatible storage and Genblaze/GMICloud provider code paths.
- Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.
- Kept public claims gated until live sponsor proof exists.

## What We Learned

The useful unit for generated media teams is not a single image. It is a packet: asset, prompt, provider, model, storage object, checksum, approval state, and risk note.

## What's Next

- Live B2 proof with a dedicated bucket and least-privilege key.
- Live Genblaze proof with provider/model/run metadata.
- Public demo deployment.
- Demo video under the event limit.
- Final Devpost submission.

## Submission Gate Checklist

- [ ] T020 B2 live proof complete.
- [ ] T021 Genblaze live proof complete.
- [ ] T040 Devpost registration complete.
- [ ] Demo URL available.
- [ ] Demo video available.
- [ ] Final secret scan complete.
- [ ] Final audit complete.
- [ ] Public copy uses only verified present-tense claims.
