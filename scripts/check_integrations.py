#!/usr/bin/env python3
"""Report integration readiness without printing secrets."""

from __future__ import annotations

import importlib.util
import json

from proofframe.config import Settings


def available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def main() -> None:
    settings = Settings.from_env()
    report = {
        "storage_backend": settings.storage_backend,
        "generation_backend": settings.generation_backend,
        "b2": {
            "configured": bool(
                settings.b2_endpoint_url
                and settings.b2_bucket
                and settings.b2_key_id
                and settings.b2_application_key
            ),
            "has_endpoint": bool(settings.b2_endpoint_url),
            "has_bucket": bool(settings.b2_bucket),
            "has_key_id": bool(settings.b2_key_id),
            "has_application_key": bool(settings.b2_application_key),
            "boto3_available": available("boto3"),
        },
        "genblaze": {
            "configured": bool(
                settings.genblaze_image_model
                and (settings.genblaze_api_key or settings.gmi_api_key)
            ),
            "has_base_url": bool(settings.genblaze_base_url),
            "has_model": bool(settings.genblaze_image_model),
            "has_api_key": bool(settings.genblaze_api_key or settings.gmi_api_key),
            "genblaze_core_available": available("genblaze_core"),
            "genblaze_s3_available": available("genblaze_s3"),
            "genblaze_gmicloud_available": available("genblaze_gmicloud"),
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
