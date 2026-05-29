# Morning briefing cron prompt
# Used by: hermes cron create "30 8 * * *" --prompt "$(cat crons/briefing-prompt.md)"
#
# Prerequisites: Google Workspace skill set up (see docs/03-google-workspace.md)

IMPORTANT: First run `date` to get today's exact date and day of week. Use that - never guess.

Compile a morning briefing for YOUR_NAME. Deliver it to Telegram.

GMAIL:
- Search: is:unread newer_than:7d -category:promotions -category:social -category:updates
- Skip: newsletters, shipping/tracking, automated CI notifications, marketing emails
- Include: personal emails, job-related, finance/legal, anything that needs action
- Summarize each important email in 1 line max

CALENDAR:
- Check today's events
- On Sundays only: show the full week ahead

WEATHER:
- Today's forecast: curl -s "wttr.in/YOUR_CITY?format=%C+%t+%h+%w"

AI/TECH NEWS (last 24h):
- New model releases
- Major AI incidents or outages
- Notable announcements
- Keep to 3-5 bullets max

ACTION ITEMS:
- List anything requiring attention today (from emails, calendar, news)

FORMAT:
- Start with: "Good morning! It's [Day], [Date]."
- Short, scannable, use emojis for sections
- Under 60 seconds to read

Deliver as text to Telegram.
