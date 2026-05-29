#!/usr/bin/env python3
"""LinkedIn Job Scraper -> stores results as Obsidian notes in the vault.

Phase 1: extract jobs from search results (title, company, location, time)
Phase 2: for NEW jobs only, visit detail pages for description + criteria
Phase 3: write each job as a Markdown note with YAML frontmatter

Runs via cron with no_agent=True. Zero LLM, zero streaming - pure scraping,
so it never burns tokens and never hits agent rate limits.

Configuration is read from environment variables (see .env.example):
  OBSIDIAN_VAULT_PATH   path to your Obsidian vault (required)
  LINKEDIN_PROXY_URL    residential proxy URL (optional but recommended)
  LINKEDIN_LOCATION     location name for the search query (default: your area)
  LINKEDIN_GEO_ID       LinkedIn geoId for the location (optional)
  LINKEDIN_SEARCHES     comma-separated job titles to search (optional)

Requires: npx agent-browser (Playwright-based headless browser CLI).
"""

import subprocess
import json
import os
import sys
import re
import time
from datetime import datetime, timezone

# ── Configuration (from environment) ───────────────────────────
VAULT = os.environ.get("OBSIDIAN_VAULT_PATH", os.path.expanduser("~/ObsidianVault"))
JOBS_DIR = os.path.join(VAULT, "linkedin-jobs")
MAX_JOBS_PER_SEARCH = int(os.environ.get("LINKEDIN_MAX_JOBS", "10"))
MAX_HOURS = int(os.environ.get("LINKEDIN_MAX_HOURS", "2"))

# Location for the search query. Replace with your city/region/country.
LOCATION = os.environ.get("LINKEDIN_LOCATION", "United States")
GEO_ID = os.environ.get("LINKEDIN_GEO_ID", "")

# Job titles to search for. Override with a comma-separated LINKEDIN_SEARCHES.
DEFAULT_TITLES = [
    "Senior Backend Engineer",
    "AI Engineer",
    "Senior Full Stack Developer",
    "Backend Developer",
]
TITLES = [
    t.strip()
    for t in os.environ.get("LINKEDIN_SEARCHES", ",".join(DEFAULT_TITLES)).split(",")
    if t.strip()
]


def _build_search_url(title: str) -> str:
    from urllib.parse import quote

    geo = f"&geoId={GEO_ID}" if GEO_ID else ""
    return (
        "https://www.linkedin.com/jobs/search/?"
        f"keywords={quote(title)}&location={quote(LOCATION)}{geo}&f_TPR=r86400"
    )


SEARCHES = [(title, _build_search_url(title)) for title in TITLES]

# Residential proxy (optional). Format:
#   http://USERNAME:PASSWORD@PROXY_HOST:PORT
PROXY_URL = os.environ.get("LINKEDIN_PROXY_URL", "")
if PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

# ── JS Extraction Scripts ───────────────────────────────────────
SEARCH_EXTRACT_JS = (
    """(()=>{const MAX_JOBS="""
    + str(MAX_JOBS_PER_SEARCH)
    + """,MAX_HOURS="""
    + str(MAX_HOURS)
    + """;const jobs=[],seen=new Set();const cards=document.querySelectorAll('a.base-card__full-link');for(const link of cards){if(jobs.length>=MAX_JOBS)break;const href=link.getAttribute('href')||'';const idMatch=href.match(/\\/jobs\\/view\\/.*?(\\d+)(?:\\?|$)/);if(!idMatch)continue;const id=idMatch[1];if(seen.has(id))continue;seen.add(id);const li=link.closest('li');const title=link.textContent.trim();const company=li?.querySelector('h4')?.textContent?.trim()||'';const timeStr=li?.querySelector('time')?.textContent?.trim()||'';const timeMatch=timeStr.match(/(\\d+)\\s*(minute|hour|day|week|month|second)s?\\s*ago/i);let hoursAgo=Infinity;if(timeMatch){const num=parseInt(timeMatch[1]);const unit=timeMatch[2].toLowerCase();if(unit.startsWith('second'))hoursAgo=num/3600;else if(unit.startsWith('minute'))hoursAgo=num/60;else if(unit.startsWith('hour'))hoursAgo=num;else if(unit.startsWith('day'))hoursAgo=num*24;else if(unit.startsWith('week'))hoursAgo=num*24*7;else if(unit.startsWith('month'))hoursAgo=num*24*30;}if(hoursAgo>MAX_HOURS)continue;let location='';const spans=li?.querySelectorAll('span');for(const s of spans||[]){const t=s.textContent.trim();if(t&&t.length<100&&/[A-Za-z]/.test(t)&&!/\\d{2,}/.test(t)){location=t;break}}jobs.push({id,title,company,location,time:timeStr,link:'https://www.linkedin.com/jobs/view/'+id});}return JSON.stringify({count:jobs.length,jobs});})();"""
)

