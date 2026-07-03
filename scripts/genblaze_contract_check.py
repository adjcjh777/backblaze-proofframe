#!/usr/bin/env python3
"""Verify the local Genblaze/B2 SDK contract before live credentials are entered."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "genblaze-contract-report.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "genblaze-contract-report.md"
SCHEMA = "proofframe.genblaze_contract_check.v1"

MODULE_SYMBOLS = {
    "genblaze_core": ["KeyStrategy", "Modality", "ObjectStorageSink", "Pipeline"],
    "genblaze_gmicloud": ["GMICloudImageProvider"],
    "genblaze_openai": ["DalleProvider"],
    "genblaze_s3": ["S3StorageBackend"],
}
PACKAGE_DISTS = {
    "genblaze_core": "genblaze-core",
    "genblaze_gmicloud": "genblaze-gmicloud",
    "genblaze_openai": "genblaze-openai",
    "genblaze_s3": "genblaze-s3",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check_item(
    check_id: str,
    label: str,
    ok: bool,
    detail: str,
    remediation: str = "",
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "ok": ok,
        "detail": detail,
        "remediation": "" if ok else remediation,
    }


def package_version(dist_name: str) -> str | None:
    try:
        return importlib.metadata.version(dist_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def param_names(callable_obj: Callable[..., Any]) -> set[str]:
    return set(inspect.signature(callable_obj).parameters)


def has_params(callable_obj: Callable[..., Any], expected: set[str]) -> tuple[bool, set[str]]:
    names = param_names(callable_obj)
    return expected <= names, expected - names


def accepts_param_or_kwargs(callable_obj: Callable[..., Any] | None, param_name: str) -> bool:
    if callable_obj is None:
        return False
    signature = inspect.signature(callable_obj)
    if param_name in signature.parameters:
        return True
    return any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values())


def signature_check(
    checks: list[dict[str, Any]],
    *,
    check_id: str,
    label: str,
    callable_obj: Callable[..., Any] | None,
    expected: set[str],
) -> None:
    if callable_obj is None:
        checks.append(
            check_item(
                check_id,
                label,
                False,
                "Callable is unavailable because an earlier import check failed.",
                "Install integrations with `pip install -e '.[integrations]'`.",
            )
        )
        return
    ok, missing = has_params(callable_obj, expected)
    checks.append(
        check_item(
            check_id,
            label,
            ok,
            (
                f"Required params: {sorted(expected)}; "
                f"observed params: {sorted(param_names(callable_obj))}."
            ),
            "Update the ProofFrame adapter or pin compatible Genblaze package versions.",
        )
    )
    if missing:
        checks[-1]["missing_params"] = sorted(missing)


def import_symbols(
    checks: list[dict[str, Any]],
    *,
    importer: Callable[[str], Any],
) -> dict[str, Any]:
    symbols: dict[str, Any] = {}
    for module_name, symbol_names in MODULE_SYMBOLS.items():
        try:
            module = importer(module_name)
        except Exception as exc:
            checks.append(
                check_item(
                    f"{module_name}_import",
                    f"{module_name} import",
                    False,
                    f"{module_name} is not importable: {type(exc).__name__}.",
                    "Install integrations with `pip install -e '.[integrations]'`.",
                )
            )
            continue
        checks.append(
            check_item(
                f"{module_name}_import",
                f"{module_name} import",
                True,
                f"{module_name} is importable.",
            )
        )
        for symbol_name in symbol_names:
            key = f"{module_name}.{symbol_name}"
            symbol = getattr(module, symbol_name, None)
            symbols[key] = symbol
            checks.append(
                check_item(
                    f"{module_name}_{symbol_name}",
                    f"{key} symbol",
                    symbol is not None,
                    f"{key} {'is present' if symbol is not None else 'is missing'}.",
                    "Update installed Genblaze packages or ProofFrame adapter imports.",
                )
            )
    return symbols


def build_report(
    *,
    importer: Callable[[str], Any] = importlib.import_module,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    symbols = import_symbols(checks, importer=importer)

    pipeline_cls = symbols.get("genblaze_core.Pipeline")
    gmicloud_provider_cls = symbols.get("genblaze_gmicloud.GMICloudImageProvider")
    openai_provider_cls = symbols.get("genblaze_openai.DalleProvider")
    object_storage_sink_cls = symbols.get("genblaze_core.ObjectStorageSink")
    s3_backend_cls = symbols.get("genblaze_s3.S3StorageBackend")
    key_strategy_cls = symbols.get("genblaze_core.KeyStrategy")

    signature_check(
        checks,
        check_id="gmicloud_image_provider_ctor",
        label="GMICloudImageProvider constructor accepts ProofFrame kwargs",
        callable_obj=gmicloud_provider_cls,
        expected={"api_key", "base_url", "http_timeout"},
    )
    signature_check(
        checks,
        check_id="openai_image_provider_ctor",
        label="DalleProvider constructor accepts ProofFrame kwargs",
        callable_obj=openai_provider_cls,
        expected={"api_key", "http_timeout"},
    )
    signature_check(
        checks,
        check_id="pipeline_ctor",
        label="Pipeline constructor accepts project_id",
        callable_obj=pipeline_cls,
        expected={"project_id"},
    )
    if pipeline_cls is not None:
        observed_methods = {name for name in {"run", "step"} if callable(getattr(pipeline_cls, name, None))}
        checks.append(
            check_item(
                "pipeline_methods_inspectable",
                "Pipeline exposes inspectable step/run methods",
                observed_methods == {"run", "step"},
                f"Required methods: ['run', 'step']; observed: {sorted(observed_methods)}.",
                "Update the ProofFrame adapter or pin a compatible genblaze-core version.",
            )
        )
    signature_check(
        checks,
        check_id="pipeline_step_signature",
        label="Pipeline.step accepts media generation params",
        callable_obj=getattr(pipeline_cls, "step", None),
        expected={"provider", "model", "prompt", "modality"},
    )
    pipeline_step = getattr(pipeline_cls, "step", None)
    checks.append(
        check_item(
            "pipeline_step_aspect_ratio",
            "Pipeline.step accepts aspect_ratio directly or through kwargs",
            accepts_param_or_kwargs(pipeline_step, "aspect_ratio"),
            "Pipeline.step must accept ProofFrame's aspect_ratio generation parameter directly or through **kwargs.",
            "Update the ProofFrame adapter or pin a compatible genblaze-core version.",
        )
    )
    signature_check(
        checks,
        check_id="pipeline_run_signature",
        label="Pipeline.run accepts sink and live-proof controls",
        callable_obj=getattr(pipeline_cls, "run", None),
        expected={"sink", "timeout", "max_retries", "raise_on_failure"},
    )
    signature_check(
        checks,
        check_id="s3_for_backblaze_signature",
        label="S3StorageBackend.for_backblaze accepts B2 credential fields",
        callable_obj=getattr(s3_backend_cls, "for_backblaze", None),
        expected={"bucket", "region", "key_id", "app_key", "public_url_base", "preflight"},
    )
    signature_check(
        checks,
        check_id="object_storage_sink_signature",
        label="ObjectStorageSink accepts ProofFrame sink settings",
        callable_obj=object_storage_sink_cls,
        expected={"backend", "prefix", "key_strategy"},
    )
    if s3_backend_cls is None:
        checks.append(
            check_item(
                "s3_readback_methods",
                "S3 backend exposes private-bucket readback helpers",
                False,
                "S3StorageBackend is unavailable.",
                "Install genblaze-s3.",
            )
        )
    else:
        required_methods = {"close", "get", "key_from_url"}
        observed_methods = {name for name in required_methods if callable(getattr(s3_backend_cls, name, None))}
        checks.append(
            check_item(
                "s3_readback_methods",
                "S3 backend exposes private-bucket readback helpers",
                observed_methods == required_methods,
                f"Required methods: {sorted(required_methods)}; observed: {sorted(observed_methods)}.",
                "Update ProofFrame readback logic or pin a compatible genblaze-s3 version.",
            )
        )
    if key_strategy_cls is None:
        checks.append(
            check_item(
                "key_strategy_hierarchical",
                "KeyStrategy.HIERARCHICAL is available",
                False,
                "KeyStrategy is unavailable.",
                "Install genblaze-core.",
            )
        )
    else:
        checks.append(
            check_item(
                "key_strategy_hierarchical",
                "KeyStrategy.HIERARCHICAL is available",
                hasattr(key_strategy_cls, "HIERARCHICAL"),
                "KeyStrategy exposes HIERARCHICAL for per-campaign Genblaze B2 keys.",
                "Update ProofFrame sink key strategy or pin a compatible genblaze-core version.",
            )
        )

    ok = all(check["ok"] for check in checks)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "sdk_contract_ready" if ok else "sdk_contract_blocked",
        "package_versions": {
            module_name: package_version(dist_name)
            for module_name, dist_name in PACKAGE_DISTS.items()
        },
        "checks": checks,
        "failed_checks": [check["id"] for check in checks if not check["ok"]],
        "secret_policy": (
            "This report reads Python package metadata and callable signatures only. "
            "It does not read environment variables, credential files, provider responses, "
            "Backblaze keys, Genblaze provider keys, cookies, or signed URLs."
        ),
    }


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Genblaze SDK Contract Check",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Created: `{report['created_at']}`",
        "",
        "## Package Versions",
        "",
    ]
    for module_name, version in report["package_versions"].items():
        lines.append(f"- `{module_name}`: `{version or 'missing'}`")
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        status = "OK" if check["ok"] else "FAIL"
        lines.append(f"- {status} `{check['id']}`: {check['detail']}")
        if check.get("remediation"):
            lines.append(f"  Remediation: {check['remediation']}")
    lines.extend(["", "## Secret Policy", "", report["secret_policy"], ""])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the local Genblaze/B2 SDK contract.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = build_report()
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "failed_checks": report["failed_checks"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
