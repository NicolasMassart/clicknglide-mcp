---
name: clicknglide-getting-started
description: Use before the first Click n' Glide task in a conversation, or when the user asks what the Click n' Glide connector can do, how to set it up, why a call failed (quota, missing key, login blocked), or how to discover their club's roles and planning fields.
---

# Click n' Glide connector: getting started

The `clicknglide` MCP connector exposes the official Click n' Glide API (planning signups, daily forum, members, roles, events, general forum) and the messenger, which goes through a headless browser logged in with the user's account.

## Ground rules (apply to every Click n' Glide skill)

1. **Preview, then explicit consent.** Every tool that creates, updates, deletes or sends has a `confirm` parameter. Call it first **without** `confirm` to get a preview. Show the preview to the user in plain words: what changes, for whom, and whether emails will go out. Call again with `confirm: true` only after the user explicitly says yes to that exact change. A general "go ahead" given earlier is not consent for a new change.
2. **Quota: 300 API calls a day, 20 a minute**, shared by the whole club key. Prefer `get_signups_range` over many `get_signups` calls, reuse results you already have in the conversation, and check `get_api_usage` before large jobs. Messenger tools use the browser and do not count toward the quota.
3. **Personal data.** `get_users` and signups return names, emails and phone numbers. Show only what the task needs, never paste member lists into public places, and never put member data in skills, notes or files you share.
4. **Admin key.** The API key has club-admin rights, and many writes trigger automatic emails to members (signup confirmations, waiting-list moves, deletions, account activation). Mention this in the preview.
5. **Never bypass a login block.** If a messenger tool reports a captcha, 2FA, wrong password or too many attempts, stop and tell the user. Do not retry in a loop.

## Discover the club configuration (once per conversation)

1. `get_roles`: list role ids and names. Roles control who can sign up in which planning field and form the messenger groups. Ids `0`, `-1` and `-2` (or similarly named administrator, member-management and billing roles) are privileged.
2. `get_signups_range` over a recent busy period (for example the last 2 to 4 weeks): for each field, note:
   - `fieldId`, `fieldName`, `column`
   - `fieldType`: `username` for a member signup, `freetext` for free-text lines
   - `roleAllowed` (who may sign up)
   - `parameterType` / `parameterName` / `parameterDefaultValue` (for example "number of students" for an instructor)
   - `signupLimit`, `commentAllowed`
   Fields with an `eventDuration` and a creator are events, not recurring fields.
3. `get_next_events`: upcoming one-off events.
4. Optionally `list_recipients`: messenger groups (one per role, plus "all members").
5. Summarize this configuration for the user and reuse it. If a club-specific skill exists (for example under `skills/clubs/<club>/`), prefer its tables and confirm they still match.

## Troubleshooting

- "CLICKNGLIDE_API_KEY n'est pas définie": the key is missing from the connector's environment. The key comes from Click n' Glide support.
- Daily quota reached: stop API work until tomorrow and tell the user. Messenger tools still work.
- Messenger "page non reconnue" or selector errors: the website may have changed. Report it with the screenshot path the tool returns.
