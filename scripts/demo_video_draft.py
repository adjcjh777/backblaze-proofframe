#!/usr/bin/env python3
"""Build a public-safe mock demo video draft from committed screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "proofframe.demo_video_draft.v1"
DEFAULT_JSON = ROOT / "docs" / "assets" / "demo-video-draft.json"
DEFAULT_MD = ROOT / "docs" / "assets" / "demo-video-draft.md"
DEFAULT_VIDEO = ROOT / "docs" / "assets" / "proofframe-demo-draft.mp4"
PUBLIC_VIDEO_DRAFT_URL = (
    "https://huggingface.co/spaces/ADJCJH/backblaze-proofframe/resolve/main/"
    "docs/assets/proofframe-demo-draft.mp4"
)
MAX_SECONDS = 180
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

SLIDES = [
    {
        "path": "docs/assets/proofframe-hf-public-smoke.png",
        "seconds": 10,
        "title": "Judge-mode public demo",
    },
    {
        "path": "docs/assets/proofframe-sponsor-model-smoke.png",
        "seconds": 12,
        "title": "Sponsor evidence model",
    },
    {
        "path": "docs/assets/proofframe-local-ui-smoke.png",
        "seconds": 12,
        "title": "Campaign and asset ledger",
    },
    {
        "path": "docs/assets/proofframe-review-console-smoke.png",
        "seconds": 12,
        "title": "Review console",
    },
    {
        "path": "docs/assets/proofframe-sponsor-model-mobile-smoke.png",
        "seconds": 8,
        "title": "Mobile-safe judge proof",
    },
]


ProbeFn = Callable[[Path], dict[str, Any]]


def slide_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for slide in SLIDES:
        path = root / slide["path"]
        records.append(
            {
                "path": slide["path"],
                "title": slide["title"],
                "seconds": slide["seconds"],
                "present": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return records


def total_seconds() -> int:
    return sum(int(slide["seconds"]) for slide in SLIDES)


def shell_quote_for_concat(path: Path) -> str:
    return str(path).replace("'", "'\\''")


def build_concat_file(root: Path, concat_path: Path) -> None:
    lines: list[str] = []
    for slide in SLIDES:
        image_path = (root / slide["path"]).resolve()
        lines.append(f"file '{shell_quote_for_concat(image_path)}'")
        lines.append(f"duration {int(slide['seconds'])}")
    last_image = (root / SLIDES[-1]["path"]).resolve()
    lines.append(f"file '{shell_quote_for_concat(last_image)}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_video(root: Path, output: Path, *, ffmpeg_bin: str | None = None) -> dict[str, Any]:
    ffmpeg = ffmpeg_bin or shutil.which("ffmpeg")
    if not ffmpeg:
        return {"ok": False, "error": "ffmpeg_not_found", "command": None}

    missing = [slide["path"] for slide in slide_records(root) if not slide["present"]]
    if missing:
        return {"ok": False, "error": "missing_slides", "missing": missing, "command": None}

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="proofframe-video-") as tmp_dir:
        concat_path = Path(tmp_dir) / "slides.txt"
        build_concat_file(root, concat_path)
        vf = (
            f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x171714,"
            "format=yuv420p"
        )
        command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vf",
            vf,
            "-r",
            "30",
            "-movflags",
            "+faststart",
            str(output),
        ]
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "command": " ".join(command[:1] + ["..."] + command[-1:]),
    }


def probe_video(path: Path, *, ffprobe_bin: str | None = None) -> dict[str, Any]:
    if not path.exists():
        return {"checked": False, "ok": False, "error": "video_missing"}
    ffprobe = ffprobe_bin or shutil.which("ffprobe")
    if not ffprobe:
        return {"checked": False, "ok": False, "error": "ffprobe_not_found"}
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=width,height",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return {
            "checked": True,
            "ok": False,
            "error": completed.stderr.strip() or "ffprobe_failed",
        }
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"checked": True, "ok": False, "error": "ffprobe_invalid_json"}
    streams = data.get("streams") or []
    first_stream = streams[0] if streams else {}
    duration = float((data.get("format") or {}).get("duration") or 0)
    size = int((data.get("format") or {}).get("size") or path.stat().st_size)
    return {
        "checked": True,
        "ok": duration > 0 and size > 0,
        "duration_seconds": round(duration, 2),
        "bytes": size,
        "width": first_stream.get("width"),
        "height": first_stream.get("height"),
        "error": None,
    }


def build_report(
    root: Path = ROOT,
    *,
    video_path: Path = DEFAULT_VIDEO,
    public_url: str = PUBLIC_VIDEO_DRAFT_URL,
    prober: ProbeFn = probe_video,
) -> dict[str, Any]:
    root = root.resolve()
    video_path = video_path.resolve()
    slides = slide_records(root)
    missing_slides = [slide["path"] for slide in slides if not slide["present"]]
    probe = prober(video_path)
    expected_seconds = total_seconds()
    duration = probe.get("duration_seconds")
    duration_ok = isinstance(duration, (int, float)) and 0 < float(duration) <= MAX_SECONDS
    video_present = video_path.exists()
    draft_ready = bool(not missing_slides and video_present and probe.get("ok") and duration_ok)
    if draft_ready:
        mode = "mock_video_draft_ready"
    elif missing_slides:
        mode = "missing_draft_inputs"
    elif not video_present:
        mode = "draft_video_missing"
    elif not probe.get("ok"):
        mode = "draft_video_unverified"
    else:
        mode = "draft_video_too_long"
    return {
        "schema": SCHEMA,
        "mode": mode,
        "ok": draft_ready,
        "safe_to_submit": False,
        "final_video_ready": False,
        "public_video_draft_url": public_url,
        "video_path": str(video_path.relative_to(root) if video_path.is_relative_to(root) else video_path),
        "expected_seconds": expected_seconds,
        "max_seconds": MAX_SECONDS,
        "slides": slides,
        "missing_slides": missing_slides,
        "video_probe": probe,
        "checks": [
            {
                "id": "draft_inputs_present",
                "ok": not missing_slides,
                "detail": f"{len(slides) - len(missing_slides)} / {len(slides)} slide inputs present.",
            },
            {
                "id": "draft_video_present",
                "ok": video_present,
                "detail": f"Video path is {video_path}.",
            },
            {
                "id": "draft_under_time_limit",
                "ok": duration_ok,
                "detail": f"Duration is {duration}; max is {MAX_SECONDS}.",
            },
        ],
        "claim_boundary": (
            "This MP4 is a mock recording draft for rehearsal and public review. It is not the "
            "final Devpost video and does not prove live B2 or Genblaze execution."
        ),
        "next_actions": [
            "Upload or sync this draft only as a mock video reference.",
            "After B2 and Genblaze live proof, record the final narrated video and set PROOFFRAME_PUBLIC_VIDEO_URL.",
            "Run scripts/public_video_check.py with --verify-url --strict-final on the final public video URL.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ProofFrame Demo Video Draft",
        "",
        f"Mode: `{report['mode']}`",
        f"OK: `{str(report['ok']).lower()}`",
        f"Safe to submit: `{str(report['safe_to_submit']).lower()}`",
        f"Final video ready: `{str(report['final_video_ready']).lower()}`",
        f"Draft URL: {report['public_video_draft_url']}",
        f"Expected duration: `{report['expected_seconds']}s / {report['max_seconds']}s max`",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"],
        "",
        "## Slides",
        "",
    ]
    for slide in report["slides"]:
        marker = "OK" if slide["present"] else "MISSING"
        lines.append(f"- {marker} `{slide['path']}` ({slide['seconds']}s): {slide['title']}")
    probe = report["video_probe"]
    lines.extend(
        [
            "",
            "## Video Probe",
            "",
            f"- Checked: `{str(probe.get('checked')).lower()}`",
            f"- OK: `{str(probe.get('ok')).lower()}`",
            f"- Duration: `{probe.get('duration_seconds')}`",
            f"- Bytes: `{probe.get('bytes')}`",
            f"- Size: `{probe.get('width')}x{probe.get('height')}`",
            f"- Error: `{probe.get('error')}`",
            "",
            "## Checks",
            "",
        ]
    )
    for check in report["checks"]:
        marker = "OK" if check["ok"] else "BLOCKED"
        lines.append(f"- {marker} `{check['id']}`: {check['detail']}")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a ProofFrame mock demo video draft report.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--video-out", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--public-url", default=PUBLIC_VIDEO_DRAFT_URL)
    parser.add_argument("--build-video", action="store_true", help="Create the MP4 from screenshot slides.")
    parser.add_argument("--strict", action="store_true", help="Fail unless the draft video is ready.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.build_video:
        build_result = build_video(args.root.resolve(), args.video_out.resolve())
        if not build_result["ok"]:
            print(json.dumps({"ok": False, "mode": "video_build_failed", **build_result}, indent=2))
            raise SystemExit(2)
    report = build_report(
        args.root,
        video_path=args.video_out,
        public_url=args.public_url,
    )
    write_outputs(report, args.json_out, args.markdown_out)
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "mode": report["mode"],
                "video": str(args.video_out),
                "json": str(args.json_out),
                "markdown": str(args.markdown_out),
                "public_url": report["public_video_draft_url"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if report["ok"] or not args.strict else 2)


if __name__ == "__main__":
    main()
