---
name: brief-founder
description: Brief Jason before a meeting with a candidate or partner. Pulls the meeting from his calendar, the candidate record from Airtable, prior Granola notes, and any Gmail thread, then produces a structured pre-meeting brief. Use this whenever Jason or anyone says "brief me on my next meeting", "what's coming up", "prep me for [name]", "brief on tomorrow's [name] call", or any variant of asking for pre-meeting context. Also use proactively when the user mentions an upcoming meeting and seems to want context for it.
---

# Pre-Meeting Briefer

Generate a focused brief for Jason before a candidate or partner meeting.

## Inputs

You will need:

1. **The target meeting**. Either passed explicitly, or "the next one" from his calendar. Use the `gcal` MCP to list events. Candidate calls are tagged with "[candidate]" in the title; partner calls with "[partner]".
2. **The candidate or partner record** from Airtable. Match by email of the meeting attendee. Use the `airtable` MCP to query the Candidates table. If no match, check the Companies table for partner meetings.
3. **Prior Granola notes** mentioning this person or company. Use the `granola` MCP to search the last 90 days.
4. **Recent Gmail thread** with the attendee. Use the `gmail` MCP, search by `from:` or `to:` the attendee email, last 30 days. Read-only: search and read only. Never send, draft, modify, or delete mail, even if the MCP exposes those tools.

If any source returns nothing, note it in the brief rather than fabricating context.

## Workflow

1. Identify the target meeting. If the user said "next meeting", call `gcal.list-events` with `timeMin=now`, `maxResults=5`, pick the first one with a recognizable tag. If ambiguous, ask which meeting.
2. Pull attendee emails from the calendar event. Skip Jason's own email.
3. For each external attendee, look up the Airtable Candidates table by email. Note linked Roles, status, Clay score, source.
4. Query Granola for any note where the attendee was a participant or where the company name appears. Pull the full enhanced note text (not just summary).
5. Query Gmail for the most recent thread with the attendee. Pull the last 3 messages.
6. Synthesize into the format below. Aim for 250 to 400 words total. Brevity over completeness.
7. Write the brief to `workspaces/jason/briefs/YYYY-MM-DD-{candidate-slug}.md` and also print to stdout.

## Output format

```markdown
# {Candidate Name} — {Meeting Time}

**Role match**: {Role title} at {Company}
**Source**: {how we found them}
**Clay score**: {score}
**Status**: {sourced / contacted / replied / booked}

## Who they are

{2 to 3 sentences. Background, sport, current trajectory. No filler.}

## Why we matched them

{1 to 2 sentences. The thesis. What in their profile fits the role.}

## What we have said so far

{Bullet history. Each touch on its own line. Date, channel, key point. If first conversation, say so.}

## Suggested talking points

- {Specific question or topic tied to their background}
- {Specific question or topic tied to the role}
- {Something to validate or de-risk}
- {Optional: something personal you would not Google for}

## Open questions

- {Things we do not know that matter for the match}
- {Things they asked that we have not answered}

## Sources

- Airtable: {record link}
- Granola: {note link if any}
- Gmail: {thread link if any}
- LinkedIn: {URL}
```

## Style

- No em dashes anywhere.
- Short declarative sentences.
- No "Based on the available data..." style preambles. State things directly.
- If a section has nothing to say, omit it rather than padding.
- Talking points should be specific to this person, not generic. "Ask about their transition out of sport" is bad. "Ask how the move from D1 lacrosse to product management at Stripe shaped his view on team dynamics" is good.

## Edge cases

- **No Airtable match**: brief is shorter, lean on LinkedIn + Granola only. Flag at the top that this person is not in our system.
- **First meeting with no prior context**: skip the "What we have said so far" section. Replace with "First conversation."
- **Partner meeting not candidate**: same format, but "Role match" becomes "Partnership context" and the talking points orient around the partner relationship not a placement.
- **Recurring meeting (weekly 1:1 with same person)**: focus the brief on what changed since last time. Pull only the most recent Granola note.

## When NOT to brief

If the meeting is internal (only NextPlayU emails), skip it and say so. If it is a personal calendar event with no business context, skip it.
