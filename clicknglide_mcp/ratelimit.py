"""Limiteur de débit persistant (20 appels/minute, 300/jour) partagé entre processus
via un fichier JSON verrouillé (fcntl)."""
from __future__ import annotations

import asyncio
import fcntl
import json
import time
from datetime import datetime
from pathlib import Path

from . import config


class DailyQuotaExceeded(RuntimeError):
    pass


class RateLimiter:
    def __init__(self, path: Path = config.USAGE_FILE,
                 per_minute: int = config.RATE_PER_MINUTE, per_day: int = config.RATE_PER_DAY):
        self.path = path
        self.per_minute = per_minute
        self.per_day = per_day

    @staticmethod
    def _today() -> str:
        return datetime.now().astimezone().strftime("%Y-%m-%d")

    def _locked_update(self, fn):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                raw = f.read()
                try:
                    state = json.loads(raw) if raw.strip() else {}
                except json.JSONDecodeError:
                    state = {}
                result = fn(state)
                f.seek(0)
                f.truncate()
                json.dump(state, f)
                f.flush()
                return result
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _try_acquire(self, state: dict):
        now = time.time()
        today = self._today()
        if state.get("day") != today:
            state["day"] = today
            state["day_count"] = 0
        recent = [t for t in state.get("recent", []) if now - t < 60]
        state["recent"] = recent
        if state["day_count"] >= self.per_day:
            raise DailyQuotaExceeded(
                f"Quota journalier de l'API Click n' Glide atteint ({self.per_day} appels le {today}). "
                "Réessayez demain."
            )
        if len(recent) >= self.per_minute:
            return 60 - (now - min(recent)) + 0.05  # secondes à attendre
        recent.append(now)
        state["day_count"] += 1
        state["total"] = state.get("total", 0) + 1
        return 0.0

    async def acquire(self, max_wait: float = 65.0) -> None:
        waited = 0.0
        while True:
            wait = self._locked_update(self._try_acquire)
            if wait <= 0:
                return
            if waited + wait > max_wait:
                raise RuntimeError("Limite de 20 appels/minute atteinte, réessayez dans une minute.")
            await asyncio.sleep(wait)
            waited += wait

    def usage(self) -> dict:
        def read(state):
            now = time.time()
            today = self._today()
            day_count = state.get("day_count", 0) if state.get("day") == today else 0
            last_min = len([t for t in state.get("recent", []) if now - t < 60])
            return {
                "date": today,
                "calls_today": day_count,
                "daily_limit": self.per_day,
                "remaining_today": max(0, self.per_day - day_count),
                "calls_last_minute": last_min,
                "per_minute_limit": self.per_minute,
            }
        return self._locked_update(read)