DETAIL_EXTRACT_JS = """(()=>{const desc=document.querySelector('[class*="description"]');const descText=desc?desc.textContent.trim():'';const criteria={};const items=document.querySelectorAll('[class*="criteria"] li');for(const item of items){const text=item.textContent.trim().replace(/\\n\\s+/g,' ');const parts=text.split(/\\s{2,}/).filter(p=>p.length>1);if(parts.length>=2){criteria[parts[0].toLowerCase().replace(/[^a-z]/g,'_')]=parts[1];}}return JSON.stringify({description:descText.substring(0,3000),seniority:criteria.seniority_level||'',employment:criteria.employment_type||'',job_function:criteria.job_function||'',industry:criteria.industries||''});})();"""


# ── Helpers ────────────────────────────────────────────────────
def ab(*args, timeout=30):
    """Run agent-browser, return parsed data.result."""
    cmd = ["npx", "agent-browser", "--json"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"agent-browser failed: {result.stderr[:200]}")
    response = json.loads(result.stdout)
    result_str = response.get("data", {}).get("result", "{}")
    return json.loads(result_str)


def sanitize_filename(s):
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    return re.sub(r"\s+", " ", s).strip()[:120]


def job_note_exists(job_id):
    """Check if a note already exists for this job ID (including rejected)."""
    if not os.path.exists(JOBS_DIR):
        return False
    for fname in os.listdir(JOBS_DIR):
        if not fname.endswith(".md"):
            continue
        content = open(os.path.join(JOBS_DIR, fname)).read()
        if f'id: "{job_id}"' in content:
            return True
    return False


def is_rejected(job_id):
    """Check if job was rejected by the curator cron."""
    rejected_file = os.path.join(JOBS_DIR, ".rejected.json")
    if os.path.exists(rejected_file):
        rejected = json.load(open(rejected_file))
        return job_id in rejected.get("ids", [])
    return False


def fetch_job_details(job):
    """Visit job detail page and extract description + criteria."""
    try:
        ab("open", job["link"], timeout=20)
        time.sleep(2)
        return ab("eval", DETAIL_EXTRACT_JS, timeout=15)
    except Exception as e:
        sys.stderr.write(f"    Detail fetch failed for {job['id']}: {e}\n")
        return {}


def write_job_note(job, search_title, details=None):
    """Write/update a job note with optional details from the detail page."""
    os.makedirs(JOBS_DIR, exist_ok=True)
    filename = sanitize_filename(f"{job['company']} - {job['title']}.md")
    filepath = os.path.join(JOBS_DIR, filename)
    now = datetime.now(timezone.utc).isoformat()

    tags = ["linkedin-job"]
    tl = job["title"].lower()
    if "backend" in tl or "back end" in tl:
        tags.append("backend")
    if "frontend" in tl or "full stack" in tl or "fullstack" in tl:
        tags.append("fullstack")
    if any(
        t in tl
        for t in [
            "ai ",
            "ml ",
            "machine learning",
            "artificial intelligence",
            "llm",
            "deep learning",
            "data science",
        ]
    ):
        tags.append("ai-ml")
    if "senior" in tl or "staff" in tl or "lead" in tl or "principal" in tl:
        tags.append("senior")
    if "devops" in tl or "infrastructure" in tl:
        tags.append("devops")

    desc = details.get("description", "") if details else ""
    seniority = details.get("seniority", "") if details else ""
    employment = details.get("employment", "") if details else ""
    job_func = details.get("job_function", "") if details else ""
    industry = details.get("industry", "") if details else ""

    if os.path.exists(filepath):
        content = open(filepath).read()
        content = re.sub(r"last_seen:.*", f'last_seen: "{now}"', content)
        if 'status: "expired"' in content:
            content = content.replace('status: "expired"', 'status: "active"')
        if desc and "description:" not in content:
            content = content.replace(
                'status: "active"',
                f'status: "active"\ndescription: "{desc[:200]}..."',
            )
        with open(filepath, "w") as f:
            f.write(content)
        return "updated"

    frontmatter = f"""---
id: "{job['id']}"
title: "{job['title']}"
company: "{job['company']}"
location: "{job['location']}"
first_seen: "{now}"
last_seen: "{now}"
time: "{job['time']}"
link: "{job['link']}"
search: "{search_title}"
seniority: "{seniority}"
employment: "{employment}"
job_function: "{job_func}"
industry: "{industry}"
tags: [{', '.join(tags)}]
status: "active"
---

# {job['title']}

**Company:** [[{job['company']}]]
**Location:** {job['location']}
**Posted:** {job['time']}
**Seniority:** {seniority}
**Employment:** {employment}
**Function:** {job_func}
**Industry:** {industry}
**Link:** {job['link']}
**Found via:** {search_title}

## Description

{desc[:2000]}
"""
    with open(filepath, "w") as f:
        f.write(frontmatter)
    return "created"


