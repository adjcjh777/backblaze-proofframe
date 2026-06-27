# ProofFrame Demo Storyboard

Mode: `mock_storyboard_ready`
Mock storyboard ready: `true`
Final video ready: `false`
Duration: `135s / 180s max`
Public demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Video URL: TBD after final B2 and Genblaze proof.

## Timeline

| Time | Shot | Screen | Narration |
| --- | --- | --- | --- |
| 0:00-0:12 | Product hook | ProofFrame dashboard and judge recording slate. | ProofFrame helps teams trust generated media after the prompt is over by turning each asset into a reviewable packet. |
| 0:12-0:30 | Sponsor evidence model | Manifest fields plus non-secret B2 setup and final-gate status. | Before any live credential is shown, the packet already has the B2-ready evidence shape: storage backend, storage key, checksum, manifest, and approval state. The private B2 bucket and runner are prepared, while live upload stays a final gate. |
| 0:30-0:48 | Campaign brief | Campaign, audience, tone, and brief fields. | The workflow starts with a creative brief while preserving the operational details teams usually lose. |
| 0:48-1:10 | Generate variants | Generated asset ledger with provider/model evidence. | The public demo uses deterministic mock generation; the same manifest fields are reserved for the final live Genblaze run. |
| 1:10-1:32 | Review and approve | Approve, reject, search, and filter evidence. | Every approval decision travels with the packet so downstream teams know which generated files are safe to use. |
| 1:32-1:55 | Manifest preview | Provenance chain and manifest JSON. | The manifest ties each asset to its prompt, provider, model, storage key, checksum, approval state, and risk note. |
| 1:55-2:08 | Export packet | Export manifest and download evidence ZIP. | The local packet exports as a downloadable ZIP; final B2 proof must verify the same flow through Backblaze storage before public claims are upgraded. |
| 2:08-2:15 | Close | Repo link, gate status, and ProofFrame title. | ProofFrame makes generated media creative enough to move fast and traceable enough to trust. |

## Required Assets

- OK `docs/demo_script.md`
- OK `docs/assets/proofframe-local-ui-smoke.png`
- OK `docs/assets/proofframe-review-console-smoke.png`
- OK `docs/assets/proofframe-hf-public-smoke.png`
- OK `docs/assets/demo-readiness-report.md`
- OK `docs/assets/live-credential-handoff.md`
- OK `docs/assets/devpost-submission-packet.json`

## Next Actions

- Capture live Backblaze B2 asset and manifest proof.
- Capture live Genblaze generation proof.
- Write sanitized final live proof evidence JSON.
- Record and upload the final public demo video under 3 minutes.
- Run final secret scan before publishing the video.
