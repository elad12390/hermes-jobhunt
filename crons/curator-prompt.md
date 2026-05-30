# Curator cron prompt
# Runs under: hermes --profile jobs cron create "0 9,10,12,13,15,16,18,19,21 * * *" --prompt "$(cat crons/curator-prompt.md)"
# Schedule: daytime hours only (9am-9pm). Runs shortly after each scraper run
# so new jobs get filtered promptly. Adjust hours to your timezone.

You are curating LinkedIn job listings in an Obsidian vault. Read your memory for job preferences first.

TASK:
1. Find ALL .md files in the linkedin-jobs/ directory of your vault where curator_status is NOT set
2. For each job WITHOUT a description: browser_navigate to the link, extract with console
3. Evaluate against your job curator preferences in memory
4. For REJECTED:
   - Set curator_status: "rejected" + curator_note in frontmatter
   - Record the job ID in linkedin-jobs/.rejected.json as {"ids": ["id1","id2",...]} (merge with existing)
5. For INTERESTED:
   - Set curator_status: "interested" + curator_note explaining why it fits
6. Report: "Reviewed X. Interested Y, Rejected Z." with names

KEY RULES (from memory - read preferences first):
- Unsure? PASS (set curator_status: "interested"). Only reject obvious mismatches.
- HARD REJECT: ad-tech/ad-services companies (ad verification, retargeting, ad networks)
- Do NOT report rejected jobs to the user.
