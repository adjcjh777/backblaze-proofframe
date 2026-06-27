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


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".env.final.local"
DEFAULT_B2_SETUP = ROOT / "docs" / "assets" / "b2-live-setup.json"
SAFE_ENV_RE = re.compile(r"^[A-Za-z0-9_./:@%+=,-]+$")

NEXT_COMMANDS = [
    "set -a; source .env.final.local; set +a",
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
    EnvField("B2_BUCKET", "Backblaze B2 bucket name"),
    EnvField("B2_KEY_ID", "Backblaze B2 application key id"),
    EnvField("B2_APPLICATION_KEY", "Backblaze B2 application key", secret=True),
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


def env_lookup(field: EnvField, environ: Mapping[str, str]) -> str:
    for name in (field.name, *field.aliases):
        value = normalize(environ.get(name))
        if value:
            return value
    return ""


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
    input_func: Callable[[str], str] = input,
    secret_input: Callable[[str], str] = getpass.getpass,
) -> dict[str, str]:
    source = os.environ if environ is None else environ
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


def load_b2_setup(path: Path = DEFAULT_B2_SETUP) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    if not data.get("safe_to_commit"):
        return {}
    return {
        "PROOFFRAME_STORAGE_BACKEND": "b2",
        "B2_ENDPOINT_URL": normalize(str(data.get("endpoint", ""))),
        "B2_BUCKET": normalize(str(data.get("bucket_name", ""))),
    }


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
    return {
        "schema": "proofframe.final_env_wizard_check.v1",
        "ok": ignored,
        "output": str(output),
        "git_ignored": ignored,
        "required_fields": [field.name for field in FIELDS if field.required],
        "secret_fields": [
            name
            for field in FIELDS
            if field.secret
            for name in (field.name, *field.mirror_to)
        ],
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
            "python scripts/final_env_wizard.py --output .env.final.local --force",
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
        values = collect_values(from_env=args.from_env)
        write_env_file(args.output, render_env_file(values), force=args.force)
    except (FileExistsError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(build_success(args.output, values), indent=2))


if __name__ == "__main__":
    main()
