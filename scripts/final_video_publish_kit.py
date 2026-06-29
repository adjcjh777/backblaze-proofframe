#!/usr/bin/env python3
"""Build a public-safe final video publishing kit for Devpost submission."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.final_video_publish_kit.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "final-video-publish-kit.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "final-video-publish-kit.md"
PUBLIC_DEMO_URL = "https://adjcjh-backblaze-proofframe.hf.space/?judge=1"
REPOSITORY_URL = "https://github.com/adjcjh777/backblaze-proofframe"
ALLOWED_HOSTS = ["YouTube", "Vimeo", "Youku"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def source_summary(root: Path, relative_path: str, schema: str) -> dict[str, Any]:
    data = load_json(root / relative_path)
    return {
        "path": relative_path,
        "present": bool(data),
        "schema": data.get("schema"),
        "schema_ok": data.get("schema") == schema,
        "mode": data.get("mode"),
        "ok": data.get("ok"),
        "safe_to_submit": data.get("safe_to_submit"),
    }


def build_chapters(storyboard: dict[str, Any]) -> list[dict[str, Any]]:
    shots = storyboard.get("shots")
    if not isinstance(shots, list) or not shots:
        shots = [
            {"id": "opening", "title": "ProofFrame judge-mode slate", "seconds": 20},
            {"id": "workflow", "title": "Generate and review a provenance packet", "seconds": 55},
            {"id": "evidence", "title": "Manifest, checksum, storage route, and evidence ZIP", "seconds": 35},
            {"id": "gates", "title": "Final B2, Genblaze, video, and audit gates", "seconds": 25},
        ]
    chapters: list[dict[str, Any]] = []
    cursor = 0
    for shot in shots:
        if not isinstance(shot, dict):
            continue
        seconds = int(shot.get("seconds") or shot.get("duration_seconds") or 0)
        title = str(shot.get("title") or shot.get("screen") or shot.get("id") or "ProofFrame section")
        chapters.append(
            {
                "timecode": f"{cursor // 60}:{cursor % 60:02d}",
                "title": title,
                "duration_seconds": seconds,
            }
        )
        cursor += max(0, seconds)
    return chapters


def description_text(*, public_demo_url: str, repository_url: str, claim_boundary: str) -> str:
    return "\n".join(
        [
            "ProofFrame is a provenance-first media operations desk for generated campaign assets.",
            "",
            "This demo walks through one creator workflow: open the judge-mode demo, create a media packet, inspect prompt/provider/model/storage/checksum metadata, approve an asset, and download the evidence ZIP.",
            "",
            f"Public demo: {public_demo_url}",
            f"Repository: {repository_url}",
            "",
            "What to look for:",
            "- Generated media is reviewed as an evidence packet, not a loose image.",
            "- Prompt, provider/model metadata, storage pointer, checksum, approval state, and risk note stay together.",
            "- Optional Backblaze B2 and Genblaze paths are implemented and fail closed until live proof is captured.",
            "",
            f"Claim boundary: {claim_boundary}",
        ]
    )


def build_upload_checklist(public_video_check: dict[str, Any]) -> list[dict[str, Any]]:
    url_analysis = public_video_check.get("url_analysis") or {}
    return [
        {
            "id": "host_family",
            "label": "Upload to an official public video host",
            "ok": bool(url_analysis.get("official_host")),
            "detail": "Allowed host families: YouTube, Vimeo, or Youku.",
        },
        {
            "id": "public_visibility",
            "label": "Use public or unlisted visibility that Devpost judges can access",
            "ok": bool(public_video_check.get("safe_to_submit")),
            "detail": "The final URL must be reachable without login, cookies, tokens, or signed query parameters.",
        },
        {
            "id": "duration",
            "label": "Keep the final video under the event time limit",
            "ok": True,
            "detail": "Use the generated storyboard and chapter plan; rerun public_video_check after upload.",
        },
        {
            "id": "devpost_field",
            "label": "Paste the final video URL into Devpost",
            "ok": bool(public_video_check.get("safe_to_submit")),
            "detail": "After upload, set PROOFFRAME_PUBLIC_VIDEO_URL and regenerate final reports.",
        },
    ]


def source_is_final_ready(source: dict[str, Any]) -> bool:
    return bool(source["schema_ok"] and source.get("ok") is True and source.get("safe_to_submit") is True)


def final_control_is_ready(source: dict[str, Any]) -> bool:
    return bool(source["schema_ok"] and source.get("ok") is True and source.get("safe_to_submit") is True)


def build_kit(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    packet = load_json(root / "docs" / "assets" / "devpost-submission-packet.json")
    storyboard = load_json(root / "docs" / "assets" / "demo-storyboard.json")
    draft = load_json(root / "docs" / "assets" / "demo-video-draft.json")
    public_video_check = load_json(root / "docs" / "assets" / "public-video-check.json")
    evidence_index = load_json(root / "docs" / "assets" / "judge-evidence-index.json")
    title = "ProofFrame: Provenance-first generated media vault"
    claim_boundary = (
        "Use this title and description for final upload only after live B2 and Genblaze proof are recorded; "
        "until then, the public demo remains local/mock and safe_to_submit=false."
    )
    sources = {
        "storyboard": source_summary(root, "docs/assets/demo-storyboard.json", "proofframe.demo_storyboard.v1"),
        "draft_video": source_summary(root, "docs/assets/demo-video-draft.json", "proofframe.demo_video_draft.v1"),
        "public_video_check": source_summary(root, "docs/assets/public-video-check.json", "proofframe.public_video_check.v1"),
        "final_control": source_summary(root, "docs/assets/final-submission-control.json", "proofframe.final_submission_control.v1"),
        "evidence_index": source_summary(root, "docs/assets/judge-evidence-index.json", "proofframe.judge_evidence_index.v1"),
    }
    ok = all(source["schema_ok"] for source in sources.values()) and bool(evidence_index.get("ok"))
    video_ready = source_is_final_ready(sources["public_video_check"])
    control_ready = final_control_is_ready(sources["final_control"])
    safe_to_submit = bool(ok and video_ready and control_ready)
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "ok": ok,
        "mode": "public_video_ready" if video_ready else "ready_for_final_upload",
        "safe_to_share": ok,
        "safe_to_submit": safe_to_submit,
        "final_video_ready": video_ready,
        "allowed_hosts": ALLOWED_HOSTS,
        "video_url": public_video_check.get("video_url") or packet.get("video_url"),
        "title": title,
        "description": description_text(
            public_demo_url=packet.get("demo_url") or PUBLIC_DEMO_URL,
            repository_url=packet.get("repository_url") or REPOSITORY_URL,
            claim_boundary=claim_boundary,
        ),
        "chapters": build_chapters(storyboard),
        "devpost_field": {
            "field_id": "video_url",
            "value": public_video_check.get("video_url") if video_ready else "TBD after final upload.",
            "ready": video_ready,
            "source": "docs/assets/public-video-check.json",
        },
        "upload_checklist": build_upload_checklist(public_video_check),
        "source_reports": sources,
        "draft_video": {
            "path": draft.get("video_path"),
            "public_url": draft.get("public_video_draft_url"),
            "safe_to_submit": draft.get("safe_to_submit"),
            "final_video_ready": draft.get("final_video_ready"),
        },
        "evidence_index_url": (
            "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/raw/main/"
            "docs/assets/judge-evidence-index.md"
        ),
        "claim_boundary": claim_boundary,
        "next_actions": [
            "Record the final narrated video after live B2 and Genblaze proof is visible.",
            "Upload to YouTube, Vimeo, or Youku with public or unlisted judge-accessible visibility.",
            "Set PROOFFRAME_PUBLIC_VIDEO_URL to the final URL and run scripts/public_video_check.py --verify-url --strict-final.",
            "Regenerate Devpost form kit, final control, submission audit, preview, and bundle before submit.",
        ],
    }


def render_markdown(kit: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Final Video Publish Kit",
        "",
        f"Mode: `{kit['mode']}`",
        f"OK: `{str(kit['ok']).lower()}`",
        f"Safe to submit: `{str(kit['safe_to_submit']).lower()}`",
        f"Final video ready: `{str(kit['final_video_ready']).lower()}`",
        f"Created: `{kit['created_at']}`",
        "",
        "## Upload Copy",
        "",
        f"Title: {kit['title']}",
        "",
        "Description:",
        "",
        "```text",
        kit["description"],
        "```",
        "",
        "## Chapters",
        "",
    ]
    lines.extend(
        f"- `{chapter['timecode']}` {chapter['title']} ({chapter['duration_seconds']}s)"
        for chapter in kit["chapters"]
    )
    lines.extend(["", "## Upload Checklist", ""])
    for item in kit["upload_checklist"]:
        status = "OK" if item["ok"] else "PENDING"
        lines.append(f"- {status} `{item['id']}`: {item['label']} - {item['detail']}")
    lines.extend(
        [
            "",
            "## Devpost Field",
            "",
            f"- Field: `{kit['devpost_field']['field_id']}`",
            f"- Ready: `{str(kit['devpost_field']['ready']).lower()}`",
            f"- Value: `{kit['devpost_field']['value']}`",
            "",
            "## Claim Boundary",
            "",
            kit["claim_boundary"],
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in kit["next_actions"])
    lines.append("")
    return "\n".join(lines)


def write_outputs(kit: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(kit, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(kit), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ProofFrame final video publishing kit.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--strict-final", action="store_true", help="Fail unless the final video URL is ready.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    kit = build_kit(args.root)
    write_outputs(kit, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": kit["safe_to_submit"] if args.strict_final else kit["ok"],
                "mode": kit["mode"],
                "safe_to_submit": kit["safe_to_submit"],
                "final_video_ready": kit["final_video_ready"],
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
            },
            indent=2,
        )
    )
    if args.strict_final and not kit["safe_to_submit"]:
        raise SystemExit(2)
    if not kit["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
