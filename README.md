# hermes-jobhunt

> Your AI assistant for daily life + autonomous job hunting. Powered by [Hermes Agent](https://hermes-agent.nousresearch.com).

This repo is a **ready-to-deploy setup guide** for turning Hermes into your personal AI assistant that:

- Sends you a **morning briefing** (emails, calendar, weather, news)
- **Scrapes LinkedIn every 2 hours** for new job postings matching your titles
- **Filters by your preferences** (role, stack, seniority, industry)
- **Researches each company** (size, funding, stability, layoffs)
- **Sends you only the good matches** to a dedicated Telegram group
- Stores everything in **Obsidian** so you can query and review it

The whole system is autonomous once configured. You tell it once what you want — it hunts for you.

---

## Architecture

```
┌───────────────────────────────────────────────────────┐
│ Default Profile (Eladiut bot)                         │
│ └── Morning Briefing cron → personal Telegram DM      │
├───────────────────────────────────────────────────────┤
│ Jobs Profile (Merc bot) — separate Hermes profile     │
│ ┌── Scraper (no-agent, 7x/day)                        │
│ │     LinkedIn → Obsidian vault                       │
│ ├── Curator (LLM, ~hourly, daytime)                   │
│ │     Filters by your memory preferences              │
│ ├── Enricher (LLM, every 40m, daytime)                │
│ │     Researches companies, extracts details          │
│ │     Sends "Hey! N jobs match" summary               │
│ └── All deliver → Hermes-Jobs Telegram group          │
└───────────────────────────────────────────────────────┘
```

**Why two profiles?** Memory, config, and context are fully isolated. Merc owns the pipeline — Eladiut handles personal tasks. If one goes down, the other keeps running.

---

## Repository structure

```
hermes-jobhunt/
├── README.md                    ← you are here
├── docs/
│   ├── 01-hermes-setup.md       ← install Hermes + pick a model
│   ├── 02-telegram-setup.md     ← Telegram bots + group + profiles
│   ├── 03-google-workspace.md   ← Gmail + Calendar OAuth
│   ├── 04-obsidian-setup.md     ← Obsidian as the job database
│   ├── 05-proxy-setup.md        ← residential proxy for LinkedIn
│   ├── 06-job-pipeline.md       ← the 3-stage pipeline (scraper/curator/enricher)
│   ├── 07-morning-briefing.md   ← daily briefing cron setup
│   ├── 08-cv-approach.md        ← CV strategy with AI
│   └── 09-troubleshooting.md    ← common issues + fixes
├── scripts/
│   └── linkedin-scraper.py      ← no-LLM scraper (copy to ~/.hermes/scripts/)
├── templates/
│   ├── config.yaml.example      ← Hermes config with placeholders
│   ├── .env.example             ← environment variables template
│   └── memory-preferences.md   ← how to tell Hermes your job preferences
└── crons/
    ├── curator-prompt.md        ← cron prompt for the curator
    ├── enricher-prompt.md       ← cron prompt for the enricher
    └── briefing-prompt.md       ← cron prompt for the morning briefing
```

---

## Prerequisites at a glance

| What | Why | Cost |
|------|-----|------|
| [Hermes Agent](https://hermes-agent.nousresearch.com) | The AI agent runtime | Free (OSS) |
| LLM provider (Ollama Cloud, Anthropic, etc.) | Powers the AI | Varies (free tiers available) |
| Telegram account + 2 bot tokens | Delivers alerts (separate assistant + pipeline bots) | Free |
| Google Cloud project (OAuth) | Gmail + Calendar access | Free |
| Obsidian | Job database + notes | Free |
| Residential proxy (optional) | LinkedIn bot detection bypass | ~$5-10/mo |

---

## Quick start

**If you want an agent to do the entire setup for you**, copy the following message and send it to your Hermes instance after installing it:

```
Please set up my job hunting assistant. Follow the guide at:
https://github.com/elad12390/hermes-jobhunt

I will provide you with:
- My Telegram bot tokens (2 bots: personal assistant + pipeline)
- My Google OAuth credentials
- My residential proxy URL (optional)
- My Obsidian vault path
- My job preferences (titles, stack, location, seniority)

Start with docs/01-hermes-setup.md and work through each doc in order.
Ask me for credentials when needed.
```

---

## Start reading

→ [1. Hermes Setup](docs/01-hermes-setup.md)
