---
name: clicknglide-events
description: Use when the user asks about upcoming club events in Click n' Glide (meetings, courses, parties, work days) or wants to create, rename, move or delete an event.
---

# Click n' Glide events

Follow the ground rules in `clicknglide-getting-started`.

- **List:** `get_next_events` returns upcoming events grouped by date. Each event is a planning field with an `eventDuration` (in days) and its own signups. Who signed up is in `signups`. The event id used by the write tools is its `fieldId`.
- **Create:** `create_event(date, title, duration)` (duration in days). Preview, explicit yes, then `confirm: true`.
- **Edit:** `update_event(event_id, title?, date?, duration?)`. The official docs only show changing the title, so tell the user that moving dates is untested and check the result with `get_next_events`.
- **Delete:** `delete_event(event_id, delete_all)`. `delete_all: true` removes every day of a multi-day event. Before asking for consent, show the user the event, its dates and how many members are signed up.
- **After creating an event,** offer to announce it with the messenger (see `clicknglide-messages-forum`). Never send without consent.
