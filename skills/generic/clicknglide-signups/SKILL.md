---
name: clicknglide-signups
description: Use when the user asks to sign a member up for, or remove them from, a Click n' Glide planning day, change a signup's comment or parameter, or add intro flights (or any free-text line) to a day's planning, one by one or in bulk.
---

# Manage Click n' Glide planning signups

Follow the ground rules in `clicknglide-getting-started`. Every change here uses the preview first, then `confirm: true` only after explicit consent.

## Identify the target

1. Resolve the date (YYYY-MM-DD) and the field. If needed, call `get_signups` for that date to see the fields, their `fieldType`, the role allowed and the current signups.
2. For a member signup, find the member's `userId` with `get_users`, or from an existing signup. If several members match the name, ask the user which one. Check that the member holds the field's `roleAllowed`, otherwise the API will refuse.

## Add

- **Member field** (`fieldType: username`): `add_signup(date, field_id, user_id, signup_parameter?, signup_comment?)`. Use the parameter only if the field defines one; otherwise the default applies.
- **Free-text field** (for example intro flights): `add_freetext_signup(date, field_id, text)`, or `add_freetext_signups_bulk(date, field_id, texts[])` for several lines. Follow the club's text convention if a club skill defines one, for example voucher number, name, phone and time.
- **Preview:** state the date, field, member or text, and that Click n' Glide may email the member (confirmation, waiting list).

## Change

- `update_signup(signup_id, signup_parameter?, signup_comment?)`. Get the `signupId` from `get_signups`. Lowering a capacity can move others to a waiting list and email them, so say so in the preview.

## Remove

- One signup: `delete_signup(signup_id, send_emails)`, or `delete_signup_by_user(date, field_id, user_id, send_emails)`.
- A whole field for a day: `delete_all_field_signups(date, field_id, send_emails)`. This is destructive: list the signups that will be removed and ask for explicit consent.
- `send_emails` defaults to true (members are notified). Ask the user if they want notifications when it is not obvious.

## After a confirmed change

Read back with `get_signups` for the date (one call) only if the user wants verification, or if the response looks unusual. The write response already contains the updated fields. Report what changed and which emails Click n' Glide said it sent (`additionalInfo`).
