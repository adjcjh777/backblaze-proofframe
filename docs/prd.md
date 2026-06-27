# ProofFrame PRD

## One-Liner

ProofFrame is a provenance-first vault for generative media teams: create AI assets, store them in Backblaze B2, and ship an auditable review packet with every file.

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

This is exactly where Backblaze B2 can be more than storage: it can be the evidence layer for generated media.

## Product Hypothesis

If ProofFrame makes provenance visible by default, judges will perceive deeper sponsor integration and real-world usefulness than a standard media generator demo.

## MVP User Journey

1. User enters a campaign brief and selects a packet type.
2. ProofFrame generates or mocks 3 media variants through a Genblaze-compatible adapter.
3. Each asset is stored locally or in B2 with a manifest.
4. User reviews a gallery, marks assets as approved/rejected, and edits risk notes.
5. User exports a shareable packet: manifest JSON, thumbnails, checksums, and approval summary.

## Differentiators

- Manifest-first, not image-first.
- B2 storage object and manifest are shown in the UI.
- Checksums and approval state make the demo feel production-ready.
- Offline demo path means no credential blocker for local verification.
- Final submission can show both local and B2-backed runs.

## MVP Features

| Feature | Priority | Notes |
| --- | --- | --- |
| Brief intake | P0 | Campaign name, audience, tone, asset goal. |
| Mock generation | P0 | Deterministic local assets for tests and demo fallback. |
| Genblaze adapter | P0 | OpenAI-compatible media request shape, optional credentials. |
| Storage adapter | P0 | Local and B2-compatible backends. |
| Manifest writer | P0 | Prompt, model, provider, checksum, storage URL/key, approval state. |
| Review gallery | P0 | Approve/reject, notes, copy/export. |
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
- B2-backed run stores a real asset and manifest.
- Exported packet is inspectable and reproducible.
- No secrets in repo, logs, screenshots, or demo video.

## Award Strategy

The pitch should emphasize:

- "Backblaze B2 is the source of truth for AI-generated assets."
- "Genblaze lets the workflow swap media providers without rewriting the app."
- "ProofFrame helps teams trust, approve, and reuse generated media."
- "This is useful tomorrow for creators and agencies, not just a hackathon trick."

