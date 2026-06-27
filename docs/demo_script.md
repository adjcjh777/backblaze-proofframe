# ProofFrame Demo Script

Target length: 2 minutes 15 seconds.  
Audience: Backblaze Generative Media Hackathon judges.  
Recording mode: browser UI first, then a short terminal/API proof if needed.

## Demo Goal

Show that ProofFrame is not just a media generator. It is an approval and provenance desk for generated media packets: prompt, provider, storage object, hash, approval status, and exportable manifest.

## Current Recording Assets

- Browser UI screenshot: `docs/assets/proofframe-local-ui-smoke.png`
- Judge recording slate: first viewport of `apps/web/index.html`
- Local app route: `http://127.0.0.1:8088/`
- Public repo: `https://github.com/adjcjh777/backblaze-proofframe`
- Demo readiness report: `docs/assets/demo-readiness-report.md`

## Script

### 0:00-0:12 - Product Hook

On screen: ProofFrame dashboard.

Narration:

> ProofFrame helps teams trust generated media after the prompt is over. It turns each generated asset into a reviewable packet with prompt history, provider metadata, storage location, checksum, and approval status.

### 0:12-0:35 - Create A Campaign

On screen: enter title, audience, tone, and campaign brief.

Narration:

> I start with a creative brief. The goal is to keep the creative workflow fast while preserving the operational details that teams usually lose: who generated what, with which model, under which brief.

Fast path:

> For a judge walkthrough, open `/?judge=1` or click Judge Demo to create a complete local packet immediately.

### 0:35-0:58 - Generate Variants

On screen: click generate and show three assets in the ledger.

Narration for current local demo:

> In local mode, ProofFrame uses a deterministic mock media provider so judges and contributors can run the workflow without secrets. The final submission gate swaps this provider path to a live Genblaze-backed run and records the provider and model metadata in the same manifest fields.

Narration after T021 is live-verified:

> This run uses the Genblaze-backed generation path. ProofFrame captures the model, provider, request metadata, prompt, and resulting asset hash for each generated file.

### 0:58-1:25 - Review And Approve

On screen: approve one asset, reject or leave drafts for others.

Narration:

> The ledger is built for creative approval. Each asset can be approved, rejected, or left in draft. The status travels with the asset packet, so downstream teams do not need to infer which generated files are safe to use.

### 1:25-1:48 - Manifest Preview

On screen: manifest panel with checksum, storage backend, provider, model, and status.

Narration:

> The manifest is the key object. It gives the team a compact audit record for every asset: prompt, provider, model, storage key, checksum, and approval state.

### 1:48-2:08 - Export Packet

On screen: click export, show exported manifest confirmation, then download the ZIP packet.

Narration for current local demo:

> In local mode, the packet exports to local storage and can be downloaded as a ZIP with manifest, README, and available local media. The Backblaze B2 adapter is already implemented behind the same storage interface, and final submission requires one live B2 upload proof before this claim is made publicly.

Narration after T020 is live-verified:

> The packet is exported through Backblaze B2-compatible storage. The asset and manifest are stored with environment-only credentials, and ProofFrame records sanitized object references rather than secrets.

### 2:08-2:15 - Close

On screen: repo link, final status, and app title.

Narration:

> ProofFrame makes generated media usable for real teams: creative enough to move fast, but traceable enough to trust.

## Shot List

| Shot | Required Before Final | Status |
| --- | --- | --- |
| Browser first screen | Yes | Ready: `docs/assets/proofframe-local-ui-smoke.png` |
| Campaign creation | Yes | Ready in local app |
| One-click Judge Demo | Yes | Ready in local app |
| Generated asset ledger | Yes | Ready in local app |
| Approval state change | Yes | Ready in local app |
| Manifest export | Yes | Ready in local app |
| Evidence ZIP download | Yes | Ready in local app |
| B2 object proof with secrets redacted | Yes | Pending T020 |
| Genblaze run proof with model/provider metadata | Yes | Pending T021 |
| Public repo view | Yes | Ready |
| Devpost final project page | Yes | Pending T042 |

## Recording Checklist

- Use a clean browser profile or hide unrelated tabs.
- Keep terminal font large enough for path and test output.
- Run `python scripts/demo_readiness.py` before mock recording, and `python scripts/demo_readiness.py --strict-final` before final sponsor-backed recording.
- Do not show `.env`, API keys, Backblaze keys, Genblaze keys, cookies, signed URLs, or account dashboards with private billing data.
- Redact full object keys if they reveal bucket names, account ids, or signed query strings.
- Record final video only after `docs/public_claim_freeze.md` is released and T020/T021 are verified.
