"""Serveur MCP (stdio) Click n' Glide : API officielle + messagerie via navigateur headless."""
from __future__ import annotations

import functools
import json
import re
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from . import config
from .api import ApiError, ClickNGlideAPI
from .config import MissingSecret
from .messenger import Messenger, MessengerError
from .ratelimit import DailyQuotaExceeded

log = config.setup_logging()
config.ensure_dirs()

mcp = FastMCP(
    "clicknglide",
    instructions=(
        "Outils pour le planning Click n' Glide de votre club. "
        "Les outils d'écriture/suppression/envoi n'agissent que si confirm=true ; sinon ils renvoient un aperçu. "
        "Toujours montrer l'aperçu à l'utilisateur et obtenir son accord avant de rappeler avec confirm=true. "
        "API limitée à 20 appels/minute et 300/jour (voir get_api_usage)."
    ),
)
api = ClickNGlideAPI()
messenger = Messenger()

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _date(d: str, name: str = "date") -> str:
    if not DATE_RE.match(d or ""):
        raise ValueError(f"{name} doit être au format AAAA-MM-JJ (reçu : {d!r}).")
    return d


def tool_errors(fn):
    """Transforme les erreurs connues en réponses lisibles (sans trace ni secret)."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except (MissingSecret, ApiError, MessengerError, DailyQuotaExceeded, ValueError) as e:
            return {"error": str(e), "type": type(e).__name__}
        except Exception as e:  # noqa: BLE001
            log.exception("Erreur inattendue dans %s", fn.__name__)
            return {"error": f"Erreur inattendue ({type(e).__name__}) : {e}", "type": "UnexpectedError"}
    return wrapper


async def _write(method: str, path: str, body: dict, confirm: bool, note: str = "") -> Any:
    if confirm is not True:
        return api.preview(method, path, body, note)
    data = await api.request(method, path, body)
    return {"executed": True, "response": data}


def _clean(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


# =============================================================== API : inscriptions
@mcp.tool()
@tool_errors
async def get_signups(date: str) -> Any:
    """Liste les champs du planning et les inscriptions d'une journée (date AAAA-MM-JJ). Lecture seule (1 appel API)."""
    return await api.request("GET", f"/signups/{_date(date)}")


@mcp.tool()
@tool_errors
async def get_signups_range(start_date: str, end_date: str) -> Any:
    """Liste les inscriptions sur une plage de dates (AAAA-MM-JJ, bornes incluses). Lecture seule (1 appel API)."""
    return await api.request("GET", f"/signups/{_date(start_date, 'start_date')}/{_date(end_date, 'end_date')}")


@mcp.tool()
@tool_errors
async def add_signup(date: str, field_id: int, user_id: int, signup_parameter: Optional[int] = None,
                     signup_comment: Optional[str] = None, confirm: bool = False) -> Any:
    """Inscrit un membre (user_id) dans un champ « membre » (field_id) d'une journée, avec paramètre et commentaire
    optionnels. Peut envoyer des emails automatiques (confirmation, liste d'attente). Sans confirm=true : aperçu seulement."""
    body = _clean({"date": _date(date), "fieldId": field_id, "userId": user_id,
                   "signupParameter": signup_parameter, "signupComment": signup_comment})
    return await _write("POST", "/signups", body, confirm, "Des emails automatiques peuvent partir.")


@mcp.tool()
@tool_errors
async def add_freetext_signup(date: str, field_id: int, text: str, confirm: bool = False) -> Any:
    """Ajoute une ligne de texte libre dans un champ « texte libre » d'une journée (ex. un vol d'initiation
    « M. Dupont 15h 30 min »). Sans confirm=true : aperçu seulement."""
    body = {"date": _date(date), "fieldId": field_id, "signupText": text}
    return await _write("POST", "/signups", body, confirm)


@mcp.tool()
@tool_errors
async def add_freetext_signups_bulk(date: str, field_id: int, texts: list[str], confirm: bool = False) -> Any:
    """Ajoute plusieurs lignes de texte libre d'un coup dans un champ « texte libre » d'une journée.
    Sans confirm=true : aperçu seulement."""
    if not texts:
        raise ValueError("texts ne doit pas être vide.")
    body = {"date": _date(date), "fieldId": field_id, "signupText": texts}
    return await _write("POST", "/signups", body, confirm)


@mcp.tool()
@tool_errors
async def update_signup(signup_id: int, signup_parameter: Optional[int] = None,
                        signup_comment: Optional[str] = None, confirm: bool = False) -> Any:
    """Modifie une inscription existante (paramètre et/ou commentaire). Peut déplacer des membres en liste
    d'attente et envoyer des emails. Sans confirm=true : aperçu seulement."""
    body = _clean({"signupId": signup_id, "signupParameter": signup_parameter, "signupComment": signup_comment})
    return await _write("PUT", "/signups", body, confirm, "Des emails automatiques peuvent partir.")


