---
name: clicknglide-planning-summary
description: Use when the user asks who is flying or signed up on a given day, weekend or week, whether a flying day can happen, what is missing (tow pilot, instructor, helpers), or wants a planning digest from Click n' Glide.
---

# Summarize the Click n' Glide planning

Follow the ground rules in `clicknglide-getting-started`. This skill is read-only.

1. **Pick the dates.** Resolve "this weekend", "Wednesday" and similar phrases to ISO dates (YYYY-MM-DD) in the club's time zone. Use one `get_signups_range` call for several days instead of one call per day.
2. **Map the fields** with the club configuration (see `clicknglide-getting-started` or the club skill): tow pilots, instructors, students, licensed pilots, intro-flight pilots, free-text intro flights, helpers, and so on.
3. **For each day, report:**
   - signups per field (first names are usually enough), with the parameter when meaningful (for example the number of students an instructor accepts) and comments
   - free-text lines (for example booked intro flights) as given, without exposing phone numbers unless the user needs them
   - waiting lists, if the response shows them
   - the day's forum (`get_daily_forum`) only if the user asks, or if it matters (weather, cancellation)
4. **Flag what is missing** for flying to happen:
   - no tow pilot (or winch operator)
   - students but no instructor, or more students than the instructors' capacity
   - intro flights booked but no intro-flight pilot, or more intro flights than the pilots' declared count
   - nobody signed up at all
   Adapt to the club's rules, since some clubs need a minimum number of members on the field.
5. **Add events** from `get_next_events` that fall in the period.
6. **Keep it short:** one block per day, gaps first, then who is signed up. Offer to prepare a message to the relevant group to fill a gap (see `clicknglide-messages-forum`), but never send without consent.

For a recurring digest (for example every Friday for the weekend), propose a routine that runs this skill. One `get_signups_range` call per run keeps the quota low.
