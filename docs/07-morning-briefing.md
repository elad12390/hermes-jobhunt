# 7. Morning Briefing

Every morning at 9:00am (configurable), Hermes compiles a briefing from your Gmail, Calendar, and live data sources and delivers it to your Telegram DMs.

## What's in the briefing

- **Unread emails** - filtered, summarized 1-line each, skips newsletters/promotions
- **Today's calendar events** - including a weekly preview on Sundays
- **Weather** - current conditions for your city
- **AI news** - new models, major releases, notable incidents (last 24h)
- **GitHub** - new issues on any repos you care about
- **Action items** - anything that needs your attention today

## Prerequisites

- Google Workspace set up (see doc 03)
- Telegram configured (see doc 02)

## Create the cron

```bash
hermes cron create "0 9 * * *" \
  --name "Morning Briefing" \
  --model claude-sonnet-4-6 \
  --provider anthropic \
  --deliver telegram:YOUR_TELEGRAM_DM_ID \
  --skills google-workspace \
  --toolsets web,terminal,file \
  --prompt "$(cat crons/briefing-prompt.md)"
```

> Use your personal Telegram DM ID (not the jobs group) for the briefing.

## Customize the briefing

Edit `crons/briefing-prompt.md` to:
- Change your city for weather
- Add/remove email filters (skip certain senders, include specific topics)
- Add GitHub repos to monitor
- Change the delivery time (the `0 9 * * *` cron expression = 9:00am daily)

## Cron expression reference

```
┌───────── minute (0-59)
│ ┌─────── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─ day of week (0-6, 0=Sunday)
│ │ │ │ │
0  9 * * *   = every day at 9:00am
0  7 * * 1   = every Monday at 7:00am
0  9 * * 1-5 = every weekday at 9:00am
0 9,11,13,15,17,19,21 * * *  = every 2h, 9am-9pm (quiet hours overnight)
```

Adjust the hour for your timezone (Hermes uses the timezone you configured).

---

→ [Next: CV Approach](08-cv-approach.md)
