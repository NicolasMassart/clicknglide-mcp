# clicknglide-mcp

An unofficial local [MCP](https://modelcontextprotocol.io) server (stdio) for [Click n' Glide](https://clicknglide.com), the online planning tool used by gliding clubs. It lets an AI assistant such as Grok Bot read and, with explicit confirmation, manage your club's planning and messages.

> **Not affiliated with Click n' Glide.** This project is community-made and is not endorsed or supported by Click n' Glide.

## What it does

- **Official API** (`https://api.clicknglide.com`, plus `https://clicknglide.com/api/forum_conversations`): one tool per documented endpoint ([Postman docs](https://documenter.getpostman.com/view/24880962/2s93RMVvfA)).
- **Messenger** (not covered by the API): drives the Click n' Glide web app (`https://app.clicknglide.com`) in a headless Chromium browser with Playwright, logged in with **your own account**.

## Skills

Ready-made assistant skills for this connector (generic ones in English, plus an example club configuration in French) are in [`skills/`](skills/README.md).

## Tools

| Area | Tools |
|---|---|
| Signups | `get_signups`, `get_signups_range`, `add_signup`, `add_freetext_signup`, `add_freetext_signups_bulk`, `update_signup`, `delete_signup`, `delete_signup_by_user`, `delete_all_field_signups` |
| Daily forum | `get_daily_forum`, `post_daily_forum_message`, `update_daily_forum_message`, `delete_daily_forum_message` |
| Members & roles | `get_users`, `create_user`, `update_user`, `delete_user`, `get_roles` |
| Events | `get_next_events`, `create_event`, `update_event`, `delete_event` |
| General forum | `get_forum_conversations` |
| Quota | `get_api_usage` (local counter, no API call) |
| Messenger (browser) | `list_messages` (inbox / sent / all, paginated), `read_message`, `list_recipients`, `send_message` |

Tool descriptions are in French.

## Important limits and caveats

- **API key**: it is provided by **Click n' Glide support** on request, is attached to your club and grants **full administrator rights**. Treat it like a password.
- **API rate limits**: 20 calls per minute and 300 per day. The server has a built-in limiter with a persistent daily counter (`state/api-usage.json`); it only counts calls made through this server.
- **Messenger**: uses a headless browser with your login and password. The browser session is kept in `state/browser-profile/`; delete that folder to log out. It relies on the web app's current structure and **may break if Click n' Glide changes its site**. Selectors live in `clicknglide_mcp/selectors.py` and can be overridden in `state/selectors.json` without touching the code.
- **Login safety**: on a captcha, 2FA prompt, wrong password or too many attempts, the server stops with an explicit error. It never tries to bypass them.
- **`confirm: true` guard**: every tool that creates, updates, deletes or sends requires `confirm: true`. Without it, the tool only returns a preview (the exact request, or the resolved recipient list for `send_message`) and does nothing.
- `read_message` does not mark the conversation as read unless `mark_as_read: true`.
- **Actually sending a message has not been tested yet.** Filling in the compose form was tested (stopping before the send button). Try your first real send with a short message to yourself.

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/NicolasMassart/clicknglide-mcp.git
cd clicknglide-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m playwright install --with-deps chromium   # --with-deps installs system libraries on Linux
```

## Add it to Grok Bot (local stdio connector)

- **command**: `/absolute/path/to/clicknglide-mcp/.venv/bin/python`
- **args**: `["-m", "clicknglide_mcp"]`
- **environment variables**:

| Variable | Required for | Description |
|---|---|---|
| `CLICKNGLIDE_API_KEY` | API tools | Club API key from Click n' Glide support |
| `CLICKNGLIDE_LOGIN` | Messenger tools | Your Click n' Glide login email |
| `CLICKNGLIDE_PASSWORD` | Messenger tools | Your Click n' Glide password |
| `CLICKNGLIDE_STATE_DIR` | optional | Where the browser session, counter and debug screenshots go (default: `./state`) |

Optional: `CLICKNGLIDE_SELECTORS_FILE` (selector overrides) and `CLICKNGLIDE_LOG_LEVEL` (logs go to stderr).

Secrets are read from the environment at call time and are never written to disk or logged. The server starts without them; the affected tools return a clear error. On failure, debug screenshots may be saved in `state/debug/`; they can contain your club's data.

## Quick test

```bash
.venv/bin/python tests/smoke_client.py               # tools/list + preview, no API call
.venv/bin/python tests/smoke_client.py --api         # also 3 read-only API calls
.venv/bin/python tests/smoke_client.py --messenger   # also read-only messenger listing
```

---

## En français

Serveur MCP local (stdio) **non officiel** pour [Click n' Glide](https://clicknglide.com), l'outil de planning des clubs de vol à voile. **Ce projet n'est pas affilié à Click n' Glide.**

- **Ce qu'il fait** : il expose toutes les fonctions de l'API officielle (inscriptions, forum du jour, membres, rôles, événements, forum général). Il donne aussi accès à la messagerie, qui n'est pas dans l'API, via un navigateur headless connecté avec **votre propre compte** : `list_messages`, `read_message`, `list_recipients` et `send_message`.
- **Clé API** : elle est fournie par le **support Click n' Glide**, rattachée au club, et donne des **droits d'administrateur**. Elle doit rester secrète.
- **Limites de l'API** : 20 appels par minute et 300 par jour. Un limiteur intégré tient un compteur journalier persistant.
- **Messagerie** : elle passe par un navigateur headless et **peut casser si Click n' Glide modifie son site**. Les sélecteurs peuvent être ajustés dans `state/selectors.json`. En cas de captcha ou de 2FA, le serveur s'arrête avec une erreur, sans jamais contourner.
- **Garde-fou `confirm: true`** : toute création, modification, suppression ou tout envoi exige `confirm: true`. Sinon, l'outil renvoie seulement un aperçu.
- **L'envoi réel d'un message n'a pas encore été testé** : seul le remplissage du formulaire l'a été. Faites un premier essai vers vous-même.
- **Installation** : `python3 -m venv .venv`, puis `.venv/bin/pip install -e .`, puis `.venv/bin/python -m playwright install --with-deps chromium`.
- **Skills** : des skills prêtes à l'emploi sont dans [`skills/`](skills/README.md), génériques en anglais et exemple de club en français.
- **Ajout dans Grok Bot** comme connecteur local stdio :
  - command : `/chemin/absolu/clicknglide-mcp/.venv/bin/python`
  - args : `["-m", "clicknglide_mcp"]`
  - variables : `CLICKNGLIDE_API_KEY`, `CLICKNGLIDE_LOGIN`, `CLICKNGLIDE_PASSWORD` et, en option, `CLICKNGLIDE_STATE_DIR`.

## License

MIT © 2026 Nicolas Massart
