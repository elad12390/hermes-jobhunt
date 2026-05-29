# Enricher cron prompt
# Used by: hermes cron create "*/40 9-21 * * *" --prompt "$(cat crons/enricher-prompt.md)"
# Schedule note: runs every 40 min during waking hours only (9am-9pm) so it
# never messages you overnight. Adjust the hours to your timezone/preference.

Enrich LinkedIn jobs in YOUR_VAULT_PATH/linkedin-jobs/. Use the obsidian skill conventions.

STEP 1 - FIND PENDING EFFICIENTLY (do NOT read every file):
Run a single grep to find candidates cheaply, e.g.:
  grep -rL 'enricher_status:' YOUR_VAULT_PATH/linkedin-jobs/ --include='*.md'
then of those, keep only files that contain curator_status: "passed". A job is
PENDING if it has curator_status:"passed" AND no enricher_status field. If there
are zero pending jobs, STOP immediately and respond "No new jobs to enrich." -
do not read or process anything else. This keeps token use minimal on idle runs.

STEP 2 - ENRICH EACH PENDING JOB (one at a time):
  a. read_file the job
  b. Web search: "<company> employees", "<company> funding crunchbase", "<company> layoffs 2026", "<company> revenue profitable"
  c. patch the frontmatter to add these lines (after the industry: line):
     enricher_status: "passed"   (use "rejected" only for outsourcing/consulting/ghost/dying companies)
     enricher_note: "one sentence why"
     company_size: "X employees"
     funding: "stage + amount or Public (NASDAQ: X)"
     company_type: "product"
     careers_page: "URL"
     company_stability: "1-2 sentences: any layoffs? revenue? growth? will AI replace this company?"
     seniority: (parse from description)
     employment: (Full-time / Hybrid / Remote - parse from description)
     job_function: (e.g. Software Engineering, AI/ML Engineering)
     industry: (e.g. Cybersecurity, Fintech, AI Platform)
     sent_to_user: false

REJECT (enricher_status: "rejected") only if:
  - Project/outsourcing/consulting shop ("we build solutions for clients")
  - Ghost company (no website, no funding info, can't find anything)
  - Company clearly dying or going to be replaced entirely by AI

Everything else: PASS.

STEP 3 - SUMMARIZE: After NO pending jobs remain, scan all files for enricher_status:"passed" AND sent_to_user:false.

If that list is non-empty, make your FINAL RESPONSE exactly:

Hey! [N] companies match your filters:

• [Company] - [Title]
  [seniority] · [employment] · [industry]
  [company_size] · [funding]
  Stability: [company_stability]
  → [careers_page]

(one block per passed job, ordered by relevance)

Then patch each of those jobs: set sent_to_user: true

ONLY include passed jobs. NEVER mention rejected ones.
If no passed+unsent jobs exist: respond "No new jobs to enrich."

Budget is 90 calls. Do NOT stop until all pending jobs are enriched and the summary is sent.
Your FINAL RESPONSE is delivered directly to the user - just write the message, do NOT say "I will deliver" or "sending now".
