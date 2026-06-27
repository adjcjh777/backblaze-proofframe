import json
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "claim_lint.py"
SPEC = importlib.util.spec_from_file_location("claim_lint", SCRIPT_PATH)
claim_lint = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(claim_lint)


def write_file(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_minimal_pre_live_tree(root: Path) -> None:
    write_file(root, "README.md", "ProofFrame includes a B2-compatible storage adapter.\n")
    write_file(
        root,
        "docs/submission.md",
        "The final submission target is B2-backed media after live proof.\n",
    )
    write_file(
        root,
        "docs/assets/devpost-submission-packet.md",
        "The final submission gate verifies Genblaze-backed generation.\n",
    )
    write_file(
        root,
        "docs/assets/devpost-submission-packet.json",
        json.dumps({"mode": "pre_live_safe", "claim_warning": "safe"}),
    )
    write_file(
        root,
        "tasks.json",
        json.dumps(
            {
                "tasks": [
                    {"id": "T020", "status": "doing", "title": "B2"},
                    {"id": "T021", "status": "doing", "title": "Genblaze"},
                    {"id": "T040", "status": "done", "title": "Devpost"},
                    {"id": "T041", "status": "todo", "title": "Audit"},
                    {"id": "T041A", "status": "todo", "title": "Secret scan"},
                    {"id": "T042", "status": "todo", "title": "Submit"},
                ]
            }
        ),
    )


def test_claim_lint_passes_safe_pre_live_copy(tmp_path):
    write_minimal_pre_live_tree(tmp_path)

    report = claim_lint.build_claim_report(tmp_path)

    assert report["ok"] is True
    assert report["mode"] == "pre_live_safe"
    assert report["findings"] == []


def test_claim_lint_fails_unsafe_b2_present_tense_claim(tmp_path):
    write_minimal_pre_live_tree(tmp_path)
    write_file(tmp_path, "README.md", "ProofFrame stores generated media in Backblaze B2.\n")

    report = claim_lint.build_claim_report(tmp_path)

    assert report["ok"] is False
    assert report["findings"][0]["status"] == "unsafe-pre-live-claim"
    assert report["findings"][0]["path"] == "README.md"


def test_claim_lint_fails_post_live_packet_without_final_evidence(tmp_path):
    write_minimal_pre_live_tree(tmp_path)
    write_file(
        tmp_path,
        "docs/assets/devpost-submission-packet.json",
        json.dumps({"mode": "post_live_verified", "claim_warning": "unsafe"}),
    )

    report = claim_lint.build_claim_report(tmp_path)

    assert report["ok"] is False
    assert report["findings"][0]["status"] == "unsafe-packet-mode"
