# Deployment Runbook

Status: public mock demo deployed. A B2/Genblaze-backed public URL is still a final gate because it requires private B2/Genblaze secrets and live sponsor proof.

## Verified Public Mock Demo

- App URL: https://adjcjh-backblaze-proofframe.hf.space/
- Judge-mode URL: https://adjcjh-backblaze-proofframe.hf.space/?judge=1
- Space repo: https://huggingface.co/spaces/ADJCJH/backblaze-proofframe
- Runtime: Docker Space, local storage, mock generation
- Verified with: `python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space`
- Judge-mode slate, sponsor evidence model, final report gate, Agent handoff report, final launch plan, judge brief, and final control alignment verified after HF Space commit `0bf36e`: runtime reports sha `0bf36eaabc491f1afda189c02a6fbcb7cd63030b`; public HTML contains `Judge recording slate`, `Sponsor Evidence Model`, `shouldAutoLoadJudgeDemo`, and `Final reports pending`; `/api/submission/gate` returns `pre_live_safe` with `pre_live_packet_pending` and `report_gate`; raw Space artifacts `docs/assets/agent-handoff-report.json`, `docs/assets/final-launch-plan.json`, and `docs/assets/judge-brief.json` return `handoff_ready`, `ready_for_credential_entry`, and `safe_to_submit=false`; public API smoke passes in local/mock mode.
- Screenshot: `docs/assets/proofframe-hf-public-smoke.png`

This URL is safe to use in Devpost as a credential-free public demo before live B2/Genblaze proof, as long as the description says local/mock mode.

## Deployment Goal

Provide judges with a working app URL that can:

- open the Proof Ledger UI
- run Judge Demo without credentials, including auto-loading it through `?judge=1`
- generate local mock assets
- export a manifest
- download an evidence ZIP
- optionally run with B2 and Genblaze environment variables for final proof

## Docker Contract

The Docker image listens on `${PORT:-8088}`.

```bash
docker build -t proofframe:local .
docker run --rm -p 8089:8088 proofframe:local
python3 scripts/api_smoke.py --base-url http://127.0.0.1:8089
```

The default image installs the core app only so public mock deployments stay fast and do not need sponsor SDK packages. Build the final integration-capable image with:

```bash
docker build --build-arg INSTALL_EXTRAS=integrations -t proofframe:integrations .
```

For Hugging Face Docker Spaces, keep README metadata in the Space repo with `sdk: docker` and `app_port: 8088`; missing `app_port` leaves the Space stuck in `APP_STARTING` because the platform probes the wrong port.

## Required Runtime Environment

Credential-free demo:

```bash
PROOFFRAME_STORAGE_BACKEND=local
PROOFFRAME_GENERATION_BACKEND=mock
PROOFFRAME_STORAGE_ROOT=var/storage
```

Final B2 proof:

```bash
PROOFFRAME_STORAGE_BACKEND=b2
B2_ENDPOINT_URL=
B2_BUCKET=
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_PUBLIC_BASE_URL=
```

Final Genblaze proof:

```bash
PROOFFRAME_GENERATION_BACKEND=genblaze
GMI_API_KEY=
GENBLAZE_IMAGE_MODEL=seedream-5.0-lite
GENBLAZE_ASPECT_RATIO=16:9
GENBLAZE_TIMEOUT_SECONDS=180
```

## Hosting Options

Use any Docker-capable app host. Recommended judging flow:

1. Create a Docker web service from `https://github.com/adjcjh777/backblaze-proofframe`.
2. Point it at branch `feature/backblaze-proofframe` or the final release branch.
3. Keep local/mock env for a public no-secret demo.
4. Add B2/Genblaze secrets only in the host's secret store for final sponsor proof.
5. Run `python scripts/api_smoke.py --base-url <public-url>` after deployment.
6. Save the public URL in `docs/evidence_package.md` and Devpost.

## Post-Deploy Checks

```bash
curl -fsS <public-url>/api/health
python scripts/api_smoke.py --base-url <public-url>
python scripts/secret_scan.py
```

Expected smoke evidence:

- `ok: true`
- `storage_backend`
- `generation_backend`
- `asset_sha256`
- `manifest_sha256`
- `packet_bytes`
- `judge_demo_campaign_id`

## Public URL Claim Rules

- Before T020/T021, describe the URL as a local/mock public demo.
- After T020/T021, describe the URL as B2/Genblaze-backed only if that exact deployment was verified with live credentials.
- Do not expose `.env`, raw object signed URLs, B2 application keys, GMI keys, browser cookies, or account dashboards.
