"""Messagerie Click n' Glide via Playwright headless (non couverte par l'API).

Principe : on pilote l'application web comme un utilisateur. Pour la lecture, on
observe les réponses JSON que la page charge elle-même (liste des conversations,
liste des membres), ce qui est plus robuste que de parser le DOM. Ouvrir une
conversation dans l'app la marque comme lue : read_message lit donc depuis la liste
sans ouvrir la conversation, sauf si mark_as_read=true.
"""
from __future__ import annotations

import asyncio
import html
import logging
import re
import time
from typing import Any

from . import config, selectors

log = logging.getLogger("clicknglide_mcp.messenger")


class MessengerError(RuntimeError):
    pass


class LoginBlocked(MessengerError):
    """Captcha, 2FA, compte bloqué ou identifiants refusés : intervention humaine requise."""


def _strip_html(s: str | None) -> str:
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def _person(first: str | None, name: str | None) -> str:
    return " ".join(x for x in (first, name) if x).strip()


class Messenger:
    def __init__(self) -> None:
        self._pw = None
        self._ctx = None
        self._lock = asyncio.Lock()
        self.sel = selectors.load()
        self._me_id: int | None = None
        self._users_cache: tuple[float, list[dict]] | None = None
        self._conv_cache: tuple[float, list[dict]] | None = None

    # ------------------------------------------------------------------ navigateur
    async def _context(self):
        if self._ctx is not None:
            return self._ctx
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:  # pragma: no cover
            raise MessengerError("Playwright n'est pas installé dans l'environnement du serveur.") from e
        config.ensure_dirs()
        self._pw = await async_playwright().start()
        self._ctx = await self._pw.chromium.launch_persistent_context(
            user_data_dir=str(config.BROWSER_PROFILE_DIR),
            headless=True,
            locale="fr-FR",
            timezone_id="Europe/Paris",
            viewport={"width": 1280, "height": 900},
        )
        self._ctx.set_default_timeout(20000)
        return self._ctx

    async def close(self) -> None:
        try:
            if self._ctx is not None:
                await self._ctx.close()
            if self._pw is not None:
                await self._pw.stop()
        finally:
            self._ctx = self._pw = None

    async def _new_page(self):
        ctx = await self._context()
        page = await ctx.new_page()
        return page

    async def _debug_shot(self, page, label: str) -> str | None:
        try:
            config.ensure_dirs()
            p = config.DEBUG_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{label}.png"
            await page.screenshot(path=str(p), full_page=True)
            return str(p)
        except Exception:  # noqa: BLE001
            return None

    # ------------------------------------------------------------------ connexion
    async def _wait_any(self, page, keys: list[str], timeout: float = 25.0) -> str | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for k in keys:
                try:
                    loc = page.locator(self.sel[k]).first
                    if await loc.count() and await loc.is_visible():
                        return k
                except Exception:  # noqa: BLE001
                    pass
            await asyncio.sleep(0.25)
        return None

    async def _check_blockers(self, page) -> None:
        for k, msg in (("captcha", "un captcha"), ("otp", "un code de vérification (2FA)")):
            loc = page.locator(self.sel[k]).first
            if await loc.count():
                shot = await self._debug_shot(page, k)
                raise LoginBlocked(
                    f"La connexion à Click n' Glide demande {msg}. Je ne le contourne pas : "
                    f"connectez-vous une fois manuellement ou contactez le support. (capture : {shot})"
                )

    async def _login_error_text(self, page) -> str | None:
        loc = page.locator(self.sel["login_error"]).first
        if await loc.count() and await loc.is_visible():
            return (await loc.inner_text()).strip()
        return None

    async def _ensure_logged_in(self, page, path: str = "/") -> None:
        await page.goto(config.APP_URL.rstrip("/") + path, wait_until="domcontentloaded")
        state = await self._wait_any(page, ["logged_in", "login_email", "login_password", "captcha", "otp"])
        if state == "logged_in":
            return
        await self._check_blockers(page)
        if state is None:
            shot = await self._debug_shot(page, "unknown-state")
            raise MessengerError(f"Page Click n' Glide non reconnue (ni connecté, ni formulaire de connexion). Capture : {shot}")
        login = config.require_secret("CLICKNGLIDE_LOGIN", "la messagerie Click n' Glide")
        password = config.require_secret("CLICKNGLIDE_PASSWORD", "la messagerie Click n' Glide")
        log.info("Connexion à Click n' Glide (session expirée ou absente)")
        if state == "login_email":
            await page.fill(self.sel["login_email"], login)
            await page.click(self.sel["login_submit"])
            nxt = await self._wait_any(page, ["login_password", "login_error", "captcha", "otp", "logged_in"], 20)
            await self._check_blockers(page)
            if nxt == "login_error":
                raise LoginBlocked(f"Connexion refusée à l'étape email : {await self._login_error_text(page)}")
            if nxt == "logged_in":
                return
            if nxt != "login_password":
                shot = await self._debug_shot(page, "login-step2")
                raise MessengerError(f"Champ mot de passe introuvable après l'email. Capture : {shot}")
        await page.fill(self.sel["login_password"], password)
        stay = page.locator(self.sel["login_stay_connected"]).first
        if await stay.count():
            try:
                if not await stay.is_checked():
                    await stay.check()
            except Exception:  # noqa: BLE001
                pass
        await page.click(self.sel["login_submit"])
        res = await self._wait_any(page, ["logged_in", "login_error", "captcha", "otp"], 25)
        await self._check_blockers(page)
        if res == "login_error":
            raise LoginBlocked(f"Connexion refusée par Click n' Glide : {await self._login_error_text(page)}")
        if res != "logged_in":
            shot = await self._debug_shot(page, "login-final")
            raise MessengerError(f"Connexion non confirmée (menu de l'application introuvable). Capture : {shot}")
        log.info("Connecté à Click n' Glide")
        if path != "/":
            await page.goto(config.APP_URL.rstrip("/") + path, wait_until="domcontentloaded")

    # ------------------------------------------------------------------ capture JSON
    async def _clear_client_cache(self, page) -> None:
        try:
            await page.evaluate("""() => new Promise(res => {
                try {
                    const r = indexedDB.deleteDatabase(%r);
                    r.onsuccess = r.onerror = r.onblocked = () => res(true);
                    setTimeout(() => res(false), 3000);
                } catch (e) { res(false); }
            })""" % selectors.CLIENT_CACHE_DB)
        except Exception:  # noqa: BLE001
            pass

    async def _load_and_capture(self, path: str, pattern_key: str, timeout: float = 25.0) -> Any:
        """Ouvre une page de l'app et renvoie le JSON de la première réponse GET dont l'URL
        contient URL_PATTERNS[pattern_key]."""
        pattern = selectors.URL_PATTERNS[pattern_key]
        page = await self._new_page()
        captured: list[Any] = []

        async def on_response(resp):
            try:
                if resp.request.method != "GET" or not resp.ok:
                    return
                if pattern in resp.url:
                    captured.append(await resp.json())
                elif selectors.URL_PATTERNS["myself"] in resp.url:
                    clubs = (await resp.json()).get("clubs") or []
                    active = next((c for c in clubs if str(c.get("activeClub")) in ("1", "true")), clubs[0] if clubs else {})
                    if active.get("myId") is not None:
                        self._me_id = int(active["myId"])
            except Exception:  # noqa: BLE001
                pass

        page.on("response", on_response)
        try:
            await self._ensure_logged_in(page, "/")
            # L'app garde ses données en cache local (IndexedDB « keyval-store », React Query)
            # et ne les redemande pas au serveur tant qu'elles sont fraîches : on vide ce cache
            # local (aucun effet côté serveur) pour forcer un chargement frais et observable.
            await self._clear_client_cache(page)
            captured.clear()
            await page.goto(config.APP_URL.rstrip("/") + path, wait_until="domcontentloaded")
            deadline = time.monotonic() + timeout
            while not captured and time.monotonic() < deadline:
                await asyncio.sleep(0.25)
            if not captured:
                shot = await self._debug_shot(page, f"no-{pattern_key}")
                raise MessengerError(
                    f"Données « {pattern_key} » non reçues en ouvrant {path} (motif d'URL {pattern}). "
                    f"Le site a peut-être changé ; ajustez URL_PATTERNS. Capture : {shot}")
            return captured[-1]
        finally:
            await page.close()

    async def _users(self, max_age: float = 300) -> list[dict]:
        if self._users_cache and time.time() - self._users_cache[0] < max_age:
            return self._users_cache[1]
        data = await self._load_and_capture("/messenger/new", "users")
        users = data.get("users", []) if isinstance(data, dict) else []
        self._users_cache = (time.time(), users)
        login = (config.secret("CLICKNGLIDE_LOGIN") or "").lower()
        for u in users:
            if login and str(u.get("email", "")).lower() == login:
                self._me_id = u.get("id")
        return users

    async def _me(self) -> int | None:
        if self._me_id is None:
            try:
                await self._users()
            except MessengerError:
                pass
        return self._me_id

    async def _conversations(self, refresh: bool = False, max_age: float = 120) -> list[dict]:
        if not refresh and self._conv_cache and time.time() - self._conv_cache[0] < max_age:
            return self._conv_cache[1]
        data = await self._load_and_capture("/messenger", "conversations")
        convs = data.get("messengerConversations", []) if isinstance(data, dict) else []
        self._conv_cache = (time.time(), convs)
        return convs

    # ------------------------------------------------------------------ outils
    async def list_messages(self, folder: str = "inbox", page: int = 1, page_size: int = 20,
                            unread_only: bool = False, refresh: bool = False) -> dict:
        async with self._lock:
            convs = await self._conversations(refresh=refresh or page == 1)
            me = await self._me()
        out = []
        for c in convs:
            msgs = c.get("messages") or []  # le plus récent en premier
            authors = {m.get("authorId") for m in msgs}
            if folder == "inbox" and me is not None and authors <= {me}:
                continue
            if folder == "sent" and (me is None or me not in authors):
                continue
            unread = sum(1 for m in msgs if m.get("viewed") is False)
            if unread_only and not unread:
                continue
            last = msgs[0] if msgs else {}
            out.append({
                "conversation_id": c.get("id"),
                "title": c.get("title"),
                "participants": [_person(r.get("firstName"), r.get("name")) for r in (c.get("recipients") or [])[:8]],
                "participant_count": len(c.get("recipients") or []),
                "message_count": len(msgs),
                "unread_count": unread,
                "last_message": {
                    "author": _person(last.get("authorFirstName"), last.get("authorName")),
                    "author_id": last.get("authorId"),
                    "date": last.get("creationDate"),
                    "excerpt": _strip_html(last.get("text"))[:200],
                },
            })
        out.sort(key=lambda x: str(x["last_message"]["date"] or ""), reverse=True)
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        start = (page - 1) * page_size
        return {
            "folder": folder,
            "note": "La messagerie Click n' Glide est organisée en conversations : « inbox » = conversations "
                    "contenant au moins un message d'un autre membre, « sent » = conversations où j'ai écrit."
                    + ("" if me is not None else " (Identifiant personnel non déterminé : filtre inbox/sent inactif.)"),
            "total": len(out),
            "page": page,
            "page_size": page_size,
            "has_more": start + page_size < len(out),
            "conversations": out[start:start + page_size],
        }

    async def read_message(self, conversation_id: int, mark_as_read: bool = False,
                           include_html: bool = False) -> dict:
        async with self._lock:
            convs = await self._conversations()
            conv = next((c for c in convs if str(c.get("id")) == str(conversation_id)), None)
            if conv is None:
                convs = await self._conversations(refresh=True)
                conv = next((c for c in convs if str(c.get("id")) == str(conversation_id)), None)
            if conv is None:
                raise MessengerError(f"Conversation {conversation_id} introuvable dans la messagerie.")
            if mark_as_read:
                page = await self._new_page()
                try:
                    await self._ensure_logged_in(page, f"/messenger/{conversation_id}")
                    await asyncio.sleep(3)
                finally:
                    await page.close()
        msgs = list(reversed(conv.get("messages") or []))
        return {
            "conversation_id": conv.get("id"),
            "title": conv.get("title"),
            "participants": [{"id": r.get("id"), "name": _person(r.get("firstName"), r.get("name"))}
                             for r in conv.get("recipients") or []],
            "marked_as_read": mark_as_read,
            "messages": [{
                "message_id": m.get("messageId"),
                "author": _person(m.get("authorFirstName"), m.get("authorName")),
                "author_id": m.get("authorId"),
                "date": m.get("creationDate"),
                "unread": m.get("viewed") is False,
                "text": _strip_html(m.get("text")),
                **({"html": m.get("text")} if include_html else {}),
            } for m in msgs],
        }

    async def list_recipients(self) -> dict:
        async with self._lock:
            users = await self._users(max_age=0)
            me = self._me_id
        members = [{"id": u.get("id"), "name": _person(u.get("firstName"), u.get("name")),
                    "roles": u.get("roles") or []} for u in users if u.get("id") != me]
        members.sort(key=lambda m: m["name"].lower())
        groups: dict[str, int] = {}
        for m in members:
            for r in m["roles"]:
                if r != "Billing_contact":
                    groups[r] = groups.get(r, 0) + 1
        return {
            "members": members,
            "groups": [{"name": "Tous", "member_count": len(members), "key": "*"}]
                      + [{"name": g, "member_count": n, "key": g} for g, n in sorted(groups.items())],
            "note": "Un groupe = un rôle du club ; le sélectionner ajoute tous ses membres. "
                    "Utilisez 'key' dans send_message.groups.",
        }

    async def _resolve(self, recipient_ids, recipient_names, groups) -> tuple[list[dict], list[str], list[str]]:
        users = await self._users()
        me = self._me_id
        pool = [u for u in users if u.get("id") != me]
        chosen: dict[Any, dict] = {}
        errors: list[str] = []
        valid_groups: list[str] = []
        for g in groups or []:
            members = pool if g in ("*", "Tous", "all") else [x for x in pool if g in (x.get("roles") or [])]
            if not members:
                errors.append(f"Groupe « {g} » inconnu ou vide")
                continue
            valid_groups.append("*" if g in ("*", "Tous", "all") else g)
            for u in members:
                chosen[u["id"]] = u
        for uid in recipient_ids or []:
            u = next((x for x in pool if str(x.get("id")) == str(uid)), None)
            if u:
                chosen[u["id"]] = u
            else:
                errors.append(f"Membre id {uid} introuvable")
        for name in recipient_names or []:
            n = name.strip().lower()
            hits = [x for x in pool if _person(x.get("firstName"), x.get("name")).lower() == n] or \
                   [x for x in pool if n in _person(x.get("firstName"), x.get("name")).lower()]
            if len(hits) == 1:
                chosen[hits[0]["id"]] = hits[0]
            elif not hits:
                errors.append(f"Aucun membre ne correspond à « {name} »")
            else:
                errors.append(f"« {name} » est ambigu : " + ", ".join(
                    f"{_person(h.get('firstName'), h.get('name'))} (id {h.get('id')})" for h in hits[:8]))
        return list(chosen.values()), errors, valid_groups

    async def send_message(self, subject: str, text: str, recipient_ids=None, recipient_names=None,
                           groups=None, confirm: bool = False, _dry_run_ui: bool = False) -> dict:
        if not subject.strip() or not text.strip():
            raise MessengerError("L'objet et le texte du message sont obligatoires.")
        async with self._lock:
            recipients, errors, valid_groups = await self._resolve(recipient_ids, recipient_names, groups)
            preview = {"subject": subject, "text": text, "recipient_count": len(recipients),
                       "groups": valid_groups,
                       "recipients": [{"id": u["id"], "name": _person(u.get("firstName"), u.get("name"))}
                                      for u in recipients]}
            if errors or not recipients:
                return {"executed": False, "errors": errors or ["Aucun destinataire"], "preview": preview}
            if not confirm and not _dry_run_ui:
                return {"executed": False, "preview": preview,
                        "message": "Aperçu uniquement : aucun message envoyé. Rappelez avec confirm=true "
                                   "pour l'envoyer (il partira aussi par email aux destinataires)."}
            return await self._send_via_ui(subject, text, recipients, valid_groups, preview,
                                           dry_run=_dry_run_ui or not confirm)

    async def _send_via_ui(self, subject, text, recipients, groups, preview, dry_run: bool) -> dict:
        """Remplit le formulaire /messenger/new. Avec dry_run=True, s'arrête juste avant le clic
        sur « Envoyer par e-mail » (sert à tester les sélecteurs sans rien envoyer)."""
        page = await self._new_page()
        sent: list[Any] = []

        async def on_response(resp):
            try:
                if selectors.URL_PATTERNS["send_message"] in resp.url and resp.request.method == "POST":
                    sent.append(await resp.json())
            except Exception:  # noqa: BLE001
                pass

        page.on("response", on_response)
        selected = page.locator(self.sel["compose_selected_recipient"])
        try:
            await self._ensure_logged_in(page, "/messenger/new")
            await page.wait_for_selector(self.sel["compose_members_selection"])
            # attendre que la liste des membres soit chargée dans le sélecteur
            await asyncio.sleep(1.5)
            if await selected.count() or (await page.locator(self.sel["compose_editor"]).first.inner_text()).strip():
                raise MessengerError("Le formulaire de nouveau message n'est pas vide (brouillon ?) : envoi annulé par sécurité.")
            await page.fill(self.sel["compose_title"], subject)
            group_labels = {"*": self.sel["group_label_all"],
                            "MemberManagementContact": self.sel["group_label_member_management"]}
            for g in groups:
                alts = [a.strip() for a in group_labels.get(g, g).split("|") if a.strip()]
                pattern = "|".join(re.escape(a) for a in alts)
                btn = page.locator(self.sel["compose_group_buttons"]).filter(
                    has_text=re.compile(rf"(^|\s)({pattern})\s*$"))
                if await btn.count() == 1:
                    await btn.first.click()
                else:
                    log.info("Bouton de groupe « %s » introuvable : ajout des membres un par un", g)
            already = set(t.strip() for t in await selected.all_inner_texts())
            for u in recipients:
                label = _person(u.get("firstName"), u.get("name"))
                if label in already:
                    continue
                inp = page.locator(self.sel["compose_recipient_input"]).first
                await inp.click()
                await inp.fill(label)
                opt = page.locator(self.sel["compose_recipient_option"]).filter(
                    has_text=re.compile(rf"^\s*{re.escape(label)}\s*$"))
                try:
                    await opt.first.wait_for(timeout=8000)
                except Exception:  # noqa: BLE001
                    shot = await self._debug_shot(page, "recipient-not-found")
                    raise MessengerError(f"Destinataire « {label} » introuvable dans le sélecteur. Capture : {shot}") from None
                if await opt.count() != 1:
                    raise MessengerError(f"Sélection ambiguë pour « {label} » ({await opt.count()} options).")
                await opt.first.click()
                already.add(label)
            n_sel = await selected.count()
            if n_sel != len(recipients):
                shot = await self._debug_shot(page, "recipients-mismatch")
                raise MessengerError(f"{n_sel} destinataires sélectionnés au lieu de {len(recipients)} : envoi annulé. Capture : {shot}")
            editor = page.locator(self.sel["compose_editor"]).first
            await editor.click()
            await page.keyboard.type(text)
            btn = page.locator(self.sel["compose_send_button"]).last
            await btn.wait_for()
            await asyncio.sleep(0.5)
            if "disabled" in (await btn.get_attribute("class") or ""):
                err = page.locator(self.sel["compose_error"]).first
                msg = (await err.inner_text()) if await err.count() else "bouton d'envoi désactivé"
                shot = await self._debug_shot(page, "send-disabled")
                raise MessengerError(f"Envoi impossible : {msg}. Capture : {shot}")
            if dry_run:
                shot = await self._debug_shot(page, "dry-run-ready")
                return {"executed": False, "dry_run": True, "selected_count": n_sel,
                        "message": "Formulaire rempli, bouton d'envoi actif ; arrêt avant l'envoi (test).",
                        "screenshot": shot, "preview": preview}
            await btn.click()
            deadline = time.monotonic() + 20
            while not sent and time.monotonic() < deadline:
                await asyncio.sleep(0.25)
            if not sent:
                shot = await self._debug_shot(page, "send-unconfirmed")
                raise MessengerError(f"Envoi non confirmé par le serveur (état inconnu, vérifiez la messagerie avant de réessayer). Capture : {shot}")
            res = sent[-1]
            ok = isinstance(res, dict) and res.get("result", "success") == "success"
            self._conv_cache = None
            return {"executed": ok, "server_response": res, "sent": preview}
        finally:
            await page.close()
