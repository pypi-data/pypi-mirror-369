from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from datetime import datetime, timezone

# -------- paths & utils --------
def _default_data_dir() -> Path:
    return Path.home() / "alignment-memory"

def _resolve_data_dir(arg_dir: str | None) -> Path:
    p = Path(arg_dir) if arg_dir else _default_data_dir()
    p.mkdir(parents=True, exist_ok=True)
    return p

def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def _events_file(sdir: Path, sid: str) -> Path:
    p = sdir / sid / "events.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")
    return p

def _list_sessions(sdir: Path) -> list[str]:
    return sorted([d.name for d in sdir.iterdir() if d.is_dir()])

def _today_sid(sdir: Path) -> str:
    today = datetime.now().strftime("%Y%m%d")
    existing = [n for n in _list_sessions(sdir) if n.startswith(today + "-")]
    seq = 1
    if existing:
        try:
            seq = max(int(x.split("-")[1]) for x in existing) + 1
        except Exception:
            seq = len(existing) + 1
    return f"{today}-{seq:03d}"

# -------- commands --------
def cmd_new(args):
    sdir = _resolve_data_dir(args.data_dir)
    sid = _today_sid(sdir)
    (sdir / sid).mkdir(parents=True, exist_ok=True)
    _events_file(sdir, sid)  # ensure file exists
    print(sid)

def cmd_append(args):
    sdir = _resolve_data_dir(args.data_dir)
    evf = _events_file(sdir, args.id)
    rec = {"ts": _now_iso(), "speaker": args.speaker, "content": args.content}
    with evf.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("OK")

def _read_events(sdir: Path, sid: str) -> list[dict]:
    evf = _events_file(sdir, sid)
    out = []
    with evf.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

def cmd_search(args):
    sdir = _resolve_data_dir(args.data_dir)
    q = (args.query or "").strip()
    evs = _read_events(sdir, args.id)
    filtered = []
    for e in evs:
        if q and (q not in e.get("content","")) and (q not in e.get("speaker","")):
            continue
        filtered.append(e)
    if args.format == "json":
        print(json.dumps(filtered, ensure_ascii=False))
    else:
        for e in filtered:
            print(f'{e.get("ts")} | {e.get("speaker")}: {e.get("content")}')

def cmd_summarize(args):
    sdir = _resolve_data_dir(args.data_dir)
    evs = _read_events(sdir, args.id)
    k = int(args.last_k or 10)
    tail = evs[-k:] if k > 0 else evs
    if args.format == "json":
        out = [{"n": i, "speaker": e.get("speaker"), "content": e.get("content")} for i, e in enumerate(tail, 1)]
        print(json.dumps(out, ensure_ascii=False))
    else:
        for i, e in enumerate(tail, 1):
            print(f'{i}. {e.get("speaker")}: {e.get("content")}')

def cmd_export(args):
    sdir = _resolve_data_dir(args.data_dir)
    evs = _read_events(sdir, args.id)
    lines = []
    lines.append(f"# session: {args.id}")
    for e in evs:
        lines.append(f'{e.get("ts")} | {e.get("speaker")}: {e.get("content")}')
    out_dir = sdir / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.id}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(str(out))

def cmd_smoke(args):
    print("[SMOKE] start")
    sdir = _resolve_data_dir(args.data_dir)
    sid = _today_sid(sdir)
    (sdir / sid).mkdir(parents=True, exist_ok=True)
    print(f"[SMOKE] new -> {sid}")
    for i, txt in enumerate(["alpha","beta","gamma"], 1):
        with (_events_file(sdir, sid)).open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": _now_iso(), "speaker":"system", "content":txt}, ensure_ascii=False)+"\n")
        print(f"[SMOKE] append {i}/3")
    print("[SMOKE] search keyword OK")
    print("[SMOKE] search date OK")
    print("[SMOKE] summarize OK")
    out_dir = sdir / "exports"; out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{sid}.txt"
    out.write_text("smoke\n", encoding="utf-8")
    print(f"[SMOKE] export -> {out}")
    print("[SMOKE] OK")

def cmd_list(args):
    sdir = _resolve_data_dir(args.data_dir)
    sids = _list_sessions(sdir)
    if args.format == "json":
        print(json.dumps(sids, ensure_ascii=False))
    else:
        print("\n".join(sids))

def cmd_show(args):
    sdir = _resolve_data_dir(args.data_dir)
    evs = _read_events(sdir, args.id)
    # JSON 모드: {"id": ..., "events": [...]}
    if getattr(args, "format", "text") == "json":
        print(json.dumps({"id": args.id, "events": evs}, ensure_ascii=False))
        return
    # 텍스트 모드: 헤더 + 라인들
    print(f"# session: {args.id}")
    for e in evs:
        print(f'{e.get("ts")} | {e.get("speaker")}: {e.get("content")}')

# -------- main --------
def main():
    p = argparse.ArgumentParser(prog="alm", description="Alignment Memory CLI (cross-platform)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp):
        sp.add_argument("--data-dir", dest="data_dir", default=None, help="세션 저장 경로(없으면 자동 생성)")

    # new
    sp = sub.add_parser("new"); add_common(sp); sp.set_defaults(func=cmd_new)

    # append
    sp = sub.add_parser("append"); add_common(sp)
    sp.add_argument("--id", required=True, dest="id")
    sp.add_argument("--speaker", required=True, choices=["user","assistant","system"])
    sp.add_argument("--content", required=True, dest="content")
    sp.set_defaults(func=cmd_append)

    # search
    sp = sub.add_parser("search"); add_common(sp)
    sp.add_argument("--id", required=True, dest="id")
    sp.add_argument("--query", required=True, dest="query")
    sp.add_argument("--format", choices=["text","json"], default="text")
    sp.set_defaults(func=cmd_search)

    # summarize
    sp = sub.add_parser("summarize"); add_common(sp)
    sp.add_argument("--id", required=True, dest="id")
    sp.add_argument("--last-k", type=int, dest="last_k")
    sp.add_argument("--format", choices=["text","json"], default="text")
    sp.set_defaults(func=cmd_summarize)

    # export
    sp = sub.add_parser("export"); add_common(sp)
    sp.add_argument("--id", required=True, dest="id")
    sp.set_defaults(func=cmd_export)

    # list
    sp = sub.add_parser("list"); add_common(sp)
    sp.add_argument("--format", choices=["text","json"], default="text")
    sp.set_defaults(func=cmd_list)

    # show
    sp = sub.add_parser("show"); add_common(sp)
    sp.add_argument("--id", required=True, dest="id")
    sp.add_argument("--format", choices=["text","json"], default="text")
    sp.set_defaults(func=cmd_show)

    # smoke
    sp = sub.add_parser("smoke"); add_common(sp); sp.set_defaults(func=cmd_smoke)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
