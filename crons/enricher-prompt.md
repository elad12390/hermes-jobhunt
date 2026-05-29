# Enricher cron prompt
# Used by: hermes cron create "every 10m" --prompt "$(cat crons/enricher-prompt.md)"

Enrich LinkedIn jobs in YOUR_VAULT_PATH/linkedin-jobs/.

STEP 1 - FIND PENDING: List all .md files. A job is PENDING if it has curator_status:"passed" but NO enricher_status field. You MUST enrich every pending job before doing anything else.

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
