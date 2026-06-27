#!/usr/bin/env python3
"""Build copy-ready Devpost submission packets from the current safe draft."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "devpost-submission-packet.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "devpost-submission-packet.md"
DEFAULT_TASKS = ROOT / "tasks.json"


BASE_PACKET = {
    "project_name": "ProofFrame",
    "tagline": "A provenance-first vault for generated media.",
    "one_liner": (
        "ProofFrame turns generated media into reviewable evidence packets with prompts, "
        "provider/model metadata, storage references, hashes, approval state, and a "
        "downloadable manifest bundle."
    ),
    "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
    "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
    "video_url": "TBD after final B2 and Genblaze proof.",
    "inspiration": (
        "Generated media is easy to make and hard to govern. Teams often lose the prompt, "
        "model, provider, approval status, and durable storage evidence for the files that "
        "eventually ship. ProofFrame treats provenance as the product, not a footer."
    ),
    "what_it_does": [
        "Create a campaign brief.",
        "Generate candidate media assets.",
        "Review, approve, or reject assets.",
        "Search and filter evidence by prompt, model, storage key, checksum, and status.",
        "Track decision coverage across approved, draft, and rejected assets.",
        "Inspect prompt, provider, model, storage backend, storage key, checksum, and risk note.",
        "Copy a safe evidence summary without credentials, cookies, signed URLs, or raw secrets.",
        "Export a manifest.",
        "Download an evidence ZIP containing the manifest, README, and available media.",
        "Use Judge Demo to create a complete local packet instantly.",
    ],
    "how_we_built_it": (
        "ProofFrame uses FastAPI for the API, a single-file browser UI for the proof ledger, "
        "local storage for credential-free demos, a Backblaze B2-compatible S3 storage "
        "backend, and a Genblaze/GMICloud provider adapter built around the official "
        "Genblaze Pipeline API. The public mock demo is deployed as a Hugging Face Space for "
        "judge-friendly product inspection while the final sponsor-backed proof remains gated."
    ),
    "challenges": (
        "The biggest challenge is avoiding shallow sponsor integration. ProofFrame has to "
        "make storage and provenance central: B2 should be the durable evidence layer, and "
        "Genblaze should be the generation orchestration path. Another challenge is public "
        "claim hygiene, so the repo separates local demo behavior from final live sponsor proof."
    ),
    "what_we_learned": (
        "The useful unit for generated media teams is not a single image. It is a packet: "
        "asset, prompt, provider, model, storage object, checksum, approval state, and risk note."
    ),
    "accomplishments": [
        "Built a working local product, not just a pitch.",
        "Deployed a credential-free public mock demo.",
        "Added a one-click Judge Demo path.",
        "Added a review console with evidence search, status filtering, decision coverage, and safe summary copy.",
        "Added downloadable evidence ZIPs.",
        "Added B2-compatible storage and Genblaze/GMICloud provider code paths.",
        "Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.",
        "Added fail-closed gates for evidence JSON exports and final submission audits.",
        "Kept public claims gated until live sponsor proof exists.",
    ],
    "whats_next": [
        "Live B2 proof with a dedicated bucket and least-privilege key.",
        "Live Genblaze proof with provider/model/run metadata.",
        "Demo video under the event limit.",
        "Final Devpost submission.",
    ],
    "current_providers_and_models": [
        {"provider": "mock", "model": "mock-svg-v1", "status": "current public mock demo"},
    ],
    "final_provider_and_model": {
        "provider": "genblaze/gmicloud-image",
        "model": "GENBLAZE_IMAGE_MODEL value used for the verified run",
        "status": "final gate after T021",
    },
}


SAFE_BEFORE_LIVE = {
    "mode": "pre_live_safe",
    "short_description": (
        "ProofFrame is a review desk for generated media. The local demo creates a campaign, "
        "generates mock variants, approves or rejects assets, exports a manifest, and downloads "
        "an evidence ZIP with prompts, provider/model fields, storage references, hashes, and "
        "approval status. The final hackathon submission gate is to verify the same flow with "
        "Genblaze-backed generation and Backblaze B2-backed storage."
    ),
    "b2_usage": (
        "ProofFrame treats Backblaze B2 as the final durable evidence layer, not as a late "
        "file-upload checkbox. The public demo currently runs in local/mock mode, but every "
        "asset packet already carries the B2-ready object model: storage backend, storage key, "
        "checksum, byte size, prompt, provider/model metadata, approval state, and risk note. "
        "The repo includes a dedicated B2 S3-compatible storage adapter, a recorded private B2 "
        "bucket setup, and a one-command B2 proof runner that will upload one generated asset "
        "and one manifest with environment-only credentials. That live upload remains the final "
        "submission gate before any public claim is upgraded to completed B2 storage."
    ),
    "genblaze_usage": (
        "ProofFrame includes a Genblaze/GMICloud provider adapter built around the official "
        "Genblaze Pipeline API. In the public mock demo, deterministic generation keeps the "
        "workflow inspectable without secrets; the same manifest fields are reserved for the "
        "final provider, model, request/run metadata, prompt, and asset checksum. The final "
        "submission gate is a live Genblaze-compatible run that proves the provider path and "
        "then carries the resulting asset into the ProofFrame review and storage packet."
    ),
    "claim_warning": "Safe for public mock demo only. Do not submit as final sponsor proof.",
}


SAFE_AFTER_LIVE = {
    "mode": "post_live_verified",
    "short_description": (
        "ProofFrame turns Genblaze-generated media into Backblaze B2-backed evidence packets. "
        "Each packet includes prompt history, provider/model metadata, B2 storage references, "
        "checksums, approval state, and a downloadable manifest bundle so teams can trust, reuse, "
        "or retire generated media."
    ),
    "b2_usage": (
        "ProofFrame stores generated media and exported manifests in Backblaze B2 using "
        "environment-only credentials. Each manifest records sanitized storage keys, byte sizes, "
        "and checksums."
    ),
    "genblaze_usage": (
        "ProofFrame generates media through Genblaze/GMICloud, records provider/model/run "
        "metadata, and carries the resulting asset into the ProofFrame storage and approval manifest."
    ),
    "claim_warning": "Use only after T020 and T021 are verified by live proof evidence.",
}


def load_task_statuses(tasks_path: Path = DEFAULT_TASKS) -> dict[str, str]:
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))["tasks"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return {}
    return {str(task.get("id", "")).upper(): str(task.get("status", "missing")) for task in tasks}


def checklist_item(
    task_statuses: dict[str, str], task: str, label: str, *, required_for_final: bool = True
) -> dict[str, Any]:
    task = task.upper()
    return {
        "task": task,
        "label": label,
        "status": task_statuses.get(task, "missing"),
        "required_for_final": required_for_final,
    }


def build_packet(*, live: bool = False, tasks_path: Path = DEFAULT_TASKS) -> dict[str, Any]:
    packet = dict(BASE_PACKET)
    packet.update(SAFE_AFTER_LIVE if live else SAFE_BEFORE_LIVE)
    task_statuses = load_task_statuses(tasks_path)
    packet["submission_checklist"] = [
        checklist_item(task_statuses, "T020", "B2 live proof complete"),
        checklist_item(task_statuses, "T021", "Genblaze live proof complete"),
        checklist_item(task_statuses, "T040", "Devpost registration complete"),
        checklist_item(task_statuses, "T041", "Final submission audit complete"),
        checklist_item(task_statuses, "T041A", "Final secret scan complete"),
        checklist_item(task_statuses, "T042", "Devpost project submitted"),
    ]
    return packet


def markdown_section(title: str, body: str | list[str]) -> str:
    if isinstance(body, list):
        content = "\n".join(f"- {item}" for item in body)
    else:
        content = body
    return f"## {title}\n\n{content}\n"


def render_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Devpost Submission Packet",
        "",
        f"Mode: `{packet['mode']}`",
        f"Claim warning: {packet['claim_warning']}",
        "",
        markdown_section("Project Name", packet["project_name"]),
        markdown_section("Tagline", packet["tagline"]),
        markdown_section("One-Liner", packet["one_liner"]),
        markdown_section("Repository", packet["repository_url"]),
        markdown_section("Demo URL", packet["demo_url"]),
        markdown_section("Short Description", packet["short_description"]),
        markdown_section("Inspiration", packet["inspiration"]),
        markdown_section("What It Does", packet["what_it_does"]),
        markdown_section("How We Built It", packet["how_we_built_it"]),
        markdown_section("Backblaze B2 Usage", packet["b2_usage"]),
        markdown_section("Genblaze Usage", packet["genblaze_usage"]),
        markdown_section("Challenges", packet["challenges"]),
        markdown_section("Accomplishments", packet["accomplishments"]),
        markdown_section("What We Learned", packet["what_we_learned"]),
        markdown_section("What's Next", packet["whats_next"]),
        markdown_section(
            "Submission Checklist",
            [
                f"{item['task']} [{item['status']}] {item['label']}"
                for item in packet["submission_checklist"]
            ],
        ),
    ]
    return "\n".join(lines).strip() + "\n"


def write_packet(packet: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(packet), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build copy-ready Devpost submission packets.")
    parser.add_argument("--live", action="store_true", help="Use post-live verified sponsor copy.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    packet = build_packet(live=args.live, tasks_path=args.tasks)
    write_packet(packet, args.json_out, args.markdown_out)
    print(json.dumps({"ok": True, "mode": packet["mode"], "json": str(args.json_out), "markdown": str(args.markdown_out)}, indent=2))


if __name__ == "__main__":
    main()
