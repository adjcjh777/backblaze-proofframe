# ProofFrame Public Space Upload Report

Mode: `uploaded`
OK: `true`
Execute: `true`
Created: `2026-07-01T10:55:49Z`
Repo: `ADJCJH/backblaze-proofframe`
Revision: `main`
Raw base: https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main

## Safety

- Required ignore patterns OK: `true`
- Included files: `210`
- Excluded files: `14772`
- Included sensitive files: `none`

## Sensitive File Checks

- OK `.env` is absent; excluded `true`.
- OK `.env.local` is absent; excluded `true`.
- OK `.env.final.local` is present; excluded `true`.
- OK `.env.production.local` is absent; excluded `true`.

## Upload

- Upload OK: `true`
- Commit: `abb09ea8fa92cae185fb08d65ae6419d85bc3c0e`
- Commit URL: https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/commit/abb09ea8fa92cae185fb08d65ae6419d85bc3c0e

## Secret Probe

- Raw `.env.final.local` public check OK: `true`
- Status: `404`

## Next Commands

```bash
python scripts/public_space_upload.py --execute --commit-message "Sync ProofFrame public Space"
```
```bash
python scripts/public_space_sync.py
```
```bash
python scripts/api_smoke.py --base-url https://adjcjh-backblaze-proofframe.hf.space
```

This uploader excludes local env files, git state, virtualenvs, caches, runtime output, and node_modules before calling Hugging Face. It records file names and commit metadata only, never credential values.
