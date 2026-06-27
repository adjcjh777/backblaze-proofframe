# ProofFrame Task Board

Use `tasks.json` as the source of truth and `scripts/task.py` for machine-readable updates.

## Commands

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py show T001
python3 scripts/task.py done T001
python3 scripts/task.py block T010 --note "Needs manual Devpost login"
```

## Phases

| Phase | Goal |
| --- | --- |
| P0 Foundation | Pick contest, create repo, write PRD/spec/todo, create team. |
| P1 MVP | Local app, manifest, mock generation, review UI. |
| P2 Integrations | B2 and Genblaze real paths, Docker, evidence. |
| P3 Polish | UI, samples, tests, demo video, public-claim freeze, evidence package. |
| P4 Submit | Devpost registration, final audit, submission. |

## Current Priority

1. Pick a UI direction: Archive Desk, Signal Lab, Proof Ledger, or a remix.
2. Implement `apps/web/index.html` after the direction is chosen.
3. Confirm Devpost registration and Backblaze B2 / Genblaze access.
4. Keep public claims frozen until real B2 and Genblaze evidence exists.
