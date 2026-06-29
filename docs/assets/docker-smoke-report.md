# ProofFrame Docker Smoke Report

Mode: `docker_smoke_ready`
OK: `true`
Image: `proofframe:submission-smoke`
Base URL: `http://127.0.0.1:18088`

## Checks

- OK `dockerignore_secret_exclusions`: missing_required=[]; missing_allow=[].
- OK `docker_daemon`: docker info completed.
- OK `docker_build`: docker build completed.
- OK `docker_run`: docker run returned a container id.
- OK `docker_health`: health={'app': 'ProofFrame', 'version': '0.1.0', 'generation_backend': 'mock', 'storage_backend': 'local', 'b2_configured': False, 'genblaze_configured': False, 'ready': True}; error=None.
- OK `api_smoke`: api_smoke.py completed.
- OK `docker_cleanup`: docker rm -f completed.

## Docker Context Policy

This smoke test uses local/mock mode, does not read .env.final.local, and requires .dockerignore to exclude local env files from the Docker build context.

## Commands

- OK `docker_info`: `docker info --format {{json .ServerVersion}}`
- OK `docker_build`: `docker build -t proofframe:submission-smoke .`
- OK `docker_run`: `docker run -d --name proofframe-submission-smoke -p 18088:8088 proofframe:submission-smoke`
- OK `api_smoke`: `/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe/.venv/bin/python scripts/api_smoke.py --base-url http://127.0.0.1:18088`
- OK `docker_logs`: `docker logs --tail 80 proofframe-submission-smoke`
- OK `docker_cleanup`: `docker rm -f proofframe-submission-smoke`
