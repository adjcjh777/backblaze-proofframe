# ProofFrame PRD

## One-Liner

ProofFrame is a provenance-first vault for generative media teams: create AI assets, preserve their review metadata, and ship an auditable packet for every file. The final hackathon target is to back that packet with Genblaze generation and Backblaze B2 storage after live integration proof is captured.

## Target Users

- Indie creators producing many AI images/videos for campaigns.
- Small agencies that need client approval before publishing AI-generated assets.
- Educators and community teams that need provenance, alt text, and reuse notes for generated visuals.

## Problem

Generative media tools make assets quickly, but teams lose the operational truth:

- Which prompt/model/provider created this asset?
- Is it approved or only a draft?
- Where is the durable original?
- Can a teammate reproduce, edit, or retire it?
- Is there a readable package for a client or judge?

This is exactly where Backblaze B2 can be more than storage in the final build: it can become the evidence layer for generated media.

## Product Hypothesis

If ProofFrame makes provenance visible by default, judges will perceive deeper sponsor integration and real-world usefulness than a standard media generator demo.

## MVP User Journey

1. User enters a campaign brief and selects a packet type.
2. ProofFrame generates or mocks 3 media variants through a provider adapter.
3. Each asset is stored locally in the current demo, then through B2 after the live storage gate passes.
4. User reviews a gallery, marks assets as approved/rejected, and edits risk notes.
5. User exports a shareable packet: manifest JSON, thumbnails, checksums, and approval summary.

## Differentiators

- Manifest-first, not image-first.
- Storage object and manifest details are shown in the UI.
- Checksums and approval state make the demo feel production-ready.
- Offline demo path means no credential blocker for local verification.
- Final submission should show both local and B2-backed runs after T020 is verified.

## MVP Features

| Feature | Priority | Notes |
| --- | --- | --- |
| Brief intake | P0 | Campaign name, audience, tone, asset goal. |
| Mock generation | P0 | Deterministic local assets for tests and demo fallback. |
| Genblaze adapter | P0 | OpenAI-compatible media request shape, optional credentials. |
| Storage adapter | P0 | Local and B2-compatible backends. |
| Manifest writer | P0 | Prompt, model, provider, checksum, storage URL/key, approval state. |
| Review gallery | P0 | Approve/reject, notes, copy/export. |
| Review console | P1 | Search/filter by prompt, model, storage key, checksum, and status; copy a safe evidence summary. |
| Packet export | P0 | Zip or folder with manifest and media. |
| Browser UI | P0 | `apps/web/index.html` entry. |
| Docker packaging | P1 | One-command demo. |
| Demo samples | P1 | Preloaded judge-friendly packets. |
| Public deployment | P2 | Optional if local Docker/video is strong. |

## Non-Goals

- Full creative suite.
- Fine-tuned model training.
- Marketplace or user accounts.
- Claiming rights clearance beyond metadata and review tooling.

## Success Metrics

- Judge can understand the product in 30 seconds.
- Local MVP runs without secrets.
- B2-backed run stores a real asset and manifest after live verification.
- Exported packet is inspectable and reproducible.
- Review console can show decision coverage and locate evidence without opening raw manifests.
- No secrets in repo, logs, screenshots, or demo video.

## Award Strategy

The pitch should emphasize:

- "Backblaze B2 becomes the source of truth for AI-generated assets after the live storage proof."
- "Genblaze lets the workflow swap media providers without rewriting the app after the live generation proof."
- "ProofFrame helps teams trust, approve, and reuse generated media."
- "This is useful tomorrow for creators and agencies, not just a hackathon trick."
