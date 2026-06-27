# ProofFrame

ProofFrame is a provenance-first generative media vault for the Backblaze Generative Media Hackathon.

It turns a creative brief into a reviewable asset packet: generated media, prompt history, model/provider metadata, hashes, approval state, and a shareable manifest. The local demo uses deterministic generation and local storage; the final hackathon gate is to verify the same packet flow through Genblaze-backed generation and Backblaze B2-compatible storage. The product goal is not "yet another image generator"; it is the missing operations desk for teams that need to know where an AI asset came from, whether it is approved, and how to reproduce or retire it.

## Hackathon Choice

Selected competition: [Backblaze Generative Media Hackathon](https://backblaze-generative-media.devpost.com/)

Why this one:

- Online Devpost format with a clear August 3, 2026 5:00 PM EDT deadline, which is August 4, 2026 05:00 in Beijing.
- Cash prizes, including a $7,000 grand prize.
- Moderate visible participant count compared with larger AI agent events.
- Sponsor requirements are specific enough to reward meaningful integration: Genblaze plus Backblaze B2.
- A polished, useful product can beat a raw model demo here.

## Core Documents

- `docs/research.md`: competition search, candidate comparison, selected-event evidence.
- `docs/prd.md`: product PRD.
- `docs/spec.md`: technical specification.
- `docs/integrations.md`: B2 and Genblaze readiness gates.
- `docs/demo_script.md`: demo video script and shot list.
- `docs/evidence_package.md`: Devpost evidence package and copy bank.
- `docs/public_claim_freeze.md`: public claim boundaries before final submission.
- `docs/submission.md`: registration and submission plan.
- `docs/todo.md`: human task board.
- `tasks.json`: queryable task ledger.

## Local Task Commands

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py show T001
python3 scripts/task.py done T001
python3 scripts/task.py block T010 --note "Requires account setup"
```

## Planned Stack

- Backend: Python, FastAPI, SQLite.
- Storage: local storage for offline demo, Backblaze B2 S3-compatible storage for submission.
- Generation: deterministic mock provider for local tests, Genblaze/OpenAI-compatible media provider adapter for real runs.
- Frontend: production-grade browser UI with `apps/web/index.html` as entry point.
- Packaging: Dockerfile and release checklist.

## Current Status

Stage 0 is complete: selected competition, repo, PRD/spec/todo, Agent Bus team, official-rule scout report, and GitHub setup.

Stage 1 is complete enough for local demo iteration: FastAPI MVP skeleton, mock generation, local storage, manifest export, and the Proof Ledger browser UI.

Stage 2 is in progress: B2-compatible storage code and a Genblaze/GMICloud image provider path exist, but live B2 and Genblaze runs still need credentials/provider verification before final submission claims.

Stage 3 preparation has started: Proof Ledger UI smoke is captured, and demo/evidence/claim-freeze docs are ready for the final sponsor-integration pass.

![ProofFrame local UI smoke](docs/assets/proofframe-local-ui-smoke.png)

## Run Locally

```bash
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn proofframe.app:app --reload --port 8088
```

Then open `http://127.0.0.1:8088/`.

## Integration Readiness

```bash
. .venv/bin/activate
python scripts/check_integrations.py
```

B2 mode intentionally fails closed unless `B2_ENDPOINT_URL`, `B2_BUCKET`, `B2_KEY_ID`, and `B2_APPLICATION_KEY` are set. Genblaze mode intentionally fails closed unless a Genblaze/GMI key and `GENBLAZE_IMAGE_MODEL` are set, and the official `genblaze-core` and `genblaze-gmicloud` packages are installed.
