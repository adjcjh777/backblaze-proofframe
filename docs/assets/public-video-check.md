# ProofFrame Public Video Check

Mode: `pending_video_url`
OK: `false`
Safe to submit: `false`
Video URL: `TBD after final B2 and Genblaze proof.`

## Checks

- OK `official_event_video_requirements`: demo_video=True; public_video_host=True; snapshot validation=True. Evidence: `docs/assets/devpost-event-snapshot.json`
- OK `storyboard_under_three_minutes`: Storyboard duration is 135s / 180s. Evidence: `docs/assets/demo-storyboard.json`
- BLOCKED `video_url_present`: Video URL source is missing or placeholder. Evidence: `docs/assets/devpost-submission-packet.json or PROOFFRAME_PUBLIC_VIDEO_URL`
- BLOCKED `video_url_public_and_safe`: scheme_ok=False; host=None; host_public=False; token_params=[]. Evidence: `public video URL`
- BLOCKED `video_url_official_public_host`: host=None; official_host_family=None; allowed families are YouTube, Vimeo, and Youku. Evidence: `Devpost public video host requirement`
- BLOCKED `video_url_accessible`: checked=False; status=None; error=URL verification was not requested.. Evidence: `public video URL`

## Access Check

- Checked: `false`
- Status: `None`
- Content type: `None`
- Final URL: `TBD after final B2 and Genblaze proof.`

## Next Actions

- Record and upload the final demo video, then set PROOFFRAME_PUBLIC_VIDEO_URL.
- Use a public http(s) video URL without credential, token, signature, or expiry query parameters.
- Upload the final demo video to YouTube, Vimeo, or Youku before strict final submission.
- Run python scripts/public_video_check.py --video-url "$PROOFFRAME_PUBLIC_VIDEO_URL" --verify-url --strict-final after upload.

This report stores only a public video URL and accessibility metadata, never credentials or browser state.
