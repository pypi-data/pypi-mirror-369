from __future__ import annotations
import os
from typing import Tuple
from alignment_memory.memory import load

def export(session_id: str, out_dir: str = "exports") -> Tuple[bool, str]:
    ok, data = load(session_id)
    if not ok: return False, data
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{session_id}.txt")
    try:
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"# Session {session_id}\n\n")
            for m in data.get("messages", []):
                f.write(f"- {m.get('ts')} | {m.get('speaker')}: {m.get('content')}\n")
        return True, path
    except Exception as e:
        return False, f"export failed: {e}"
