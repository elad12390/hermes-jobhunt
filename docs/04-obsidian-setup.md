# 4. Obsidian Setup

Obsidian is used as the **job database**. Every scraped job becomes a markdown note with structured YAML frontmatter. You can open the vault to browse jobs, query them with Dataview, and see what the agent found and filtered.

You don't have to use Obsidian - you could use any folder of markdown files. But Obsidian gives you a nice UI to browse and query.

## Install Obsidian

Download from https://obsidian.md - free, available on Windows, macOS, Linux, iOS, Android.

## Create a vault

1. Open Obsidian
2. Create new vault (e.g. "JobHunt")
3. Note the vault path (e.g. `/home/user/JobHunt` or `~/Documents/JobHunt`)

## Recommended plugins

Install these from Settings → Community Plugins → Browse:

| Plugin | Why |
|--------|-----|
| **Dataview** | Query your job notes like a database (e.g. "show all passed jobs from this week") |
| **Templater** | Auto-fill note templates |

## Folder structure

The agent will create and manage this structure automatically:

```
JobHunt/
└── linkedin-jobs/         <- all scraped job notes live here
    ├── Acme Corp - Senior Backend Engineer.md
    ├── Globex - Staff Full Stack Engineer.md
    └── .rejected.json     <- IDs the curator rejected (not re-scraped)
```

## Job note structure

Each job note has YAML frontmatter + readable body:

```yaml
---
id: "1234567890"
title: "Senior Backend Engineer"
company: "Acme Corp"
location: "Your City, Your Region"
first_seen: "2026-01-01T11:45:26Z"
last_seen: "2026-01-01T11:45:26Z"
time: "31 minutes ago"
link: "https://www.linkedin.com/jobs/view/1234567890"
search: "Senior Backend Engineer"
seniority: "Senior"
employment: "Full-time"
job_function: "Software Engineering"
industry: "Software"
tags: [linkedin-job, backend, senior]
curator_status: "passed"      # set by the Curator cron
curator_note: "Strong match on stack"
enricher_status: "passed"     # set by the Enricher cron
enricher_note: "95 employees, Series A, growing"
company_size: "95 employees"
funding: "Series A"
company_type: "product"
careers_page: "https://example.com/careers/"
company_stability: "No recent layoffs. Growing."
sent_to_user: true            # sent to Telegram already
---

# Senior Backend Engineer

**Company:** [[Acme Corp]]
...

## Description

...
```

## Useful Dataview queries

Add these to a `Dashboard.md` note in your vault:

````markdown
## Active jobs (passed all filters)
```dataview
TABLE company, seniority, funding, company_stability
FROM "linkedin-jobs"
WHERE curator_status = "passed" AND enricher_status = "passed"
SORT first_seen DESC
```

## Jobs to review
```dataview
TABLE company, title, curator_note
FROM "linkedin-jobs"
WHERE curator_status = "passed" AND enricher_status = null
```

## All jobs this week
```dataview
TABLE company, title, curator_status, enricher_status
FROM "linkedin-jobs"
SORT first_seen DESC
LIMIT 20
```
````

## Set the vault path

Tell the scraper where your vault is. In `~/.hermes/.env`:

```
OBSIDIAN_VAULT_PATH=/home/yourname/JobHunt
```

Or just edit the `VAULT` variable at the top of `scripts/linkedin-scraper.py`.

---

→ [Next: Proxy Setup](05-proxy-setup.md)
