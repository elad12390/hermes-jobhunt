# Curator cron prompt
# Used by: hermes cron create "every 90m" --prompt "$(cat crons/curator-prompt.md)"

You are curating LinkedIn job listings in the Obsidian vault. Read your memory for job preferences first.

TASK:
1. Read ALL .md files in YOUR_VAULT_PATH/linkedin-jobs/ where curator_status is NOT set
2. For each job WITHOUT a description: browser_navigate to the link, extract with console:
   `(()=>{const d=document.querySelector('[class*="description"]');return d?d.textContent.trim().substring(0,1500):'none';})();`
3. Evaluate against your memory (job curator preferences)
4. For REJECTED:
   - Set curator_status: "rejected" + curator_note in frontmatter
   - Record the job ID in YOUR_VAULT_PATH/linkedin-jobs/.rejected.json as {"ids": ["id1","id2",...]} (merge with existing)
   - DELETE the .md file
5. For PASSED:
   - Set curator_status: "passed" + curator_note explaining why it fits
6. Report: "Reviewed X. Passed Y, Rejected Z." with names

KEY RULES (from memory - read preferences first):
- Unsure → PASS. Only delete obvious mismatches.
- Do NOT report rejected jobs to the user.
