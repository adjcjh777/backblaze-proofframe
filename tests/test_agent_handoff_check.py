import importlib.util
import json
import subprocess
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "agent_handoff_check.py"
SPEC = importlib.util.spec_from_file_location("agent_handoff_check", SCRIPT_PATH)
agent_handoff_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(agent_handoff_check)


def write_agents(root: Path, *, work_path: str, branch: str = "feature/backblaze-proofframe") -> None:
    root.joinpath("AGENTS.md").write_text(
        "\n".join(
            [
                "# ProofFrame Agent Rules",
                "",
                "## Git",
                f"- Work only inside `{work_path}`.",
                "- Keep this as an independent Git repo.",
                f"- Current branch: `{branch}`.",
                "",
                "## Agent Bus",
                "- Team id: `proofframe-hackathon-58c62c50`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_handoff_report_passes_when_agents_path_matches_repo(tmp_path):
    write_agents(tmp_path, work_path=str(tmp_path))

    report = agent_handoff_check.build_report(tmp_path)

    assert report["schema"] == "proofframe.agent_handoff.v1"
    assert report["ok"] is True
    assert report["mode"] == "handoff_ready"
    assert report["bus"]["status"] == "skipped"
    assert all(item["ok"] for item in report["checks"])


def test_handoff_report_fails_when_agents_path_is_stale(tmp_path):
    write_agents(tmp_path, work_path=str(tmp_path / "old-proofframe-path"))

    report = agent_handoff_check.build_report(tmp_path)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert report["mode"] == "handoff_mismatch"
    assert "work_path_matches_repo" in failed
    assert "work_path_exists" in failed


def test_handoff_report_accepts_local_agents_path_in_github_actions(tmp_path, monkeypatch):
    root = tmp_path / "backblaze-proofframe"
    root.mkdir()
    write_agents(root, work_path="/Users/junhaocheng/working-dir/ai-competitions/backblaze-proofframe")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    report = agent_handoff_check.build_report(root)

    assert report["ok"] is True
    assert report["environment"]["ci"] is True
    assert report["agents"]["normalized_work_path"].endswith("/backblaze-proofframe")
    assert all(item["ok"] for item in report["checks"])


def test_handoff_report_rejects_wrong_repo_name_in_github_actions(tmp_path, monkeypatch):
    root = tmp_path / "backblaze-proofframe"
    root.mkdir()
    write_agents(root, work_path="/Users/junhaocheng/working-dir/ai-competitions/old-proofframe")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    report = agent_handoff_check.build_report(root)

    failed = {item["id"] for item in report["checks"] if not item["ok"]}
    assert report["ok"] is False
    assert "work_path_matches_repo" in failed
    assert "work_path_exists" in failed


def test_handoff_markdown_lists_next_actions(tmp_path):
    write_agents(tmp_path, work_path=str(tmp_path / "old-proofframe-path"), branch="bugfix/wrong")

    report = agent_handoff_check.build_report(tmp_path)
    markdown = agent_handoff_check.render_markdown(report)

    assert "# ProofFrame Agent Handoff Report" in markdown
    assert "Update AGENTS.md so Work only inside points to the current repo path." in markdown
    assert "Update AGENTS.md Current branch" in markdown


def test_bus_summary_reports_active_role_cwd_when_project_is_stale(tmp_path, monkeypatch):
    write_agents(tmp_path, work_path=str(tmp_path))
    fake_bus = tmp_path / "agent-bus"
    fake_bus.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(agent_handoff_check, "BUS_CLI", fake_bus)

    def fake_run(args, cwd, capture_output, text, check):
        assert cwd == tmp_path.resolve()
        if args[-3:] == ["team", "show", "proofframe-hackathon-58c62c50"]:
            payload = {
                "team": {
                    "team_id": "proofframe-hackathon-58c62c50",
                    "project": "/old/backblaze-proofframe",
                    "roles": {
                        "reviewer": {
                            "status": "active",
                            "session_id": "reviewer-session",
                            "thread_id": "reviewer-session",
                        },
                        "tester": {"status": "pending", "session_id": None},
                    },
                }
            }
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
        if args[-2:] == ["resolve", "reviewer-session"]:
            payload = {
                "agent": {
                    "agent_id": "proofframe-hackathon-reviewer",
                    "name": "proofframe-hackathon-reviewer",
                    "session_id": "reviewer-session",
                    "cwd": str(tmp_path.resolve()),
                    "status": "idle",
                    "stale": False,
                }
            }
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
        raise AssertionError(f"Unexpected args: {args}")

    monkeypatch.setattr(agent_handoff_check.subprocess, "run", fake_run)

    report = agent_handoff_check.build_report(tmp_path, check_bus=True)

    assert report["ok"] is True
    assert report["bus"]["status"] == "stale"
    assert report["bus"]["active_role_cwd_ok"] is True
    assert report["bus"]["active_roles"][0]["role"] == "reviewer"
    assert report["bus"]["active_roles"][0]["cwd_matches_repo"] is True
    assert "Reattach active Agent Bus roles" not in " ".join(report["next_actions"])


def test_bus_summary_flags_stale_active_role_cwd(tmp_path, monkeypatch):
    write_agents(tmp_path, work_path=str(tmp_path))
    fake_bus = tmp_path / "agent-bus"
    fake_bus.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(agent_handoff_check, "BUS_CLI", fake_bus)

    def fake_run(args, cwd, capture_output, text, check):
        if args[-3:] == ["team", "show", "proofframe-hackathon-58c62c50"]:
            payload = {
                "team": {
                    "team_id": "proofframe-hackathon-58c62c50",
                    "project": str(tmp_path.resolve()),
                    "roles": {
                        "scout": {
                            "status": "active",
                            "session_id": "scout-session",
                            "thread_id": "scout-session",
                        }
                    },
                }
            }
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
        if args[-2:] == ["resolve", "scout-session"]:
            payload = {
                "agent": {
                    "agent_id": "proofframe-hackathon-scout",
                    "session_id": "scout-session",
                    "cwd": "/old/backblaze-proofframe",
                    "status": "idle",
                }
            }
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")
        raise AssertionError(f"Unexpected args: {args}")

    monkeypatch.setattr(agent_handoff_check.subprocess, "run", fake_run)

    report = agent_handoff_check.build_report(tmp_path, check_bus=True)

    assert report["bus"]["status"] == "current"
    assert report["bus"]["active_role_cwd_ok"] is False
    assert report["bus"]["active_roles"][0]["cwd_matches_repo"] is False
    assert any("Reattach active Agent Bus roles" in action for action in report["next_actions"])
