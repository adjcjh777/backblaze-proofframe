# Scout Report: Backblaze Generative Media Hackathon

Date checked: 2026-06-27  
Latest lightweight refresh: 2026-06-28 Asia/Shanghai
Scout: proofframe-hackathon-scout  
Scope: official rules and competition-risk review only

## Verdict

GO, with compliance caveats. Backblaze Generative Media Hackathon is a strong fit for ProofFrame because the official theme and judging criteria explicitly reward generative media workflows, durable storage of generated media, metadata/provenance records, and meaningful Genblaze orchestration. The main risk is not schedule; it is rule fit: Backblaze B2 and Genblaze are not optional decoration. They must be materially integrated and explained in the submission.

## Source URLs

- Main Devpost page: https://backblaze-generative-media.devpost.com/
- Official rules: https://backblaze-generative-media.devpost.com/rules
- Dates page: https://backblaze-generative-media.devpost.com/details/dates
- Resources page: https://backblaze-generative-media.devpost.com/resources
- Participants/login signal: https://backblaze-generative-media.devpost.com/participants
- Genblaze repo: https://github.com/backblaze-labs/genblaze
- Backblaze B2 signup/docs entry: https://www.backblaze.com/cloud-storage?utm_source=github&utm_medium=referral&utm_campaign=genhackathon
- GMI Cloud optional credits path: https://www.gmicloud.ai/
- Devpost AI hackathon index for alternatives: https://devpost.com/c/artificial-intelligence
- Alternative checked: Slack Agent Builder Challenge: https://slackhack.devpost.com/
- Alternative checked: Global AI Hackathon Series with Qwen Cloud: https://qwencloud-hackathon.devpost.com/
- Alternative checked: Build with Gemini XPRIZE: https://xprize.devpost.com/

## Deadlines

Primary submission deadline:

- Official rules: August 3, 2026, 5:00 pm Eastern Time.
- UTC: 2026-08-03 21:00 UTC, assuming Eastern Time is EDT / UTC-4 on that date.
- Beijing: 2026-08-04 05:00 Asia/Shanghai.

Other official timing:

- Registration/submission period in rules: June 22, 2026, 10:00 am ET to August 3, 2026, 5:00 pm ET.
- Devpost dates page lists submissions from June 22, 2026, 12:30 pm EDT to August 3, 2026, 5:00 pm EDT. This start-time mismatch is low risk because the event has already started; if a conflict matters, official rules say rules prevail.
- Judging: August 5, 2026, 10:00 am ET to August 11, 2026, 5:00 pm ET. Inferred Beijing window: 2026-08-05 22:00 to 2026-08-12 05:00.
- Winners: on or around August 12, 2026, 2:00 pm ET. Inferred Beijing: 2026-08-13 02:00.

## Rules And Fit Notes

- Eligibility: open to individuals above the age of majority, teams, and organizations. Exclusions include jurisdictions where US/local law prohibits participation or prize receipt, with examples including Brazil, Quebec, Russia, Crimea, Cuba, Iran, North Korea, and OFAC-designated countries. Sponsor/admin employees and related promotion entities are excluded.
- Required build: entrants must submit a working software application for generative AI media that uses Backblaze B2 Cloud Storage and Genblaze.
- Existing-project rule: pre-existing projects are allowed only if they use B2 storage and Genblaze SDK after the hackathon submission period starts, and the submission should explain significant updates during the period.
- B2 requiredness: hard requirement. Rules require B2 use, and judging asks whether the app meaningfully stores, organizes, serves, or manages generated media, metadata, provenance, or app assets in B2.
- Genblaze requiredness: hard requirement. Rules require Genblaze use, Stage One checks required APIs/SDKs on pass/fail, and judging asks whether Genblaze meaningfully builds, connects, or orchestrates media workflows across models/providers/steps.
- GMI Cloud: optional. The page says other cloud providers may be used. Credits are limited to the first 270 eligible participants who sign up and submit the request form; current public participant count is already above that range, so do not rely on credits.
- Submission must include: working app URL, public or private GitHub repo URL with source/assets/setup README, text description explaining features, B2 and Genblaze usage, and AI providers/models used, plus a demo video.
- Demo video: should be under 3 minutes, show the project functioning, and be publicly visible on YouTube, Vimeo, or Youku.
- App access: judges need a functioning app link. If auth is required, include a test account and clear login instructions. The app must remain free of charge and unrestricted for sponsor/admin/judges through judging.
- Repository access: private repo is allowed, but Backblaze testing account access must be granted once sponsor shares that account. Public repo reduces access friction but exposes implementation.
- Publicity/IP: entrants keep IP, but sponsor/Devpost may promote/display submission materials and use participant name/likeness/comments for hackathon publicity. Some submission components may be public. Avoid third-party copyrighted media, trademarks, or assets without rights.
- Language: all submission materials must be English or include English translations.
- Prizes: $10,000 USD total cash across overall prizes: Grand Prize $7,000, Second Place $2,000, Third Place $1,000. Bonus Feedback Prize: 10 winners receive one hour of mentorship / architecture guidance from Backblaze. Entrants may win one overall prize and one feedback prize.
- Dynamic participant count: `docs/assets/devpost-event-snapshot.json` is the authoritative refreshed count. Recheck before final submission and avoid using a stale exact count in public copy.

