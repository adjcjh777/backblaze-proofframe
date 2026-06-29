# ProofFrame Secret Scan Report

Mode: `clear`
OK: `true`
Created: `2026-06-29T13:34:26Z`

## Counts

- Scanned text files: `227`
- Inventoried binary files: `6`
- Skipped local secret files: `1`
- Findings: `0`

## Coverage

- Docs/assets text scanned: `true`
- Var/log text scanned: `true`
- Screenshot/media inventory: `true`
- Local secret files excluded without reading: `.env.final.local`

- Text files are scanned for key-like assignments, bearer tokens, signed URL parameters, and GMI-style keys.
- Binary screenshots/media are inventoried by path and size; review visible content before marking final T041A done.
- Local credential files such as .env.final.local are intentionally excluded without reading values.

## Findings

- None

No credential values, matched line text, browser cookies, or signed URLs are printed in this report.
