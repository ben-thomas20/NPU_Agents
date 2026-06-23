---
name: draft-followup
description: Phase 2. Draft a post-meeting follow-up after a candidate or partner call. Reads the fresh Granola note, updates the Airtable Candidate status, drafts a follow-up email in Jason's voice, and suggests the next action. Use when Jason says "draft the follow-up for the [name] call", "what's next after that meeting", or any variant of post-meeting wrap-up. Not yet built out. Confirm scope with the user before running.
---

# Post-Meeting Follow-Up (Phase 2 — placeholder)

This skill is planned but not yet implemented. Do not run it as if it were complete.
When asked to draft a follow-up, tell the user this is Phase 2 and outline the steps below,
then offer to build it out.

## Intended workflow

1. Identify the meeting that just ended. Use `gcal` to find the most recent past event, or take the name from the user.
2. Read the fresh Granola note for that meeting via the `granola` MCP. Pull the full enhanced note, not the summary.
3. Update the Candidate record in Airtable: set status (replied, interested, declined, etc.) and log the touch in Notes.
4. Draft a follow-up email in Jason's voice. Load tone from `workspaces/jason/preferences.md`. Do not send. Output the draft for review.
5. Suggest one clear next action: book follow-up, intro to client, drop, or nurture. Tie it to what was said in the meeting.

## Style

- Match Jason's voice from `workspaces/jason/preferences.md`.
- No em dashes. Short declarative sentences. No jargon.
- The email is a draft only. Never send without explicit approval.

## Trigger

"draft the follow-up for the {name} call" or scheduled 1 hour after a meeting ends (Phase 2 scheduler).