## Risks

- Rule-fit risk: a superficial B2 bucket upload or thin Genblaze wrapper may fail Stage One or score poorly. ProofFrame should make B2-backed provenance/media storage and Genblaze orchestration central to the product narrative.
- Account/setup risk: Devpost login is required; participant browsing already prompts login. Backblaze B2 account and bucket setup are required. GMI Cloud credits may be unavailable due to first-270 limit.
- Public access risk: demo video must be public, and the app must be reachable for judging. If the product handles sensitive media/provenance, create sanitized examples and a dedicated test account.
- Secret-handling risk: B2 keys, AI provider keys, and test-account credentials must not be committed. Submission instructions can include a judge login, but repo and docs should never contain production secrets.
- Existing-project evidence risk: if ProofFrame code predates June 22, maintain commit notes showing the post-start B2/Genblaze integration and the significant update.
- IP/content risk: generated media examples must avoid copyrighted music, brands, or private likenesses unless rights are clear.
- Time-zone risk: Beijing deadline is early morning on August 4, 2026. Operational cutoff should be August 3 Beijing daytime/evening, not the final hour.

## Next Registration Steps

1. Controller or representative logs into Devpost and joins https://backblaze-generative-media.devpost.com/.
2. Create/confirm Backblaze B2 account, create a dedicated B2 bucket, and generate least-privilege application keys for runtime deployment only.
3. Integrate Genblaze from https://github.com/backblaze-labs/genblaze and keep a clear README section explaining how Genblaze orchestrates providers/steps.
4. Optional only: request GMI Cloud credits, but plan with another provider fallback because credits are limited and may already be exhausted.
5. Prepare public demo video under 3 minutes, working app URL, GitHub repo URL, English text description, AI provider/model list, and B2/Genblaze explanation before 2026-08-03 21:00 UTC / 2026-08-04 05:00 Beijing.

## Alternative Hackathon Comparison

- Slack Agent Builder Challenge: attractive $42,000 prize pool and strong distribution path, but it is Slack-agent/Marketplace specific. ProofFrame would have to bend toward Slack workflow automation instead of generated-media provenance, B2 storage, and media pipeline evidence.
- Global AI Hackathon Series with Qwen Cloud: larger prize pool than Backblaze, but the deadline is much earlier and the platform center of gravity is Qwen Cloud / agent building. It is less directly aligned with ProofFrame's storage-backed provenance story.
- Build with Gemini XPRIZE: huge prize pool and later deadline, but extremely broad impact scope and very high visible participant count. It is more competitive and less targeted than Backblaze for a focused media provenance/storage product.

Backblaze remains the best fit among these because ProofFrame can satisfy the sponsor's explicit desired path: prompt/model output -> Genblaze workflow -> SHA/provenance/metadata -> B2 durable media storage -> production-minded user experience.

## Questions For Controller

- Who will be the Devpost representative for the team or organization?
- Should the GitHub repo be public for lower judging friction, or private with Backblaze test-account access?
- What sanitized sample media/provenance data can be publicly shown in the demo video?
- Which provider stack should Genblaze orchestrate if GMI Cloud credits are unavailable?
- What is the submission name and one-sentence positioning: "ProofFrame" as provenance audit layer, media verification tool, or storage-backed generation pipeline?
- What is the internal freeze time before the Beijing deadline?