@mcp.tool()
@tool_errors
async def delete_signup(signup_id: int, send_emails: bool = True, confirm: bool = False) -> Any:
    """Supprime une inscription par son identifiant. send_emails (vrai par défaut) prévient les membres concernés
    par email. Sans confirm=true : aperçu seulement."""
    body = {"signupId": signup_id, "sendEmails": send_emails}
    return await _write("DELETE", "/signups", body, confirm)


@mcp.tool()
@tool_errors
async def delete_signup_by_user(date: str, field_id: int, user_id: int, send_emails: bool = True,
                                confirm: bool = False) -> Any:
    """Supprime l'inscription d'un membre dans un champ donné d'une journée. send_emails (vrai par défaut)
    prévient par email. Sans confirm=true : aperçu seulement."""
    body = {"date": _date(date), "fieldId": field_id, "userId": user_id, "sendEmails": send_emails}
    return await _write("DELETE", "/signups", body, confirm)


@mcp.tool()
@tool_errors
async def delete_all_field_signups(date: str, field_id: int, send_emails: bool = True, confirm: bool = False) -> Any:
    """Supprime TOUTES les inscriptions d'un champ pour une journée. send_emails (vrai par défaut) prévient
    chaque membre par email. Sans confirm=true : aperçu seulement."""
    body = {"date": _date(date), "fieldId": field_id, "deleteAllSignups": True, "sendEmails": send_emails}
    return await _write("DELETE", "/signups", body, confirm, "ATTENTION : supprime toutes les inscriptions du champ.")


# =============================================================== API : forum du jour
@mcp.tool()
@tool_errors
async def get_daily_forum(date: str) -> Any:
    """Lit les messages du forum d'une journée (AAAA-MM-JJ). Lecture seule (1 appel API)."""
    return await api.request("GET", f"/daily_forum/{_date(date)}")


@mcp.tool()
@tool_errors
async def post_daily_forum_message(date: str, user_id: int, text: str, confirm: bool = False) -> Any:
    """Publie un message dans le forum d'une journée, au nom du membre user_id. Sans confirm=true : aperçu seulement."""
    body = {"date": _date(date), "userId": user_id, "text": text}
    return await _write("POST", "/daily_forum", body, confirm)


@mcp.tool()
@tool_errors
async def update_daily_forum_message(message_id: int, text: str, confirm: bool = False) -> Any:
    """Modifie le texte d'un message du forum du jour. Sans confirm=true : aperçu seulement."""
    return await _write("PUT", "/daily_forum", {"messageId": message_id, "text": text}, confirm)


@mcp.tool()
@tool_errors
async def delete_daily_forum_message(message_id: int, confirm: bool = False) -> Any:
    """Supprime un message du forum du jour. Sans confirm=true : aperçu seulement."""
    return await _write("DELETE", "/daily_forum", {"messageId": message_id}, confirm)


# =============================================================== API : membres et rôles
@mcp.tool()
@tool_errors
async def get_users() -> Any:
    """Liste les membres du club (nom, email, téléphone, rôles, dernière visite). Données personnelles. Lecture seule (1 appel API)."""
    return await api.request("GET", "/users")


@mcp.tool()
@tool_errors
async def create_user(first_name: str, name: str, email: str, phone_number: Optional[str] = None,
                      preferred_language: str = "fr", roles: Optional[list[int]] = None,
                      confirm: bool = False) -> Any:
    """Crée un membre (un email d'activation lui est envoyé). roles = liste d'identifiants de rôles (voir get_roles).
    Sans confirm=true : aperçu seulement."""
    body = _clean({"firstName": first_name, "name": name, "email": email, "phoneNumber": phone_number,
                   "preferredLanguage": preferred_language, "roles": roles})
    return await _write("POST", "/users", body, confirm, "Un email d'activation sera envoyé au membre.")


@mcp.tool()
@tool_errors
async def update_user(user_id: int, first_name: Optional[str] = None, name: Optional[str] = None,
                      phone_number: Optional[str] = None, roles: Optional[list[int]] = None,
                      confirm: bool = False) -> Any:
    """Modifie un membre (prénom, nom, téléphone, rôles). roles REMPLACE la liste complète des rôles
    (identifiants, voir get_roles). Sans confirm=true : aperçu seulement."""
    body = _clean({"userId": user_id, "firstName": first_name, "name": name,
                   "phoneNumber": phone_number, "roles": roles})
    return await _write("PUT", "/users", body, confirm,
                        "roles remplace l'ensemble des rôles du membre." if roles is not None else "")


@mcp.tool()
@tool_errors
async def delete_user(user_id: int, confirm: bool = False) -> Any:
    """Supprime un membre du club. Irréversible. Sans confirm=true : aperçu seulement."""
    return await _write("DELETE", "/users", {"userId": user_id}, confirm, "ATTENTION : suppression irréversible.")


