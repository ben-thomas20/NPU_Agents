#!/usr/bin/env python3
"""
Phase 2 scheduler (skeleton). Do not deploy until manual briefing proves its value.

Polls Google Calendar every 15 minutes, finds meetings starting in the next 30 to 45
minutes that carry a "[candidate]" or "[partner]" tag, fires the brief-founder skill for
each, and ships the output to a Slack DM via webhook.

Run via cron or a launchd job on Jason's machine, e.g.:
    */15 * * * * cd /path/to/nextplayu-agents && python3 scripts/schedule-briefs.py

This file is intentionally a skeleton. Wire up the calendar read and Slack post when ready.
"""

import os
import subprocess
from datetime import datetime, timedelta, timezone

# Window: fire for meetings starting between LEAD_MIN and LEAD_MAX from now.
LEAD_MIN = timedelta(minutes=30)
LEAD_MAX = timedelta(minutes=45)
TAGS = ("[candidate]", "[partner]")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def upcoming_tagged_meetings():
    """Return calendar events starting within the lead window that carry a known tag.

    TODO: implement against the same Google OAuth creds used by the gcal MCP, or shell
    out to a helper. Each item should expose at least: summary, start time, attendees.
    """
    raise NotImplementedError("Hook up Google Calendar read before deploying.")


def run_brief(meeting_summary: str) -> str:
    """Invoke the brief-founder skill headlessly for one meeting and capture the brief."""
    prompt = (
        f"Brief me on the meeting titled '{meeting_summary}' using the brief-founder skill."
    )
    result = subprocess.run(
        ["claude", "-p", prompt],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def post_to_slack(text: str) -> None:
    """Send the brief to Jason's Slack DM via incoming webhook."""
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set; printing instead.\n")
        print(text)
        return
    # TODO: POST {"text": text} to SLACK_WEBHOOK_URL with urllib or requests.
    raise NotImplementedError("Hook up Slack webhook before deploying.")


def main() -> None:
    now = datetime.now(timezone.utc)
    window_start, window_end = now + LEAD_MIN, now + LEAD_MAX
    print(f"Checking for tagged meetings between {window_start} and {window_end} UTC.")

    for event in upcoming_tagged_meetings():
        summary = event.get("summary", "")
        if not any(tag in summary.lower() for tag in TAGS):
            continue
        brief = run_brief(summary)
        post_to_slack(brief)


if __name__ == "__main__":
    main()
