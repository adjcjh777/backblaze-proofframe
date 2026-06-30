#!/usr/bin/env python3
"""Create a local final live-proof env file without printing secrets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import getpass
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Callable, Mapping
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".env.final.local"
DEFAULT_B2_SETUP = ROOT / "docs" / "assets" / "b2-live-setup.json"
SAFE_ENV_RE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]+$")
PLACEHOLDERS = {"", "placeholder", "change-me", "changeme", "todo", "tbd", "none", "null", "..."}

NEXT_COMMANDS = [
    "python scripts/live_env_handoff.py --env-file .env.final.local --strict",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --preflight-only",
    "python scripts/run_final_live_proof.py --env-file .env.final.local --evidence-out docs/assets/final-live-proof-evidence.json",
]


@dataclass(frozen=True)
class EnvField:
    name: str
    prompt: str
    default: str = ""
    required: bool = True
    secret: bool = False
    aliases: tuple[str, ...] = ()
    mirror_to: tuple[str, ...] = ()


FIELDS = [
    EnvField("PROOFFRAME_STORAGE_BACKEND", "ProofFrame storage backend", default="b2"),
    EnvField("PROOFFRAME_GENERATION_BACKEND", "ProofFrame generation backend", default="genblaze"),
    EnvField("B2_ENDPOINT_URL", "Backblaze B2 S3 endpoint URL"),
    EnvField("B2_REGION", "Backblaze B2 region", required=False),
    EnvField("B2_BUCKET", "Backblaze B2 bucket name"),
    EnvField("B2_KEY_ID", "Backblaze B2 application key id"),
    EnvField(
        "B2_APPLICATION_KEY",
        "Backblaze B2 application key",
        secret=True,
        aliases=("B2_APP_KEY",),
        mirror_to=("B2_APP_KEY",),
    ),
    EnvField("B2_PUBLIC_BASE_URL", "Optional B2 public base URL", required=False),
    EnvField(
        "GENBLAZE_API_KEY",
        "Genblaze/GMI API key",
        secret=True,
        aliases=("GMI_API_KEY",),
        mirror_to=("GMI_API_KEY",),
    ),
    EnvField("GENBLAZE_IMAGE_MODEL", "Genblaze image model", default="seedream-5.0-lite"),
    EnvField("GENBLAZE_ASPECT_RATIO", "Genblaze aspect ratio", default="16:9", required=False),
    EnvField("GENBLAZE_TIMEOUT_SECONDS", "Genblaze timeout seconds", default="180", required=False),
]


def normalize(value: str | None) -> str:
    return (value or "").strip()


def has_real_value(value: str | None) -> bool:
    normalized = normalize(value).strip('"').strip("'")
    if normalized.lower() in PLACEHOLDERS:
        return False
    if normalized.startswith("<") and normalized.endswith(">"):
        return False
    return bool(normalized)


def env_lookup(field: EnvField, environ: Mapping[str, str]) -> str:
    for name in (field.name, *field.aliases):
        value = normalize(environ.get(name))
        if has_real_value(value):
            return value
    return ""


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        if key:
            values[key] = normalize(value).strip('"').strip("'")
    return values


def default_source(environ: Mapping[str, str], initial_values: Mapping[str, str] | None) -> dict[str, str]:
    values = dict(initial_values or {})
    values.update(environ)
    return values


def prompt_for_field(
    field: EnvField,
    default: str,
    *,
    input_func: Callable[[str], str],
    secret_input: Callable[[str], str],
) -> str:
    if field.secret:
        suffix = " [set; press Enter to keep]" if default else ""
        value = secret_input(f"{field.prompt}{suffix}: ")
        return normalize(value) or default

    suffix = f" [{default}]" if default else ""
    value = input_func(f"{field.prompt}{suffix}: ")
    return normalize(value) or default


def collect_values(
    *,
    from_env: bool,
    environ: Mapping[str, str] | None = None,
    initial_values: Mapping[str, str] | None = None,
    input_func: Callable[[str], str] = input,
    secret_input: Callable[[str], str] = getpass.getpass,
) -> dict[str, str]:
    source = default_source(os.environ if environ is None else environ, initial_values)
    values: dict[str, str] = {}
    missing: list[str] = []

    for field in FIELDS:
        default = env_lookup(field, source) or field.default
        value = default if from_env else prompt_for_field(
            field,
            default,
            input_func=input_func,
            secret_input=secret_input,
        )
        if field.required and not value:
            missing.append(field.name)
            continue
        if value:
            values[field.name] = value
            for mirror_name in field.mirror_to:
                values[mirror_name] = value

    if missing:
        raise ValueError("Missing required final env values: " + ", ".join(missing))
    return values


def missing_required_fields(values: Mapping[str, str]) -> list[EnvField]:
    missing: list[EnvField] = []
    for field in FIELDS:
        if field.required and not env_lookup(field, values):
            missing.append(field)
    return missing


def collect_missing_values(
    *,
    initial_values: Mapping[str, str],
    environ: Mapping[str, str] | None = None,
    input_func: Callable[[str], str] = input,
    secret_input: Callable[[str], str] = getpass.getpass,
) -> tuple[dict[str, str], list[str]]:
    values = dict(initial_values)
    for field in missing_required_fields(values):
        env_value = env_lookup(field, environ or {})
        if env_value:
            values[field.name] = env_value
            for mirror_name in field.mirror_to:
                values[mirror_name] = env_value
    filled_names: list[str] = []

    for field in missing_required_fields(values):
        default = field.default
        value = prompt_for_field(
            field,
            default,
            input_func=input_func,
            secret_input=secret_input,
        )
        if not value:
            continue
        values[field.name] = value
        filled_names.append(field.name)
        for mirror_name in field.mirror_to:
            values[mirror_name] = value
            filled_names.append(mirror_name)

    still_missing = [field.name for field in missing_required_fields(values)]
    if still_missing:
        raise ValueError("Missing required final env values: " + ", ".join(still_missing))
    return values, filled_names


def load_b2_setup(path: Path = DEFAULT_B2_SETUP) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    if not data.get("safe_to_commit"):
        return {}
    endpoint = normalize(str(data.get("endpoint", "")))
    return {
        "PROOFFRAME_STORAGE_BACKEND": "b2",
        "B2_ENDPOINT_URL": endpoint,
        "B2_REGION": region_from_b2_endpoint(endpoint),
        "B2_BUCKET": normalize(str(data.get("bucket_name", ""))),
    }


def region_from_b2_endpoint(endpoint_url: str) -> str:
    if not endpoint_url:
        return ""
    parsed = urlparse(endpoint_url if "://" in endpoint_url else f"https://{endpoint_url}")
    host = parsed.netloc or parsed.path
    match = re.match(r"^s3[.-]([a-z0-9-]+)\.backblazeb2\.com$", host)
    return match.group(1) if match else ""


def non_secret_prefill_values(*, b2_setup_path: Path = DEFAULT_B2_SETUP) -> dict[str, str]:
    values = {
        "PROOFFRAME_STORAGE_BACKEND": "b2",
        "PROOFFRAME_GENERATION_BACKEND": "genblaze",
        "GENBLAZE_IMAGE_MODEL": "seedream-5.0-lite",
        "GENBLAZE_ASPECT_RATIO": "16:9",
        "GENBLAZE_TIMEOUT_SECONDS": "180",
    }
    values.update({key: value for key, value in load_b2_setup(b2_setup_path).items() if value})
    return values


def quote_env_value(value: str) -> str:
    if SAFE_ENV_RE.fullmatch(value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def ordered_names() -> list[str]:
    names: list[str] = []
    for field in FIELDS:
        names.append(field.name)
        names.extend(field.mirror_to)
    return names


def render_env_file(values: Mapping[str, str]) -> str:
    lines = [
        "# Generated by scripts/final_env_wizard.py.",
        "# Local secret file for final live proof. Do not commit.",
        "",
    ]
    for name in ordered_names():
        value = values.get(name, "")
        lines.append(f"{name}={quote_env_value(value)}")
    return "\n".join(lines) + "\n"


def render_env_file_preserving_extra(values: Mapping[str, str]) -> str:
    rendered_names = set(ordered_names())
    content = render_env_file(values).rstrip("\n")
    extra_lines = [
        f"{name}={quote_env_value(value)}"
        for name, value in values.items()
        if name not in rendered_names
    ]
    if extra_lines:
        content = "\n".join([content, "", "# Preserved local-only values.", *extra_lines])
    return content + "\n"


def path_for_git(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def fallback_gitignore_check(root: Path, path: Path) -> bool:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return False
    name = path.name
    ignored_by_env_glob = False
    explicitly_unignored = False
    for raw_line in gitignore.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == ".env.*" and name.startswith(".env."):
            ignored_by_env_glob = True
        if line.startswith("!") and line.removeprefix("!") == name:
            explicitly_unignored = True
    return ignored_by_env_glob and not explicitly_unignored


def target_is_git_ignored(root: Path, path: Path) -> bool:
    relative = path_for_git(root, path)
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", relative],
            cwd=root,
            check=False,
        )
    except FileNotFoundError:
        return fallback_gitignore_check(root, path)
    if completed.returncode == 0:
        return True
    return fallback_gitignore_check(root, path)


def build_check(root: Path = ROOT, output: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    output = output.resolve()
    ignored = target_is_git_ignored(root, output)
    env_file_present = output.exists()
    values = parse_env_file(output) if env_file_present else {}
    missing_required_names = [
        field.name for field in FIELDS if field.required and not env_lookup(field, values)
    ]
    placeholder_names: list[str] = []
    seen_placeholders: set[str] = set()
    for field in FIELDS:
        if not (field.required or field.secret):
            continue
        for name in (field.name, *field.aliases, *field.mirror_to):
            if name in values and not has_real_value(values.get(name)) and name not in seen_placeholders:
                placeholder_names.append(name)
                seen_placeholders.add(name)
    mode = output.stat().st_mode & 0o777 if env_file_present else None
    mode_ok = mode == 0o600 if env_file_present else False
    b2_endpoint = env_lookup(next(field for field in FIELDS if field.name == "B2_ENDPOINT_URL"), values)
    b2_region_value = env_lookup(next(field for field in FIELDS if field.name == "B2_REGION"), values)
    b2_region_derived = region_from_b2_endpoint(b2_endpoint)
    b2_region_ok = bool(b2_region_value or b2_region_derived)
    return {
        "schema": "proofframe.final_env_wizard_check.v1",
        "ok": ignored,
        "output": str(output),
        "git_ignored": ignored,
        "env_file_present": env_file_present,
        "env_file_mode": oct(mode) if mode is not None else None,
        "env_file_mode_ok": mode_ok,
        "required_fields": [field.name for field in FIELDS if field.required],
        "secret_fields": [
            name
            for field in FIELDS
            if field.secret
            for name in (field.name, *field.mirror_to)
        ],
        "present_required_names": [
            field.name for field in FIELDS if field.required and env_lookup(field, values)
        ],
        "missing_required_names": missing_required_names,
        "placeholder_names": placeholder_names,
        "b2_region": {
            "present": bool(b2_region_value),
            "derived_from_endpoint": b2_region_derived,
            "ok": b2_region_ok,
        },
        "ready_for_live_entry": bool(
            ignored and env_file_present and mode_ok and not missing_required_names and b2_region_ok
        ),
        "next_commands": NEXT_COMMANDS,
        "policy": (
            "The wizard writes only to a git-ignored local env file and command output lists "
            "variable names only, never credential values."
        ),
    }


def write_env_file(path: Path, content: str, *, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT
    flags |= os.O_TRUNC if force else os.O_EXCL
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise FileExistsError(
            f"{path} already exists. Pass --force only after confirming it is safe to overwrite."
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    os.chmod(path, 0o600)


def build_success(output: Path, values: Mapping[str, str]) -> dict[str, object]:
    return {
        "ok": True,
        "mode": "final_env_written",
        "output": str(output),
        "chmod": "0600",
        "written_names": [name for name in ordered_names() if name in values],
        "next_commands": NEXT_COMMANDS,
        "secret_policy": "Credential values were written locally and were not printed.",
    }


def build_missing_only_success(
    output: Path,
    values: Mapping[str, str],
    filled_names: list[str],
) -> dict[str, object]:
    return {
        "ok": True,
        "mode": "final_env_missing_values_filled",
        "output": str(output),
        "chmod": "0600",
        "filled_names": filled_names,
        "written_names": [name for name in ordered_names() if name in values],
        "next_commands": NEXT_COMMANDS,
        "secret_policy": "Only missing local values were prompted and written; credential values were not printed.",
    }


def build_prefill_success(output: Path, values: Mapping[str, str]) -> dict[str, object]:
    missing_secret_names = [
        name
        for field in FIELDS
        if field.secret
        for name in (field.name, *field.mirror_to)
        if name not in values
    ]
    missing_required_names = [
        field.name for field in FIELDS if field.required and field.name not in values
    ]
    return {
        "ok": True,
        "mode": "final_env_non_secret_prefilled",
        "output": str(output),
        "chmod": "0600",
        "written_names": [name for name in ordered_names() if name in values],
        "missing_required_names": missing_required_names,
        "missing_secret_names": missing_secret_names,
        "next_commands": [
            "python scripts/final_env_wizard.py --output .env.final.local --missing-only --force",
            *NEXT_COMMANDS,
        ],
        "secret_policy": "Only non-secret values were written. Credential values were not printed or stored.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely create .env.final.local for ProofFrame live proof."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    parser.add_argument(
        "--from-env",
        action="store_true",
        help="Read values from the current process environment instead of interactive prompts.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate the output target is git-ignored without prompting or writing secrets.",
    )
    parser.add_argument(
        "--prefill-non-secret",
        action="store_true",
        help="Write known non-secret B2/default values to the local env file and leave secrets empty.",
    )
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="Prompt only for missing required values, preserving existing local values.",
    )
    parser.add_argument("--b2-setup", type=Path, default=DEFAULT_B2_SETUP)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    check = build_check(ROOT, args.output)
    if args.check_only:
        print(json.dumps(check, indent=2))
        raise SystemExit(0 if check["ok"] else 2)
    if not check["ok"]:
        print(json.dumps(check, indent=2))
        raise SystemExit(2)
    if args.prefill_non_secret:
        values = non_secret_prefill_values(b2_setup_path=args.b2_setup)
        try:
            write_env_file(args.output, render_env_file(values), force=args.force)
        except FileExistsError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
            raise SystemExit(2) from exc
        print(json.dumps(build_prefill_success(args.output, values), indent=2))
        raise SystemExit(0)

    try:
        initial_values = parse_env_file(args.output) if args.output.exists() else {}
        if args.missing_only:
            values, filled_names = collect_missing_values(
                initial_values=initial_values,
                environ=os.environ if args.from_env else None,
            )
            write_env_file(args.output, render_env_file_preserving_extra(values), force=args.force)
            print(json.dumps(build_missing_only_success(args.output, values, filled_names), indent=2))
            raise SystemExit(0)
        values = collect_values(from_env=args.from_env, initial_values=initial_values)
        write_env_file(args.output, render_env_file(values), force=args.force)
    except (FileExistsError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(build_success(args.output, values), indent=2))


if __name__ == "__main__":
    main()
