import argparse, os, sys, json, datetime as dt
from pathlib import Path

TITLE = "Alignment Memory CLI (scope-lock v1.0)"

# ---------------------------
# Helpers
# ---------------------------
def _now_iso():
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")

def _sessions_dir(explicit: str | None = None) -> Path:
    # 우선순위: --data-dir > ALMEM_DIR > 패키지 로컬 경로
    if explicit:
        base = Path(explicit)
    else:
        env = os.environ.get("ALMEM_DIR")
        if env:
            base = Path(env)
        else:
            base = Path(__file__).resolve().parent / "data" / "sessions"
    base.mkdir(parents=True, exist_ok=True)
    return base

def _exports_dir(base: Path) -> Path:
    d = Path.cwd() / "exports"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        d = base / "exports"
        d.mkdir(parents=True, exist_ok=True)
    return d

def _next_sid(sdir: Path) -> str:
    today = dt.datetime.now().strftime("%Y%m%d")
    existing = sorted(sdir.glob(f"{today}-*.json"))
    if not existing:
        return f"{today}-001"
    last = existing[-1].stem
    try:
        n = int(last.split("-")[-1]) + 1
    except Exception:
        n = 1
    return f"{today}-{n:03d}"

def _sid_path(sdir: Path, sid: str) -> Path:
    return sdir / f"{sid}.json"

def _ensure_sid(sdir: Path, sid: str) -> Path:
    p = _sid_path(sdir, sid)
    if not p.exists():
        raise SystemExit(f"[ERROR] session not found: {sid}")
    return p

def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def _save_json(p: Path, data: dict):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _new_session(sdir: Path) -> str:
    sid = _next_sid(sdir)
    data = {"id": sid, "created_at": _now_iso(), "events": []}
    _save_json(_sid_path(sdir, sid), data)
    return sid

def _append_event(sdir: Path, sid: str, speaker: str, content: str):
    p = _ensure_sid(sdir, sid)
    data = _load_json(p) or {"id": sid, "events": []}
    data.setdefault("events", []).append({"time": _now_iso(), "speaker": speaker, "content": content})
    _save_json(p, data)

def _search(sdir: Path, sid: str, query: str) -> list[dict]:
    p = _ensure_sid(sdir, sid)
    data = _load_json(p)
    events = data.get("events", [])
    q = (query or "").strip()
    if not q:
        return events
    hits = []
    for ev in events:
        hay = f"{ev.get('time','')} {ev.get('speaker','')} {ev.get('content','')}"
        if q.lower() in hay.lower():
            hits.append(ev); continue
        if len(q) == 10 and q[4] == "-" and q[7] == "-" and ev.get("time","").startswith(q):
            hits.append(ev)
    return hits

def _summarize(sdir: Path, sid: str, last_k: int = 20) -> list[str]:
    p = _ensure_sid(sdir, sid)
    data = _load_json(p)
    evs = data.get("events", [])[-last_k:]
    lines = []
    for i, ev in enumerate(evs[-5:], 1):
        speaker = ev.get("speaker", "?")
        content = (ev.get("content","") or "").strip()
        if len(content) > 120: content = content[:117] + "..."
        lines.append(f"{i}. {speaker}: {content}")
    return lines or ["(no recent events)"]

def _export_txt(sdir: Path, sid: str) -> Path:
    p = _ensure_sid(sdir, sid)
    data = _load_json(p)
    exp = _exports_dir(sdir)
    out = exp / f"{sid}.txt"
    lines = [f"# Session {sid}", ""]
    for ev in data.get("events", []):
        ts = ev.get("time",""); sp = ev.get("speaker",""); ct = (ev.get("content","") or "").replace("\r","").replace("\n"," ")
        lines.append(f"- {ts} | {sp}: {ct}")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out

# ---------------------------
# Commands
# ---------------------------
def cmd_new(args):
    sdir = _sessions_dir(args.data_dir)
    print(_new_session(sdir))

def cmd_append(args):
    sdir = _sessions_dir(args.data_dir)
    _append_event(sdir, args.id, args.speaker, args.content)
    print("OK")

def cmd_search(args):
    sdir = _sessions_dir(args.data_dir)
    hits = _search(sdir, args.id, args.query)
    for ev in hits:
        print(f"{ev.get('time','')} | {ev.get('speaker','')}: {ev.get('content','')}")
    if not hits: print("(no hits)")

def cmd_summarize(args):
    sdir = _sessions_dir(args.data_dir)
    print("\n".join(_summarize(sdir, args.id, args.last_k)))

def cmd_export(args):
    sdir = _sessions_dir(args.data_dir)
    print(str(_export_txt(sdir, args.id)))

def cmd_smoke(args):
    print("[SMOKE] start")
    sdir = _sessions_dir(args.data_dir)
    sid = _new_session(sdir); print(f"[SMOKE] new -> {sid}")
    for i in range(1, 4):
        _append_event(sdir, sid, "user" if i % 2 else "assistant", f"hello {i}")
        print(f"[SMOKE] append {i}/3")
    _ = _search(sdir, sid, "hello"); print("[SMOKE] search keyword OK")
    today = dt.datetime.now().strftime("%Y-%m-%d")
    _ = _search(sdir, sid, today); print("[SMOKE] search date OK")
    if _summarize(sdir, sid, 20): print("[SMOKE] summarize OK")
    out = _export_txt(sdir, sid); print(f"[SMOKE] export -> {out}")
    print("[SMOKE] OK")

# ---------------------------
# Main (parents로 --data-dir를 각 서브커맨드에 포함)
# ---------------------------
def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data-dir", default=None, help="세션 저장 경로(지정 시 ALMEM_DIR보다 우선)")

    p = argparse.ArgumentParser(prog="cli.py", description=TITLE)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", parents=[common], help="새 세션 생성")
    p_new.set_defaults(func=cmd_new)

    p_append = sub.add_parser("append", parents=[common], help="이벤트 추가")
    p_append.add_argument("--id", required=True)
    p_append.add_argument("--speaker", required=True, choices=["user","assistant","system"])
    p_append.add_argument("--content", required=True)
    p_append.set_defaults(func=cmd_append)

    p_search = sub.add_parser("search", parents=[common], help="키워드/날짜 검색")
    p_search.add_argument("--id", required=True)
    p_search.add_argument("--query", required=True)
    p_search.set_defaults(func=cmd_search)

    p_sum = sub.add_parser("summarize", parents=[common], help="최근 k개 요약(최대 5줄)")
    p_sum.add_argument("--id", required=True)
    p_sum.add_argument("--last-k", dest="last_k", type=int, default=20)
    p_sum.set_defaults(func=cmd_summarize)

    p_exp = sub.add_parser("export", parents=[common], help=".txt 타임라인 내보내기")
    p_exp.add_argument("--id", required=True)
    p_exp.set_defaults(func=cmd_export)

    p_smoke = sub.add_parser("smoke", parents=[common], help="1분 스모크")
    p_smoke.set_defaults(func=cmd_smoke)

    return p

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "data_dir", None):
        os.environ["ALMEM_DIR"] = str(Path(args.data_dir).resolve())
    args.func(args)

if __name__ == "__main__":
    main()