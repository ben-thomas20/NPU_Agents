# NextPlayU Pre-Meeting Briefer

A Claude Code-based agent that briefs the founder before every candidate or partner meeting. Built on the gtmiles model: shared filesystem + skills + MCP connectors, no workflow engine.

## What this builds

A skill Jason can invoke before any meeting that returns:

- Who he is meeting in 3 lines (background, current role, why they are in our pipeline)
- The match thesis (which role, why this person, what Clay scored them on)
- Conversation history (last touch, what was said, where it left off)
- 3 to 4 specific talking points
- Open questions and things we still do not know

Inputs are pulled live from Granola, Airtable, Google Calendar, and Gmail. No manual prep.

## Architecture

```
Calendar event ──┐
Airtable record ─┼──► Claude Code + brief-founder skill ──► Markdown brief
Granola notes ───┤                                          (Slack DM or stdout)
Gmail thread ────┘
```

Three components do the work:

1. **Claude Code** as the runtime. Installed on Jason's laptop or a shared dev box.
2. **The `brief-founder` skill** at `skills/brief-founder/SKILL.md`. Defines the agent's job.
3. **MCP servers** for Granola, Airtable, Google Calendar, and Gmail. Configured once in `.mcp.json`.

Optional later: a cron or scheduled trigger that fires the skill 30 minutes before any tagged meeting and ships output to Slack.

## Prerequisites

- Node.js 20+ on the machine that will run Claude Code
- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- An Anthropic API key with sufficient credits
- Granola on Business plan ($14/user/mo) if you need transcripts. Basic plan works for enhanced notes only, limited to last 30 days
- Airtable Personal Access Token with read access to the NextPlayU base
- Google Workspace OAuth credentials for Calendar and Gmail MCPs
- The Airtable base from the schema work (Candidates, Roles, Meetings, Outreach, Notes tables)

## Repo structure

```
nextplayu-agents/
├── .mcp.json                      # MCP server config (committed)
├── .env                           # Secrets (gitignored)
├── .gitignore
├── CLAUDE.md                      # Project-level instructions Claude reads on every session
├── README.md                      # This file
├── skills/
│   ├── brief-founder/
│   │   └── SKILL.md               # The pre-meeting briefer
│   ├── draft-followup/            # Phase 2 (later)
│   └── pipeline-review/           # Phase 3 (later)
├── candidates/                    # Per-candidate context dumps (optional cache)
│   └── .gitkeep
├── workspaces/
│   └── jason/                     # Jason's personal context, briefs land here
│       ├── briefs/                # Generated briefs by date
│       └── preferences.md         # Voice/tone notes for outreach drafting
└── scripts/
    ├── brief-next-meeting.sh      # Wrapper to invoke the skill
    └── schedule-briefs.py         # Optional cron worker (Phase 2)
```

## Initial setup

### 1. Create the repo

```bash
mkdir nextplayu-agents && cd nextplayu-agents
git init
mkdir -p skills/brief-founder workspaces/jason/briefs candidates scripts
```

