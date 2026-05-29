# 6. Job Pipeline

The job pipeline has 3 stages, each running on its own schedule:

```
LinkedIn --> Scraper (every 2h, daytime) --> Obsidian vault
                                          |
                                     Curator (daytime)
                                     filters by role/stack
                                          |
                                     Enricher (every 40m, daytime)
                                     researches companies
                                          |
                              "Hey! N jobs match" --> Telegram group
```

## Stage 1: Scraper (no-LLM)

The scraper is a Python script that runs without any LLM - pure browser automation + file writes. This makes it extremely reliable (no API costs, no streaming drops, no token limits).

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
    # Find your location's geoId by searching on LinkedIn and checking the URL
    # (the production scripts/linkedin-scraper.py reads these from env vars:
    #  LINKEDIN_LOCATION, LINKEDIN_GEO_ID, LINKEDIN_SEARCHES)
]

PROXY_URL = "http://USER:PASS@HOST:PORT"     # leave empty string "" if no proxy
```

**Test it manually:**
```bash
python ~/.hermes/scripts/linkedin-scraper.py
```

You should see output like:
```
<Your Search Title 1>: 7 jobs (2h filter)
<Your Search Title 2>: 9 jobs (2h filter)
...
LinkedIn scan (2026-01-01 14:25)
  Created: 12 | Updated: 0
  With details: 12
```

**Create the cron** (runs every 2h during waking hours only - no overnight pings):
```bash
hermes cron create "0 9,11,13,15,17,19,21 * * *" \
  --name "LinkedIn Job Scraper" \
  --script linkedin-scraper.py \
  --no-agent \
  --deliver telegram:YOUR_JOBS_GROUP_ID
```

> `--no-agent` means Hermes runs the script directly and delivers stdout as the message. No LLM involved.

> **Quiet hours:** the schedule above only fires 9am-9pm. Tune the hours
> (`9,11,13,...`) to your timezone and waking hours.

> **Timeout safety:** Hermes hard-kills cron scripts at 120s. The script
> enforces a 95s wall-clock budget (`LINKEDIN_BUDGET_SECONDS`) and defers any
> remaining detail-fetches to the next run instead of being killed mid-write.
> Deferred jobs are picked up and fully enriched on the following run.

---

## Stage 2: Curator (LLM)

The curator reads new job notes and filters them based on your profile. It deletes notes that don't match and marks good ones as `curator_status: "passed"`.

**It reads your Hermes memory** to understand your preferences - you don't hardcode filters in the cron prompt. To set your preferences, tell Hermes something like:

```
Remember my job search preferences:
- I'm a [your role], [N] years experience
- Stack: [your languages/frameworks]
- WANT: [the roles/industries/company types you're targeting]
- AVOID: [roles/stacks/company types to filter out]
- Location: [your location], [remote/hybrid/onsite preference]
- Seniority: [Junior / Mid / Senior / Staff / Lead / IC vs management]
Save this as "Job curator preferences" in memory.
```

See `templates/memory-preferences.md` for a fuller template.

**Create the cron** (daytime hours, shortly after each scrape):
```bash
hermes cron create "0 9,10,12,13,15,16,18,19,21 * * *" \
  --name "LinkedIn Job Curator" \
  --model claude-sonnet-4-6 \
  --provider anthropic \
  --deliver telegram:YOUR_JOBS_GROUP_ID \
  --skills obsidian \
  --prompt "$(cat crons/curator-prompt.md)"
```

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
- AI disruption risk

**It sends you a message like:**
```
Hey! 3 companies match your filters:

• Acme Corp - Senior Backend Engineer
  Senior · Full-time · Software
  95 employees · Series A
  Stability: No recent layoffs. Growing fast.
  -> https://example.com/careers/
```

It also marks jobs with `sent_to_user: true` so it won't repeat them.

**Create the cron** (every 40 min during waking hours):
```bash
hermes cron create "*/40 9-21 * * *" \
  --name "Job Enricher" \
  --model claude-sonnet-4-6 \
  --provider anthropic \
  --deliver telegram:YOUR_JOBS_GROUP_ID \
  --skills obsidian \
  --prompt "$(cat crons/enricher-prompt.md)"
```

> The enricher runs every 40 minutes during the day but is smart about it: a single cheap `grep` checks for pending jobs first, and if nothing changed (no new passed jobs, nothing unsent) it returns "No new jobs to enrich." silently - so you only get messages when there's something relevant, and idle runs cost almost no tokens.

---

## LinkedIn search URL builder

To build your own search URLs:

1. Go to https://www.linkedin.com/jobs/search/
2. Enter your keywords + location + filter "Past 24 hours"
3. Copy the URL from your browser
4. Copy the `geoId=` value from that URL - it is your location's numeric LinkedIn ID

Key URL parameters:
- `keywords=` - job title to search
- `location=` - location name (display only)
- `geoId=` - numeric LinkedIn location ID
- `f_TPR=r86400` - past 24 hours filter

---

→ [Next: Morning Briefing](07-morning-briefing.md)