@mcp.tool()
@tool_errors
async def get_roles() -> Any:
    """Liste les rôles du club (identifiant et nom). Lecture seule (1 appel API)."""
    return await api.request("GET", "/roles")


# =============================================================== API : événements
@mcp.tool()
@tool_errors
async def get_next_events() -> Any:
    """Liste les prochains événements du club, regroupés par date. Lecture seule (1 appel API)."""
    return await api.request("GET", "/next_events")


@mcp.tool()
@tool_errors
async def create_event(date: str, title: str, duration: int = 1, confirm: bool = False) -> Any:
    """Crée un événement à une date (AAAA-MM-JJ) avec un titre et une durée en jours. Sans confirm=true : aperçu seulement."""
    body = {"date": _date(date), "title": title, "duration": duration}
    return await _write("POST", "/events", body, confirm)


@mcp.tool()
@tool_errors
async def update_event(event_id: int, title: Optional[str] = None, date: Optional[str] = None,
                       duration: Optional[int] = None, confirm: bool = False) -> Any:
    """Modifie un événement (identifiant = fieldId renvoyé par get_next_events). La doc n'illustre que le titre ;
    date et durée sont transmises si fournies. Sans confirm=true : aperçu seulement."""
    body = _clean({"id": event_id, "title": title, "date": _date(date) if date else None, "duration": duration})
    return await _write("PUT", "/events", body, confirm)


@mcp.tool()
@tool_errors
async def delete_event(event_id: int, delete_all: bool = False, confirm: bool = False) -> Any:
    """Supprime un événement. delete_all=true supprime toutes les occurrences d'un événement sur plusieurs jours.
    Sans confirm=true : aperçu seulement."""
    return await _write("DELETE", "/events", {"id": event_id, "delete_all": delete_all}, confirm)


# =============================================================== API : forum général
@mcp.tool()
@tool_errors
async def get_forum_conversations() -> Any:
    """Lit les conversations du forum général du club avec leurs messages. Lecture seule (1 appel API)."""
    return await api.request("GET", config.FORUM_CONVERSATIONS_URL)


@mcp.tool()
@tool_errors
async def get_api_usage() -> Any:
    """Indique la consommation locale du quota API (appels aujourd'hui / 300, dernière minute / 20). N'appelle pas l'API."""
    return api.limiter.usage()


# =============================================================== Messagerie (navigateur)
@mcp.tool()
@tool_errors
async def list_messages(folder: str = "inbox", page: int = 1, page_size: int = 20,
                        unread_only: bool = False) -> Any:
    """Liste les conversations de la messagerie Click n' Glide (messages envoyés aussi par email), les plus récentes
    d'abord. folder : « inbox » (reçus), « sent » (où j'ai écrit) ou « all ». Paginé (page, page_size ≤ 100).
    N'ouvre aucune conversation : rien n'est marqué comme lu. Utilise le navigateur headless (pas le quota API)."""
    if folder not in ("inbox", "sent", "all"):
        raise ValueError("folder doit valoir 'inbox', 'sent' ou 'all'.")
    return await messenger.list_messages(folder, page, page_size, unread_only)


@mcp.tool()
@tool_errors
async def read_message(conversation_id: int, mark_as_read: bool = False, include_html: bool = False) -> Any:
    """Lit une conversation complète de la messagerie (tous les messages, du plus ancien au plus récent).
    Par défaut ne la marque pas comme lue ; mark_as_read=true l'ouvre dans l'application pour la marquer lue."""
    return await messenger.read_message(conversation_id, mark_as_read, include_html)


@mcp.tool()
@tool_errors
async def list_recipients() -> Any:
    """Liste les destinataires sélectionnables dans la messagerie : membres (id, nom, rôles) et groupes
    (« Tous » et un groupe par rôle, avec le nombre de membres)."""
    return await messenger.list_recipients()


@mcp.tool()
@tool_errors
async def send_message(subject: str, text: str, recipient_ids: Optional[list[int]] = None,
                       recipient_names: Optional[list[str]] = None, groups: Optional[list[str]] = None,
                       confirm: bool = False) -> Any:
    """Envoie un nouveau message via la messagerie Click n' Glide (il part aussi par email). Destinataires :
    recipient_ids et/ou recipient_names (prénom nom) et/ou groups (clés de list_recipients, « * » = tous).
    Sans confirm=true : renvoie seulement l'aperçu avec la liste résolue des destinataires, rien n'est envoyé."""
    return await messenger.send_message(subject, text, recipient_ids, recipient_names, groups, confirm=confirm is True)


def main() -> None:
    log.info("Démarrage du serveur MCP Click n' Glide (stdio). API key: %s, login: %s",
             "définie" if config.secret("CLICKNGLIDE_API_KEY") else "absente",
             "défini" if config.secret("CLICKNGLIDE_LOGIN") else "absent")
    mcp.run("stdio")


if __name__ == "__main__":
    main()
