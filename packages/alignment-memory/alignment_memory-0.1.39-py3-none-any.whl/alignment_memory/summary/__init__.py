from __future__ import annotations
from typing import Tuple, List
from collections import Counter
import re
from alignment_memory.memory import load_recent

_STOP = set("""
the a an and or to of in on for with is are was were be been being do does did
이 그 저 가 을 를 은 는 에 의 로 도 과 와 에서 으로 에게 을/를 은/는 가/이
""".split())
_token = re.compile(r"[A-Za-z0-9가-힣]+")

def _top_keywords(texts: List[str], k: int = 3) -> List[str]:
    c = Counter()
    for t in texts:
        for tok in _token.findall(t.lower()):
            if tok in _STOP or len(tok) <= 1: continue
            c[tok] += 1
    return [w for w,_ in c.most_common(k)]

def summarize(session_id: str, last_k: int = 20) -> Tuple[bool, str]:
    ok, msgs = load_recent(session_id, max(0,int(last_k)))
    if not ok: return False, msgs
    if not msgs: return True, "No messages."
    start_ts = msgs[0]["ts"]; end_ts = msgs[-1]["ts"]
    users = sum(1 for m in msgs if m.get("speaker")=="user")
    assists = sum(1 for m in msgs if m.get("speaker")=="assistant")
    kws = _top_keywords([m.get("content","") for m in msgs], 3)
    lines = [
        f"Window: {len(msgs)} messages ({start_ts} → {end_ts})",
        f"Speakers: user={users}, assistant={assists}",
        f"Top keywords: {', '.join(kws) if kws else '(none)'}",
        f"First: {msgs[0]['speaker']}: {msgs[0]['content'][:60]}",
        f"Last:  {msgs[-1]['speaker']}: {msgs[-1]['content'][:60]}",
    ]
    return True, "\n".join(lines)
