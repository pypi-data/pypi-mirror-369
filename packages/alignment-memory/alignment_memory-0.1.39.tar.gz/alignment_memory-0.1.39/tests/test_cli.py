import subprocess, sys
from pathlib import Path

def run_ok(args):
    p = subprocess.run([sys.executable, "-m", "alignment_memory.cli", *args],
                       text=True, capture_output=True, check=True)
    return p.stdout.strip()

def test_smoke(tmp_path):
    out = run_ok(["smoke", "--data-dir", str(tmp_path)])
    assert "SMOKE" in out

def test_new_and_append_search(tmp_path):
    sid = run_ok(["new", "--data-dir", str(tmp_path)])
    assert sid
    run_ok(["append", "--data-dir", str(tmp_path), "--id", sid, "--speaker", "user", "--content", "hello"])
    out = run_ok(["search", "--data-dir", str(tmp_path), "--id", sid, "--query", "hello"])
    assert "hello" in out

def test_summarize_returns_lines(tmp_path):
    sid = run_ok(["new", "--data-dir", str(tmp_path)])
    run_ok(["append", "--data-dir", str(tmp_path), "--id", sid, "--speaker", "user", "--content", "line one"])
    out = run_ok(["summarize", "--data-dir", str(tmp_path), "--id", sid, "--last-k", "10"])
    assert "line one" in out

def test_export_writes_txt(tmp_path):
    sid = run_ok(["new", "--data-dir", str(tmp_path)])
    path = run_ok(["export", "--data-dir", str(tmp_path), "--id", sid])
    p = Path(path)
    assert p.exists()