# ── Main ───────────────────────────────────────────────────────
# Cron runs this with a hard timeout (default 120s in Hermes). Detail-page
# fetches are the slow part, so we enforce a wall-clock BUDGET below the cron
# limit and defer any remaining jobs to the next run instead of being killed
# mid-write. Deferred jobs are NOT written detail-less, so they get picked up
# (and fully enriched) on the following run.
BUDGET_SECONDS = int(os.environ.get("LINKEDIN_BUDGET_SECONDS", "95"))


def main():
    if not os.environ.get("OBSIDIAN_VAULT_PATH"):
        sys.stderr.write(
            "WARNING: OBSIDIAN_VAULT_PATH not set; using default "
            f"{VAULT}. Set it in ~/.hermes/.env\n"
        )
    if not PROXY_URL:
        sys.stderr.write(
            "WARNING: LINKEDIN_PROXY_URL not set. LinkedIn may block "
            "datacenter IPs - a residential proxy is strongly recommended.\n"
        )

    all_jobs = {}
    errors = []
    start = time.monotonic()

    # Phase 1: Search results
    for search_title, url in SEARCHES:
        try:
            ab("open", url, timeout=20)
            time.sleep(2)
            data = ab("eval", SEARCH_EXTRACT_JS, timeout=20)
            for job in data.get("jobs", []):
                job["_search"] = search_title
                if job["id"] not in all_jobs:
                    all_jobs[job["id"]] = job
            sys.stderr.write(
                f"  {search_title}: {data['count']} jobs ({MAX_HOURS}h filter)\n"
            )
        except Exception as e:
            msg = f"  {search_title}: ERROR - {e}"
            sys.stderr.write(msg + "\n")
            errors.append(msg)

    # Phase 2: Fetch details for NEW jobs only (skip rejected), under budget
    new_jobs = {
        jid: j
        for jid, j in all_jobs.items()
        if not job_note_exists(jid) and not is_rejected(jid)
    }
    sys.stderr.write(f"\n  Fetching details for {len(new_jobs)} new job(s)...\n")

    details_cache = {}
    skipped_budget = 0
    for jid, job in new_jobs.items():
        if time.monotonic() - start > BUDGET_SECONDS:
            skipped_budget = len(new_jobs) - len(details_cache)
            sys.stderr.write(
                f"\n  Budget reached, deferring {skipped_budget} job(s) to next run\n"
            )
            break
        details = fetch_job_details(job)
        details_cache[jid] = details
        desc_preview = details.get("description", "")[:80]
        sys.stderr.write(f"    {job['title'][:50]}... -> {desc_preview}...\n")
        time.sleep(1)  # Rate limit

    # Phase 3: Write to vault. Only write notes for jobs we processed this run:
    # existing notes (updates) and new jobs we fetched details for. New jobs
    # deferred by the budget are skipped so they get fetched next run instead
    # of being written detail-less (which would make job_note_exists skip them
    # forever).
    created = updated = 0
    for jid, job in all_jobs.items():
        is_new = jid in new_jobs
        if is_new and jid not in details_cache:
            continue  # deferred to next run
        details = details_cache.get(jid, {})
        result = write_job_note(job, job["_search"], details)
        if result == "created":
            created += 1
        else:
            updated += 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = (
        f"LinkedIn scan ({now})\n"
        f"  Created: {created} | Updated: {updated}\n"
        f"  With details: {len(details_cache)}\n"
    )
    if errors:
        summary += f"  Errors: {len(errors)}\n"
    if skipped_budget:
        summary += f"  Deferred (budget): {skipped_budget}\n"
    print(summary)


if __name__ == "__main__":
    main()
