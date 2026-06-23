---
name: pipeline-review
description: Phase 3. Generate a weekly pipeline review for Jason. Reads Airtable Candidates with status changes in the last 7 days and the week's Granola notes, then produces a one-pager covering hot candidates, stalled threads, roles needing sourcing, and replies Jason owes. Use when Jason says "pipeline review", "what's the state of the pipeline", "weekly recap", or any variant. Not yet built out. Confirm scope with the user before running.
---

# Weekly Pipeline Review (Phase 3 — placeholder)

This skill is planned but not yet implemented. Do not run it as if it were complete.
When asked for a pipeline review, tell the user this is Phase 3 and outline the steps below,
then offer to build it out.

## Intended workflow

1. Query Airtable for all Candidates with a status change in the last 7 days. Note movements both ways.
2. Read all Granola notes from the past week via the `granola` MCP.
3. Synthesize a one-pager with these sections:
   - **Hot candidates**: moving forward, worth Jason's time this week.
   - **Stalled threads**: no movement, at risk of going cold.
   - **Roles needing sourcing**: open roles with thin candidate pools.
   - **Replies owed**: candidates Jason has not answered.
4. Write the review to `workspaces/jason/briefs/YYYY-MM-DD-pipeline-review.md` and print to stdout.

## Style

- No em dashes. Short declarative sentences. No jargon.
- Lead with what needs action. Cut anything that does not change a decision.

## Trigger

"pipeline review" or scheduled Sunday night via cron (Phase 3 scheduler).
