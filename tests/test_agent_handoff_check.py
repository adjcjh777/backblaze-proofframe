import importlib.util
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


def test_handoff_markdown_lists_next_actions(tmp_path):
    write_agents(tmp_path, work_path=str(tmp_path / "old-proofframe-path"), branch="bugfix/wrong")

    report = agent_handoff_check.build_report(tmp_path)
    markdown = agent_handoff_check.render_markdown(report)

    assert "# ProofFrame Agent Handoff Report" in markdown
    assert "Update AGENTS.md so Work only inside points to the current repo path." in markdown
    assert "Update AGENTS.md Current branch" in markdown
