# 9. Troubleshooting

Real issues encountered building this setup, and how to fix them.

## Cron job keeps going to "completed" state and not repeating

Hermes cron jobs using `once in Xm` syntax run once and stop. Use interval syntax instead:

```bash
# Wrong:
hermes cron create "once in 10m" ...

# Right:
hermes cron create "*/40 9-21 * * *" ...
hermes cron create "0 9 * * *" ...
```

If a job is in "completed" state, resume it:
```bash
hermes cron list   # get the job_id
hermes cron resume JOB_ID
```

## Cron agent does partial work and stops

Symptom: the agent enriches 1 job, marks sent_to_user, and returns - ignoring the other 4.

Root cause: the prompt allows early exit (e.g. "if no pending jobs, send summary"). The agent finds one job already done and skips the rest.

Fix: make the prompt phases explicit with hard requirements:
```
STEP 1 - FIND PENDING: [definition]
STEP 2 - ENRICH ALL PENDING (do NOT skip any. Do NOT proceed to step 3 until all are done)
STEP 3 - SUMMARIZE
```

## API streaming drops mid-response

Symptom: `WARNING: peer closed connection without sending complete message body`

Hermes retries automatically (3 attempts). If it fails all 3, the job fails.

Fix:
1. Pin important crons to a stable provider (Anthropic has better streaming reliability than self-hosted/Ollama)
2. Remove dead providers from the fallback chain - a 429-dead provider causes 120s retry delays

```bash
# Check your fallback chain:
grep -A5 "fallback_providers" ~/.hermes/config.yaml

# Remove dead providers:
hermes config set fallback_providers '[{"provider": "anthropic", "model": "claude-sonnet-4-6"}]'
```

## Provider hits monthly quota (429)

Symptom: `HTTP 429: Monthly usage limit reached`

This is most common with budget providers (OpenCode Go, etc.). If a fallback provider hits 429, Hermes retries every 120 seconds - this **blocks the entire cron run** and wastes your budget.

Fix: remove the exhausted provider from fallbacks immediately:
```bash
# Edit ~/.hermes/config.yaml and remove the dead provider from fallback_providers
hermes gateway restart
```

## LinkedIn scraper extracts 0 jobs

Symptom: the scraper runs but finds nothing.

Possible causes:
1. **LinkedIn changed their DOM** - the selector `a.base-card__full-link` no longer works
   - Open a LinkedIn jobs search in a real browser, inspect the job card links
   - Update the selector in the `SEARCH_EXTRACT_JS` variable in `linkedin-scraper.py`

2. **Sign-in dialog is blocking** - but the DOM should still have data behind it. Check if any jobs appear with:
   ```js
   document.querySelectorAll('a.base-card__full-link').length
   ```

3. **IP blocked** - add a residential proxy (see doc 05)

## Google OAuth token expires every 7 days

Symptom: `REFRESH_FAILED` or `NOT_AUTHENTICATED` errors in cron jobs

Cause: Google Testing mode tokens expire every 7 days.

Fix: Publish your OAuth app (doesn't require Google review for personal use):
1. https://console.cloud.google.com/auth/overview
2. Click "Publish app" → confirm
3. Tokens now last 6 months

Re-auth after publishing:
```bash
GSETUP="python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --revoke
$GSETUP --auth-url
# visit URL, paste code back
$GSETUP --auth-code "http://localhost:1/?code=..."
```

## Hermes sends output to wrong Telegram chat

Symptom: cron delivery goes to your DMs instead of the jobs group.

Fix: make sure `deliver` is set to the group chat ID (a negative number):
```bash
hermes cron list  # find the job_id
hermes cron edit JOB_ID  # update deliver field to telegram:-XXXXXXXXX
```

Or when creating:
```bash
hermes cron create "0 9,11,13,15,17,19,21 * * *" --deliver telegram:YOUR_GROUP_ID ...
```

> The group chat ID is always negative (e.g. `-1001234567890`). Your personal DM ID is positive.

## Cron delivers "Cronjob Response" header but no content

The cron ran, the prompt executed, but the agent's final response was just metadata. This happens when the agent says something like "I'll deliver this now" instead of just writing the message.

Fix: add to your cron prompt:
```
Your FINAL RESPONSE is delivered directly to the user. 
Do NOT say "I will send..." or "Delivering now...".
Just write the message content directly as your response.
```

## Morning briefing has wrong date

Hermes can hallucinate the current date in briefings if it doesn't check the system clock.

Fix: add to your briefing prompt:
```
IMPORTANT: First run `date` to get today's exact date and day of week. 
Use that, never guess.
```

---

## Getting help

- [Hermes docs](https://hermes-agent.nousresearch.com/docs)
- [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- Run `hermes doctor` to check your setup
- Run `hermes debug` to generate a debug report
