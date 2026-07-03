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
DEFAULT_FINAL_EVIDENCE = ROOT / "docs" / "assets" / "final-live-proof-evidence.json"


BASE_PACKET = {
    "schema": "proofframe.devpost_packet.v1",
    "project_name": "ProofFrame",
    "tagline": "B2-ready provenance desk for GenAI media.",
    "one_liner": (
        "ProofFrame turns generated media into approved evidence packets with B2-ready "
        "manifests, Genblaze-gated provider metadata, checksums, review status, and an "
        "exportable proof bundle."
    ),
    "repository_url": "https://github.com/adjcjh777/backblaze-proofframe",
    "demo_url": "https://adjcjh-backblaze-proofframe.hf.space/?judge=1",
    "video_url": "TBD after final public video upload.",
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
        "backend, and Genblaze provider adapters for GMICloud, OpenAI, and a credential-free "
        "local Pipeline provider built around the official Genblaze Pipeline API. The public "
        "mock demo is deployed as a Hugging Face Space for judge-friendly product inspection "
        "while final reports separate live proof, video, audit, and Devpost receipt gates."
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
        "Added B2-compatible storage and Genblaze provider code paths for GMICloud, OpenAI, and a credential-free local Pipeline provider.",
        "Added CI that runs readiness checks, lint, tests, API smoke, and secret scan.",
        "Added fail-closed gates for evidence JSON exports and final submission audits.",
        "Kept public claims gated by reports, task status, and secret-scan artifacts.",
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
        "provider": "genblaze/<verified-provider>-image",
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
        "ProofFrame includes Genblaze provider adapters for GMICloud, OpenAI, and a credential-free "
        "local Pipeline provider built around the official Genblaze Pipeline API. In the public mock demo, deterministic generation keeps the "
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
        "environment-only credentials. The final proof evidence records sanitized B2 storage keys, "
        "byte sizes, and checksums without exposing credentials or signed URLs. B2 is the durable "
        "evidence layer: the media asset and manifest are separate objects under the ProofFrame "
        "campaign prefix, and the app uses those hashes to make later review, export, and audit "
        "steps reproducible."
    ),
    "genblaze_usage": (
        "ProofFrame generates media through Genblaze's official Pipeline. The final proof uses "
        "the credential-free local image provider, records provider/model metadata, and carries "
        "the resulting asset through Genblaze's B2 sink into the ProofFrame storage and approval manifest."
    ),
    "claim_warning": "Use only after T020 and T021 are verified by live proof evidence.",
    "whats_next": [
        "Upload the final demo video under the event limit.",
        "Run the final secret scan and submission audit after video artifacts are ready.",
        "Submit the Devpost project and preserve the receipt URL.",
    ],
}


def load_task_statuses(tasks_path: Path = DEFAULT_TASKS) -> dict[str, str]:
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))["tasks"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return {}
    return {str(task.get("id", "")).upper(): str(task.get("status", "missing")) for task in tasks}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def apply_final_evidence(packet: dict[str, Any], evidence_path: Path) -> None:
    evidence = load_json(evidence_path)
    if evidence.get("ok") is not True:
        return
    provider = str(evidence.get("asset_provider") or "").strip()
    model = str(evidence.get("asset_model") or "").strip()
    if not (provider and model):
        return
    packet["final_provider_and_model"] = {
        "provider": provider,
        "model": model,
        "status": "verified by docs/assets/final-live-proof-evidence.json",
    }
    packet["current_providers_and_models"] = [
        {"provider": "mock", "model": "mock-svg-v1", "status": "current public mock demo"},
        {"provider": provider, "model": model, "status": "final B2-backed Genblaze proof"},
    ]


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


def usable_video_url(value: str) -> bool:
    text = value.strip()
    return text.startswith(("https://", "http://")) and not text.lower().startswith("tbd")


def build_packet(
    *,
    live: bool = False,
    tasks_path: Path = DEFAULT_TASKS,
    video_url: str | None = None,
    final_evidence_path: Path = DEFAULT_FINAL_EVIDENCE,
) -> dict[str, Any]:
    packet = dict(BASE_PACKET)
    packet.update(SAFE_AFTER_LIVE if live else SAFE_BEFORE_LIVE)
    if live:
        packet["video_url"] = "TBD after final public video upload."
        apply_final_evidence(packet, final_evidence_path)
    if video_url is not None:
        if not usable_video_url(video_url):
            raise ValueError("video_url must be an http(s) URL, not a placeholder.")
        packet["video_url"] = video_url.strip()
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
        markdown_section("Demo Video URL", packet["video_url"]),
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
    parser.add_argument(
        "--post-live",
        action="store_true",
        help="Alias for --live; useful in final operator runbooks.",
    )
    parser.add_argument(
        "--video-url",
        help="Final public demo video URL. Must be an http(s) URL when provided.",
    )
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        packet = build_packet(
            live=args.live or args.post_live,
            tasks_path=args.tasks,
            video_url=args.video_url,
        )
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        raise SystemExit(2) from exc
    write_packet(packet, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": True,
                "mode": packet["mode"],
                "video_url": packet["video_url"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
