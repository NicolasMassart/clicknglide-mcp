---
name: clicknglide-members
description: Use when the user asks to add a new member to Click n' Glide, give or change a member's rights or roles (for example a student going solo, then licensed), update a member's name or phone, or remove a member.
---

# Add and manage Click n' Glide members with the right roles

Follow the ground rules in `clicknglide-getting-started`. Roles decide which planning fields a member can sign up in and which messenger groups they receive, so get them right.

## Before anything: the member type to roles table

Use the club skill's table if one exists (for example `skills/clubs/<club>/`). Otherwise build it:

1. `get_roles` for ids and names.
2. From `get_users` (one call), count which role combinations current members actually hold. Use anonymous counts only, never names.
3. Propose a table to the user ("beginner student → roles …", "licensed pilot → …") and get it confirmed before using it.

## Privileged roles (administrator, member management, billing)

Ids `0`, `-1`, `-2` or equivalents:
- **Never at creation**, even if asked. Create the member with their normal roles first.
- Only for an **existing, activated member who has logged in recently**:
  - `lastVisit` from `get_users` is not `0000-00-00 00:00:00`
  - and it is within a threshold the club has validated (suggested default: **30 days**).
  If `lastVisit` is empty or too old, refuse and explain why: the account may not be activated, or may not be used by that person.
- Only on an **explicit request** naming the person and the role, with a before/after preview and an explicit yes.

## Add a new member

1. **Collect:** first name, last name, email, phone (optional), preferred language (`fr`, `en`…) and member type. Ask for anything missing; do not guess the email.
2. **Check for duplicates** with `get_users` (reuse a recent result if you have one):
   - same email, case-insensitive
   - same first name + last name, or a close variant
   If a match exists, stop and ask. It may be a returning member to update with `update_user` instead of a new account.
3. **Derive the roles** from the member type using the table. Show role names, not just ids. Flag any uncertain mapping. Never include privileged roles at creation (see above).
4. **Preview:** call `create_user(first_name, name, email, phone_number, preferred_language, roles)` **without** `confirm`. Tell the user that Click n' Glide **emails an activation link to the member** as soon as the account is created.
5. **Create:** only after an explicit yes, call again with `confirm: true`.
6. **Verify:** use `get_users` (one call) to check the new member's roles, then report the new `userId`.

## Change a member's roles (progression)

Examples: a beginner student going solo, then licensed; a pilot qualifying as tow pilot or intro-flight pilot; an instructor rating.

1. Find the member (`get_users`), then show their current roles.
2. Compute the new **complete** role list. Adding a privileged role follows the rule above (recent `lastVisit`, explicit request). `update_user(..., roles)` **replaces** all roles, so start from the current list, then add or remove. Keep roles the member must keep (for example the base role that lets licensed pilots still book instruction flights, if the club uses one).
3. Preview with `update_user(user_id, roles=[...])` without `confirm`. Show a "before → after" list. Apply only after explicit consent, then verify with `get_users`.

Name or phone changes use `update_user` the same way; omitted fields are left unchanged.

## Remove a member

`delete_user(user_id)` is irreversible. Confirm the identity (name + email) with the user, show the preview, and require an explicit yes. Suggest removing roles instead if the person may come back.
