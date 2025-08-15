from __future__ import annotations
import os, json, re, datetime as _dt
from typing import Dict, Any, Tuple, List, Optional

BASE_DIR = os.environ.get("ALMEM_DIR", os.path.join(os.getcwd(), "alignment_memory", "data", "sessions"))
def _ensure_dir(p: str) -> None: os.makedirs(p, exist_ok=True)
def _now_iso() -> str: return _dt.datetime.now().isoformat(timespec="seconds")
def _session_path(session_id: str) -> str: _ensure_dir(BASE_DIR); return os.path.join(BASE_DIR, f"{session_id}.json")
_id_rx = re.compile(r"[^A-Za-z0-9_-]")
def _sanitize_id(raw: str) -> str:
    s = (raw or "").strip(); s = _id_rx.sub("-", s)[:64].strip("-._ "); return s
def _next_id() -> str:
    today = _dt.date.today().strftime("%Y%m%d"); _ensure_dir(BASE_DIR)
    existing = [fn for fn in os.listdir(BASE_DIR) if fn.startswith(today + "-") and fn.endswith(".json")]
    nums=[]; 
    for fn in existing:
        try: nums.append(int(fn[len(today)+1:-5]))
        except: pass
    n = max(nums)+1 if nums else 1
    return f"{today}-{n:03d}"

def new_session(session_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any] | str]:
    sid = _sanitize_id(session_id) if session_id else _next_id()
    if not sid: return False, "invalid session id"
    return True, {"id": sid, "created_at": _now_iso(), "updated_at": _now_iso(), "messages": []}

def save(session: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(session, dict) or not session.get("id"): return False, "invalid session object"
    session["updated_at"] = _now_iso(); path = _session_path(session["id"])
    try:
        _ensure_dir(os.path.dirname(path)); tmp = path + ".tmp"
        with open(tmp,"w",encoding="utf-8") as f: json.dump(session,f,ensure_ascii=False,indent=2)
        os.replace(tmp,path); return True, path
    except Exception as e:
        return False, f"save failed: {e}"

def load(session_id: str) -> Tuple[bool, Dict[str, Any] | str]:
    sid = _sanitize_id(session_id); path = _session_path(sid)
    if not os.path.isfile(path): return False, "file not found"
    try:
        with open(path,"r",encoding="utf-8") as f: data = json.load(f)
        return True, data
    except Exception as e:
        return False, f"load failed: {e}"

def load_recent(session_id: str, n: int = 20) -> Tuple[bool, List[Dict[str, Any]] | str]:
    ok, data = load(session_id); 
    if not ok: return False, data
    msgs = data.get("messages", []); n = max(0,int(n))
    return True, msgs[-n:] if n>0 else []

def append(session_id: str, speaker: str, content: str, timestamp: Optional[str] = None) -> Tuple[bool, str]:
    if not content: return False, "empty content"
    speaker = (speaker or "").strip().lower()
    if speaker not in ("user","assistant","system"): return False, "invalid speaker (user/assistant/system)"
    ok, data = load(session_id)
    if not ok: return False, data
    msg = {"speaker": speaker, "content": content, "ts": timestamp or _now_iso()}
    data["messages"] = data.get("messages", []) + [msg]
    ok2, res = save(data); 
    if not ok2: return False, res
    return True, "ok"
