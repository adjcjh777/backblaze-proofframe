#!/usr/bin/env python3
"""Build a no-secret checklist for the final Backblaze B2 application key."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.b2_key_scope_checklist.v1"
DEFAULT_SETUP = ROOT / "docs" / "assets" / "b2-live-setup.json"
DEFAULT_JSON = ROOT / "docs" / "assets" / "b2-key-scope-checklist.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "b2-key-scope-checklist.md"
PROOFFRAME_B2_PREFIX = "campaigns/"
RECOMMENDED_MAX_DURATION_SECONDS = 7 * 24 * 60 * 60
CONFIRMATION_PHRASE = (
    "I confirm ProofFrame B2 key scope: standard key, bucket "
    "proofframe-demo-a6b4e49, prefix campaigns/, no all-bucket access, "
    "no delete/admin permissions, and no secrets in chat/docs/git."
)
SAFE_PENDING_KEY_STATUSES = {
    "form_prepared_not_created",
    "created_outside_repo",
    "created_not_recorded",
}
SECRET_FIELD_NAMES = {
    "access_token",
    "api_key",
    "application_key",
    "authorization",
    "b2_application_key",
    "cookie",
    "key_id",
    "password",
    "refresh_token",
    "secret",
    "signed_url",
    "token",
}
ALLOWED_SECRET_POLICY_FIELDS = {"secret_policy"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def find_forbidden_secret_fields(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            child_path = f"{path}.{key}"
            if normalized in SECRET_FIELD_NAMES and normalized not in ALLOWED_SECRET_POLICY_FIELDS:
                findings.append(child_path)
                continue
            findings.extend(find_forbidden_secret_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_forbidden_secret_fields(child, f"{path}[{index}]"))
    return findings


def setup_summary(setup: dict[str, Any]) -> dict[str, Any]:
    bucket_name = setup.get("bucket_name") or setup.get("bucket")
    key_name = setup.get("application_key_name") or setup.get("prepared_application_key_name")
    key_status = setup.get("application_key_status")
    checks = [
        {
            "id": "setup_present",
            "ok": bool(setup),
            "detail": "B2 live setup JSON is present and parseable.",
        },
        {
            "id": "schema",
            "ok": setup.get("schema") == "proofframe.b2_live_setup.v1",
            "detail": "Setup record uses the expected schema.",
        },
        {
            "id": "safe_to_commit",
            "ok": setup.get("safe_to_commit") is True,
            "detail": "Setup record declares that it contains no secrets.",
        },
        {
            "id": "private_bucket",
            "ok": setup.get("bucket_type") == "private",
            "detail": "Live proof bucket remains private.",
        },
        {
            "id": "single_bucket_target",
            "ok": bool(bucket_name),
            "detail": "A single target bucket name is recorded.",
        },
        {
            "id": "s3_endpoint",
            "ok": bool(setup.get("endpoint")),
            "detail": "S3-compatible endpoint is recorded.",
        },
        {
            "id": "application_key_name",
            "ok": bool(key_name),
            "detail": "Prepared application key name is recorded.",
        },
        {
            "id": "application_key_status_safe",
            "ok": key_status in SAFE_PENDING_KEY_STATUSES,
            "detail": "The committed setup must not contain created key material.",
        },
    ]
    return {
        "present": bool(setup),
        "schema": setup.get("schema"),
        "status": setup.get("status"),
        "bucket_name": bucket_name,
        "bucket_type": setup.get("bucket_type"),
        "endpoint": setup.get("endpoint"),
        "application_key_name": key_name,
        "application_key_status": key_status,
        "checks": checks,
        "ok": all(check["ok"] for check in checks),
    }


def official_sources() -> list[dict[str, str]]:
    return [
        {
            "label": "Backblaze B2 S3-Compatible App Keys",
            "url": "https://www.backblaze.com/docs/cloud-storage-s3-compatible-app-keys",
            "used_for": "Manual app key requirement, listAllBucketNames compatibility, and S3 capability mapping.",
        },
        {
            "label": "Backblaze Cloud Storage Application Keys",
            "url": "https://www.backblaze.com/docs/cloud-storage-application-keys",
            "used_for": "Standard versus master application key, single-bucket scope, file prefix, and duration controls.",
        },
    ]


def required_capabilities() -> list[dict[str, str]]:
    return [
        {
            "capability": "writeFiles",
            "why": "ProofFrame's B2 backend uploads generated media and manifests with S3 PutObject.",
            "proof_path": "src/proofframe/storage.py:B2StorageBackend.put_bytes",
        },
        {
            "capability": "listAllBucketNames",
            "why": "Backblaze documents this as required for bucket-restricted app keys used with S3 SDKs and integrations.",
            "proof_path": "Backblaze S3-compatible app key documentation",
        },
    ]


def conditional_capabilities() -> list[dict[str, str]]:
    return [
        {
            "capability": "readFiles",
            "allowed_only_if": "A final verification command is changed to perform HeadObject or GetObject against the uploaded proof objects.",
            "required_now": "false",
        },
        {
            "capability": "listFiles",
            "allowed_only_if": "A final verification command is changed to list only the configured ProofFrame prefix.",
            "required_now": "false",
        },
    ]


def forbidden_capabilities() -> list[dict[str, str]]:
    return [
        {
            "capability": "deleteFiles",
            "reason": "The live proof only uploads new media and manifest objects; deletion is unnecessary.",
        },
        {
            "capability": "writeBuckets/deleteBuckets",
            "reason": "The bucket is already created; key must not create, modify, or delete buckets.",
        },
        {
            "capability": "writeBucketLifecycleRules",
            "reason": "Lifecycle policy changes are outside the proof path.",
        },
        {
            "capability": "writeBucketEncryption",
            "reason": "Encryption configuration is not needed for the one-bucket upload proof.",
        },
        {
            "capability": "writeBucketRetentions/writeFileRetentions/bypassGovernance",
            "reason": "Object Lock and governance operations are not part of ProofFrame's proof.",
        },
        {
            "capability": "writeFileLegalHolds",
            "reason": "Legal hold updates are not needed for submission evidence.",
        },
        {
            "capability": "writeBucketReplications/writeBucketNotifications/writeBucketLogging",
            "reason": "Replication, notifications, and logging are admin features outside the live proof.",
        },
    ]


def operator_steps(setup: dict[str, Any]) -> list[str]:
    bucket = setup.get("bucket_name") or "the dedicated ProofFrame B2 bucket"
    key_name = setup.get("application_key_name") or "proofframe-demo-live-proof"
    return [
        "Before creating the key, explicitly confirm the confirmation phrase from this checklist without adding any key values.",
        "Create a standard application key, not a master application key.",
        f"Set the key name to `{key_name}`.",
        f"Limit bucket access to the single bucket `{bucket}`; do not choose all buckets.",
        "Set the file name prefix to `campaigns/` so the key can only write ProofFrame proof objects.",
        "Use Write Only access for the upload proof; add read/list only if a changed verification command explicitly needs it.",
        "Enable `listAllBucketNames` for S3 SDK compatibility with the bucket-restricted key.",
        "Set an expiration no longer than 604800 seconds for the hackathon proof window.",
        "Copy the key id and application key only into `.env.final.local` through `python scripts/final_env_wizard.py --output .env.final.local --missing-only --force`.",
        "Immediately run `python scripts/live_env_handoff.py --env-file .env.final.local --strict` and then the B2 proof runner.",
    ]


def stop_conditions(setup: dict[str, Any]) -> list[str]:
    bucket = setup.get("bucket_name") or "the dedicated ProofFrame B2 bucket"
    return [
        "Stop if the UI asks for or displays a master application key.",
        f"Stop if bucket access cannot be limited to `{bucket}`.",
        "Stop if the file prefix cannot be set to `campaigns/` and ask before widening scope.",
        "Stop if the key requires all-bucket access, bucket write/delete permissions, or deleteFiles.",
        "Stop if a screenshot, recording, terminal, browser address bar, or chat message would expose the key id or application key.",
        "Stop if any key value appears in a commit diff, generated report, or Devpost field.",
    ]


def build_expected_key(setup: dict[str, Any]) -> dict[str, Any]:
    bucket = setup.get("bucket_name") or "missing"
    key_name = setup.get("application_key_name") or "proofframe-demo-live-proof"
    return {
        "key_kind": "standard_application_key",
        "forbidden_key_kind": "master_application_key",
        "key_name": key_name,
        "bucket_scope": {
            "mode": "single_bucket",
            "bucket_name": bucket,
            "forbidden": "all_buckets",
        },
        "file_name_prefix": {
            "value": PROOFFRAME_B2_PREFIX,
            "required": True,
            "matches_uploaded_keys": [
                "campaigns/{campaign_id}/media/{filename}",
                "campaigns/{campaign_id}/manifests/{campaign_id}-manifest.json",
            ],
        },
        "duration": {
            "recommended_max_seconds": RECOMMENDED_MAX_DURATION_SECONDS,
            "reason": "Short-lived proof key for final hackathon verification.",
        },
        "web_ui_access": {
            "preferred": "Write Only",
            "upgrade_to_read_write_only_if": "Final verification is changed to perform HeadObject, GetObject, or ListObjects.",
        },
        "required_capabilities": required_capabilities(),
        "conditional_capabilities": conditional_capabilities(),
        "forbidden_capabilities": forbidden_capabilities(),
    }


def build_report(setup_path: Path = DEFAULT_SETUP) -> dict[str, Any]:
    setup_raw = load_json(setup_path)
    setup = setup_summary(setup_raw)
    forbidden_secret_fields = find_forbidden_secret_fields(setup_raw)
    scope_ready = bool(setup["ok"] and not forbidden_secret_fields)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "mode": "scope_ready_key_not_created" if scope_ready else "scope_blocked",
        "ok": scope_ready,
        "safe_to_commit": not forbidden_secret_fields,
        "requires_user_confirmation_before_key_creation": True,
        "pre_key_creation_confirmation": {
            "status": "required_before_key_creation",
            "required_phrase": CONFIRMATION_PHRASE,
            "why": "The B2 application key is a real credential; ProofFrame must not create or use it from a vague instruction.",
            "safe_to_store": True,
            "forbidden_confirmation_contents": [
                "B2 key id",
                "B2 application key",
                "Backblaze account identifiers",
                "browser cookies",
                "screenshots that show secrets",
            ],
        },
        "setup_path": str(setup_path.relative_to(ROOT) if setup_path.is_relative_to(ROOT) else setup_path),
        "setup": setup,
        "expected_key": build_expected_key(setup),
        "operator_steps": operator_steps(setup),
        "stop_conditions": stop_conditions(setup),
        "secret_policy": {
            "allowed_destination": ".env.final.local via final_env_wizard",
            "forbidden_destinations": [
                "git",
                "docs",
                "chat",
                "screenshots",
                "Devpost fields",
                "browser recordings",
            ],
            "forbidden_setup_fields": forbidden_secret_fields,
        },
        "next_commands_after_key_entry": [
            "python scripts/live_env_handoff.py --env-file .env.final.local --strict",
            "python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json",
        ],
        "official_sources": official_sources(),
    }


def render_markdown(report: dict[str, Any]) -> str:
    setup = report["setup"]
    expected = report["expected_key"]
    lines = [
        "# ProofFrame B2 Key Scope Checklist",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Safe to commit: `{str(report['safe_to_commit']).lower()}`",
        f"Requires user confirmation before key creation: `{str(report['requires_user_confirmation_before_key_creation']).lower()}`",
        "",
        "## Required Pre-Key Confirmation",
        "",
        f"- Status: `{report['pre_key_creation_confirmation']['status']}`",
        f"- Phrase: `{report['pre_key_creation_confirmation']['required_phrase']}`",
        "- Do not include any key id, application key, account identifier, cookie, or screenshot in the confirmation.",
        "",
        "## Target",
        "",
        f"- Bucket: `{setup.get('bucket_name')}`",
        f"- Bucket type: `{setup.get('bucket_type')}`",
        f"- Endpoint: `{setup.get('endpoint')}`",
        f"- Key name: `{expected['key_name']}`",
        f"- Key kind: `{expected['key_kind']}`",
        f"- Forbidden key kind: `{expected['forbidden_key_kind']}`",
        f"- File prefix: `{expected['file_name_prefix']['value']}`",
        f"- Preferred access: `{expected['web_ui_access']['preferred']}`",
        f"- Recommended max duration: `{expected['duration']['recommended_max_seconds']}` seconds",
        "",
        "## Required Capabilities",
        "",
    ]
    lines.extend(
        f"- `{item['capability']}` - {item['why']}" for item in expected["required_capabilities"]
    )
    lines.extend(["", "## Conditional Only", ""])
    lines.extend(
        f"- `{item['capability']}` - {item['allowed_only_if']}"
        for item in expected["conditional_capabilities"]
    )
    lines.extend(["", "## Forbidden", ""])
    lines.extend(
        f"- `{item['capability']}` - {item['reason']}"
        for item in expected["forbidden_capabilities"]
    )
    lines.extend(["", "## Operator Steps", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(report["operator_steps"], start=1))
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend(f"- {item}" for item in report["stop_conditions"])
    lines.extend(["", "## Next Commands After Key Entry", ""])
    lines.extend(f"- `{command}`" for command in report["next_commands_after_key_entry"])
    lines.extend(["", "## Sources", ""])
    lines.extend(
        f"- [{source['label']}]({source['url']}) - {source['used_for']}"
        for source in report["official_sources"]
    )
    lines.append("")
    lines.append("No key id, application key, token, cookie, signed URL, or account secret is stored here.")
    return "\n".join(lines) + "\n"


def write_outputs(
    report: dict[str, Any],
    *,
    json_path: Path = DEFAULT_JSON,
    markdown_path: Path = DEFAULT_MD,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the no-secret Backblaze B2 key scope checklist.")
    parser.add_argument("--setup", type=Path, default=DEFAULT_SETUP)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report(args.setup)
    write_outputs(report, json_path=args.json_out, markdown_path=args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
