# NextPlayU Pre-Meeting Briefer

A Claude Code agent that briefs Jason before every candidate or partner meeting. Built on the gtmiles model: shared filesystem + skills + MCP connectors, no workflow engine.

## What it does

Jason asks "brief me on my next meeting" and gets back, in one markdown page:

- Who he is meeting in 3 lines (background, current role, why they are in our pipeline)
- The match thesis (which role, why this person, what Clay scored them on)
- Conversation history (last touch, what was said, where it left off)
- 3 to 4 specific talking points
- Open questions and what we still do not know

Inputs are pulled live from Granola, Airtable, Google Calendar, and Gmail. No manual prep.

## Architecture

```
Calendar event ──┐
Airtable record ─┼──► Claude Code + brief-founder skill ──► Markdown brief
Granola notes ───┤                                          (stdout or Slack DM)
Gmail thread ────┘
```

- **Claude Code** is the runtime, on Jason's laptop or a shared box.
- **[skills/brief-founder/SKILL.md](skills/brief-founder/SKILL.md)** defines the agent's job.
- **[.mcp.json](.mcp.json)** wires up the four MCP servers (airtable, granola, gcal, gmail).
- **[CLAUDE.md](CLAUDE.md)** loads on every session with data sources, conventions, and style.

## Repo structure

```
.mcp.json                  MCP server config (committed)
.env                       Secrets (gitignored; copy from .env.example)
CLAUDE.md                  Project instructions Claude reads each session
skills/
  brief-founder/SKILL.md   The pre-meeting briefer (live)
  draft-followup/SKILL.md  Phase 2 placeholder
  pipeline-review/SKILL.md Phase 3 placeholder
workspaces/jason/
  briefs/                  Generated briefs by date (gitignored)
  preferences.md           Voice/tone notes for drafting
candidates/                Optional per-candidate cache
scripts/
  brief-next-meeting.sh    One-command wrapper
  schedule-briefs.py       Phase 2 scheduler skeleton
```

## Setup

1. **Install Claude Code:** `npm install -g @anthropic-ai/claude-code` (Node 20+). Set `ANTHROPIC_API_KEY` via env or `~/.claude/config.json`.
2. **Fill secrets:** `cp .env.example .env` and add the Airtable PAT + base ID, Granola key, and the Google Calendar OAuth creds. Mint the Calendar refresh token with the `calendar.readonly` scope only.
3. **Authorize Gmail (read-only):** see [Gmail setup](#gmail-setup) below. Gmail does not use `.env`.
4. **Verify MCP servers:** run `claude`, then `/mcp`. All four (airtable, granola, gcal, gmail) should show connected.

Other prerequisites: Airtable PAT with read access to the NextPlayU base (Candidates, Roles, Meetings, Outreach, Notes tables); Granola Business plan ($14/user/mo) for transcripts, Basic for enhanced notes (last 30 days only); a Google Cloud project with the Gmail and Calendar APIs enabled.

> Community MCP package names drift. Verify each at setup time; if one is unmaintained, fall back to the underlying API. The official Granola MCP is the source of truth for that integration.

### Gmail setup

Gmail uses [`@klodr/gmail-mcp`](https://www.npmjs.com/package/@klodr/gmail-mcp), authorized read-only. Read-only is enforced twice: Google rejects writes at the API, and the server only registers tools the granted scope allows, so write tools (`send`, `delete`, `draft`) never reach the agent.

1. **Google Cloud Console** ([console.cloud.google.com](https://console.cloud.google.com)): create a project, enable the **Gmail API**, and configure the **OAuth consent screen** (Internal if Jason is on a Workspace, otherwise External + add him as a Test user).
2. **Create an OAuth client ID**, type **Desktop app**. Download the JSON and save it to `~/.gmail-mcp/gcp-oauth.keys.json`.
3. **Run the read-only auth flow** as Jason:
   ```bash
   npx -y @klodr/gmail-mcp auth --scopes=gmail.readonly
   ```
   A browser opens. Jason logs in and approves. The consent screen should say only "Read your email" — not send or delete. The token is cached at `~/.gmail-mcp/credentials.json` (mode `0600`).
4. Confirm at [myaccount.google.com/permissions](https://myaccount.google.com/permissions) that the app lists read access only.

`.mcp.json` also sets `GMAIL_MCP_DRY_RUN=true` as defense in depth: even if a broader-scoped token is ever used by mistake, mutating calls become no-ops.

## Running it

```bash
cd nextplayu-agents
claude
> brief me on my next meeting
```

Claude reads `CLAUDE.md`, triggers the `brief-founder` skill, runs the workflow, writes the brief to `workspaces/jason/briefs/`, and prints it. Or run the wrapper from anywhere: `./scripts/brief-next-meeting.sh`.

For back-to-back meetings, be explicit: "brief me on the 2pm call" or "brief me on the meeting with {name}".

## Demoing to Jason

Show the output, not the architecture. Pick a real upcoming candidate meeting, run the briefer, hand him the brief, and ask: "Would this have saved you 20 minutes of prep?" If yes, wire up the rest. If it is thin in ways that matter, iterate on [SKILL.md](skills/brief-founder/SKILL.md) before adding sources.

## Roadmap

- **Phase 2 — [draft-followup](skills/draft-followup/SKILL.md):** after a meeting, read the fresh Granola note, update Airtable status, draft a follow-up in Jason's voice, suggest the next action.
- **Phase 2 — scheduler ([schedule-briefs.py](scripts/schedule-briefs.py)):** poll Calendar, fire the briefer 30 to 45 min before tagged meetings, ship to a Slack DM. Do not build until manual mode proves its value.
- **Phase 3 — [pipeline-review](skills/pipeline-review/SKILL.md):** weekly one-pager of hot candidates, stalled threads, roles needing sourcing, and replies Jason owes.

## Troubleshooting

- **Skill does not trigger.** The frontmatter `description` must list the trigger phrases; skills under-trigger by default. Make it pushy.
- **MCP server not connecting.** `/mcp` shows status. If red: check the package name is current, env vars are loaded, the API key is valid. OAuth refresh tokens expire; re-run the flow.
- **Brief is thin.** Confirm data was pulled. Temporarily add to the skill: "output a one-line summary of what each MCP returned." Empty source = missing data, not a bug. Data present but unused = tighten the synthesis instructions.
- **Granola returns nothing.** The MCP only returns notes Jason owns. If he was not the host or did not have Granola open, the note does not exist.
- **Brief reads generic.** Strengthen the negative examples in the "Suggested talking points" section of the skill.

## Reference

- gtmiles writeup: https://www.gtmiles.com
- [Claude Code docs](https://docs.claude.com/en/docs/claude-code) · [Skill format](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) · [MCP](https://modelcontextprotocol.io)
- [Granola docs](https://docs.granola.ai) · [Airtable MCP](https://github.com/domdomegg/airtable-mcp-server)
