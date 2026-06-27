# ProofFrame Task Board

Use `tasks.json` as the source of truth and `scripts/task.py` for machine-readable updates.

## Commands

```bash
python3 scripts/task.py list
python3 scripts/task.py list --status todo
python3 scripts/task.py search B2
python3 scripts/task.py search Devpost
python3 scripts/task.py show T001
python3 scripts/task.py add T099 "Record final demo" --phase "P4 Submit" --owner controller --after T041
python3 scripts/task.py done T001
python3 scripts/task.py doing T020 --note "Live B2 proof in progress"
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

1. Complete live Backblaze B2 upload proof for one asset and one manifest.
2. Complete live Genblaze-backed generation proof and capture provider/model metadata.
3. Run the final secret scan and final audit after live proof evidence exists.
4. Record the demo video using `docs/demo_script.md`.
5. Keep public claims frozen with `docs/public_claim_freeze.md` until real B2 and Genblaze evidence exists.
