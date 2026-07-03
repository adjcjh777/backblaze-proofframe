# Devpost Submission Packet

Mode: `post_live_verified`
Claim warning: Use only after T020 and T021 are verified by live proof evidence.

## Project Name

ProofFrame

## Tagline

B2-ready provenance desk for GenAI media.

## One-Liner

ProofFrame turns generated media into approved evidence packets with B2-ready manifests, Genblaze-gated provider metadata, checksums, review status, and an exportable proof bundle.

## Repository

https://github.com/adjcjh777/backblaze-proofframe

## Demo URL

https://adjcjh-backblaze-proofframe.hf.space/?judge=1

## Demo Video URL

TBD after final public video upload.

## Short Description

ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. Each packet includes prompt history, provider/model metadata, B2 storage references, checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, or retire generated media.

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

ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, local storage for credential-free demos, a Backblaze B2-compatible S3 storage backend, and Genblaze provider adapters for GMICloud, OpenAI, and a credential-free local Pipeline provider built around the official Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for judge-friendly product inspection while final reports separate live proof, video, audit, and Devpost receipt gates.

## Backblaze B2 Usage

ProofFrame stores generated media and exported manifests in Backblaze B2 using environment-only credentials. The final proof evidence records sanitized B2 storage keys, byte sizes, and checksums without exposing credentials or signed URLs. B2 is the durable evidence layer: the media asset and manifest are separate objects under the ProofFrame campaign prefix, and the app uses those hashes to make later review, export, and audit steps reproducible.

## Genblaze Usage

ProofFrame generates media through Genblaze's official Pipeline. The final proof uses the credential-free local image provider, records provider/model metadata, and carries the resulting asset through Genblaze's B2 sink into the ProofFrame storage and approval manifest.

## Challenges

The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to make storage and provenance central: B2 should be the durable evidence layer, and Genblaze should be the generation orchestration path. Another challenge is public claim hygiene, so the repo separates local demo behavior from final live sponsor proof.

## Accomplishments

- Built a working local product, not just a pitch.
- Deployed a credential-free public mock demo.
- Added a one-click Judge Demo path.
- Added a review console with evidence search, status filtering, decision coverage, and safe summary copy.
- Added downloadable evidence ZIPs.
- Added B2-compatible storage and Genblaze provider code paths for GMICloud, OpenAI, and a credential-free local Pipeline provider.
- Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.
- Added fail-closed gates for evidence JSON exports and final submission audits.
- Kept public claims gated by reports, task status, and secret-scan artifacts.

## What We Learned

The useful unit for generated media teams is not a single image. It is a packet: asset, prompt, provider, model, storage object, checksum, approval state, and risk note.

## What's Next

- Upload the final demo video under the event limit.
- Run the final secret scan and submission audit after video artifacts are ready.
- Submit the Devpost project and preserve the receipt URL.

## Submission Checklist

- T020 [done] B2 live proof complete
- T021 [done] Genblaze live proof complete
- T040 [done] Devpost registration complete
- T041 [todo] Final submission audit complete
- T041A [todo] Final secret scan complete
- T042 [todo] Devpost project submitted
