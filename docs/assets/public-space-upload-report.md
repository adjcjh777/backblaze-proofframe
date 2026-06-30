# ProofFrame Public Space Upload Report

Mode: `dry_run_ready`
OK: `true`
Execute: `false`
Created: `2026-06-30T05:35:44Z`
Repo: `ADJCJH/backblaze-proofframe`
Revision: `main`
Raw base: https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main

## Safety

- Required ignore patterns OK: `true`
- Included files: `209`
- Excluded files: `13579`
- Included sensitive files: `none`

## Sensitive File Checks

- OK `.env` is absent; excluded `true`.
- OK `.env.local` is absent; excluded `true`.
- OK `.env.final.local` is present; excluded `true`.
- OK `.env.production.local` is absent; excluded `true`.

## Upload

- Upload not attempted.

## Secret Probe

- Secret probe not attempted.

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
