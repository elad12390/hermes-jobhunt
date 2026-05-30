# Enricher cron prompt
# Runs under: hermes --profile jobs cron create "*/40 9-21 * * *" --prompt "$(cat crons/enricher-prompt.md)"
# Schedule: every 40 min during waking hours (9am-9pm). Low-traffic overnight.

Enrich LinkedIn jobs in your vault's linkedin-jobs/ directory. Use the obsidian skill conventions.

STEP 1 - FIND PENDING EFFICIENTLY (do NOT read every file):
Run a single grep to find candidates cheaply:
  grep -rL 'enricher_status:' linkedin-jobs/ --include='*.md'
then of those, keep only files that contain curator_status: "interested". A job is
PENDING if it has curator_status:"interested" AND no enricher_status field. If there
are zero pending jobs, STOP immediately and respond "No new jobs to enrich." -
do not read or process anything else. This keeps token use minimal on idle runs.

STEP 2 - ENRICH EACH PENDING JOB (in parallel where possible):
  a. Read all pending files at once (batch read_file calls)
  b. Fire all web searches in parallel (not one-by-one):
     - "<company> employees size"
     - "<company> funding crunchbase"
     - "<company> layoffs 2026"
     - "<company> revenue growth"
     - "<company> careers page"
  c. Patch each file's frontmatter to add:
     enricher_status: "passed"   (use "rejected" only for project/outsourcing/consulting/ghost/dying companies)
     enricher_note: "one sentence why"
     company_size: "X employees"
     funding: "stage + amount or Public (TICKER)"
     company_type: "product"
     careers_page: "URL"
     company_stability: "1-2 sentences: layoffs? revenue? growth? AI disruption risk?"
     sent_to_user: false

REJECT (enricher_status: "rejected") only if:
  - Project/outsourcing/consulting shop ("we build solutions for clients")
  - Ghost company (no website, no employees, can't find anything)
  - Company clearly dying or will be replaced entirely by AI

Everything else: PASS. Company size and funding stage do NOT matter.

STEP 3 - SUMMARIZE: After ALL pending jobs are enriched, scan for enricher_status:"passed" AND sent_to_user:false.

If that list is non-empty, make your FINAL RESPONSE:

Hey! [N] job listings match your filters:

⭐ Top Pick: [Company] - [Title]
  [seniority] · [employment] · [industry]
  [company_size] · [funding]
  Stack: [from description]
  → [careers_page]

(one block per passed job, grouped by category: ⭐ top pick, 🔐 cyber, 🧠 AI/ML)

Then patch each of those jobs: set sent_to_user: true

ONLY include passed jobs. NEVER mention rejected ones.
If no passed+unsent jobs exist: respond "No new jobs to enrich."

Budget is 90 calls. Do NOT stop until all pending jobs are enriched and the summary is sent.
Your FINAL RESPONSE is delivered directly to the user - just write the message, do NOT say "I will deliver" or "sending now".
