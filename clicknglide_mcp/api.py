"""Client de l'API officielle Click n' Glide (clé club, header Authorization)."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from . import config
from .ratelimit import RateLimiter

log = logging.getLogger("clicknglide_mcp.api")


class ApiError(RuntimeError):
    pass


class ClickNGlideAPI:
    def __init__(self, limiter: RateLimiter | None = None):
        self.limiter = limiter or RateLimiter()

    @staticmethod
    def url(path: str) -> str:
        if path.startswith("http"):
            return path
        return config.API_BASE.rstrip("/") + "/" + path.lstrip("/")

    def preview(self, method: str, path: str, body: dict | None, note: str = "") -> dict:
        return {
            "executed": False,
            "message": "Aperçu uniquement : rien n'a été envoyé à Click n' Glide. "
                       "Rappelez l'outil avec confirm=true pour exécuter cette requête."
                       + (f" {note}" if note else ""),
            "request": {"method": method, "url": self.url(path), "json": body},
        }

    async def request(self, method: str, path: str, body: dict | None = None) -> Any:
        key = config.require_secret("CLICKNGLIDE_API_KEY", "l'API Click n' Glide")
        await self.limiter.acquire()
        url = self.url(path)
        log.info("API %s %s", method, url)  # jamais d'en-têtes ni de clé dans les logs
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.request(
                    method, url,
                    headers={"Authorization": key, "Accept": "application/json"},
                    json=body if body is not None else None,
                )
        except httpx.HTTPError as e:
            raise ApiError(f"Erreur réseau vers Click n' Glide ({type(e).__name__}).") from None
        text = resp.text
        try:
            data = resp.json()
        except ValueError:
            data = None
        if resp.status_code >= 400:
            detail = data if data is not None else text[:500]
            if resp.status_code in (401, 403):
                raise ApiError(f"Accès refusé par l'API (HTTP {resp.status_code}) : clé API invalide ou révoquée ? Détail : {detail}")
            if resp.status_code == 429:
                raise ApiError(f"L'API signale un dépassement de quota (HTTP 429). Détail : {detail}")
            raise ApiError(f"Erreur HTTP {resp.status_code} de l'API : {detail}")
        if data is None:
            raise ApiError(f"Réponse non JSON de l'API (HTTP {resp.status_code}) : {text[:300]}")
        if isinstance(data, dict) and data.get("result") not in (None, "success"):
            raise ApiError(f"L'API a refusé l'opération : {data}")
        return data
