# Skills for the Click n' Glide connector

Ready-made skills that teach an assistant (for example Grok Bot) how to use the `clicknglide` MCP connector safely. Each skill is a folder containing a `SKILL.md` file: YAML frontmatter (`name`, plus a `description` saying when to use it), then step-by-step instructions.

## Generic skills (any club, English)

| Skill | Use it when |
|---|---|
| [`clicknglide-getting-started`](generic/clicknglide-getting-started/SKILL.md) | first use, ground rules, discovering roles and fields, quota and errors |
| [`clicknglide-planning-summary`](generic/clicknglide-planning-summary/SKILL.md) | who is flying on a day or week, what is missing |
| [`clicknglide-self-signup`](generic/clicknglide-self-signup/SKILL.md) | signing yourself up, out or changing your own signup, for one or several days |
| [`clicknglide-signups`](generic/clicknglide-signups/SKILL.md) | signing members up or out, adding free-text lines such as intro flights |
| [`clicknglide-messages-forum`](generic/clicknglide-messages-forum/SKILL.md) | reading or summarizing messages and forums, sending a message to a group |
| [`clicknglide-inbox-digest`](generic/clicknglide-inbox-digest/SKILL.md) | digest of recent messages with the actions expected from you (works from a scheduled task) |
| [`clicknglide-members`](generic/clicknglide-members/SKILL.md) | adding a member with the right roles, changing roles, privileged-role rules |
| [`clicknglide-events`](generic/clicknglide-events/SKILL.md) | listing, creating, editing or deleting events |

## Club-specific skills

`clubs/<club>/` holds skills that add one club's configuration (role and field ids, groups, habits, reply templates) on top of the generic ones. Example: [`clubs/caen-falaise-planeurs/`](clubs/caen-falaise-planeurs/) (in French). To adapt it to your club, copy the folder, then run the discovery steps of `clicknglide-getting-started` to replace the ids and names. Never put member names, emails, phone numbers or message contents in a skill.

## Install in Grok Bot

- **Ask your bot:** "Save the skills from https://github.com/NicolasMassart/clicknglide-mcp/tree/main/skills/generic as my skills" (add the club folder if it applies to you). The bot reads each `SKILL.md` and registers it.
- **Or copy the folders:** put each skill folder (the folder that contains `SKILL.md`) into your bot's skills store, keeping the folder name.

The skills assume the connector is registered under the name `clicknglide` (see the main [README](../README.md)).

---

**En français :** des skills prêtes à l'emploi pour utiliser le connecteur en sécurité. `generic/` contient les skills pour tous les clubs (en anglais), `clubs/caen-falaise-planeurs/` un exemple de configuration de club (en français). Pour les installer dans Grok Bot, demandez à votre bot d'enregistrer les skills depuis ce dossier GitHub, ou copiez chaque dossier contenant un `SKILL.md` dans le store de skills de votre bot.
