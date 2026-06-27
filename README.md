# ProofFrame

ProofFrame is a provenance-first generative media vault for the Backblaze Generative Media Hackathon.

It turns a creative brief into a reviewable asset packet: generated media, prompt history, model/provider metadata, hashes, approval state, and a shareable manifest stored through a Backblaze B2-compatible layer. The product goal is not "yet another image generator"; it is the missing operations desk for teams that need to know where an AI asset came from, whether it is approved, and how to reproduce or retire it.

## Hackathon Choice

Selected competition: [Backblaze Generative Media Hackathon](https://backblaze-generative-media.devpost.com/)

Why this one:

- Online Devpost format with a clear August 3, 2026 5:00 PM PDT deadline.
- Cash prizes, including a $5,000 grand prize.
- Moderate visible participant count compared with larger AI agent events.
- Sponsor requirements are specific enough to reward meaningful integration: Genblaze plus Backblaze B2.
- A polished, useful product can beat a raw model demo here.

## Core Documents

- `docs/research.md`: competition search, candidate comparison, selected-event evidence.
- `docs/prd.md`: product PRD.
- `docs/spec.md`: technical specification.
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

Stage 0 is the project foundation: selected competition, repo, PRD/spec/todo, Agent Bus team, and GitHub setup.

