"""Configuration commune. Les secrets sont lus uniquement depuis l'environnement,
au moment de l'appel, et ne sont jamais écrits ni journalisés."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PKG_DIR.parent

STATE_DIR = Path(os.environ.get("CLICKNGLIDE_STATE_DIR", PROJECT_DIR / "state")).expanduser()
BROWSER_PROFILE_DIR = STATE_DIR / "browser-profile"
DEBUG_DIR = STATE_DIR / "debug"
USAGE_FILE = STATE_DIR / "api-usage.json"

API_BASE = "https://api.clicknglide.com"
FORUM_CONVERSATIONS_URL = "https://clicknglide.com/api/forum_conversations"
APP_URL = os.environ.get("CLICKNGLIDE_APP_URL", "https://app.clicknglide.com")

RATE_PER_MINUTE = int(os.environ.get("CLICKNGLIDE_RATE_PER_MINUTE", "20"))
RATE_PER_DAY = int(os.environ.get("CLICKNGLIDE_RATE_PER_DAY", "300"))


def ensure_dirs() -> None:
    for d in (STATE_DIR, BROWSER_PROFILE_DIR, DEBUG_DIR):
        d.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(STATE_DIR, 0o700)
    except OSError:
        pass


def secret(name: str) -> str | None:
    v = os.environ.get(name)
    return v.strip() if v and v.strip() else None


class MissingSecret(RuntimeError):
    pass


def require_secret(name: str, purpose: str) -> str:
    v = secret(name)
    if not v:
        raise MissingSecret(
            f"La variable d'environnement {name} n'est pas définie : impossible d'utiliser {purpose}. "
            f"Définissez-la dans la configuration du connecteur puis relancez le serveur."
        )
    return v


def setup_logging() -> logging.Logger:
    # stdio MCP : stdout est réservé au protocole, tout log va sur stderr.
    logging.basicConfig(
        stream=sys.stderr,
        level=os.environ.get("CLICKNGLIDE_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return logging.getLogger("clicknglide_mcp")
