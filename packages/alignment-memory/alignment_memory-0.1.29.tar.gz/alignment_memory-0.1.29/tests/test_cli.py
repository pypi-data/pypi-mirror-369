import os, subprocess, sys
from pathlib import Path

PY = sys.executable

def run_ok(args, env=None, cwd=None):
    env_all = os.environ.copy()
    if env:
        env_all.update(env)
    p = subprocess.run(
        [PY, "-m", "alignment_memory.cli", *args],
        env=env_all, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    assert p.returncode == 0, f"exit={p.returncode}\n{p.stdout}"
    return p.stdout

def _latest_sid(dir_):
    js = sorted(Path(dir_).glob("*.json"))
    return js[-1].stem if js else None

def test_smoke(tmp_path):
    out = run_ok(["smoke", "--data-dir", str(tmp_path)])
    assert "SMOKE" in out

def test_new_and_append_search(tmp_path):
    # --data-dir 옵션으로 고정
    out = run_ok(["new", "--data-dir", str(tmp_path)])
    sid = _latest_sid(tmp_path); assert sid
    run_ok(["append", "--data-dir", str(tmp_path), "--id", sid, "--speaker", "user", "--content", "hello world"])
    out = run_ok(["search", "--data-dir", str(tmp_path), "--id", sid, "--query", "hello"])
    assert "hello" in out.lower()

def test_summarize_returns_lines(tmp_path):
    run_ok(["new", "--data-dir", str(tmp_path)])
    sid = _latest_sid(tmp_path)
    run_ok(["append", "--data-dir", str(tmp_path), "--id", sid, "--speaker", "user", "--content", "line one"])
    out = run_ok(["summarize", "--data-dir", str(tmp_path), "--id", sid, "--last-k", "20"])
    assert out.strip(), "empty summarize output"

def test_export_writes_txt(tmp_path):
    run_ok(["new", "--data-dir", str(tmp_path)])
    sid = _latest_sid(tmp_path)
    run_ok(["export", "--data-dir", str(tmp_path), "--id", sid])
    candidates = [Path.cwd() / "exports", Path(tmp_path) / "exports"]
    found = False
    for d in candidates:
        if d.exists() and any(p.suffix == ".txt" and sid in p.stem for p in d.glob("*.txt")):
            found = True; break
    assert found, "export .txt not found in expected locations"