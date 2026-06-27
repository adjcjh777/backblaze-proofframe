import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "secret_scan.py"
SPEC = importlib.util.spec_from_file_location("secret_scan", SCRIPT_PATH)
secret_scan = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(secret_scan)


def write_file(root: Path, relative_path: str, content: bytes | str = "ok") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def test_secret_scan_detects_assigned_secret_without_storing_line_text(tmp_path):
    secret_value = "abcdefghij" + "klmnopqrst" + "uvwxyz123456"
    write_file(tmp_path, "docs/assets/evidence.json", '{"api_key": "' + secret_value + '"}\n')

    report = secret_scan.collect_scan(tmp_path)

    assert report["ok"] is False
    assert report["root"] == "."
    assert report["findings"][0]["path"] == "docs/assets/evidence.json"
    assert report["findings"][0]["pattern"] == "assigned_secret"
    assert "abcdefghijklmnopqrstuvwxyz" not in json.dumps(report)


def test_secret_scan_excludes_local_final_env_without_reading_values(tmp_path):
    local_key = "gmi-" + ("localvalue" * 4)
    write_file(tmp_path, ".env.final.local", "GMI_API_KEY=" + local_key + "\n")
    write_file(tmp_path, ".env.final.example", "GMI_API_KEY=\n")
    write_file(tmp_path, "docs/assets/report.md", "# public\n")

    report = secret_scan.collect_scan(tmp_path)

    assert report["ok"] is True
    assert report["coverage"]["local_secret_files_excluded_without_reading"] == [".env.final.local"]
    assert ".env.final.example" in report["scanned_text_files"]
    assert ".env.final.local" not in report["scanned_text_files"]
    assert "super-secret" not in json.dumps(report)


def test_secret_scan_inventories_screenshots_and_scans_var_logs(tmp_path):
    write_file(tmp_path, "docs/assets/proofframe-local-ui-smoke.png", b"\x89PNG\r\n\x1a\nfixture")
    write_file(tmp_path, "var/live-proof/uvicorn.log", "server started without secrets\n")
    write_file(tmp_path, "README.md", "# ProofFrame\n")

    report = secret_scan.collect_scan(tmp_path)

    assert report["ok"] is True
    assert report["coverage"]["screenshot_binary_inventory"] is True
    assert report["coverage"]["var_log_text_files_scanned"] is True


def test_secret_scan_writes_json_and_markdown(tmp_path):
    write_file(tmp_path, "README.md", "# ProofFrame\n")
    report = secret_scan.collect_scan(tmp_path)
    json_path = tmp_path / "out/secret.json"
    markdown_path = tmp_path / "out/secret.md"

    secret_scan.write_outputs(report, json_path, markdown_path)

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["schema"] == "proofframe.secret_scan.v1"
    assert "# ProofFrame Secret Scan Report" in markdown
    assert "No credential values" in markdown
