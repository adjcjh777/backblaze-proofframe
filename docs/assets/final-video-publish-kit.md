# ProofFrame Final Video Publish Kit

Mode: `ready_for_final_upload`
OK: `true`
Safe to submit: `false`
Final video ready: `false`
Created: `2026-06-29T10:31:10Z`

## Upload Copy

Title: ProofFrame: Provenance-first generated media vault

Description:

```text
ProofFrame is a provenance-first media operations desk for generated campaign assets.

This demo walks through one creator workflow: open the judge-mode demo, create a media packet, inspect prompt/provider/model/storage/checksum metadata, approve an asset, and download the evidence ZIP.

Public demo: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
Repository: https://github.com/adjcjh777/backblaze-proofframe

What to look for:
- Generated media is reviewed as an evidence packet, not a loose image.
- Prompt, provider/model metadata, storage pointer, checksum, approval state, and risk note stay together.
- Optional Backblaze B2 and Genblaze paths are implemented and fail closed until live proof is captured.

Claim boundary: Use this title and description for final upload only after live B2 and Genblaze proof are recorded; until then, the public demo remains local/mock and safe_to_submit=false.
```

## Chapters

- `0:00` ProofFrame judge-mode slate (20s)
- `0:20` Generate and review a provenance packet (55s)
- `1:15` Manifest, checksum, storage route, and evidence ZIP (35s)
- `1:50` Final B2, Genblaze, video, and audit gates (25s)

## Upload Checklist

- PENDING `host_family`: Upload to an official public video host - Allowed host families: YouTube, Vimeo, or Youku.
- PENDING `public_visibility`: Use public or unlisted visibility that Devpost judges can access - The final URL must be reachable without login, cookies, tokens, or signed query parameters.
- OK `duration`: Keep the final video under the event time limit - Use the generated storyboard and chapter plan; rerun public_video_check after upload.
- PENDING `devpost_field`: Paste the final video URL into Devpost - After upload, set PROOFFRAME_PUBLIC_VIDEO_URL and regenerate final reports.

## Devpost Field

- Field: `video_url`
- Ready: `false`
- Value: `TBD after final upload.`

## Claim Boundary

Use this title and description for final upload only after live B2 and Genblaze proof are recorded; until then, the public demo remains local/mock and safe_to_submit=false.

## Next Actions

- Record the final narrated video after live B2 and Genblaze proof is visible.
- Upload to YouTube, Vimeo, or Youku with public or unlisted judge-accessible visibility.
- Set PROOFFRAME_PUBLIC_VIDEO_URL to the final URL and run scripts/public_video_check.py --verify-url --strict-final.
- Regenerate Devpost form kit, final control, submission audit, preview, and bundle before submit.
