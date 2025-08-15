from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional
from alignment_memory.memory import load
def _isoday(ts: str) -> str: return str(ts)[:10]

def search(session_id: str, query: Optional[str] = None, date: Optional[str] = None
           ) -> Tuple[bool, List[Dict[str, Any]] | str]:
    if not query and not date: return False, "provide query or date"
    ok, data = load(session_id)
    if not ok: return False, data
    results: List[Dict[str, Any]] = []
    q = (query or "").strip().lower(); d = (date or "").strip()
    for m in data.get("messages", []):
        ts = str(m.get("ts","")); sp = str(m.get("speaker","")); txt = str(m.get("content",""))
        if q and (q in txt.lower()): results.append({"ts": ts, "speaker": sp, "snippet": txt[:160]})
        elif d and _isoday(ts) == d: results.append({"ts": ts, "speaker": sp, "snippet": txt[:160]})
    return True, results
