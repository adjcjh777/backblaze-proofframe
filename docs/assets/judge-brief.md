# ProofFrame Judge Brief

Created: `2026-07-03T10:57:05Z`
Tagline: B2-ready provenance desk for GenAI media.
Public demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Repository: https://github.com/adjcjh777/backblaze-proofframe

## 30-Second Opening

ProofFrame is not another image generator. It is a media operations desk that turns each generated asset into a reviewable packet: prompt, provider/model metadata, storage reference, checksum, approval state, risk note, manifest, and exportable evidence.

## Why It Can Win

- Storage and provenance are the product surface, not a hidden implementation detail.
- Backblaze B2 and Genblaze Pipeline proof are captured; final public video and Devpost receipt remain gated.
- The app feels useful after the hackathon: teams can approve, reject, search, export, and audit generated media.
- Fail-closed reports make the submission defensible and prevent overclaiming before live proof.

## Current Status

- Packet mode: `post_live_verified`
- Safe to submit: `false`
- Launch phase: `public_video`
- Next command: `python scripts/devpost_packet.py --post-live --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL"`
- Award readiness: `105/115` (proof_verified_video_pending)
- Final closure: `0/10`
- Public Space: `public_space_synced` (see `docs/assets/public-space-sync-report.md` for runtime sha)
- Devpost submission open: `True`

## Safe Claims

- ProofFrame is a working provenance and approval desk for generated media.
- The public demo is credential-free and runs in deterministic local/mock mode.
- The repository includes Backblaze B2-compatible storage and Genblaze provider paths for GMICloud, OpenAI, and a credential-free local Pipeline provider.
- Every public claim is gated by reports, task status, and secret-scan artifacts.
- Backblaze B2 live storage proof is captured in the sanitized evidence package.
- Genblaze Pipeline proof is captured with the credential-free local image provider and B2-backed manifests.

## Not Yet Claimed

- Submitted Devpost project receipt.

## Judge Walkthrough

- Open the public demo in judge mode and create the one-click Judge Demo packet.
- Inspect generated assets, provider/model fields, storage references, checksums, and approval state.
- Approve or reject an asset and download the evidence ZIP.
- Read the final control and launch plan reports to see exactly what remains before final sponsor proof.

## Evidence Artifacts

- `docs/assets/devpost-form-kit.md`
- `docs/assets/final-submission-control.md`
- `docs/assets/final-launch-plan.md`
- `docs/assets/award-readiness-report.md`
- `docs/assets/public-space-sync-report.md`
- `docs/assets/submission-bundle-manifest.md`

## Copy Blocks

### devpost_intro

ProofFrame makes generated media operationally trustworthy: the demo creates media packets that include prompts, provider/model metadata, storage references, checksums, review state, risk notes, and downloadable manifests.

### judge_note

Current public demo is safe local/mock mode. Final sponsor claims stay gated until Backblaze B2 live storage proof, Genblaze live generation proof, final video, audit, and Devpost receipt are complete.
