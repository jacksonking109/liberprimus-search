"""Usage-limit handling for subscription-backed CLIs (Claude Code, Codex).

The harness cannot read a plan's real remaining quota (that would mean reading the
CLI's stored login, which the providers do not allow). Instead it:
  1. counts its own calls per model in a rolling window (default 5 hours) and
     pauses at a cap you set (`max_calls_per_window` in the models config);
  2. recognises the CLI's "usage limit reached" replies, records when the limit
     resets (parsed from the message when possible, otherwise a cool-down), and
     pauses until then.
Both are recorded in the ledger (budget_event, rate_limit_event), so they hold
across runs that share a ledger.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta

DEFAULT_COOLDOWN_S = 30 * 60

_LIMIT_RE = re.compile(
    r"(usage|rate)[ _-]?limit|limit (reached|exceeded|hit)|hit your (usage )?limit|"
    r"too many requests|\b429\b|quota (exceeded|reached)|out of (credits|usage)", re.I)
_UNIX_RE = re.compile(r"\|\s*(\d{10})\b")
_IN_RE = re.compile(r"(?:try again|retry|resets?|available again)\s+in\s+(?:about\s+)?"
                    r"(\d+(?:\.\d+)?)\s*(s|sec|second|m|min|minute|h|hr|hour|d|day)s?\b", re.I)
_AT_RE = re.compile(r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.I)

_UNIT_S = {"s": 1, "sec": 1, "second": 1, "m": 60, "min": 60, "minute": 60, "h": 3600, "hr": 3600,
           "hour": 3600, "d": 86400, "day": 86400}


class RateLimited(RuntimeError):
    """A model is paused until `resume_at` (epoch seconds)."""

    def __init__(self, model: str, resume_at: float, reason: str):
        self.model, self.resume_at, self.reason = model, float(resume_at), reason
        when = datetime.fromtimestamp(self.resume_at).strftime("%Y-%m-%d %H:%M")
        super().__init__(f"{model} is paused until {when} ({reason})")


def looks_like_limit(text: str) -> bool:
    return bool(text) and bool(_LIMIT_RE.search(text))


def parse_resume_at(text: str, now: float | None = None,
                    default_cooldown_s: float = DEFAULT_COOLDOWN_S) -> tuple[float, bool]:
    """(resume time, parsed?) from a limit message. Falls back to now + cool-down."""
    now = time.time() if now is None else now
    m = _UNIX_RE.search(text or "")
    if m:
        ts = float(m.group(1))
        if now - 3600 < ts < now + 8 * 86400:
            return max(ts, now), True
    m = _IN_RE.search(text or "")
    if m:
        unit = m.group(2).lower().rstrip("s") or "s"
        secs = float(m.group(1)) * _UNIT_S.get(unit, _UNIT_S.get(m.group(2).lower(), 60))
        return now + secs, True
    m = _AT_RE.search(text or "")
    if m:
        hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        if 0 <= hour < 24 and 0 <= minute < 60:
            local_now = datetime.fromtimestamp(now)
            target = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= local_now:
                target += timedelta(days=1)
            return target.timestamp(), True
    return now + default_cooldown_s, False