### 2. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # verify install
```

Set your API key in `~/.claude/config.json` or via env var `ANTHROPIC_API_KEY`.

### 3. Write `.gitignore`

```
.env
.env.local
workspaces/*/briefs/
candidates/cache/
node_modules/
.DS_Store
```

### 4. Write `.env`

```
ANTHROPIC_API_KEY=sk-ant-...
AIRTABLE_TOKEN=pat...
AIRTABLE_BASE_ID=app...
GRANOLA_API_KEY=...           # only if on Business plan and using API
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REFRESH_TOKEN=...
```

### 5. Write project-level `CLAUDE.md`

This loads on every Claude Code session in this repo. Keep it short.

```markdown
# NextPlayU Agents

This repo runs agents that support Jason (founder) and the recruiting team.

## Data sources

- Airtable base `appXXXX` is the system of record. Tables: Candidates, Roles, Meetings, Outreach, Notes.
- Granola holds meeting notes. Use the Granola MCP to query owned notes.
- Google Calendar holds upcoming meetings. Candidate calls are tagged with "[candidate]" in the title.
- Gmail holds email threads with candidates and partners.

## Conventions

- Candidate identifier is their LinkedIn URL (canonical, lowercased, no trailing slash).
- Meeting context is anything in the 90 days prior to a candidate meeting.
- All briefs are written to `workspaces/jason/briefs/YYYY-MM-DD-{candidate-slug}.md`.
- Output is plain markdown, no preamble, no postamble.

## Style

Jason prefers short declarative sentences, no em dashes, no jargon.
```

## MCP configuration

Write `.mcp.json` at the repo root. This tells Claude Code which MCP servers to load.

```json
{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": ["-y", "airtable-mcp-server"],
      "env": {
        "AIRTABLE_API_KEY": "${AIRTABLE_TOKEN}"
      }
    },
    "granola": {
      "command": "npx",
      "args": ["-y", "@granola/mcp-server"],
      "env": {
        "GRANOLA_API_KEY": "${GRANOLA_API_KEY}"
      }
    },
    "gcal": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_OAUTH_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_OAUTH_CLIENT_SECRET}",
        "GOOGLE_REFRESH_TOKEN": "${GOOGLE_OAUTH_REFRESH_TOKEN}"
      }
    },
    "gmail": {
      "command": "npx",
      "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_OAUTH_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_OAUTH_CLIENT_SECRET}",
        "GOOGLE_REFRESH_TOKEN": "${GOOGLE_OAUTH_REFRESH_TOKEN}"
      }
    }
  }
}
```

Note: the exact package names for community MCPs change. Verify each one at the time of setup. The official Granola MCP is the source of truth for that integration. If a package is not maintained, fall back to the underlying API.

Verify the servers load:

```bash
claude
> /mcp
```

You should see all four servers listed as connected.

## The brief-founder skill

Write this to `skills/brief-founder/SKILL.md`:

````markdown
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
4. **Recent Gmail thread** with the attendee. Use the `gmail` MCP, search by `from:` or `to:` the attendee email, last 30 days.

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
````

## Running it

### Manual invocation (start here)

```bash
cd nextplayu-agents
claude
> brief me on my next meeting
```

Claude reads `CLAUDE.md`, sees the `brief-founder` skill in `skills/`, triggers it on the request, runs the workflow, writes the brief to `workspaces/jason/briefs/`, and prints it.

### Wrapper script

Write `scripts/brief-next-meeting.sh`:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
claude -p "Brief me on my next candidate meeting using the brief-founder skill."
```

Make it executable: `chmod +x scripts/brief-next-meeting.sh`. Jason can run it with one command from anywhere.

### Scheduled mode (Phase 2)

Write `scripts/schedule-briefs.py` to poll Calendar every 15 minutes, identify meetings starting in the next 30 to 45 minutes, and fire the skill for each. Output goes to a Slack DM via webhook. Run via cron or a launchd job on Jason's machine.

This adds complexity. Do not build it until manual mode is proving its value.


### Phase 2: post-meeting follow-up agent

`skills/draft-followup/SKILL.md`. After a meeting ends:

- Read the fresh Granola note for that meeting
- Update the Candidate status in Airtable (replied, interested, declined, etc.)
- Draft a follow-up email in Jason's voice (his preferences live in `workspaces/jason/preferences.md`)
- Suggest the next action (book follow-up, intro to client, drop, etc.)

Trigger: "draft the follow-up for the {name} call" or scheduled 1 hour after meeting ends.

### Phase 3: weekly pipeline review

`skills/pipeline-review/SKILL.md`. Every Sunday night:

- Read all Airtable Candidates with status changes in the last 7 days
- Read all Granola notes from the week
- Generate a one-pager: hot candidates, stalled threads, roles needing more sourcing, candidates Jason owes a reply to

Trigger: "pipeline review" or scheduled cron.

## Troubleshooting

**Claude does not trigger the skill.** Check that the description in the frontmatter explicitly lists the trigger phrases. Skills under-trigger by default. Make the description pushy.

**MCP server not connecting.** Run `claude` then `/mcp` to see connection status. If a server shows red, check the package name is current, env vars are loaded, and the underlying API key is valid. For OAuth-based servers, the refresh token expires; re-run the OAuth flow.

**Brief is thin.** First check whether the data was actually pulled. Add a temporary debug line to the skill: "Before generating the brief, output a one-line summary of what each MCP returned." If a source returned nothing, the skill is working but the data is missing. If the source returned data but the brief did not use it, refine the synthesis instructions.

**Granola returns nothing for a known meeting.** Granola MCP only returns notes you own. If Jason was not the host or did not have Granola open, the note will not exist. This is a Granola limitation, not a skill bug.

**Brief reads generic.** The skill is pulling but not synthesizing. Tighten the "Suggested talking points" section in SKILL.md with stronger negative examples of what bad talking points look like. Claude responds well to "do this, not that" framing.

**Calendar query returns the wrong meeting.** The skill picks the first tagged event. If Jason has back-to-back meetings, be explicit: "brief me on the 2pm call" or "brief me on the meeting with {name}".

## Reference

- gtmiles writeup: https://www.gtmiles.com
- Claude Code docs: https://docs.claude.com/en/docs/claude-code
- Skill format: https://docs.claude.com/en/docs/agents-and-tools/agent-skills
- Granola integrations: https://docs.granola.ai
- Airtable MCP: https://github.com/domdomegg/airtable-mcp-server
- Model Context Protocol: https://modelcontextprotocol.io
