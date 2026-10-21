"""Sélecteurs de l'application web https://app.clicknglide.com (SPA React).

Déduits du bundle JavaScript public (assets/index-*.js) et vérifiés sur une session
connectée en octobre 2026 (interface en français). Pour les ajuster sans toucher au code, créez un
fichier JSON (par défaut state/selectors.json, ou le chemin de CLICKNGLIDE_SELECTORS_FILE)
contenant uniquement les clés à remplacer, par ex. {"compose_send_button": "..."}.
"""
from __future__ import annotations

import json
import logging
import os

from . import config

log = logging.getLogger("clicknglide_mcp.selectors")

DEFAULTS: dict[str, str] = {
    # --- Connexion (2 étapes : email puis mot de passe) ---
    "login_container": ".login_container",
    "login_email": "form input[name='email'][type='email']",
    "login_password": "form input[name='password'][type='password']",
    "login_submit": ".login_container form button.large_button, .login_container form button[type=submit]",
    "login_stay_connected": "input#cookie[type='checkbox']",
    "login_error": ".error_login",
    # Indices d'une étape non gérée (on s'arrête net, jamais de contournement)
    "captcha": "iframe[src*='recaptcha'], iframe[src*='hcaptcha'], iframe[src*='turnstile'], .g-recaptcha, .h-captcha, .cf-turnstile",
    "otp": "input[autocomplete='one-time-code'], input[name*='otp' i], input[name*='totp' i], input[name*='2fa' i]",
    # --- Application connectée ---
    "logged_in": "#left_menu, #bottom_menu",
    "messenger_page": ".messenger",
    # --- Nouveau message (/messenger/new) ---
    "compose_title": ".new_conversation_title input[type='text']",
    "compose_members_selection": ".members_selection",
    "compose_recipient_input": ".members_selection .select_control input",
    "compose_recipient_option": ".select_menu [id*='-option-']",
    "compose_selected_recipient": ".members_selection .selected_multi_value",
    "compose_group_buttons": ".members_selection button",
    "compose_editor": ".item_text_editor .ql-editor",
    "compose_send_button": "div.large_button:has-text('mail')",
    "compose_error": ".error_message",
    # Libellés des boutons de groupe spéciaux (alternatives séparées par « | », FR et EN).
    # Les autres boutons portent le nom du rôle. Si un bouton est introuvable, le serveur
    # ajoute les membres un par un à la place.
    "group_label_all": "Tous les membres|All members",
    "group_label_member_management": "Contact gestion des membres|Member management contact",
}

# Fragments d'URL des réponses JSON que l'application charge elle-même (lecture seule ;
# on se contente d'observer le trafic de la page, sans appeler ces routes directement).
URL_PATTERNS: dict[str, str] = {
    "conversations": "/api/messenger_conversations/",
    "users": "/api/users/",
    "send_message": "/api/messenger_message/",
    "login": "/api/login",
    "myself": "/api/myself",
}


# Base IndexedDB où l'application met en cache ses requêtes (vidée avant chaque lecture).
CLIENT_CACHE_DB = "keyval-store"


def load() -> dict[str, str]:
    sel = dict(DEFAULTS)
    path = os.environ.get("CLICKNGLIDE_SELECTORS_FILE", str(config.STATE_DIR / "selectors.json"))
    if os.path.exists(path):
        try:
            with open(path) as f:
                override = json.load(f)
            sel.update({k: v for k, v in override.items() if isinstance(v, str)})
            log.info("Sélecteurs surchargés depuis %s : %s", path, sorted(override))
        except Exception as e:  # noqa: BLE001
            log.warning("Fichier de sélecteurs illisible (%s) : %s", path, e)
    return sel
