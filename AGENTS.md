# ProofFrame Agent Rules

## Language
- User-facing updates should be in Chinese.
- Public product copy, README sections, demo video script, and submission text may be English.

## Git
- Work only inside `/Users/junhaocheng/Documents/Codex/2026-06-27/quan/backblaze-proofframe`.
- Keep this as an independent Git repo. Do not commit changes from the parent `/Users/junhaocheng` tree.
- Current branch: `feature/backblaze-proofframe`.
- Before editing, confirm `pwd` and `git status --short --branch`.
- Commit by meaningful stages and push to GitHub after each stable stage.
- Never commit secrets, API keys, Backblaze credentials, Devpost cookies, or generated private media.

## Hackathon Target
- Primary event: Backblaze Generative Media Hackathon.
- Product: ProofFrame, a provenance-first generative media vault that uses Genblaze-compatible generation and Backblaze B2-compatible storage.
- Winning angle: production-grade media operations, storage/provenance depth, and a demo that feels useful beyond the hackathon.

## Agent Bus
- Team id: `proofframe-hackathon-58c62c50`.
- Controller session: `019f075b-d44b-7f12-9460-1782719ecbaa`.
- Roles:
  - `planner`: roadmap, scope, task ledger, submission evidence.
  - `scout`: rules, competitors, deadlines, judging risks.
  - `executor`: bounded implementation.
  - `tester`: verification, browser smoke, Docker and release gates.
  - `reviewer`: claims, secrets, compliance, award readiness.
- Durable Bus storage is not enough. For live role work, visible Codex delivery or a subagent id must also be recorded.

## Product Constraints
- MVP must run locally without paid credentials using deterministic mock generation and local file storage.
- B2/Genblaze integration must be real, optional, and fail closed when credentials are absent.
- Every generated asset must have a manifest with prompt, provider, model, checksum, storage pointer, approval state, and license/risk note.
- Keep the demo focused on one creator workflow, not a generic image generator.

## Task Ledger
- Canonical machine-readable task file: `tasks.json`.
- Human overview: `docs/todo.md`.
- Query and mark tasks with:

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py done T001
python3 scripts/task.py block T010 --note "Needs Backblaze account"
```

