# Hackathon Research And Selection

Date: 2026-06-27 Asia/Shanghai

## Decision

Choose the Backblaze Generative Media Hackathon and build ProofFrame.

ProofFrame is a provenance-first generative media vault: generate or ingest AI media, store it through a B2-compatible layer, preserve a tamper-evident manifest, and give creators a fast review surface for approval, reuse, and submission.

## Selection Heuristic

The user asked for one AI hackathon project that can be finished within roughly three GPT Pro 5x weekly cycles and has a real chance to win. I weighted:

- Online submission and low human-touch logistics.
- Clear deadline and rules.
- Practical fraction Codex can execute: product, docs, frontend, backend, tests, video script.
- Sponsor integration that can be shown deeply rather than superficially.
- Competition intensity: not merely prize size.
- Demo story: understandable in 90 seconds.

## Candidate Shortlist

| Candidate | Evidence | Upside | Concern | Decision |
| --- | --- | --- | --- | --- |
| Backblaze Generative Media Hackathon | Devpost AI list showed roughly `323-324 participants`, deadline `Aug 3, 2026`, and `$10,000` prizes. Event page says it requires generative media apps powered by Genblaze and Backblaze B2. | Product-led, online, moderate competition, sponsor integration is concrete. | Requires Backblaze account/B2 bucket and Genblaze setup for final demo. | Chosen. |
| AMD Developer Hackathon ACT II | Lablab active AI hackathon with prize and technical tracks. | Strong technical fit if track is token-efficient routing. | Tracks/rules may require AMD-specific environment and hidden task timing; less product-showcase leverage. | Backup. |
| Global AI Hackathon Series with Qwen Cloud | Devpost AI list showed high prize pool and AI theme. | Large prize pool and agentic app fit. | Very high visible participant count and cloud/account friction. | Not primary. |
| UiPath Agentic Automation Hackathon | Devpost AI list showed large prizes and agent automation theme. | Strong enterprise automation category. | Deadline too close on 2026-06-29 from today's date. | Too compressed. |
| Arm Create AI Optimization Challenge | Devpost AI list showed longer deadline and ARM optimization theme. | Local Apple Silicon could help. | Optimization contests are harder to guarantee prize placement and can become benchmark-heavy. | Backup. |

## Official Evidence

- Devpost event page: https://backblaze-generative-media.devpost.com/
- Devpost artificial-intelligence listing: https://devpost.com/c/artificial-intelligence
- Genblaze repo: https://github.com/backblaze-labs/genblaze

Observed details from official pages on 2026-06-27, updated after scout verification:

- Backblaze event schedule: registration/submissions run June 22, 2026 through August 3, 2026 at 5:00 PM EDT.
- Beijing deadline conversion: 2026-08-04 05:00 Asia/Shanghai.
- Prizes: $7,000 Grand Prize, $2,000 Second Place, $1,000 Third Place, plus feedback rewards.
- Devpost page describes the challenge as building apps that use Genblaze and Backblaze B2 Cloud Storage.
- Judging criteria on the event page: real-world utility, production readiness, B2 storage/data orchestration, and use of Genblaze.

## Why ProofFrame Can Win

Most hackathon entries in generative media tend to cluster around "prompt to image/video" demos. ProofFrame instead makes storage and provenance the product center:

- Every media object is stored with manifest, checksum, generation metadata, approval status, and usage notes.
- Backblaze B2 is not a file dump; it becomes the durable creative evidence layer.
- Genblaze is not a checkbox; it powers provider routing and reproducible media generation.
- The UI can show a judge a real before/after workflow: brief, generate, review, approve, export packet.
- The fallback mock provider lets us test and demo locally even before credentials are available.

## Scope For Three Weekly GPT Pro 5x Cycles

Cycle 1: repo, PRD/spec, task ledger, local MVP, B2/Genblaze adapter interfaces, offline demo.

Cycle 2: real integrations, polished UI, Docker, tests, browser smoke, sample media packets.

Cycle 3: submission page, demo video, public repo polish, final Devpost submission, compliance review.

## Stop/Go Gates

- Gate A: Can create or access Backblaze B2 account and bucket.
- Gate B: Can run Genblaze or Genblaze-compatible API locally or via documented remote provider.
- Gate C: Can deploy or present a working public demo without leaking credentials.
- Gate D: Devpost submission accepted before 2026-08-04 05:00 Beijing.
