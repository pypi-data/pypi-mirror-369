import subprocess, sys

def run_ok(args):
    cmd = [sys.executable, "-m", "alignment_memory.cli"] + list(map(str, args))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()

def test_list_and_show(tmp_path):
    sdir = str(tmp_path)
    sid1 = run_ok(["new", "--data-dir", sdir])
    sid2 = run_ok(["new", "--data-dir", sdir])
    out_list = run_ok(["list", "--data-dir", sdir])
    assert sid1 in out_list and sid2 in out_list

    run_ok(["append", "--data-dir", sdir, "--id", sid2, "--speaker", "user", "--content", "line one"])
    out_show = run_ok(["show", "--data-dir", sdir, "--id", sid2])
    assert "line one" in out_show
