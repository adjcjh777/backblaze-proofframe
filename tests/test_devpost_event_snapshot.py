import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "devpost_event_snapshot.py"
SPEC = importlib.util.spec_from_file_location("devpost_event_snapshot", SCRIPT_PATH)
devpost_event_snapshot = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(devpost_event_snapshot)


OVERVIEW_HTML = """
<html><body>
Backblaze Generative Media Hackathon
Deadline: Aug 3, 2026 @ 5:00pm EDT
$ 10,000 in cash
Participants (343)
Backblaze B2 Genblaze
</body></html>
"""

RULES_HTML = """
<html><body>
Participants (338)
Registration and Submission Period: June 22, 2026 at 9:00 AM EDT to August 3, 2026 at 5:00 PM EDT Judging Period:
August 3, 2026 at 5:00 PM EDT to August 12, 2026 at 5:00 PM EDT Winners Announced:
August 12, 2026 at 5:00 PM EDT Requirements
Provide a URL to a working application
Provide a URL to your public or private GitHub code repository
Include a demonstration video less than three (3) minutes
YouTube, Vimeo, or Youku
Backblaze B2
Genblaze
Real-world Utility
Production Readiness
B2 Storage + Data Orchestration
Use of Genblaze
Feedback Prize
</body></html>
"""


def test_snapshot_parses_official_overview_and_rules():
    snapshot = devpost_event_snapshot.build_snapshot_from_text(
        OVERVIEW_HTML,
        RULES_HTML,
        fetched_at="2026-06-27T16:00:00Z",
    )

    assert snapshot["schema"] == devpost_event_snapshot.SCHEMA
    assert snapshot["event"]["participant_count_observed"] == 343
    assert snapshot["event"]["deadline_utc"] == "2026-08-03T21:00:00Z"
    assert snapshot["event"]["deadline_beijing"] == "2026-08-04 05:00 Asia/Shanghai"
    assert snapshot["rules"]["requirements"]["working_app_url"] is True
    assert all(criterion["present"] for criterion in snapshot["rules"]["judging_criteria"])
    assert "different dynamic participant counts" in snapshot["event"]["participant_count_note"]


def test_snapshot_validation_passes_before_deadline():
    snapshot = devpost_event_snapshot.build_snapshot_from_text(
        OVERVIEW_HTML,
        RULES_HTML,
        fetched_at="2026-06-27T16:00:00Z",
    )

    validation = devpost_event_snapshot.validate_snapshot(
        snapshot,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )

    assert validation["ok"] is True
    assert validation["submission_open"] is True


def test_snapshot_validation_fails_when_stale():
    snapshot = devpost_event_snapshot.build_snapshot_from_text(
        OVERVIEW_HTML,
        RULES_HTML,
        fetched_at="2026-05-01T00:00:00Z",
    )

    validation = devpost_event_snapshot.validate_snapshot(
        snapshot,
        max_age_days=14,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )

    assert validation["ok"] is False
    assert any("days old" in finding for finding in validation["findings"])


def test_snapshot_writes_json_and_markdown(tmp_path):
    snapshot = devpost_event_snapshot.build_snapshot_from_text(
        OVERVIEW_HTML,
        RULES_HTML,
        fetched_at="2026-06-27T16:00:00Z",
    )
    json_path = tmp_path / "event.json"
    markdown_path = tmp_path / "event.md"

    devpost_event_snapshot.write_outputs(snapshot, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == devpost_event_snapshot.SCHEMA
    assert "# ProofFrame Devpost Event Snapshot" in markdown
    assert "## Judging Criteria" in markdown
