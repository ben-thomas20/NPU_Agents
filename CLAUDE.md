# NextPlayU Agents

This repo runs agents that support Jason and the recruiting team.

## Data sources

- Airtable base `appXXXX` is the system of record. Tables: Candidates, Roles, Meetings, Outreach, Notes.
- Granola holds meeting notes. Use the Granola MCP to query owned notes.
- Google Calendar holds upcoming meetings. Candidate calls are tagged with "[candidate]" in the title.
- Gmail holds email threads with candidates and partners. Access is read-only: search and read threads only. Never send, draft, modify, or delete mail.

## Conventions

- Candidate identifier is their LinkedIn URL (canonical, lowercased, no trailing slash).
- Meeting context is anything in the 90 days prior to a candidate meeting.
- All briefs are written to `workspaces/jason/briefs/YYYY-MM-DD-{candidate-slug}.md`.
- Output is plain markdown, no preamble, no postamble.

## Style

Jason prefers short declarative sentences, no em dashes, no jargon.
