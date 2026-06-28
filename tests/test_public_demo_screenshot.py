import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "public_demo_screenshot.py"
SPEC = importlib.util.spec_from_file_location("public_demo_screenshot", SCRIPT_PATH)
public_demo_screenshot = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_demo_screenshot)


def complete_body_text() -> str:
    return "\n".join(public_demo_screenshot.VISIBLE_MARKERS.values())


def complete_html_text() -> str:
    return "\n".join(public_demo_screenshot.HTML_MARKERS.values())


def test_marker_report_requires_visible_and_html_markers():
    markers = public_demo_screenshot.marker_report(complete_body_text(), complete_html_text())

    assert markers["visible_ok"] is True
    assert markers["html_ok"] is True
    assert markers["visible"]["sponsor_evidence_model"]["present"] is True
    assert markers["html"]["judge_recording_slate"]["present"] is True


def test_marker_report_fails_when_gate_copy_is_missing():
    body = complete_body_text().replace("Final reports pending", "")

    markers = public_demo_screenshot.marker_report(body, complete_html_text())

    assert markers["visible_ok"] is False
    assert markers["visible"]["final_reports_pending"]["present"] is False
    assert markers["html_ok"] is True


def test_build_report_is_public_safe_with_verified_screenshot(monkeypatch, tmp_path):
    screenshot = tmp_path / "docs/assets/proofframe-hf-public-smoke.png"

    monkeypatch.setattr(
        public_demo_screenshot,
        "image_record",
        lambda path: {
            "present": True,
            "path": "docs/assets/proofframe-hf-public-smoke.png",
            "ok": True,
            "bytes": 717007,
            "width": 1440,
            "height": 2692,
            "luma_mean": 236.6,
            "luma_stddev": 47.11,
        },
    )

    report = public_demo_screenshot.build_report(
        url=public_demo_screenshot.PUBLIC_JUDGE_URL,
        screenshot_path=screenshot,
        body_text=complete_body_text(),
        html_text=complete_html_text(),
    )
    markdown = public_demo_screenshot.render_markdown(report)
    serialized = json.dumps(report)

    assert report["schema"] == "proofframe.public_demo_screenshot.v1"
    assert report["mode"] == "public_judge_screenshot_ready"
    assert report["ok"] is True
    assert report["safe_to_commit"] is True
    assert report["secret_policy"]["no_secret_values_recorded"] is True
    assert "local/mock judge demo" in report["claim_boundary"]
    assert "Sponsor Evidence Model" in markdown
    assert "secret" not in serialized.lower() or "no_secret_values_recorded" in serialized
