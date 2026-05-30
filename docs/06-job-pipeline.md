# 6. Job Pipeline

The job pipeline has 3 stages, each running on its own schedule. All three run under the **jobs profile** (separate bot, separate gateway, separate memory).

```
┌─────────────────────────────────────────────────────────┐
│ Jobs Profile (Merc bot)                                 │
│                                                         │
│ LinkedIn → Scraper (no-agent, 2h) → Obsidian vault      │
│                                    ↓                    │
│                               Curator (LLM, ~hourly)    │
│                               filters by preferences    │
│                                    ↓                    │
│                               Enricher (LLM, every 40m) │
│                               researches companies      │
│                                    ↓                    │
│                        "Hey! N jobs match" → Telegram   │
│                                                         │
│ Default Profile (Eladiut bot)                           │
│ └── Morning Briefing only                               │
└─────────────────────────────────────────────────────────┘
```

**Why two profiles?** The jobs profile has its own memory (job preferences, company lists), its own config (cheap/free provider for scraping, reliable fallbacks for LLM work), and its own Telegram bot that only delivers pipeline output. The default profile handles personal tasks without the pipeline cluttering its context or memory.

## Create the jobs profile

```bash
hermes profile create jobs --clone-from default
# Edit ~/.hermes/profiles/jobs/.env and set TELEGRAM_BOT_TOKEN to your jobs bot
# Edit ~/.hermes/profiles/jobs/config.yaml and set model/fallback chain
```

All `hermes cron create` commands below use `--profile jobs`.

## Profile provider chain

Edit `~/.hermes/profiles/jobs/config.yaml`:
```yaml
model:
  default: deepseek-v4-pro:cloud
  provider: ollama-cloud

fallback_providers:
  - provider: anthropic
    model: claude-sonnet-4-6
  - provider: opencode-go
    model: deepseek-v4-pro
```

The cron jobs inherit this chain — no per-job model pinning needed:
1. **Primary:** ollama-cloud (free) — tried first
2. **Fallback 1:** anthropic (reliable) — kicks in if ollama drops
3. **Fallback 2:** opencode-go (paid plan) — last resort

## Stage 1: Scraper (no-LLM)

The scraper is a Python script that runs without any LLM — pure browser automation + file writes. This makes it extremely reliable (no API costs, no streaming drops, no token limits).

**What it does:**
1. Uses `agent-browser` (headless Chromium) to open LinkedIn job search URLs
2. Injects a JS snippet to extract job cards directly from the DOM
3. For new jobs only: visits each job page and extracts the full description
4. Writes each job as a markdown note to your Obsidian vault
5. Skips jobs that were previously rejected by the curator (`.rejected.json`)

**Install agent-browser (one time):**
```bash
npm install -g agent-browser
agent-browser install --with-deps
```

**Copy the script:**
```bash
cp scripts/linkedin-scraper.py ~/.hermes/scripts/
```

**Edit the configuration at the top of the script:**
```python
VAULT = "/path/to/your/ObsidianVault"       # your vault path
MAX_JOBS_PER_SEARCH = 10                     # jobs per search query
MAX_HOURS = 2                                # only show jobs posted in last N hours

SEARCHES = [
    ("Senior Backend Engineer", "https://www.linkedin.com/jobs/search/?keywords=Senior%20Backend%20Engineer&location=YOUR_LOCATION&geoId=YOUR_GEO_ID&f_TPR=r86400"),
    # Add your own searches here
]

PROXY_URL = "http://USER:PASS@HOST:PORT"     # leave empty string "" if no proxy
```

**Test it manually:**
```bash
python ~/.hermes/scripts/linkedin-scraper.py
```

**Create the cron** (runs 7x/day during waking hours, no overnight pings):
```bash
hermes --profile jobs cron create "0 9,11,13,15,17,19,21 * * *" \
  --name "LinkedIn Job Scraper" \
  --script linkedin-scraper.py \
  --no-agent \
  --deliver telegram:YOUR_JOBS_GROUP_ID
```

> `--no-agent` means Hermes runs the script directly and delivers stdout as the message. No LLM involved.

> **Quiet hours:** the schedule above only fires 9am-9pm. Tune the hours to your timezone.

> **Timeout safety:** Hermes hard-kills cron scripts at 120s. The script enforces a 95s wall-clock budget and defers any remaining detail-fetches to the next run instead of being killed mid-write.

---

## Stage 2: Curator (LLM)

The curator reads new job notes and filters them based on your profile. It marks good ones as `curator_status: "interested"` and rejects mismatches.

**It reads your Hermes memory** to understand your preferences — you don't hardcode filters in the cron prompt. To set your preferences, tell Hermes something like:

```
Remember my job search preferences:
- I'm a [your role], [N] years experience
- Stack: [your languages/frameworks]
- WANT: [the roles/industries/company types you're targeting]
- AVOID: [roles/stacks/company types to filter out]
- Location: [your location], [remote/hybrid/onsite preference]
- Seniority: [Junior / Mid / Senior / Staff / Lead]
Save this as "Job curator preferences" in memory.
```

See `templates/memory-preferences.md` for a fuller template.

**Create the cron** (daytime hours, shortly after each scrape):
```bash
hermes --profile jobs cron create "0 9,10,12,13,15,16,18,19,21 * * *" \
  --name "LinkedIn Job Curator" \
  --deliver telegram:YOUR_JOBS_GROUP_ID \
  --skills obsidian \
  --prompt "$(cat crons/curator-prompt.md)"
```

> No `--model` or `--provider` flags — the job inherits the profile's fallback chain.

See `crons/curator-prompt.md` for the full prompt.

---

## Stage 3: Enricher (LLM)

The enricher processes jobs that passed curation, researches the company, and sends you the final summary.

**What it researches:**
- Company size (employees)
- Funding stage and amount
- Recent layoffs or financial trouble
- Product vs. project/outsourcing company
- Careers page URL
- Job details: seniority, employment type, job function, industry

**It sends you a message like:**
```
Hey! 3 companies match your filters:

⭐ Pick: CompanyName - Senior Backend Engineer
  Senior · Full-time · Cybersecurity
  120 employees · Series B
  Stack: Python, Go, AWS
  → https://company.com/careers/
```

It also marks jobs with `sent_to_user: true` so it won't repeat them.

**Create the cron** (every 40 min during waking hours):
```bash
hermes --profile jobs cron create "*/40 9-21 * * *" \
  --name "Job Enricher" \
  --deliver telegram:YOUR_JOBS_GROUP_ID \
  --skills obsidian \
  --prompt "$(cat crons/enricher-prompt.md)"
```

> The enricher runs every 40 minutes but is token-efficient: a single `grep` checks for pending jobs first, and if none exist it returns immediately with minimal cost. You only get messages when there's something relevant.

---

## View all cron jobs

```bash
hermes cron list                    # default profile (Morning Briefing only)
hermes --profile jobs cron list     # jobs profile (pipeline)
```

---

## LinkedIn search URL builder

1. Go to https://www.linkedin.com/jobs/search/
2. Enter your keywords + location + filter "Past 24 hours"
3. Copy the URL from your browser
4. Copy the `geoId=` value — your location's numeric LinkedIn ID

Key URL parameters:
- `keywords=` — job title to search
- `location=` — location name (display only)
- `geoId=` — numeric LinkedIn location ID
- `f_TPR=r86400` — past 24 hours filter

---

→ [Next: Morning Briefing](07-morning-briefing.md)
