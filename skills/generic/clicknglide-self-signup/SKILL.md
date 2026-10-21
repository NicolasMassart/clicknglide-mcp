---
name: clicknglide-self-signup
description: Use when the user wants to sign THEMSELVES up on the Click n' Glide planning (or cancel or change their own signup) for one or more days, in a given slot such as pilot, student, instructor, tow pilot, maintenance or overnight stay, for example "sign me up as tow pilot on Saturday" or "put me down for the 14th, I'll arrive late".
---

# Sign the user up on the Click n' Glide planning

Follow the ground rules in `clicknglide-getting-started` (preview, then explicit consent, then `confirm: true`). For signing up other members, see `clicknglide-signups`.

## 1. Find the user's own `userId` (once)

- If you already know it (your private notes or memory), reuse it.
- Otherwise, call `get_users` once and match on the user's Click n' Glide login email (ask them for it if unknown), or on their first name + last name. If several members match, ask the user.
- Save the `userId` in your **private** notes or memory for next time. Never put it in a shared skill or file.
- Note the user's roles from the same response: they decide which slots the user may sign up in.

## 2. Resolve the date or dates

- Turn natural language ("Saturday", "the 14th", "next weekend", "every Wednesday in November") into ISO dates (YYYY-MM-DD) in the user's time zone.
- **Check the weekday:** if the user says "Saturday the 14th" but the 14th is not a Saturday, ask before going further.
- "Saturday" means the next upcoming Saturday. Say which date you picked.
- For several days, list them all and use one `get_signups_range` call instead of one call per day.

## 3. Find the slot (`fieldId`)

1. Read the day's planning: `get_signups(date)`, or `get_signups_range` for several days.
2. Map the requested slot to a field by its `fieldName` and `roleAllowed`, for example:
   - "pilot" → licensed pilots, "student" → students, "instructor", "tow pilot"
   - "maintenance", "overnight stay"
   Use the club skill's table if one exists.
3. Check that the user holds the field's `roleAllowed` role; otherwise the API refuses.
4. Note the field's parameter:
   - `parameterType`, `parameterName` (for example "number of students"), `parameterDefaultValue`
   - `signupLimit` (if full, the user goes on the waiting list)
   - `commentAllowed`
5. Event slots (one-off fields with an `eventDuration`, from `get_next_events`) work the same way.

## 4. Check the current state

- If the user is **already signed up** in that field that day, say so and offer to update the comment or parameter instead of adding a second signup.
- Mention useful context in one line, for example "no tow pilot yet that day" or "student slots full: you would be on the waiting list".

## 5. Preview, consent, write

- **Add:** `add_signup(date, field_id, user_id, signup_parameter?, signup_comment?)` without `confirm`.
  - Add the comment if the user gave one ("I'll arrive late"), and only if `commentAllowed`.
  - Set the parameter only if the field defines one and the user specified it; otherwise the default applies.
- **Change:** `update_signup(signup_id, signup_parameter?, signup_comment?)`.
- **Cancel:** `delete_signup(signup_id, send_emails)`. Ask whether others should be notified if the cancellation matters (for example the only tow pilot).
- Show a short preview: date and weekday, slot, comment, parameter. Several days go in one preview listing every date.
- After an explicit yes, run each call with `confirm: true`, then report the result per day, including any emails Click n' Glide said it sent.
