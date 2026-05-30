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

If a job is in "completed" state, update it:
```bash
hermes --profile jobs cron list   # get the job_id
hermes --profile jobs cron update JOB_ID --schedule "0 9,11,13,15,17,19,21 * * *"
```

## Cron jobs run on wrong profile

All pipeline jobs MUST be created with `--profile jobs`. If you accidentally create them on default:

```bash
# Check what profile has what:
hermes cron list                    # default
hermes --profile jobs cron list     # jobs
```

## API streaming drops mid-response

Symptom: `WARNING: peer closed connection without sending complete message body`

This is common with Ollama Cloud on long LLM runs. The fix is the profile fallback chain — ollama is tried first (free), but if it drops, the job automatically falls back to anthropic.

```yaml
# ~/.hermes/profiles/jobs/config.yaml
fallback_providers:
  - provider: anthropic
    model: claude-sonnet-4-6
  - provider: opencode-go
    model: deepseek-v4-pro
```

No per-job model pinning needed — cron jobs inherit the chain.

## Provider hits monthly quota (429)

Symptom: `HTTP 429: Monthly usage limit reached`

Remove the exhausted provider from fallbacks:

```bash
# Edit ~/.hermes/profiles/jobs/config.yaml and remove the dead provider
hermes --profile jobs gateway restart
```

If opencode-go is exhausted (common), the chain will try ollama → anthropic and stop there.

## LinkedIn scraper extracts 0 jobs

Symptom: the scraper runs but finds nothing.

Possible causes:
1. **LinkedIn changed their DOM** — the selector `a.base-card__full-link` no longer works
   - Open a LinkedIn jobs search in a real browser, inspect the job card links
   - Update the selector in the `SEARCH_EXTRACT_JS` variable in `linkedin-scraper.py`

2. **Agent-browser not installed**: run `npx agent-browser` to auto-download

3. **IP blocked** — add a residential proxy (see doc 05)

## Google OAuth token expires every 7 days

Symptom: `REFRESH_FAILED` or `NOT_AUTHENTICATED` errors in cron jobs

Cause: Google Testing mode tokens expire every 7 days.

Fix: Publish your OAuth app (doesn't require Google review for personal use):
1. https://console.cloud.google.com/auth/overview
2. Click "Publish app" → confirm
3. Tokens now last 6 months

## Hermes sends output to wrong Telegram chat

Symptom: cron delivery goes to your DMs instead of the jobs group.

Fix: make sure `deliver` is set to the group chat ID:
```bash
hermes --profile jobs cron list
# If delivery is wrong, recreate with --deliver telegram:YOUR_GROUP_ID
```

> The group chat ID is always negative (e.g. `-1001234567890`). Your personal DM ID is positive.

## Bot doesn't see messages in group

Symptom: bot only responds to /commands in group, ignores regular messages.

Fix: Privacy Mode is designed this way — it's actually correct behavior. With privacy mode ON, bots only see /commands and @mentions. Cron deliveries still work because they're send operations. If you want the bot to see all messages, turn privacy mode OFF via @BotFather and remove + re-add the bot to the group.

## Cron delivers "Cronjob Response" header but no content

The cron ran but the agent's final response was just metadata.

Fix: add to your cron prompt:
```
Your FINAL RESPONSE is delivered directly to the user. 
Do NOT say "I will send..." or "Delivering now...".
Just write the message content directly as your response.
```

## Morning briefing has wrong date

Fix: add to your briefing prompt:
```
IMPORTANT: First run `date` to get today's exact date and day of week. 
Use that, never guess.
```

## Gateway service management

```bash
# Default profile
hermes gateway restart
systemctl --user status hermes-gateway

# Jobs profile
hermes --profile jobs gateway restart
systemctl --user status hermes-gateway-jobs
```

## Tool progress not showing in Telegram

By default, Hermes hides tool progress messages on Telegram (hardcoded platform default). To see what the agent is doing:

```bash
hermes config set display.platforms.telegram.tool_progress all
hermes --profile jobs config set display.platforms.telegram.tool_progress all
hermes gateway restart
hermes --profile jobs gateway restart
```

---

## Getting help

- [Hermes docs](https://hermes-agent.nousresearch.com/docs)
- [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- Run `hermes doctor` to check your setup
