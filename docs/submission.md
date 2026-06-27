# Registration And Submission Plan

## Event

- Backblaze Generative Media Hackathon
- Official page: https://backblaze-generative-media.devpost.com/
- Submission deadline: 2026-08-03 17:00 EDT
- Beijing time: 2026-08-04 05:00 Asia/Shanghai

## Account Requirements

Likely required:

- Devpost account for registration/submission.
- Backblaze account and B2 bucket for final integration evidence.
- Genblaze setup from https://github.com/backblaze-labs/genblaze.
- Optional deployment account if we choose public demo hosting.

Resolved setup:

- Devpost registration is complete.

Manual/user-touch blockers remaining:

- Creating or authorizing Backblaze B2 credentials.
- Any payment-card or identity step.

Codex can handle:

- Preparing all submission text.
- Maintaining copy-ready text in `docs/devpost_draft.md`.
- Creating GitHub repo and release commits.
- Running local/demo verification.
- Drafting Devpost answers.
- Creating demo video script/storyboard.
- Producing screenshots and evidence package.
- Preparing public demo deployment instructions in `docs/deployment.md`.

## Submission Assets

- Public GitHub repository.
- Credential-free public mock demo URL: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
- B2/Genblaze-backed demo URL or Docker instructions after T020/T021.
- Devpost text from `docs/devpost_draft.md`.
- Field-by-field Devpost form kit from `docs/assets/devpost-form-kit.md` and `.json`.
- Safe submission bundle manifest from `docs/assets/submission-bundle-manifest.md` and `.json`.
- Final submission control report from `docs/assets/final-submission-control.md` and `.json`.
- Structured demo storyboard from `docs/assets/demo-storyboard.md` and `.json`.
- Local final credential setup via `scripts/final_env_wizard.py`.
- 2 minute demo video.
- Project title: ProofFrame.
- Tagline: "A provenance-first vault for generated media."
- Description emphasizing Backblaze B2 and Genblaze.
- Screenshots: brief intake, asset review, manifest panel, B2 object evidence.
- Compliance note: no secrets, sample assets safe for public use.

## Draft Devpost Pitch

ProofFrame helps creators and agencies trust the AI media they generate. The current local demo creates a reviewable asset packet with generated media, prompts, provider metadata, hashes, approval states, and exportable manifests. The final submission target is to run the same flow through a Genblaze-backed generation path and Backblaze B2-backed media/manifest storage.

The result is a shareable asset packet that explains where each generated file came from, whether it is approved, and how it can be reproduced or retired.

## Final Submission Checklist

- [x] Registered on Devpost.
- [x] Backblaze B2 bucket created.
- [ ] Least-privilege B2 application key created.
- [ ] B2 media and manifest upload verified.
- [ ] Genblaze run captured.
- [ ] Public GitHub repo complete.
- [x] Public mock demo URL deployed.
- [ ] B2/Genblaze-backed public demo URL verified or Docker path accepted.
- [ ] README has setup, demo, architecture, and sponsor usage.
- [ ] Docker run verified.
- [ ] Browser smoke verified.
- [ ] No secrets in repo.
- [ ] Demo video recorded.
- [ ] Devpost packet regenerated with the public video URL.
- [ ] `python scripts/submission_audit.py --strict-final` passes.
- [ ] Devpost draft reviewed.
- [x] Safe submission bundle manifest generated.
- [ ] Public Devpost submission receipt generated after submit.
- [ ] Submitted before 2026-08-04 05:00 Beijing.
