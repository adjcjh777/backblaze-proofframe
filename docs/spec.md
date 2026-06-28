# ProofFrame Technical Spec

## Architecture

```text
Browser UI
  |
FastAPI app
  |-- Campaign service
  |-- Generation service
  |     |-- MockMediaProvider
  |     |-- GenblazeMediaProvider
  |-- Storage service
  |     |-- LocalStorageBackend
  |     |-- B2StorageBackend
  |-- Manifest service
  |-- Submission gate service
  |-- SQLite repository
```

## Data Model

### Campaign

- `id`
- `title`
- `brief`
- `audience`
- `tone`
- `created_at`

### Asset

- `id`
- `campaign_id`
- `kind`: image, video, audio, text
- `status`: draft, approved, rejected
- `prompt`
- `provider`
- `model`
- `storage_backend`
- `storage_key`
- `public_url`
- `sha256`
- `generation_metadata`
- `risk_note`
- `created_at`

### Manifest

- `manifest_version`
- `campaign`
- `assets[]`
- `exported_at`
- `app_version`

## API Draft

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serve the Proof Ledger browser UI. |
| `GET` | `/api/health` | Runtime health and adapter availability. |
| `GET` | `/api/submission/gate` | Return fail-closed final submission readiness for task gates, Devpost packet, live proof evidence, and final report artifacts. |
| `GET` | `/api/judge/brief` | Return the public-safe judge brief artifact that powers the first-screen Judge Brief panel. |
| `POST` | `/api/campaigns` | Create campaign. |
| `GET` | `/api/campaigns` | List campaigns. |
| `POST` | `/api/campaigns/{id}/generate` | Generate variants. |
| `POST` | `/api/demo/judge-packet` | Create a one-click judge-ready local demo packet. |
| `POST` | `/api/assets/{id}/status` | Approve/reject asset. |
| `GET` | `/api/campaigns/{id}/manifest` | Return manifest JSON. |
| `POST` | `/api/campaigns/{id}/export` | Export packet. |
| `GET` | `/api/campaigns/{id}/packet.zip` | Download manifest, README, and available local media as an evidence packet. |

## Review Console

The browser UI includes local-only review operations over the in-memory asset set:

- scorecard counts for total, approved, draft, rejected, and decision coverage
- status filter for all/draft/approved/rejected
- search across prompt, provider, model, storage backend, storage key, checksum, and risk note
- copy-safe evidence summary that includes campaign id, counts, backend names, first checksum, and storage key, but no credentials or signed URLs

## Submission Gate Dashboard

The browser sidebar includes a final gate panel backed by `GET /api/submission/gate`:

- required final tasks: T020, T021, T040, T041, T041A, and T042
- Devpost packet presence and claim mode
- final live proof evidence status for B2 storage plus Genblaze generation
- final report artifacts for secret scan, submission audit, and Devpost submission receipt
- next-action copy for whichever final blocker remains first

The gate intentionally stays in `pre_live_safe` mode until all required tasks are done, `docs/assets/final-live-proof-evidence.json` proves B2 plus Genblaze with nonempty sanitized object/checksum fields, and the final secret scan, submission audit, and Devpost receipt reports all declare the expected schema with `ok=true`.

## Storage

Local mode:

- Writes media and manifests under `var/storage`.
- Used by tests, demo fallback, and contributors without credentials.

B2 mode:

- Uses S3-compatible settings:
  - `B2_ENDPOINT_URL`
  - `B2_S3_ENDPOINT_URL` as an accepted alias
  - `B2_BUCKET`
  - `B2_KEY_ID`
  - `B2_APPLICATION_KEY`
  - `B2_APP_KEY` as an accepted alias
- Credentials are environment-only.
- If required variables are missing, B2 mode must be unavailable rather than silently falling back during final verification.
- Current status: code-level backend and fake-client tests exist. Live B2 bucket verification is still required before public submission claims.

## Generation

Mock mode:

- Creates deterministic SVG/PNG-like artifacts and metadata from the prompt.
- Guarantees repeatable tests.

Genblaze mode:

- Uses the official Genblaze `Pipeline` API with `GMICloudImageProvider`.
- Records provider/model/run/manifest metadata in the manifest without storing raw provider URLs.
- Must never persist raw secrets.
- Current status: code-level provider path exists and fails closed without packages/config. Live official Genblaze package/provider route is still required before public submission claims.

## Frontend Direction

The selected interface is Proof Ledger, a restrained audit-and-approval board for media approvals:

- Dense but calm asset ledger.
- Visible storage and manifest details.
- Strong first-viewport product signal: ProofFrame, campaign status, asset packet.
- No generic purple AI hero.
- Use an `index.html` entry file.
- Include subtle "Created By Deerflow" signature as required by the frontend-design skill when generated frontend code is added.

## Security

- `.env` is ignored.
- Provide `.env.example`.
- Add a secret scan before final submission.
- Do not print full storage keys or signed URLs in test logs unless sanitized.

## Verification Gates

- Unit tests for task ledger, manifest, storage adapters.
- API smoke for `/api/health`.
- Browser smoke for create/review/export happy path.
- Docker build and local run.
- Submission audit against Devpost requirements.
- Submission gate API and UI checks.
- Schema-stamped judge crosswalk from official criteria to evidence, safe claims, final gates, and demo shots.
- No-secret final rehearsal checklist before credential entry and Devpost submission.
- No-secret Devpost web submission checklist before pressing the final submit button.
- Public demo video URL check for token-free, reachable final video evidence.
