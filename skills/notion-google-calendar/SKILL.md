---
name: notion-google-calendar
description: "Use when accessing Google Agenda via Notion Calendar."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [calendar, notion, google, scheduling]
    related_skills: []
---
# Google Agenda via Notion Calendar

## When to Use

Use for creating, changing, or reviewing this user's calendar events and daily agenda. **Google Agenda is the user's default**; do not ask which calendar provider on each request. Discover the Notion MCP calendar tools before starting a separate Google OAuth setup: Notion Calendar can expose connected Google calendars with write permissions even without local Google token files.

1. Use `mcp__notion__notion_calendar_list_calendars` and select the Google primary calendar with `isReadOnly: false` and account capability `writeEvents: true`. Do not confuse a Notion database calendar with Google Agenda.
2. Load schemas with tool_describe. Tools are plural: `mcp__notion__notion_calendar_create_events` and `mcp__notion__notion_calendar_list_events`.
3. Resolve the requested date and timezone. For relative dates, check the live local date rather than the conversation-start date or UTC date; use local midnight through the following midnight when querying a day. Preserve a previously confirmed absolute date across follow-up turns: a short addition such as a lunch time after reviewing tomorrow's agenda belongs to that reviewed day. Use `America/Sao_Paulo` for Brasília time. Act on a clear event-creation request without repeating a confirmation; ask only when a missing detail materially changes the event.
4. Create with an explicit calendar accountId/calendarId, DATE_TIME period with offset, summary, empty attendees and recurrenceRules for a single personal event, and disableConferencing true unless requested otherwise.
5. Read back with list_events over the requested time window and verify the eventId, title, calendar and start/end before reporting success.

## Reporting an agenda

- Show the requested absolute date and timezone, then list timed events chronologically.
- Separate all-day events from timed appointments; an all-day exam entry does not establish the exam's actual hour.
- Treat multiweek program entries as context, not as continuous attendance obligations. Preserve the concrete session's actual start/end and flag RSVP `needsAction`.
- Keep work-calendar entries labeled only `Busy` separate; do not invent their titles or assume overlapping blocks are duplicates.
- Exclude another person's shared calendar from the user's commitments unless participation is established or the user requests it; access to a shared calendar does not establish attendance.
- After creating an event, confirm only the verified title, absolute date, time range, and timezone in a short sentence.

Never store credentials or assume account/calendar IDs from old sessions; discover them anew.
